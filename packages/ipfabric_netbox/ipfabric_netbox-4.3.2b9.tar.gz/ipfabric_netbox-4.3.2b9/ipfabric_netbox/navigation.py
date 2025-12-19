from django.utils.translation import gettext as _
from netbox.plugins import PluginMenu
from netbox.plugins import PluginMenuButton
from netbox.plugins import PluginMenuItem


sync_buttons = [
    PluginMenuButton(
        link="plugins:ipfabric_netbox:ipfabricsync_add",
        title=_("Add"),
        icon_class="mdi mdi-plus-thick",
        permissions=["ipfabric_netbox.add_ipfabricsync"],
    )
]

source_buttons = [
    PluginMenuButton(
        link="plugins:ipfabric_netbox:ipfabricsource_add",
        title=_("Add"),
        icon_class="mdi mdi-plus-thick",
        permissions=["ipfabric_netbox.add_ipfabricsource"],
    )
]

source = PluginMenuItem(
    link="plugins:ipfabric_netbox:ipfabricsource_list",
    link_text=_("Sources"),
    buttons=source_buttons,
    permissions=["ipfabric_netbox.view_ipfabricsource"],
)

snapshot = PluginMenuItem(
    link="plugins:ipfabric_netbox:ipfabricsnapshot_list",
    link_text=_("Snapshots"),
    permissions=["ipfabric_netbox.view_ipfabricsnapshot"],
)


ingestion = PluginMenuItem(
    link="plugins:ipfabric_netbox:ipfabricsync_list",
    link_text=_("Syncs"),
    buttons=sync_buttons,
    permissions=["ipfabric_netbox.view_ipfabricsync"],
)

tmg = PluginMenuItem(
    link="plugins:ipfabric_netbox:ipfabrictransformmapgroup_list",
    link_text=_("Transform Map Groups"),
    permissions=["ipfabric_netbox.view_ipfabrictransformmapgroup"],
    buttons=[
        PluginMenuButton(
            link="plugins:ipfabric_netbox:ipfabrictransformmapgroup_add",
            title=_("Add"),
            icon_class="mdi mdi-plus-thick",
            permissions=["ipfabric_netbox.add_ipfabrictransformmapgroup"],
        )
    ],
)

tm = PluginMenuItem(
    link="plugins:ipfabric_netbox:ipfabrictransformmap_list",
    link_text=_("Transform Maps"),
    permissions=["ipfabric_netbox.view_ipfabrictransformmap"],
    buttons=[
        PluginMenuButton(
            link="plugins:ipfabric_netbox:ipfabrictransformmap_add",
            title=_("Add"),
            icon_class="mdi mdi-plus-thick",
            permissions=["ipfabric_netbox.add_ipfabrictransformmap"],
        )
    ],
)
menu = PluginMenu(
    label="IP Fabric",
    icon_class="mdi mdi-cloud-sync",
    groups=(("IP Fabric", (source, snapshot, ingestion, tmg, tm)),),
)
