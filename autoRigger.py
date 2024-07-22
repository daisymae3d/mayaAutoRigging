import maya.cmds as cmds
import maya.mel as mel
import fnmatch

class SkelCreator:
    '''Class for creating biped skeleton'''
    def __init__(self):
        self.valid_strings = ["_Pelvis", "_Midsection", "_UpperTorso", "_Head", 
            "_Calf_Left", "_Thigh_Left", "_Foot_Left", "_Calf_Right", "_Thigh_Right", 
            "_Foot_Right", "_Shoulder_Left", "_Forearm_Left", "_Hand_Left", "_Shoulder_Right", 
            "_Forearm_Right", "_Hand_Right", "_Finger01_Left", "_Finger02_Left", "_Finger01_Right",
            "_Finger02_Right", "_Thumb_Right", "_Thumb_Left"
            ]
        self.feet = ["_Foot_Left", "_Foot_Right", 
            ]
        
        self.mesh = cmds.ls(sl=True,g=True)
    def invalid_names(self, mesh):
        '''Function which checks for invalid names that 
        don't match the list of valid strings in the geometry names'''
        gMainWindow = mel.eval('$tmpVar=$gMainWindow')
        mesh = cmds.ls(sl=True,g=True)
        invalid_meshes = []
        for geo in mesh:
            if not any(valid_str in geo for valid_str in self.valid_strings):
                invalid_meshes.append(geo)
        if invalid_meshes:
            name_warning = cmds.confirmDialog(icn = 'warning', button = ('Confirm', 'Cancel'), defaultButton='Confirm', cancelButton='Cancel', dismissString='No', parent=gMainWindow, m = ("Object doesn't contain correct naming convention, or isn't part of the body mesh. Would you still like to continue? Joint for this mesh will not be created. See Script Editor for list of objects."))
            print("Invalid Mesh Names:", invalid_meshes)
            if name_warning == 'Cancel':
                print('Operation Cancelled')
                return True
        return False
    def create_skeleton(self, geo_sel):
        '''Function which creates skeleton'''
        gMainWindow = mel.eval('$tmpVar=$gMainWindow')
        geo_sel = cmds.ls(sl=True)
        if not cmds.objExists('geo_grp'):
            cmds.group(geo_sel, n='geo_grp')
        if len(cmds.ls(type='joint')) > 0:
            cmds.confirmDialog(icn = 'warning', button = ('OK'),  dismissString='No',
            m = "Already pre-existing joints in the scene. Please remove these joints.", parent=gMainWindow)
            cmds.select(cl=True)
            return

        if not geo_sel:
            cmds.confirmDialog(icn = 'warning', button = ('OK'),
            dismissString='Cancel', m = "No mesh selected.", parent=gMainWindow)
            return None
        if self.invalid_names(geo_sel):
            return
        
        cmds.select('*_Foot_Left', '*_Foot_Right') 
        footsel = cmds.ls(sl=True)
        for geo in footsel:
            if any(valid_str in geo for valid_str in self.feet):
                piv = cmds.xform(geo, q=True, piv=True, ws=True)
                cmds.select(clear=True)
                cmds.joint(p=piv[0:3], rad=3, n=geo + 'Base' + '%s' % "_jnt")
                cmds.move(y=-piv[1])
                cmds.joint(p=piv[0:3], rad=3, n=geo + 'Toe' + '%s' % "_jnt")
                cmds.move(0,0,0.2, wd = True, os = True)
                cmds.select(clear=True)
        for geo in geo_sel:
            if any(valid_str in geo for valid_str in self.valid_strings):
                piv = cmds.xform(geo, q=True, piv=True, ws=True,)   
                cmds.select(clear=True)
                cmds.joint(p=piv[0:3], n=geo + '%s' % "_jnt", rad=3)
                cmds.joint(edit=True, orientJoint='xyz', roo='xyz', 
                secondaryAxisOrient='yup', children=True, zeroScaleOrient=True)
                cmds.select(clear=True)

        cmds.select(clear=True)
        cmds.joint(a=True, n='root_jnt', rad=3)
        cmds.select(clear=True)
            

