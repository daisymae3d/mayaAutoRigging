import maya.cmds as cmds
cmds.undoInfo(openChunk=True)

def parent_to_group():
    sel = cmds.ls(selection=True)

    if not sel:
        cmds.warning("No object selected.")
        return
    
    for obj in sel:
        group_name = obj + ("_offset")
        group_node = cmds.group(empty=True, name=group_name)
        
        cmds.parent(group_node, obj)
        
        cmds.makeIdentity(group_node, apply=True, translate=True, rotate=True, scale=True, normal=False)
        
        cmds.parent(group_node, world=True)
        
        cmds.parent(obj, group_node)

        if group_node == 'offset_ctrl_offset' :
            cmds.rename('offset_ctrl_offset', 'offset_grp')
        
        elif group_node == 'main_ctrl_offset':
            cmds.rename('main_ctrl_offset', 'ctrl_grp')
        
        else:
            pass
        
        print(f"Parented {obj} to {group_node}")

parent_to_group()

cmds.undoInfo(closeChunk=True)
