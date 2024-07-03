from maya import cmds

def locatorCreator():
    sel = cmds.ls(sl=True)

    for obj in sel:
        locator_pos = cmds.xform(obj, q=True, rp=True, ws = True)
        locator_name = obj.replace("_ctrl", "_loc")
        locator = cmds.spaceLocator(n=locator_name)[0]
        locator_shape = cmds.listRelatives(locator, shapes=True)[0]
        cmds.xform(locator, translation=locator_pos, worldSpace = True)
        cmds.setAttr(f'{locator_shape}.localScaleX', 0.001)
        cmds.setAttr(f'{locator_shape}.localScaleY', 0.001)
        cmds.setAttr(f'{locator_shape}.localScaleZ', 0.001)

        cmds.parent(locator, obj)
        cmds.makeIdentity(locator, apply=True, translate=True, rotate=True, scale=True, normal=False)
        cmds.parent(locator, world=True)
        cmds.parent(obj, locator)

locatorCreator()
