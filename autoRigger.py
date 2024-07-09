import maya.cmds as cmds
import maya.mel as mel

class SkelCreator:
    '''Class for creating biped skeleton'''
    def __init__(self):
        self.valid_strings = ["_Pelvis", "_Midsection", "_UpperTorso", "_Head", 
            "_Calf_Left", "_Thigh_Left", "_Foot_Left", "_Calf_Right", "_Thigh_Right", 
            "_Foot_Right", "_Shoulder_Left", "_Forearm_Left", "_Hand_Left", "_Shoulder_Right", 
            "_Forearm_Right", "_Hand_Right", 
            ]
        self.mesh = cmds.ls(sl=True,g=True)
    def invalid_names(self, mesh):
        '''Function which checks for invalid names that 
        don't match the list of valid strings in the geometry names'''
        gMainWindow = mel.eval('$tmpVar=$gMainWindow')
       # mesh = cmds.ls(sl=True,g=True)
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
            ("*_Thigh_Right_jnt", "*_Pelvis_jnt"),
            ("*_Calf_Right_jnt", "*_Thigh_Right_jnt"),
            ("*_Foot_Right_jnt", "*_Calf_Right_jnt"),
            ("*_Shoulder_Left_jnt", "*_UpperTorso_jnt"),
            ("*_Forearm_Left_jnt", "*_Shoulder_Left_jnt"),
            ("*_Hand_Left_jnt", "*_Forearm_Left_jnt"),
            ("*_Shoulder_Right_jnt", "*_UpperTorso_jnt"),
            ("*_Forearm_Right_jnt", "*_Shoulder_Right_jnt"),
            ("*_Hand_Right_jnt", "*_Forearm_Right_jnt")
            ]
    def create_joint_hierarchy(self):
        '''Parenting the joints to create the skeleton hierarchy'''
        for child_pattern , parent_pattern in self.joint_hierarchy:
            if parent_pattern:
                cmds.select(cmds.ls(child_pattern, type='joint'))
                cmds.select(cmds.ls(parent_pattern, type='joint'), add=True)
                cmds.parent(child_pattern, parent_pattern)
                cmds.select(clear=True)
            else:
                cmds.select(cmds.ls(child_pattern, type='joint'))
                cmds.delete()
                cmds.select(clear=True)

        cmds.select('*_Midsection_jnt', hi=True)
        cmds.select('root_jnt',"*_Pelvis_jnt", d=True)
        cmds.joint(edit=True, orientJoint='xyz', roo='xyz', secondaryAxisOrient='yup', 
            children=True, zeroScaleOrient=True)
        cmds.select(cl=True)
        cmds.select(cmds.ls(type="joint"))
        cmds.joint(edit=True, zeroScaleOrient=True)
        cmds.makeIdentity(apply=True, rotate=True)
        cmds.select(cl=True)

        jnt_grp = cmds.group(empty=True, name='jnt_grp')
        cmds.select('root_jnt', 'jnt_grp')
        cmds.parent()
        cmds.select(cl=True)

jointHierarchy = JointHierarchy()
jointHierarchy.create_joint_hierarchy()
cmds.select(cl=True)
cmds.select(cmds.ls(typ='joint'))

class ControlRig:
    '''Creating the rig controllers'''
    def __init__(self):
        pass
    def create_rig_controllers(self):
        '''Defining the conditions for which the controllers should be created'''
        root = 'root_jnt'
        jntSel = cmds.ls(sl=True)
        gMainWindow = mel.eval('$tmpVar=$gMainWindow')

        if not cmds.objExists(root):
            cmds.confirmDialog(icn = 'warning', button = ('OK'),  dismissString='No', m = "No existing root_jnt in scene.", p = gMainWindow)
            return

        for joint in jntSel:
            joint_translate = cmds.xform(joint, query=True, translation=True, worldSpace=True)
        
            ctrl_name = joint.replace("_jnt", "_ctrl")
            new_circl = cmds.circle(nr=(0,1,0), c=(0, 0, 0), r=0.2, n=ctrl_name)
            cmds.xform(new_circl, translation=joint_translate, worldSpace=True)#
            cmds.orientConstraint(joint, new_circl, mo=False)
            cmds.delete(cmds.orientConstraint(new_circl, mo=False))
            cmds.parentConstraint(new_circl, joint, mo=False)
            cmds.bakePartialHistory(new_circl,query=True,prePostDeformers=True )
            cmds.bakePartialHistory(new_circl,prePostDeformers=True )
            cmds.makeIdentity(apply=True, translate=True)
            cmds.transformLimits(tx = (0, 0),ty = (0, 0),tz = (0, 0), etx=(True, True), ety=(True, True), etz=(True, True ))
            cmds.transformLimits(sx = (1, 1),sy = (1, 1),sz = (1, 1), esx=(True, True), esy=(True, True), esz=(True, True ))

            shape_node = cmds.listRelatives(ctrl_name, shapes=True)[0]
            cmds.setAttr(f"{shape_node}.overrideEnabled", 1)
            cmds.setAttr(f"{shape_node}.overrideColor", 13)
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
        print("Controllers Created.")

controlRig = ControlRig()
controlRig.create_rig_controllers()

