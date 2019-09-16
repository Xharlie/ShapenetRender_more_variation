import os
import sys
import time
from joblib import Parallel, delayed
import argparse

#
parser = argparse.ArgumentParser()
parser.add_argument('--model_root_dir', type=str, default="/ssd1/datasets/ShapeNet/ShapeNetCore.v1")
parser.add_argument('--render_root_dir', type=str, default="/ssd1/datasets/ShapeNet/ShapeNetRendering.v1")
parser.add_argument('--filelist_dir', type=str, default="./filelists_half")
parser.add_argument('--blender_location', type=str, default="~/dev/blender/blender")
parser.add_argument('--num_thread', type=int, default=10, help='1/3 of the CPU number')
parser.add_argument('--shapenetversion', type=str, default="v1", help='v1 or v2')
parser.add_argument('--debug', type=bool, default=False)
FLAGS = parser.parse_args()

model_root_dir = FLAGS.model_root_dir
render_root_dir = FLAGS.render_root_dir
filelist_dir = FLAGS.filelist_dir

# cat_ids = {
#         "watercraft": "04530566",
#         "rifle": "04090263",
#         "display": "03211117",
#         "lamp": "03636649",
#         "speaker": "03691459",
#         "cabinet": "02933112",
#         "chair": "03001627",
#         "bench": "02828884",
#         "car": "02958343",
#         "airplane": "02691156",
#         "sofa": "04256520",
#         "table": "04379243",
#         "phone": "04401088"
#     }

def gen_obj(model_root_dir, cat_id, obj_id):
	if FLAGS.shapenetversion == "v2":
		objpath = os.path.join(model_root_dir, cat_id, obj_id, "models", "model_normalized")
	else:
		objpath = os.path.join(model_root_dir, cat_id, obj_id, "model") #for v1
	obj_image_easy_dir = os.path.join(render_root_dir, "image", cat_id, obj_id, "easy")
	obj_albedo_easy_dir = os.path.join(render_root_dir, "albedo", cat_id, obj_id, "easy")
	obj_depth_easy_dir = os.path.join(render_root_dir, "depth", cat_id, obj_id, "easy")
	obj_normal_easy_dir = os.path.join(render_root_dir, "normal", cat_id, obj_id, "easy")
	obj_image_hard_dir = os.path.join(render_root_dir, "image", cat_id, obj_id, "hard")
	obj_albedo_hard_dir = os.path.join(render_root_dir, "albedo", cat_id, obj_id, "hard")
	obj_depth_hard_dir = os.path.join(render_root_dir, "depth", cat_id, obj_id, "hard")
	obj_normal_hard_dir = os.path.join(render_root_dir, "normal", cat_id, obj_id, "hard")
	os.makedirs(obj_image_easy_dir, exist_ok=True)
	os.makedirs(obj_albedo_easy_dir, exist_ok=True)
	os.makedirs(obj_depth_easy_dir, exist_ok=True)
	os.makedirs(obj_normal_easy_dir, exist_ok=True)
	os.makedirs(obj_image_hard_dir, exist_ok=True)
	os.makedirs(obj_albedo_hard_dir, exist_ok=True)
	os.makedirs(obj_depth_hard_dir, exist_ok=True)
	os.makedirs(obj_normal_hard_dir, exist_ok=True)
	if os.path.exists(os.path.join(obj_normal_hard_dir, "rendering_metadata.txt")):
		print("Exist!!!, skip %s %s" % (cat_id, obj_id))
	else:
		print("Start %s %s" % (cat_id, obj_id))
		if FLAGS.debug:
			os.system(FLAGS.blender_location + ' --background --python render_blender.py -- --views %d --obj_image_easy_dir %s --obj_albedo_easy_dir %s --obj_depth_easy_dir %s --obj_normal_easy_dir %s --obj_image_hard_dir %s --obj_albedo_hard_dir %s --obj_depth_hard_dir %s --obj_normal_hard_dir %s %s ' % (36, obj_image_easy_dir, obj_albedo_easy_dir, obj_depth_easy_dir, obj_normal_easy_dir, obj_image_hard_dir, obj_albedo_hard_dir, obj_depth_hard_dir, obj_normal_hard_dir, objpath))

		else:
			os.system(FLAGS.blender_location + ' --background --python render_blender.py -- --views %d --obj_image_easy_dir %s --obj_albedo_easy_dir %s --obj_depth_easy_dir %s --obj_normal_easy_dir %s --obj_image_hard_dir %s --obj_albedo_hard_dir %s --obj_depth_hard_dir %s --obj_normal_hard_dir %s %s > /dev/null 2>&1' % (36, obj_image_easy_dir, obj_albedo_easy_dir, obj_depth_easy_dir, obj_normal_easy_dir, obj_image_hard_dir, obj_albedo_hard_dir, obj_depth_hard_dir, obj_normal_hard_dir, objpath))

		print("Finished %s %s"%(cat_id, obj_id))
#

for filename in os.listdir(filelist_dir):
	if filename.endswith(".lst"):
		cat_id = filename.split(".")[0]
		file = os.path.join(filelist_dir, filename)
		lst = []
		with open(file) as f:
			content = f.read().splitlines()
			for line in content:
				lst.append(line)

		model_root_dir_lst = [model_root_dir for i in range(len(lst))]
		cat_id_lst = [cat_id for i in range(len(lst))]
		with Parallel(n_jobs=5) as parallel:
			parallel(delayed(gen_obj)(model_root_dir, cat_id, obj_id) for
					 model_root_dir, cat_id, obj_id in
					 zip(model_root_dir_lst, cat_id_lst, lst))
	print("Finished %s"%cat_id)


# if not os.path.exists(output_path):
#     os.makedirs(output_path)
# for objpath in objpaths:
# 	print objpath.split('/')[-3],
# 	tic = time.time()
# 	os.system('blender --background --python render_blender.py -- --output_folder %s %s > /dev/null 2>&1' % (output_path, objpath))
# 	print time.time()-tic





# def convertfilelst(filelist_dir):
# 	for filename in os.listdir(filelist_dir):
# 		if filename.endswith(".lst"):
# 			file = os.path.join(filelist_dir, filename)
# 			file_target = os.path.join(filelist_dir, filename[:8]+".lst")
# 			lst = []
# 			with open(file) as f:
# 				content = f.read().splitlines()
# 				for line in content:
# 					lst.append(line.split("/")[-1][:-3])
# 			with open(file_target, "w") as f:
# 				for obj in lst:
# 					f.write(obj+"\n")
#
# convertfilelst(filelist_dir)
