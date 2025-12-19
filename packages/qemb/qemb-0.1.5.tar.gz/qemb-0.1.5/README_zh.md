[English Version](./README.md)
---
# qemb
一个获取各种形态簇的脚本。从VASP弛豫的CONTCAR出发，为后续簇矫正计算提供xyz或输入卡。

## 1. 总览
### 1.1 安装
可以通过pypi直接安装：
```shell
pip3 install qemb
```
或者从git下载安装：
```shell
git clone https://github.com/Makarov3821/qemb
# 国内用户用gitee可能会更舒心
# git clone https://gitee.com/Marshall3821/qemb
cd qemb
pip3 install .
```

### 1.2 基本用法
基本用法可以用`qemb -h`来查看：
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
其中**input_dir**，**output_dir**，和**control_file**三个是必填项，关于他们我们会在后文详述。其余的选项基本只在你需要生成输入卡时用到。

***注意***：这个脚本目前仅支持调用主程序qemb，如果你在Python中调用它可能什么也不会得到。并且按照这个脚本的设计，很有可能在很长一段时间内不会添加库的使用方式（因为最初是面向[DFET](https://github.com/EACcodes/VASPEmbedding)编程，CONTCAR结构的读入都是内置的方法，现在没有办法读入其他结构，比如ase之类的）。

虽然也可以调用其中的函数，但是生死我难以预料，也没法负责。

## 2. 输入与输出
### 2.1 输入文件
对于一个传统的异相催化过程，常常就是计算纯slab与表面物种的各种吸附。因而如果要使用这个脚本，建议你的输入目录如：
```
root_dir/
├── absorb
│   ├── CO-bridge
│   │   └── VASP计算文件
│   ├── CO-hollow
│   │   └── VASP计算文件
│   └── CO-top
│       └── VASP计算文件
└── clean
    └── VASP计算文件
```
有一些功能，比如检查吸附物簇与纯表面簇大小是否一致，依赖这样的目录结构。因而推荐您这样组织计算目录（也不算坏事吧）

这个脚本会从弛豫的CONTCAR里面获取结构，但是同时也会检查CONTCAR目录中是否有POSCAR、POTCAR、KPOINTS、和正常结束的OUTCAR（有“General timing and accounting informations for this job:”一行）几个文件。这样确保了每个要切簇的结构都是“经过VASP计算”的，你当然可以欺骗这个过程（目前，以后可能会给一个不检查这个的选项），但是这个过程对做DFET是有益的，所以目前保持打开。

### 2.2 输出文件
脚本会按2.1中的方法检查所有的计算目录，将其重整到新的目录中。比如你有一个2.1中的“root_dir”作为输入，并且指定输出目录为“root_dir_out”，那么输出目录会长成这样：
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
其中：

**ref**里面存放你在VASP中使用的POTCAR，KPOINTS，获得的CONTCAR，以及新生成的簇或者赝势xyz文件。这样的设计主要还是为了适配Emily A. Carter开发的[DFET](https://github.com/EACcodes/VASPEmbedding)方法，即便这个东西现在还没有适配。

**run**里面存放基于簇结构生成的程序输入卡。现在其实只适配了[REST](https://gitee.com/restgroup)程序的输入，后面也会尝试多适配几个量化程序。

### 2.3 控制文件
你可以在[emb.toml.template](./template/emb.toml.template)这个模板文件里看到所有的选项，每个选项都有厚厚的注释解释。下面我们只解释一下几种不同的切簇方法。

#### 2.3.1 切簇方法
1： 从ori_point切一个球，对于表面催化经常就是一个半球；

2： 从ori_point切一个圆柱；

3： 近邻法。对于Cu(111)之类的密堆积面如：

![cutting3_cu(111)](./figs/cut_3_cu111.png)

如果是MgO(100)这样的离子面就会如：

![cutting_mgo(100)](./figs/cut_3_mgo.png)

6： 对于NaCl这种晶体的另一种切法，示例图如：

![another_cutting_mgo(100)](./figs/cut_6_mgo.png)

#### 2.3.2 一些例子
一个经典的Cu31簇：
```toml
jobtype = 1.1
cluster_cutting_major_method = 2
cluster_cutting_minor_method = 5
cluster_layers = 2
cluster_expand_num = 2
```

![Cu31 cluster](./figs/cu31_cluster.png)

一个Mg中心的Mg9O9簇，周边围绕一个半圆的点电荷阵列：
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

这个脚本还有一个很有意思的功能，如果你设置的切簇大小超出了原胞包含的范围，那么脚本会帮你自动扩胞。因而我们可以做出一些比较搞的结构：

大平原（原胞为一个4x4的三层MgO(100)slab）：
```toml
jobtype = 1.1
cluster_cutting_major_method = 2
cluster_cutting_minor_method = 7
cluster_layers = 2
cluster_expand_num = 15
```

![Big Mgo plain "cluster"](./figs/huge_plain.png)

也可以造大棒（原胞依旧是4x4的三层MgO(100)slab）：
```toml
jobtype = 1.1
cluster_cutting_major_method = 2
cluster_cutting_minor_method = 7
cluster_layers = 20
cluster_expand_num = 1
```

![Rod MgO "cluster"](./figs/big_rod.png)