class OffsetGroup:
    def __init__(offset):
        offset.curves = cmds.ls(type='nurbsCurve', ni=True, o=True, r=True, l = True)
        offset.transforms = cmds.listRelatives(offset.curves, p=True, type = "transform")
        cmds.select(offset.transforms)
        offset.curveSel = cmds.ls(offset.transforms)
    

    def parent_to_group(offset):
        for offset.curves in offset.curveSel:
            group_name = offset.curves.replace("_ctrl", "_offset")
            group_node = cmds.group(empty=True, name=group_name)

            cmds.parent(group_node, offset.curves)
            cmds.makeIdentity(group_node, apply=True, translate=True, rotate=True, scale=True, normal=False)
            cmds.parent(group_node, world=True)
            cmds.parent(offset.curves, group_node)
            
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
            ("*_Hand_Right_ctrl", "*_Hand_Right_jnt")
        ]
        for child_pattern, parent_pattern in constrain_hierarchy:
                cmds.parentConstraint(child_pattern, parent_pattern, mo=False, weight=1)

        cmds.rename('offset_offset', "offset_grp")
        cmds.rename('main_offset', "ctrl_grp")
        cmds.select(cl=True)
        cmds.select(cl=True)


        control_hierarchy = [
            ("*_Pelvis_offset", 'offset_ctrl'),
            ("*_Midsection_offset", "*_Pelvis_ctrl"),
            ("*_UpperTorso_offset", "*_Midsection_ctrl"),
            ("*_Head_offset", "*_UpperTorso_ctrl"),
            ("*_Thigh_Left_offset", "*_Pelvis_ctrl"),
            ("*_Calf_Left_offset", "*_Thigh_Left_ctrl"),
            ("*_Foot_Left_offset", "*_Calf_Left_ctrl"),
            ("*_Thigh_Right_offset", "*_Pelvis_ctrl"),
            ("*_Calf_Right_offset", "*_Thigh_Right_ctrl"),
            ("*_Foot_Right_offset", "*_Calf_Right_ctrl"),
            ("*_Shoulder_Left_offset", "*_UpperTorso_ctrl"),
            ("*_Forearm_Left_offset", "*_Shoulder_Left_ctrl"),
            ("*_Hand_Left_offset", "*_Forearm_Left_ctrl"),
            ("*_Shoulder_Right_offset", "*_UpperTorso_ctrl"),
            ("*_Forearm_Right_offset", "*_Shoulder_Right_ctrl"),
            ("*_Hand_Right_offset", "*_Forearm_Right_ctrl")
        ]

        for child_pattern, parent_pattern in control_hierarchy:
            if parent_pattern:
                child = cmds.ls(child_pattern, type='transform')
                parent = cmds.ls(parent_pattern, type='transform')
                if child and parent:
                    cmds.select(child)
                    cmds.select(parent, add=True)
                    cmds.parent()
                    cmds.select(clear=True)
            else:
                child = cmds.ls(child_pattern, type='transform')
                if child:
                    cmds.select(child)
                    cmds.delete()
                    cmds.select(clear=True)
        print(f"Parented controls to respective offset groups.")
        cmds.parent('offset_grp', 'main_ctrl')
offsetGroup = OffsetGroup()
offsetGroup.parent_to_group()

class SkinningRig:
    def __init__(skinRig):
        skinRig.joint = cmds.select(cmds.ls(type="joint"))
        skinRig.geo = cmds.ls(g=True)

    def find_existing_skinCluster(skinRig, geo):
        history = cmds.listHistory(geo)
        skinClusters = cmds.ls(history, type='skinCluster')
        if skinClusters:
            return skinClusters[0]
        return None

    def skin_mesh(skinRig):
        skinJoints = cmds.ls(type="joint")
        mesh = skinRig.geo
            
        # for geo in mesh:
        #     existing_skinCluster = skinRig.find_existing_skinCluster(geo)
        #     if existing_skinCluster:
        #         print(f"Mesh {geo} already has a skinCluster: {existing_skinCluster}")
        #         continue
        #     cmds.skinCluster(skinJoints, geo, bm=1, sm=0, dr=5)
        #     print(f"Skinned {geo} with new skinCluster.")
        for skinRig.joint in skinJoints:

            skin_hierarchy = [
                ("*_Pelvis", '*_Pelvis_jnt'),
                ("*_Midsection", "*_Midsection_jnt"),
                ("*_UpperTorso", "*_UpperTorso_jnt"),
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
                ("*_Hand_Right", "*_Hand_Right_jnt")
            ]
            for child_pattern, parent_pattern in skin_hierarchy:
                cmds.skinCluster(child_pattern, parent_pattern, tsb=True, bm=3, mi=1, nw=1, wd=0, omi=True, dr=4, rui=True, hmf= 0.2, sm=0)
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
            ("*_Hand_Right_ctrl", "*_Hand_Right_jnt")
        ]
        for child_pattern, parent_pattern in constrain_hierarchy:
                cmds.parentConstraint(child_pattern, parent_pattern, mo=False, weight=1)
skinningRig = SkinningRig()
skinningRig.skin_mesh()


#select -r HK_Enemy_D_Hand_Right_ctrl.cv[0:7] ;
#rotate -r -p -69.632981cm 147.913552cm -5.993093cm -os -fo 0 0 -90.000007 ;
