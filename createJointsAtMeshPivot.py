import maya.cmds as cmds
cmds.undoInfo(openChunk=True)
def createJointAtMeshPivot():
    root = 'root_jnt'
    sel = cmds.ls(sl=True)
    if not sel:
        cmds.warning("No object selected.")
        return

    for geo in cmds.ls(sl=True):
        piv = cmds.xform(geo, q=True, piv=True, ws=True)    
        cmds.select(clear=True)   
        cmds.joint(p=piv[0:3], n=geo + '%s' % "_jnt", rad=3)
        cmds.select(clear=True)

    cmds.select(clear=True)
    if not cmds.objExists(root):
        cmds.joint(a=True, n='root_jnt', rad=3)
        return
    cmds.select(clear=True)
createJointAtMeshPivot()
cmds.undoInfo(closeChunk=True)
