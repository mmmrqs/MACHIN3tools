from . tools import prettify_tool_name
from . system import printd
from . registration import get_addon_operator_idnames


addons = None

addon_abbr_mapping = {'MACHIN3tools': 'M3',
                      'DECALmachine': 'DM',
                      'MESHmachine': 'MM',
                      'HyperCursor': 'HC'}


def get_last_operators(context, debug=False):
    def get_parent_addon(idname):
        if idname.startswith('hops.'):
            return 'HO'
        elif idname.startswith('bc.'):
            return 'BC'

        for name, idnames in addons.items():
            if idname in idnames:
                return addon_abbr_mapping[name]
        return None

    global addons

    if addons is None:
        addons = {}

        for addon in ['MACHIN3tools', 'DECALmachine', 'MESHmachine', 'HyperCursor']:
            addons[addon] = get_addon_operator_idnames(addon)

        if debug:
            printd(addons)

    operators = []

    for op in context.window_manager.operators:
        idname = op.bl_idname.replace('_OT_', '.').lower()
        label = op.bl_label.replace('MACHIN3: ', '')
        addon = get_parent_addon(idname)
        prop = ''


        # skip pie menu calls

        if idname.startswith('machin3.call_'):
            continue

        # show props, special modes and custom labels

        # MACHIN3tools

        elif idname == 'machin3.set_tool_by_name':
            prop = prettify_tool_name(op.properties.get('name', ''))

        elif idname == 'machin3.switch_workspace':
            prop = op.properties.get('name', '')

        elif idname == 'machin3.switch_shading':
            toggled_overlays = getattr(op, 'toggled_overlays', False)
            prop = op.properties.get('shading_type', '').capitalize()

            if toggled_overlays:
                label = f"{toggled_overlays} Overlays"

        elif idname == 'machin3.edit_mode':
            toggled_object = getattr(op, 'toggled_object', False)
            label = 'Object Mode' if toggled_object else 'Edit Mesh Mode'

        elif idname == 'machin3.mesh_mode':
            mode = op.properties.get('mode', '')
            label = f"{mode.capitalize()} Mode"

        elif idname == 'machin3.smart_vert':
            if op.properties.get('slideoverride', ''):
                prop = 'SideExtend'

            elif op.properties.get('vertbevel', False):
                prop = 'VertBevel'

            else:
                modeint = op.properties.get('mode')
                mergetypeint = op.properties.get('mergetype')
                mousemerge = getattr(op, 'mousemerge', False)

                mode = 'Merge' if modeint== 0 else 'Connect'
                mergetype = 'AtMouse' if mousemerge else 'AtLast' if mergetypeint == 0 else 'AtCenter' if mergetypeint == 1 else 'Paths'

                if mode == 'Merge':
                    prop = mode + mergetype
                else:
                    pathtype = getattr(op, 'pathtype', False)
                    prop = mode + 'Pathsby' + pathtype.title()


        elif idname == 'machin3.smart_edge':
            if op.properties.get('is_knife_project', False):
                prop = 'KnifeProject'

            elif op.properties.get('sharp', False):
                mode = getattr(op, 'sharp_mode')

                if mode == 'SHARPEN':
                    prop = 'ToggleSharp'
                elif mode == 'CHAMFER':
                    prop = 'ToggleChamfer'
                elif mode == 'KOREAN':
                    prop = 'ToggleKoreanBevel'

            elif op.properties.get('offset', False):
                prop = 'KoreanBevel'

            elif getattr(op, 'draw_bridge_props'):
                prop = 'Bridge'

            elif getattr(op, 'is_knife'):
                prop = 'Knife'

            elif getattr(op, 'is_connect'):
                prop = 'Connect'

            elif getattr(op, 'is_starconnect'):
                prop = 'StarConnect'

            elif getattr(op, 'is_select'):
                mode = getattr(op, 'select_mode')

                if getattr(op, 'is_region'):
                    prop = 'SelectRegion'
                else:
                    prop = f'Select{mode.title()}'

            elif getattr(op, 'is_loop_cut'):
                prop = 'LoopCut'

            elif getattr(op, 'is_turn'):
                prop = 'Turn'

        elif idname == 'machin3.smart_face':
            mode = getattr(op, 'mode')

            if mode[0]:
                prop = "FaceFromVert"
            if mode[1]:
                prop = "FaceFromEdge"
            elif mode[2]:
                prop = "MeshFromFaces"

        elif idname == 'machin3.focus':
            if op.properties.get('method', 0) == 1:
                prop = 'LocalView'

        # DECALmachine

        elif idname == 'machin3.decal_library_visibility_preset':
            label = f"{label} {op.properties.get('name')}"
            prop = 'Store' if op.properties.get('store') else 'Recall'


        # MESHmachine

        elif idname == 'machin3.select':
            if getattr(op, 'vgroup', False):
                prop = 'VertexGroup'
            elif getattr(op, 'faceloop', False):
                prop = 'FaceLoop'
            else:
                prop = 'Loop' if op.properties.get('loop', False) else 'Sharp'

        elif idname == 'machin3.boolean':
            prop = getattr(op, 'method', False).capitalize()


        # HyperCursor

        elif idname == 'machin3.add_object_at_cursor':
            prop = getattr(op, 'type', False).capitalize()


        operators.append((addon, label, idname, prop))

    # if there aren#t any last ops, it's because you've just done an undo
    if not operators:
        operators.append((None, 'Undo', 'ed.undo', ''))

    if debug:
        for addon, label, idname, prop in operators:
            print(addon, label, f"({idname})", prop)

    return operators
