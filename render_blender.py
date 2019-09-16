# A simple script that uses blender to render views of a single object by rotation the camera around it.
# Also produces depth map at the same time.
#
# Example:
# blender --background --python mytest.py -- --views 10 /path/to/my.obj
#

import argparse, sys, os
parser = argparse.ArgumentParser(description='Renders given obj file by rotation a camera around it.')
parser.add_argument('--views', type=int, default=1,
                    help='number of views to be rendered')
parser.add_argument('obj', type=str,
                    help='Path to the obj file to be rendered.')
parser.add_argument('--scale', type=float, default=1,
                    help='Scaling factor applied to model. Depends on size of mesh.')
parser.add_argument('--remove_doubles', type=bool, default=False,
                    help='Remove double vertices to improve mesh quality.')
parser.add_argument('--edge_split', type=bool, default=False,
                    help='Adds edge split filter.')
parser.add_argument('--depth_scale', type=float, default=1.4,
                    help='Scaling that is applied to depth. Depends on size of mesh. Try out various values until you get a good result. Ignored if format is OPEN_EXR.')
parser.add_argument('--color_depth', type=str, default='8',
                    help='Number of bit per channel used for output. Either 8 or 16.')
parser.add_argument('--format', type=str, default='PNG',
                    help='Format of files generated. Either PNG or OPEN_EXR')
parser.add_argument('--obj_image_easy_dir', type=str)
parser.add_argument('--obj_albedo_easy_dir', type=str)
parser.add_argument('--obj_depth_easy_dir', type=str)
parser.add_argument('--obj_normal_easy_dir', type=str)
parser.add_argument('--obj_image_hard_dir', type=str)
parser.add_argument('--obj_albedo_hard_dir', type=str)
parser.add_argument('--obj_depth_hard_dir', type=str)
parser.add_argument('--obj_normal_hard_dir', type=str)

argv = sys.argv[sys.argv.index("--") + 1:]
args = parser.parse_args(argv)
import numpy as np
import bpy
import cv2

# Set up rendering of depth map.
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
links = tree.links
# Add passes for additionally dumping albedo and normals.
bpy.context.scene.render.layers["RenderLayer"].use_pass_normal = True
bpy.context.scene.render.layers["RenderLayer"].use_pass_color = True
bpy.context.scene.render.image_settings.file_format = args.format
bpy.context.scene.render.image_settings.color_depth = args.color_depth

# Clear default nodes
for n in tree.nodes:
    tree.nodes.remove(n)

# Create input render layer node.
render_layers = tree.nodes.new('CompositorNodeRLayers')

depth_file_output = tree.nodes.new(type="CompositorNodeOutputFile")
depth_file_output.label = 'Depth Output'
if args.format == 'OPEN_EXR':
  links.new(render_layers.outputs['Depth'], depth_file_output.inputs[0])
else:
  # Remap as other types can not represent the full range of depth.
  map = tree.nodes.new(type="CompositorNodeMapValue")
  # Size is chosen kind of arbitrarily, try out until you're satisfied with resulting depth map.
  map.offset = [-0.7]
  map.size = [args.depth_scale]
  map.use_min = True
  map.min = [0]
  links.new(render_layers.outputs['Depth'], map.inputs[0])

  links.new(map.outputs[0], depth_file_output.inputs[0])

scale_normal = tree.nodes.new(type="CompositorNodeMixRGB")
scale_normal.blend_type = 'MULTIPLY'
# scale_normal.use_alpha = True
scale_normal.inputs[2].default_value = (0.5, 0.5, 0.5, 1)
links.new(render_layers.outputs['Normal'], scale_normal.inputs[1])

bias_normal = tree.nodes.new(type="CompositorNodeMixRGB")
bias_normal.blend_type = 'ADD'
# bias_normal.use_alpha = True
bias_normal.inputs[2].default_value = (0.5, 0.5, 0.5, 0)
links.new(scale_normal.outputs[0], bias_normal.inputs[1])

normal_file_output = tree.nodes.new(type="CompositorNodeOutputFile")
normal_file_output.label = 'Normal Output'
links.new(bias_normal.outputs[0], normal_file_output.inputs[0])

