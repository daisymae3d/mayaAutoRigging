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

        if cmds.objExists(group_name):
            cmds.warning("Name already exists for offset group.")
            break
        
        cmds.parent(group_node, obj)
        
        cmds.makeIdentity(group_node, apply=True, translate=True, rotate=True, scale=True, normal=False)
        
        cmds.parent(group_node, world=True)
        
        cmds.parent(obj, group_node)
        
        print(f"Parented {obj} to {group_node}")

parent_to_group()

cmds.undoInfo(closeChunk=True)
