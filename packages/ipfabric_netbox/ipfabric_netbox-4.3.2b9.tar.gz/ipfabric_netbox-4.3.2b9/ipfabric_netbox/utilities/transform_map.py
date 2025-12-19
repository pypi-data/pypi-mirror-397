import importlib.resources
import json

from django.apps import apps as django_apps

# region Transform Map Creation

# These functions are used in the migration file to prepare the transform maps
# Because of this we have to use historical models
# see https://docs.djangoproject.com/en/5.1/topics/migrations/#historical-models


def build_fields(data, apps, db_alias):
    ContentType = apps.get_model("contenttypes", "ContentType")
    if "target_model" in data:
        ct = ContentType.objects.db_manager(db_alias).get_for_model(
            apps.get_model(
                data["target_model"]["app_label"],
                data["target_model"]["model"],
            )
        )
        data["target_model"] = ct
    elif "source_model" in data:
        ct = ContentType.objects.db_manager(db_alias).get_for_model(
            apps.get_model(
                data["source_model"]["app_label"],
                data["source_model"]["model"],
            )
        )
        data["source_model"] = ct
    return data


def build_transform_maps(data, apps: django_apps = None, db_alias: str = "default"):
    apps = apps or django_apps
    IPFabricTransformMap = apps.get_model("ipfabric_netbox", "IPFabricTransformMap")
    IPFabricTransformField = apps.get_model("ipfabric_netbox", "IPFabricTransformField")
    IPFabricRelationshipField = apps.get_model(
        "ipfabric_netbox", "IPFabricRelationshipField"
    )
    for tm in data:
        field_data = build_fields(tm["data"], apps, db_alias)
        tm_obj = IPFabricTransformMap.objects.using(db_alias).create(**field_data)
        for fm in tm["field_maps"]:
            field_data = build_fields(fm, apps, db_alias)
            IPFabricTransformField.objects.using(db_alias).create(
                transform_map=tm_obj, **field_data
            )
        for rm in tm["relationship_maps"]:
            relationship_data = build_fields(rm, apps, db_alias)
            IPFabricRelationshipField.objects.using(db_alias).create(
                transform_map=tm_obj, **relationship_data
            )


def get_transform_map() -> dict:
    for data_file in importlib.resources.files("ipfabric_netbox.data").iterdir():
        if data_file.name != "transform_map.json":
            continue
        with open(data_file, "rb") as data_file:
            return json.load(data_file)
    raise FileNotFoundError("'transform_map.json' not found in installed package")


# endregion
# region Transform Map Updating


class Record:
    """Base class for field and relationship records."""

    def __init__(
        self,
        coalesce: bool | None = None,
        old_template: str = None,
        new_template: str = None,
    ):
        self.coalesce = coalesce
        # Keep the original template here rather than loading it from transform_map.json
        # so our revert won’t break if that template ever changes.
        self.old_template = old_template
        self.new_template = new_template


class FieldRecord(Record):
    def __init__(
        self,
        source_field: str,
        target_field: str,
        new_source_field: str | None = None,
        new_target_field: str | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.source_field = source_field
        self.target_field = target_field
        self.new_source_field = new_source_field
        self.new_target_field = new_target_field


class RelationshipRecord(Record):
    def __init__(self, source_model: str, target_field: str, **kwargs):
        super().__init__(**kwargs)
        self.source_model = source_model
        self.target_field = target_field


class TransformMapRecord:
    def __init__(
        self,
        source_model: str,
        target_model: str,
        fields: tuple[FieldRecord, ...] = tuple(),
        relationships: tuple[RelationshipRecord, ...] = tuple(),
    ):
        self.source_model = source_model
        self.target_model = target_model
        self.fields = fields
        self.relationships = relationships


def do_change(
    apps, schema_editor, changes: tuple[TransformMapRecord, ...], forward: bool = True
):
    """Apply the changes, `forward` determines direction."""

    ContentType = apps.get_model("contenttypes", "ContentType")
    IPFabricTransformMap = apps.get_model("ipfabric_netbox", "IPFabricTransformMap")
    IPFabricTransformField = apps.get_model("ipfabric_netbox", "IPFabricTransformField")
    IPFabricRelationshipField = apps.get_model(
        "ipfabric_netbox", "IPFabricRelationshipField"
    )

    try:
        for change in changes:
            app, model = change.target_model.split(".")
            try:
                transform_map = IPFabricTransformMap.objects.get(
                    source_model=change.source_model,
                    target_model=ContentType.objects.get(app_label=app, model=model),
                )
            except IPFabricTransformMap.DoesNotExist:
                continue

            for field in change.fields:
                # Find the correct transform field.
                # Only 1 should be found if it exists, but keep it as queryset so we can filter and update.
                transform_field_qs = IPFabricTransformField.objects.filter(
                    transform_map=transform_map,
                    source_field=field.source_field
                    if forward
                    else field.new_source_field or field.source_field,
                    target_field=field.target_field
                    if forward
                    else field.new_target_field or field.target_field,
                )
                if not transform_field_qs.exists():
                    continue

                if field.old_template is not None and field.new_template is not None:
                    # First update the template if needed
                    transform_field_qs.filter(
                        template=field.old_template if forward else field.new_template
                    ).update(
                        template=field.new_template if forward else field.old_template
                    )

                if field.coalesce is not None:
                    # Next update coalesce if needed
                    transform_field_qs.filter(
                        coalesce=not field.coalesce if forward else field.coalesce
                    ).update(coalesce=field.coalesce if forward else not field.coalesce)

                if (
                    field.new_target_field is not None
                    or field.new_source_field is not None
                ):
                    # And at the end update source_field/target_field if needed
                    transform_field_qs.update(
                        source_field=field.new_source_field or field.source_field
                        if forward
                        else field.source_field,
                        target_field=field.new_target_field or field.target_field
                        if forward
                        else field.target_field,
                    )

            for relationship in change.relationships:
                s_app, s_model = relationship.source_model.split(".")
                source_model = ContentType.objects.get(app_label=s_app, model=s_model)

                # Find the correct relationship field.
                # Only 1 should be found if it exists, but keep it as queryset so we can filter and update.
                relationship_qs = IPFabricRelationshipField.objects.filter(
                    transform_map=transform_map,
                    source_model=source_model,
                    target_field=relationship.target_field,
                )
                if not relationship_qs.exists():
                    continue

                if (
                    relationship.old_template is not None
                    and relationship.new_template is not None
                ):
                    # First update the template if needed
                    relationship_qs.filter(
                        template=relationship.old_template
                        if forward
                        else relationship.new_template,
                    ).update(
                        template=relationship.new_template
                        if forward
                        else relationship.old_template
                    ),

                if relationship.coalesce is not None:
                    # Next update coalesce if needed
                    relationship_qs.filter(
                        coalesce=not relationship.coalesce
                        if forward
                        else relationship.coalesce,
                    ).update(
                        coalesce=relationship.coalesce
                        if forward
                        else not relationship.coalesce
                    ),

    except Exception as e:
        print(f"Error applying Transform map updates: {e}")


# endregion
