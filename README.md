# ShapenetRender_more_variation

## A new shapenet rendering 2D image dataset that also contains deph map, normal map and albedo map.

Please cite our paper[DISN: Deep Implicit Surface Network for High-quality Single-view 3D Reconstruction (NeurIPS 2019)](https://arxiv.org/abs/1905.10711) if you plan to download the rendered images or use our code to render by yourself.

``` 
@inProceedings{xu2019disn,
  title={DISN: Deep Implicit Surface Network for High-quality Single-view 3D Reconstruction},
  author={Xu, Qiangeng and Wang, Weiyue and Ceylan, Duygu and Mech, Radomir and Neumann, Ulrich},
  booktitle={NeurIPS},
  year={2019}
}
``` 
Code contact: [Qiangeng Xu*](https://xharlie.github.io/) and [Weiyue Wang*](https://weiyuewang.github.io/)

Also please cite [Shapenet's original paper](https://arxiv.org/abs/1512.03012) as well.

### Dataset Intro:
 The categories included are: 
    ```cat_ids = {
        "watercraft": "04530566",
        "rifle": "04090263",
        "display": "03211117",
        "lamp": "03636649",
        "speaker": "03691459",
        "cabinet": "02933112",
        "chair": "03001627",
        "bench": "02828884",
        "car": "02958343",
        "airplane": "02691156",
        "sofa": "04256520",
        "table": "04379243",
        "phone": "04401088"
        }
    ```
    
Our rendering is based on the convention of [3DR2N2](https://arxiv.org/abs/1604.00449)'s 2d image rendering.
 
 * #### Each model object has 36 easy views and 36 hard views.(3DR2N2 has 24 easy views)
 * #### Each view of each model object, we have albedo, depth, normal and RGB images.(3DR2N2 has only RGB images)
 * #### different from 3DR2N2, our resolution is 224 * 224 instead of 137 * 137

<img src="samples/albedo_1176dff7f0ec879719d740e0f6a9a113/hard/06.png" /> <img src="samples/image_1176dff7f0ec879719d740e0f6a9a113/hard/06.png"  /> <img src="samples/depth_1176dff7f0ec879719d740e0f6a9a113/hard/06.png"  /> <img src="samples/normal_1176dff7f0ec879719d740e0f6a9a113/hard/06.png"  />



