[神秘的东方文字版](./README_zh.md)
---
# qemb
A toolscript to cut cluster for quantum embedding. Accept VASP structure (CONTCAR).

## 1. General
### 1.1 Installation
This project is now on PYPI, so a convenient way to install is like:
```shell
pip3 install qemb
```
or from git repo to get nightly update:
```shell
git clone https://github.com/Makarov3821/qemb
# if you are in China, gitee repo maybe faster
# git clone https://gitee.com/Marshall3821/qemb
cd qemb
pip3 install .
```

### 1.2 Basic usage
A help of input & output can be obtained by `qemb -h`:
```
$ qemb -h
usage: qemb [-h] --input INPUT_DIR --output OUTPUT_DIR -f CONTROL_FILE [-q QUEUE] [-p CORE_NUMBER] [--xc XC_FUNCTIONAL] [--basis BASIS_SET]

An embedding calculation tool from GGA@PBC to embedded hybrids

options:
  -h, --help           show this help message and exit
  --input INPUT_DIR    Input directory location
  --output OUTPUT_DIR  Output directory location
  -f CONTROL_FILE      control file location, must set
  -q QUEUE             Queue names. 'xp72mc10' is default.
  -p CORE_NUMBER       Core number used per node: 1/2/3/4/8/28...; 36 is default.
  --xc XC_FUNCTIONAL   Set xc if REST input generation is needed; b3lyp is default.
  --basis BASIS_SET    Set basis if REST input generation is needed; def2-SVP is default.
```
in which **input_dir**, **output_dir**, and **control_file** is a required field. We'll explain this three part in the following section.

Argument such as core_number, xc, is needed while using input file generation.

***IMPORTANT NOTICE:*** This project is not intended for a pythonic package, so import qemb in Python will be **void**, only main program "qemb" is supported. This feature may be considered later in development.

## 2. Inputs and Outputs
### 2.1 Input_dir
For a classic catalytic procedure, you have to calculate both clean slab and absorbant on slab. So we suggest your folder is organized like:
```
root_dir/
├── absorb
│   ├── CO-bridge
│   │   └── VASP_CALCULATION_FILES
│   ├── CO-hollow
│   │   └── VASP_CALCULATION_FILES
│   └── CO-top
│       └── VASP_CALCULATION_FILES
└── clean
    └── VASP_CALCULATION_FILES
```
for best user experience, since some feature is upon this structure.

This script will obtain structure from CONTCAR, but POSCAR, POTCAR, KPOINTS, and a normal terminated OUTCAR will also be checked to assure it a true VASP running directory, not a dangling CONTCAR.

### 2.2 Output_dir
The script will find all possible dir from input dir, and reform them in a new output dir given. For example, if you use root_dir in 2.1 as your input_dir, your output_dir, maybe named root_dir_out, will be like:
```
root_dir_out/
├── absorb
│   ├── CO-bri
│   │   ├── ref
│   │   │   └── REGENERATED_FILES
│   │   └── run
│   │       └── INPUT_FILES
│   ├── CO-hollow
│   │   ├── ref
│   │   │   └── REGENERATED_FILES
│   │   └── run
│   │       └── INPUT_FILES
│   └── CO-top
│       ├── ref
│       │   └── REGENERATED_FILES
│       └── run
│           └── INPUT_FILES
└── clean
    ├── ref
    │   └── REGENERATED_FILES
    └── run
        └── INPUT_FILES
```
**ref** is designed to store original CONTCAR, and cluster generated. This design is meant to compatible for [DFET method](https://github.com/EACcodes/VASPEmbedding) developed by Emily A. Carter, though this is not implemented at this time.

**run** is where to store input file of the cluster generated. Now we support [REST program](https://gitee.com/restgroup) incar generation. More program support will be added in the future.

### 2.3 Control file
A full option template with detailed commemt is listed in [emb.toml.template](./template/emb.toml.template). We'll only explain modes of cutting in below.

#### 2.3.1 Cutting_method
1: A sphere from the ori_point. Mostly hemisphere for surface slab.

2: A cylinder from the ori_point.

3: A near expanding. For surface like Cu(111) will be:

![cutting3_cu(111)](./figs/cut_3_cu111.png)

For surface like Mgo(100) will be:

![cutting_mgo(100)](./figs/cut_3_mgo.png)

6: Alternative way for NaCl-like system like:

![another_cutting_mgo(100)](./figs/cut_6_mgo.png)

#### 2.3.2 Some example
A Cu31 clutser:
```toml
jobtype = 1.1
cluster_cutting_major_method = 2
cluster_cutting_minor_method = 5
cluster_layers = 2
cluster_expand_num = 2
```

![Cu31 cluster](./figs/cu31_cluster.png)

A Mg-centered Mg9O9 cluster surrounded by a hemispherical pseudoes/point charges:
```toml
jobtype = 1.3
cluster_cutting_major_method = 2
cluster_cutting_minor_method = 7
cluster_layers = 2
cluster_expand_num = 1
charge_cutting = true
charge_cutting_sub_method = 1
charge_radius = 8.0
```

![MgO cluster with surrouding point charges](./figs/mg9o9_cluster_with_charges.png)

Another interesting thing is this script will automatically supercell when your input exceeded the original cell. Thus we can make:

A huge plain (based on a 4x4, 3 layered MgO(100) slab):
```toml
jobtype = 1.1
cluster_cutting_major_method = 2
cluster_cutting_minor_method = 7
cluster_layers = 2
cluster_expand_num = 15
```

![Big Mgo plain "cluster"](./figs/huge_plain.png)

Or a big rod (based on a 4x4, 3 layered MgO(100) slab):
```toml
jobtype = 1.1
cluster_cutting_major_method = 2
cluster_cutting_minor_method = 7
cluster_layers = 20
cluster_expand_num = 1
```

![Rod MgO "cluster"](./figs/big_rod.png)