skelCreator = SkelCreator()
geosel = cmds.ls(sl=True)
skelCreator.create_skeleton(geosel)
cmds.select(clear=True)

class JointHierarchy:
    '''Creating the hierarchy of which the skeleton should follow'''
    def __init__(self):
        self.joint_hierarchy = [
            ("*_Pelvis_jnt", 'root_jnt'),
            ("*_Midsection_jnt", "*_Pelvis_jnt"),
            ("*_UpperTorso_jnt", "*_Midsection_jnt"),
            ("*_Head_jnt", "*_UpperTorso_jnt"),
            ("*_Thigh_Left_jnt", "*_Pelvis_jnt"),
            ("*_Calf_Left_jnt", "*_Thigh_Left_jnt"),
            ("*_Foot_Left_jnt", "*_Calf_Left_jnt"),
            ("*_Foot_LeftBase_jnt", "*_Foot_Left_jnt"),
            ("*_Thigh_Right_jnt", "*_Pelvis_jnt"),
            ("*_Calf_Right_jnt", "*_Thigh_Right_jnt"),
            ("*_Foot_Right_jnt", "*_Calf_Right_jnt"),
            ("*_Foot_RightBase_jnt", "*_Foot_Right_jnt"),
            ("*_Shoulder_Left_jnt", "*_UpperTorso_jnt"),
            ("*_Forearm_Left_jnt", "*_Shoulder_Left_jnt"),
            ("*_Hand_Left_jnt", "*_Forearm_Left_jnt"),
            ("*_Shoulder_Right_jnt", "*_UpperTorso_jnt"),
            ("*_Forearm_Right_jnt", "*_Shoulder_Right_jnt"),
            ("*_Hand_Right_jnt", "*_Forearm_Right_jnt"),
            ("*_Thumb_Right_jnt", "*_Hand_Right_jnt"),
            ("*_Finger02_Right_jnt", "*_Hand_Right_jnt"),
            ("*_Finger01_Right_jnt", "*_Hand_Right_jnt"),
            ("*_Thumb_Left_jnt", "*_Hand_Left_jnt"),
            ("*_Finger02_Left_jnt", "*_Hand_Left_jnt"),
            ("*_Finger01_Left_jnt", "*_Hand_Left_jnt"),
            ]
        self.extremities = [
             "*_Finger01_Left_jnt", "*_Finger02_Left_jnt", 
             "*_Finger01_Right_jnt", "*_Finger02_Right_jnt"
        ]
    def create_joint_hierarchy(self):
        '''Parenting the joints to create the skeleton hierarchy'''
        for child_pattern , parent_pattern in self.joint_hierarchy:
            child = cmds.ls(child_pattern, type='joint')
            parent = cmds.ls(parent_pattern, type='joint')
            if child and parent:
                for child, parent in zip(child, parent):
                    cmds.parent(child, parent)
                    cmds.select(clear=True)

        if cmds.ls('*_Midsection_jnt'):
            cmds.select('*_Midsection_jnt', hi=True)
            cmds.select('root_jnt', "*_Pelvis_jnt", d=True)
            cmds.joint(edit=True, orientJoint='xyz', roo='xyz', secondaryAxisOrient='yup', 
            children=True, zeroScaleOrient=True)
        if cmds.ls(type="joint"):
            cmds.select(cmds.ls(type="joint"))
            cmds.joint(edit=True, zeroScaleOrient=True)
            cmds.makeIdentity(apply=True, rotate=True)
        cmds.select(cl=True)

        if not cmds.objExists('jnt_grp'):
            if cmds.objExists('root_jnt'):
                cmds.group(empty=True, name='jnt_grp')
                cmds.select('root_jnt', 'jnt_grp')
                cmds.parent()
        cmds.select(cl=True)
        list = self.extremities
        for i in range(1, len(list), 2):
            cmds.select(self.extremities[i], hi=True)
            cmds.joint(edit=True, orientJoint='none', zeroScaleOrient=True)
        cmds.select(cl=True)
        for i in range(0, len(list), 2):
            cmds.select(self.extremities[i], hi=True)
            parent = cmds.listRelatives(p=True)
            cmds.select(parent)
            cmds.select(self.extremities[i], hi=True, add = True)
            aim = cmds.aimConstraint(aim=(-1, 0 ,0), u=(0, 1, 0), wut= 'vector', wu = (0,1,0))
            cmds.delete(aim)
            cmds.makeIdentity(apply=True, rotate=True)
        cmds.select(cl=True)