albedo_file_output = tree.nodes.new(type="CompositorNodeOutputFile")
albedo_file_output.label = 'Albedo Output'
links.new(render_layers.outputs['Color'], albedo_file_output.inputs[0])

# Delete default cube
bpy.data.objects['Cube'].select = True
bpy.ops.object.delete()
target_obj = None
bpy.ops.import_scene.obj(filepath=args.obj+'.obj')
for object in bpy.context.scene.objects:
    if object.name in ['Camera', 'Lamp']:
        continue
    bpy.context.scene.objects.active = object
    target_obj = object
    if args.scale != 1:
        bpy.ops.transform.resize(value=(args.scale,args.scale,args.scale))
        bpy.ops.object.transform_apply(scale=True)
    if args.remove_doubles:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode='OBJECT')
    if args.edge_split:
        bpy.ops.object.modifier_add(type='EDGE_SPLIT')
        bpy.context.object.modifiers["EdgeSplit"].split_angle = 1.32645
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="EdgeSplit")

# Make light just directional, disable shadows.
lamp = bpy.data.lamps['Lamp']
lamp.type = 'SUN'
lamp.shadow_method = 'NOSHADOW'
# Possibly disable specular shading:
lamp.use_specular = False

# Add another light source so stuff facing away from light is not completely dark
light_data = bpy.data.lamps.new(name="light_2", type='HEMI')
light_data.energy = 0.5
light2 = bpy.data.objects.new(name="light_2", object_data=light_data)
bpy.context.scene.objects.link(light2)
# make it active
bpy.context.scene.objects.active = light2

# light_data.use_specular = False
# bpy.data.objects['light_2'].rotation_euler = bpy.data.objects['Lamp'].rotation_euler
# bpy.data.objects['light_2'].rotation_euler[0] += 180
# bpy.data.objects['light_2'].location= (30, 0, 30)


# Add another light source so stuff facing away from light is not completely dark
bpy.ops.object.lamp_add(type='SUN')
lamp2 = bpy.data.lamps['Sun']
lamp2.shadow_method = 'NOSHADOW'
lamp2.use_specular = False
lamp2.energy = 0.5
# bpy.data.objects['Sun'].location = (0, 100, 0)
# bpy.data.objects['Sun'].rotation_euler = bpy.data.objects['Lamp'].rotation_euler
bpy.data.objects['Sun'].rotation_euler[0] += 180

def parent_obj_to_camera(b_camera):
    origin = (0.0, 0.0, 0.0)
    b_empty = bpy.data.objects.new("Empty", None)
    b_empty.location = origin
    b_camera.parent = b_empty  # setup parenting

    scn = bpy.context.scene
    scn.objects.link(b_empty)
    scn.objects.active = b_empty
    return b_empty

