import bpy
from .. utils.registration import get_prefs, get_addon
from .. utils.group import get_group_polls


hypercursor = None


# MACHIN3tools SUB MENU

class MenuMACHIN3toolsObjectContextMenu(bpy.types.Menu):
    bl_idname = "MACHIN3_MT_machin3tools_object_context_menu"
    bl_label = "MACHIN3tools"

    def draw(self, context):
        global hypercursor

        if hypercursor is None:
            hypercursor = get_addon('HyperCursor')[0]

        layout = self.layout
        p = get_prefs()

        if p.activate_mirror:
            layout.operator("machin3.unmirror", text="Un-Mirror")

        if hypercursor:
            layout.operator("machin3.remove_array", text="Un-Array")
            layout.operator("machin3.remove_boolean", text="Un-Boolean")

        if p.activate_select:
            layout.operator("machin3.select_center_objects", text="Select Center Objects")
            layout.operator("machin3.select_wire_objects", text="Select Wire Objects")

        if p.activate_apply:
            layout.operator("machin3.apply_transformations", text="Apply Transformations")

        if p.activate_mesh_cut:
            layout.operator("machin3.mesh_cut", text="Mesh Cut")

        if p.activate_material_picker:
            layout.operator("machin3.material_picker", text="Material Picker")


class MenuMACHIN3toolsMeshContextMenu(bpy.types.Menu):
    bl_idname = "MACHIN3_MT_machin3tools_mesh_context_menu"
    bl_label = "MACHIN3tools"

    def draw(self, context):
        layout = self.layout

        if get_prefs().activate_thread:
            layout.operator("machin3.add_thread", text="Add Thread")


# AppendMaterilas SUB MENU

class MenuAppendMaterials(bpy.types.Menu):
    bl_idname = "MACHIN3_MT_append_materials"
    bl_label = "Append Materials"

    def draw(self, context):
        layout = self.layout

        names = [mat.name for mat in get_prefs().appendmats]

        if names:
            names.insert(0, "ALL")
        else:
            layout.label(text="No Materials added yet!", icon="ERROR")
            layout.label(text="Check MACHIN3tools prefs.", icon="INFO")


        for name in names:
            layout.operator_context = 'INVOKE_DEFAULT'

            if name == "ALL":
                layout.operator("machin3.append_material", text=name, icon="MATERIAL_DATA").name = name
                layout.separator()

            elif name == "---":
                layout.separator()

            else:
                mat = bpy.data.materials.get(name)
                icon_val = layout.icon(mat) if mat else 0

                layout.operator("machin3.append_material", text=name, icon_value=icon_val).name = name


# Group SUB MENU

class MenuGroupObjectContextMenu(bpy.types.Menu):
    bl_idname = "MACHIN3_MT_group_object_context_menu"
    bl_label = "Group"

    def draw(self, context):
        layout = self.layout
        m3 = context.scene.M3

        active_group, active_child, group_empties, groupable, ungroupable, addable, removable, selectable, duplicatable, groupifyable = get_group_polls(context)


        # SCENE PROPS

        row = layout.row()
        row.active = group_empties
        row.prop(m3, "group_select")

        row = layout.row()
        row.active = group_empties
        row.prop(m3, "group_recursive_select")

        row = layout.row()
        row.active = group_empties
        row.prop(m3, "group_hide")

        layout.separator()


        # CREATE / DESTRUCT

        row = layout.row()
        row.active = groupable
        row.operator("machin3.group", text="Group")

        row = layout.row()
        row.active = ungroupable
        row.operator("machin3.ungroup", text="Un-Group")

        row = layout.row()
        row.active = groupifyable
        row.operator("machin3.groupify", text="Groupify")

        layout.separator()


        # SELECT / DUPLICATE

        row = layout.row()
        row.active = selectable
        row.operator("machin3.select_group", text="Select Group")

        row = layout.row()
        row.active = duplicatable
        row.operator("machin3.duplicate_group", text="Duplicate Group")

        layout.separator()


        # ADD / REMOVE

        row = layout.row()
        row.active = addable and (active_group or active_child)
        row.operator("machin3.add_to_group", text="Add to Group")

        row = layout.row()
        row.active = removable
        row.operator("machin3.remove_from_group", text="Remove from Group")


# OBJECT CONTEXT MENU

