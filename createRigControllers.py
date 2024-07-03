import maya.cmds as cmds
cmds.undoInfo(openChunk=True)
def createRigControllers():
    # For this to work, there cannot be another joint chain
    # with the same names in the scene.
    sel = cmds.ls(sl=True)
    for joint in sel:
        joint_translate = cmds.xform(joint, query=True, translation=True, worldSpace=True)
        
        ctrl_name = joint.replace('_jnt', '_ctrl')
        newCircl = cmds.circle(nr=(0,1,0), c=(0, 0, 0), r=0.2, n=ctrl_name)
        cmds.xform(newCircl, translation=joint_translate, worldSpace=True)
        cmds.bakePartialHistory(newCircl,query=True,prePostDeformers=True )
        cmds.bakePartialHistory(newCircl,prePostDeformers=True )
        cmds.makeIdentity(apply=True, translate=True)
        shape_node = cmds.listRelatives(ctrl_name, shapes=True)[0]
        cmds.setAttr(f"{shape_node}.overrideEnabled", 1)
        cmds.setAttr(f"{shape_node}.overrideColor", 13)

createRigControllers()
cmds.undoInfo(closeChunk=True)