jointHierarchy = JointHierarchy()
jointHierarchy.create_joint_hierarchy()
cmds.select(cl=True)
cmds.select(cmds.ls(typ='joint'))
#cmds.select('*_FootLeftBase_jnt','*_FootRightBase_jnt','*_FootLeftToe_jnt','*_FootRightToe_jnt', d=True)

class ControlRig:
    '''Creating the rig controllers'''
    def __init__(self):
         self.joints = ["*_Pelvis_jnt", "*_Midsection_jnt", "*_UpperTorso_jnt", "*_Head_jnt", 
            "*_Calf_Left_jnt", "*_Thigh_Left_jnt", "*_Foot_Left_jnt", "*_Calf_Right_jnt", "*_Thigh_Right_jnt", 
            "*_Foot_Right_jnt", "*_Shoulder_Left_jnt", "*_Forearm_Left_jnt", "*_Hand_Left_jnt", "*_Shoulder_Right_jnt", 
            "*_Forearm_Right_jnt", "*_Hand_Right_jnt", "*_Finger01_Left_jnt", "*_Finger02_Left_jnt", "*_Finger01_Right_jnt",
            "*_Finger02_Right_jnt", "*_Thumb_Right_jnt", "*_Thumb_Left_jnt"
            ]
         self.joint_rotate = ["*_Midsection_jnt", "*_Shoulder_Left_jnt", "*_Forearm_Left_jnt", "*_Hand_Left_jnt", "*_Shoulder_Right_jnt", 
          "*_Forearm_Right_jnt", "*_Hand_Right_jnt", "*_Finger01_Left_jnt", "*_Finger02_Left_jnt", "*_Finger01_Right_jnt",
          "*_Finger02_Right_jnt", "*_Thumb_Right_jnt", "*_Thumb_Left_jnt"
            ]
         self.feet = ["*_Foot_LeftBase_jnt", "*_Foot_RightBase_jnt", "*_Foot_LeftToe_jnt", "*_Foot_RightToe_jnt"
            ]
    def create_rig_controllers(self):
        '''Defining the conditions for which the controllers should be created'''
        root = 'root_jnt'
        jntSel = cmds.ls(sl=True)
        gMainWindow = mel.eval('$tmpVar=$gMainWindow')

        if not cmds.objExists(root):
            cmds.confirmDialog(icn = 'warning', button = ('OK'),  dismissString='No', m = "No existing root_jnt in scene.", p = gMainWindow)
            return

        for joint in jntSel:
            if any(fnmatch.fnmatch(joint, pattern) for pattern in self.feet):
                continue
            if any(fnmatch.fnmatch(joint, pattern) for pattern in self.joint_rotate):
                    joint_translate = cmds.xform(joint, query=True, translation=True, worldSpace=True)
                
                    ctrl_name = joint.replace("_jnt", "_ctrl")
                    new_circl = cmds.circle(nr=(1,0,0), c=(0, 0, 0), r=0.2, n=ctrl_name)
                    cmds.xform(new_circl, translation=joint_translate, worldSpace=True)
                    cmds.orientConstraint(joint, new_circl, mo=False)
                    cmds.delete(cmds.orientConstraint(new_circl, mo=False))
                    cmds.parentConstraint(new_circl, joint, mo=False)
                    cmds.bakePartialHistory(new_circl,query=True,prePostDeformers=True )
                    cmds.bakePartialHistory(new_circl,prePostDeformers=True )
                    cmds.makeIdentity(apply=True, translate=True)
                    cmds.transformLimits(sx = (1, 1),sy = (1, 1),sz = (1, 1), esx=(True, True), esy=(True, True), esz=(True, True ))

                    shape_node = cmds.listRelatives(ctrl_name, shapes=True)[0]
                    cmds.setAttr(f"{shape_node}.overrideEnabled", 1)
                    cmds.setAttr(f"{shape_node}.overrideColor", 13)
                    cmds.select(cl=True)

            else:
                joint_translate = cmds.xform(joint, query=True, translation=True, worldSpace=True)
            
                ctrl_name = joint.replace("_jnt", "_ctrl")
                new_circl = cmds.circle(nr=(0,1,0), c=(0, 0, 0), r=0.2, n=ctrl_name)
                cmds.xform(new_circl, translation=joint_translate, worldSpace=True)
                cmds.orientConstraint(joint, new_circl, mo=False)
                cmds.delete(cmds.orientConstraint(new_circl, mo=False))
                cmds.parentConstraint(new_circl, joint, mo=False)
                cmds.bakePartialHistory(new_circl,query=True,prePostDeformers=True )
                cmds.bakePartialHistory(new_circl,prePostDeformers=True )
                cmds.makeIdentity(apply=True, translate=True)
                cmds.transformLimits(sx = (1, 1),sy = (1, 1),sz = (1, 1), esx=(True, True), esy=(True, True), esz=(True, True ))

                shape_node = cmds.listRelatives(ctrl_name, shapes=True)[0]
                cmds.setAttr(f"{shape_node}.overrideEnabled", 1)
                cmds.setAttr(f"{shape_node}.overrideColor", 13)
                
        cmds.delete('*_UpperTorso_ctrl')
        cmds.delete('root_ctrl')
        cmds.select(cl=True)
        cmds.circle(nr=(0,1,0), c=(0, 0, 0), r=1.0, n='main_ctrl')
        cmds.setAttr('main_ctrl' + ".overrideEnabled", 1)
        cmds.setAttr('main_ctrl' + ".overrideColor", 13)
        cmds.circle(nr=(0,1,0), c=(0, 0, 0), r=0.8, n='offset_ctrl')
        cmds.setAttr('offset_ctrl' + ".overrideEnabled", 1)
        cmds.setAttr('offset_ctrl' + ".overrideColor", 17)
        cmds.parentConstraint('offset_ctrl', 'root_jnt', mo=False)

        cmds.select(cl=True)

        ctrl = cmds.ls(type = 'nurbsCurve')
        ctrl_list = cmds.listRelatives(ctrl, p=True, type = "transform")
        cmds.select(ctrl_list)
        cmds.select('main_ctrl', 'offset_ctrl',d=True)
        sel = cmds.ls(sl=True)
        for ctrl in sel:
            cmds.transformLimits(ctrl, tx = (0, 0),ty = (0, 0),tz = (0, 0), etx=(True, True), ety=(True, True), etz=(True, True ))
        cmds.select(cl=True)
        print("Controllers Created.")