def object_context_menu(self, context):
    layout = self.layout
    m3 = context.scene.M3
    p = get_prefs()

    if any([p.activate_mirror, p.activate_select, p.activate_apply, p.activate_mesh_cut, p.activate_material_picker]):
        layout.menu("MACHIN3_MT_machin3tools_object_context_menu")
        layout.separator()

    if p.activate_group:

        if p.use_group_sub_menu:
            layout.menu("MACHIN3_MT_group_object_context_menu")
            layout.separator()

        else:
            active_group, active_child, group_empties, groupable, ungroupable, addable, removable, selectable, duplicatable, groupifyable = get_group_polls(context)


            # SCENE PROPS

            if group_empties and any([m3.show_group_select, m3.show_group_recursive_select, m3.show_group_hide]):
                if m3.show_group_select:
                    layout.prop(m3, "group_select")

                if m3.show_group_recursive_select:
                    layout.prop(m3, "group_recursive_select")

                if m3.show_group_hide:
                    layout.prop(m3, "group_hide")

                if groupable or group_empties or selectable or duplicatable or groupifyable or (addable and (active_group or active_child)) or removable:

                    # custom spacer
                    row = layout.row()
                    row.scale_y = 0.3
                    row.label(text="")


            # GROUP

            if groupable:
                layout.operator_context = "INVOKE_REGION_WIN"
                layout.operator("machin3.group", text="Group")
                layout.operator_context = "EXEC_REGION_WIN"


            # UN-GROUP

            if ungroupable:
                layout.operator_context = "INVOKE_REGION_WIN"
                layout.operator("machin3.ungroup", text="(X) Un-Group")
                layout.operator_context = "EXEC_REGION_WIN"


            # GROUPIFY

            if groupifyable:
                layout.operator("machin3.groupify", text="Groupify")


            # SELECT

            if selectable:
                # custom spacer
                row = layout.row()
                row.scale_y = 0.3
                row.label(text="")

                layout.operator_context = "INVOKE_REGION_WIN"
                layout.operator("machin3.select_group", text="Select Group")
                layout.operator_context = "EXEC_REGION_WIN"

            if duplicatable:

                if not selectable:
                    # custom spacer
                    row = layout.row()
                    row.scale_y = 0.3
                    row.label(text="")

                layout.operator_context = "INVOKE_REGION_WIN"
                layout.operator("machin3.duplicate_group", text="Duplicate Group")
                layout.operator_context = "EXEC_REGION_WIN"


            # ADD and REMOVE

            if (addable and (active_group or active_child)) or removable:

                # custom spacer
                row = layout.row()
                row.scale_y = 0.3
                row.label(text="")

                if addable and (active_group or active_child):
                    layout.operator("machin3.add_to_group", text="Add to Group")

                if removable:
                    layout.operator("machin3.remove_from_group", text="Remove from Group")

            if group_empties or groupable or (addable and (active_group or active_child)) or removable or groupifyable:
                layout.separator()


# MESH CONTEXT MENU

def mesh_context_menu(self, context):
    layout = self.layout
    p = get_prefs()

    if any([p.activate_thread]):
        layout.menu("MACHIN3_MT_machin3tools_mesh_context_menu")
        layout.separator()


# ADD OBJECTS - QUADSPHERE

def add_object_buttons(self, context):
    self.layout.operator("machin3.quadsphere", text="Quad Sphere", icon='SPHERE')


# EXTRUDE - CURSOR SPIN

def cursor_spin(self, context):
    if getattr(bpy.types, 'MACHIN3_OT_cursor_spin', False):
        self.layout.operator("machin3.cursor_spin", text="Cursor Spin")


# MATERIAL PICKER HEADER

def material_pick_button(self, context):
    workspaces = [ws.strip() for ws in get_prefs().matpick_workspace_names.split(',')]

    if any([s in context.workspace.name for s in workspaces]):
        if getattr(bpy.types, 'MACHIN3_OT_material_picker', False):
            row = self.layout.row()
            row.scale_x = 1.25
            row.scale_y = 1.1
            # row.separator_spacer()
            row.separator(factor=get_prefs().matpick_spacing_obj if context.mode == 'OBJECT' else get_prefs().matpick_spacing_edit)
            row.operator("machin3.material_picker", text="", icon="EYEDROPPER")


# OUTLINER GROUP BUTTONS

def outliner_group_toggles(self, context):
    if getattr(bpy.types, 'MACHIN3_OT_group', False) and get_prefs().use_group_outliner_toggles:

        if get_group_polls(context)[2]:
            m3 = context.scene.M3
            self.layout.prop(m3, "group_select", text='', icon='GROUP_VERTEX')
            self.layout.prop(m3, "group_recursive_select", text='', icon='CON_SIZELIKE')
            self.layout.prop(m3, "group_hide", text='', icon='HIDE_ON' if m3.group_hide else 'HIDE_OFF', emboss=False)