def unit(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v
    return v / norm

def camera_info(param):
    theta = np.deg2rad(param[0])
    phi = np.deg2rad(param[1])
    # print(param[0],param[1], theta, phi, param[6])

    camY = param[3]*np.sin(phi) * param[6]
    temp = param[3]*np.cos(phi) * param[6]
    camX = temp * np.cos(theta)
    camZ = temp * np.sin(theta)
    cam_pos = np.array([camX, camY, camZ])

    axisZ = cam_pos.copy()
    axisY = np.array([0,1,0])
    axisX = np.cross(axisY, axisZ)
    # axisY = np.cross(axisZ, axisX)

    # cam_mat = np.array([unit(axisX), unit(axisY), unit(axisZ)])
    print(camX, camY, camZ)
    return camX, -camZ, camY

def check_valid(file):
    img = cv2.imread(file, cv2.IMREAD_UNCHANGED)
    if np.sum(img[:,0,3]) + np.sum(img[:,-1,3]) + np.sum(img[0,:,3]) + np.sum(img[-1,:,3]) < 600:
        return True
    return False

scene = bpy.context.scene
scene.render.resolution_x = 224
scene.render.resolution_y = 224
scene.render.resolution_percentage = 100
scene.render.alpha_mode = 'TRANSPARENT'
cam = scene.objects['Camera']
cam_constraint = cam.constraints.new(type='TRACK_TO')
cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
cam_constraint.up_axis = 'UP_Y'
b_empty = parent_obj_to_camera(cam)
cam_constraint.target = b_empty

# scene.render.image_settings.file_format = 'PNG'  # set output format to .png

rotation_mode = 'XYZ'

stepsize = 360 / args.views


for output_node in [depth_file_output, normal_file_output, albedo_file_output]:
    output_node.base_path = ''
    output_node.format.file_format="PNG"

#
# obj_image_easy_dir, obj_albedo_easy_dir, obj_depth_easy_dir, obj_normal_easy_dir, obj_image_hard_dir, obj_albedo_hard_dir, obj_depth_hard_dir, obj_normal_hard_dir

obj_image_dir = [args.obj_image_easy_dir, args.obj_image_hard_dir]
obj_albedo_dir = [args.obj_albedo_easy_dir, args.obj_albedo_hard_dir]
obj_depth_dir = [args.obj_depth_easy_dir, args.obj_depth_hard_dir]
obj_normal_dir = [args.obj_normal_easy_dir, args.obj_normal_hard_dir]

target_obj.location = (0.0, 0.0, 0.0)


for j in range(2):
    current_rot_value = 0
    metastring = ""
    for i in range(args.views):
        current_rot_value += stepsize
        counter = 0
        while True:
            counter+=1
            if j == 1:
                if counter < 5:
                    shift_rand = np.random.rand(3) * 0.4 - 0.2
                    target_obj.location = (shift_rand[0], shift_rand[1], shift_rand[2])
                    print("target_obj.location", target_obj.location)
                else:
                    shift_rand = np.random.rand(3) * 0.2 - 0.1
                    target_obj.location = (shift_rand[0], shift_rand[1], shift_rand[2])
                    print("target_obj.location", target_obj.location)

            angle_rand = np.random.rand(3)
            y_rot = current_rot_value + angle_rand[0] * 10 - 5
            if j == 0:
                x_rot = 20 + angle_rand[1] * 10
            else:
                x_rot = angle_rand[1] * 45
            if j== 0:
                dist = 0.65 + angle_rand[2] * 0.35
            elif counter >= 5:
                dist = 0.75 + angle_rand[2] * 0.35
            else:
                dist = 0.60 + angle_rand[2] * 0.40
            param = [y_rot, x_rot, 0, dist, 35, 32, 1.75]
            camX, camY, camZ = camera_info(param)
            cam.location = (camX, camY, camZ)
            scene.render.filepath = obj_image_dir[j] + '/{0:02d}'.format(i)#
            depth_file_output.file_slots[0].path = obj_depth_dir[j] + '/{0:02d}'.format(i)#
            normal_file_output.file_slots[0].path = obj_normal_dir[j] + '/{0:02d}'.format(i)#
            albedo_file_output.file_slots[0].path = obj_albedo_dir[j] + '/{0:02d}'.format(i)#
            bpy.ops.render.render(write_still=True)  # render still
            if check_valid(scene.render.filepath+".png"):
                os.rename(obj_depth_dir[j] + '/{0:02d}'.format(i) + "0001.png",
                          obj_depth_dir[j] + '/{0:02d}'.format(i) + ".png")
                os.rename(obj_normal_dir[j] + '/{0:02d}'.format(i) + "0001.png",
                          obj_normal_dir[j] + '/{0:02d}'.format(i) + ".png")
                os.rename(obj_albedo_dir[j] + '/{0:02d}'.format(i) + "0001.png",
                          obj_albedo_dir[j] + '/{0:02d}'.format(i) + ".png")
                break
            else:
                print("regen: ", scene.render.filepath+".png")
        metastring = metastring + "[{},{},{},{},{},{},{},{},{},{}], \n" \
                     .format(y_rot, x_rot, 0, dist, 35, 32, 1.75,
                        target_obj.location[0], target_obj.location[1], target_obj.location[2])
    with open(obj_image_dir[j]+"/rendering_metadata.txt", "w") as f:
        f.write(metastring)
    with open(obj_albedo_dir[j]+"/rendering_metadata.txt", "w") as f:
        f.write(metastring)
    with open(obj_depth_dir[j]+"/rendering_metadata.txt", "w") as f:
        f.write(metastring)
    with open(obj_normal_dir[j]+"/rendering_metadata.txt", "w") as f:
        f.write(metastring)