controlRig = ControlRig()
controlRig.create_rig_controllers()

class OffsetGroup:
    def __init__(self):
        self.curves = cmds.ls(type='nurbsCurve', ni=True, o=True, r=True, l = True)
        self.transforms = cmds.listRelatives(self.curves, p=True, type = "transform")
        cmds.select(self.transforms)
        self.curveSel = cmds.ls(self.transforms)
    

    def parent_to_group(self):
        for self.curves in self.curveSel:
            group_name = self.curves.replace("_ctrl", "_offset")
            group_node = cmds.group(empty=True, name=group_name)

            cmds.parent(group_node, self.curves)
            cmds.makeIdentity(group_node, apply=True, translate=True, rotate=True, scale=True, normal=False)
            cmds.parent(group_node, world=True)
            cmds.parent(self.curves, group_node)

        if cmds.objExists('offset_offset'):
            cmds.rename('offset_offset', "offset_grp")
        if cmds.objExists('main_offset'):
            cmds.rename('main_offset', "ctrl_grp")
        cmds.select(cl=True)

        control_hierarchy = [
            ("*_Pelvis_offset", 'offset_ctrl'),
            ("*_Midsection_offset", "*_Pelvis_ctrl"),
            ("*_Head_offset", "*_Midsection_ctrl"),
            ("*_Thigh_Left_offset", "offset_ctrl"),
            ("*_Calf_Left_offset", "*_Thigh_Left_ctrl"),
            ("*_Foot_Left_offset", "*_Calf_Left_ctrl"),
            ("*_Thigh_Right_offset", "offset_ctrl"),
            ("*_Calf_Right_offset", "*_Thigh_Right_ctrl"),
            ("*_Foot_Right_offset", "*_Calf_Right_ctrl"),
            ("*_Shoulder_Left_offset", "*_Midsection_ctrl"),
            ("*_Forearm_Left_offset", "*_Shoulder_Left_ctrl"),
            ("*_Hand_Left_offset", "*_Forearm_Left_ctrl"),
            ("*_Shoulder_Right_offset", "*_Midsection_ctrl"),
            ("*_Forearm_Right_offset", "*_Shoulder_Right_ctrl"),
            ("*_Hand_Right_offset", "*_Forearm_Right_ctrl"),
            ("*_Thumb_Right_offset", "*_Hand_Right_ctrl"),
            ("*_Finger01_Right_offset", "*_Hand_Right_ctrl"),
            ("*_Finger02_Right_offset", "*_Hand_Right_ctrl"),
            ("*_Thumb_Left_offset", "*_Hand_Left_ctrl"),
            ("*_Finger01_Left_offset", "*_Hand_Left_ctrl"),
            ("*_Finger02_Left_offset", "*_Hand_Left_ctrl"),
        ]
        for child_pattern, parent_pattern in control_hierarchy:
            children = cmds.ls(child_pattern, type='transform')
            parents = cmds.ls(parent_pattern, type='transform')
            if children and parents:
                for child, parent in zip(children, parents):
                    cmds.parent(child, parent)
        if cmds.objExists('offset_grp') and cmds.objExists('main_ctrl'):
            cmds.parent('offset_grp', 'main_ctrl')
        print(f"Parented controls to respective offset groups.")
offsetGroup = OffsetGroup()
offsetGroup.parent_to_group()

class SkinningRig:
    def __init__(self):
        self.joint = cmds.select(cmds.ls(type="joint"))
        self.geo = cmds.ls(g=True)

    def find_existing_skinCluster(self, geo):
        history = cmds.listHistory(geo)
        skinClusters = cmds.ls(history, type='skinCluster')
        if skinClusters:
            return skinClusters[0]
        return None

    def skin_mesh(self):
        skinJoints = cmds.ls(type="joint")
        for self.joint in skinJoints:

            skin_hierarchy = [
                ("*_Pelvis", '*_Pelvis_jnt'),
                ("*_Midsection", "*_Pelvis_jnt"),
                ("*_UpperTorso", "*_Midsection_jnt"),
                ("*_Head", "*_Head_jnt"),
                ("*_Thigh_Left", "*_Thigh_Left_jnt"),
                ("*_Calf_Left", "*_Calf_Left_jnt"),
                ("*_Foot_Left", "*_Foot_Left_jnt"),
                ("*_Thigh_Right", "*_Thigh_Right_jnt"),
                ("*_Calf_Right", "*_Calf_Right_jnt"),
                ("*_Foot_Right", "*_Foot_Right_jnt"),
                ("*_Shoulder_Left", "*_Shoulder_Left_jnt"),
                ("*_Forearm_Left", "*_Forearm_Left_jnt"),
                ("*_Hand_Left", "*_Hand_Left_jnt"),
                ("*_Shoulder_Right", "*_Shoulder_Right_jnt"),
                ("*_Forearm_Right", "*_Forearm_Right_jnt"),
                ("*_Hand_Right", "*_Hand_Right_jnt"),
                ("*_Thumb_Right", "*_Thumb_Right_jnt"),
                ("*_Finger01_Right", "*_Finger01_Right_jnt"),
                ("*_Finger02_Right", "*_Finger02_Right_jnt"),
                ("*_Thumb_Right", "*_Thumb_Right_jnt"),
                ("*_Finger01_Left", "*_Finger01_Left_jnt"),
                ("*_Finger02_Left", "*_Finger02_Left_jnt"),
                ]
            for child_pattern, parent_pattern in skin_hierarchy:
                children = cmds.ls(child_pattern, type='transform')
                parents = cmds.ls(parent_pattern, type='joint')
                if children and parents:
                    for child, parent in zip(children, parents):
                        existing_skinCluster = self.find_existing_skinCluster(child)
                        if existing_skinCluster:
                            pass
                        else:
                            # Create new skinCluster
                            cmds.skinCluster(child, parent, tsb=True, bm=3, mi=1, nw=1, wd=0, omi=True, dr=4, rui=True, hmf=0.2, sm=0)

        constrain_hierarchy = [
            ("*_Pelvis_ctrl", '*_Pelvis_jnt'),
            ("*_Midsection_ctrl", "*_Midsection_jnt"),
            ("*_UpperTorso_ctrl", "*_UpperTorso_jnt"),
            ("*_Head_ctrl", "*_Head_jnt"),
            ("*_Thigh_Left_ctrl", "*_Thigh_Left_jnt"),
            ("*_Calf_Left_ctrl", "*_Calf_Left_jnt"),
            ("*_Foot_Left_ctrl", "*_Foot_Left_jnt"),
            ("*_Thigh_Right_ctrl", "*_Thigh_Right_jnt"),
            ("*_Calf_Right_ctrl", "*_Calf_Right_jnt"),
            ("*_Foot_Right_ctrl", "*_Foot_Right_jnt"),
            ("*_Shoulder_Left_ctrl", "*_Shoulder_Left_jnt"),
            ("*_Forearm_Left_ctrl", "*_Forearm_Left_jnt"),
            ("*_Hand_Left_ctrl", "*_Hand_Left_jnt"),
            ("*_Shoulder_Right_ctrl", "*_Shoulder_Right_jnt"),
            ("*_Forearm_Right_ctrl", "*_Forearm_Right_jnt"),
            ("*_Hand_Right_ctrl", "*_Hand_Right_jnt"),
            ("*_Thumb_Right_ctrl", "*_Thumb_Right_jnt"),
            ("*_Finger01_Right_ctrl", "*_Finger01_Right_jnt"),
            ("*_Finger02_Right_ctrl", "*_Finger02_Right_jnt"),
            ("*_Thumb_Right_ctrl", "*_Thumb_Right_jnt"),
            ("*_Finger01_Left_ctrl", "*_Finger01_Left_jnt"),
            ("*_Finger02_Left_ctrl", "*_Finger02_Left_jnt"),
            ]
        for child_pattern, parent_pattern in constrain_hierarchy:
            children = cmds.ls(child_pattern, type='transform')
            parents = cmds.ls(parent_pattern, type='joint')
            if children and parents:
                for child, parent in zip(children, parents):
                    cmds.parentConstraint(child_pattern, parent_pattern, mo=False, weight=1)
skinningRig = SkinningRig()
skinningRig.skin_mesh()
