# **Floor Plan Analytics Package**

Tested Python versions are 3.9, 3.10, 3.12 and 3.13

## **Description**

This is package that includes some of the most used Space Syntax tools to be applied on floor plans or floor plates.
The package is build to utilize Numba to accelerate calculations of the analytics either by CPU multithreading or by utilizing JIT compiled CUDA kernels.
The Numba kernels are exclusively written for CUDA, therefore a Nvidia GPU and CUDA installation are needed for running the GPU accelerated version of the code.

The package can also be installed form PyPI:

```bash
pip install FloorplanAnalytics
```

If your Cuda version differs from Cuda 13 please make sure that you install the correct numba-cuda version after installing the pip package.
For updating to the correct numba-cuda after the installation is finished just run this to overwrite the CUDA 13 installation (here with CUDA 12 as an example)

```bash
pip install numba-cuda[cu12]
```

## **0.0.3 Features**

Features for the new version are:

- Revisited all GPU methods for speed gains and/or reducing memory consumption
- Added a new method for calculating shortest distance to an obstacle only if a ray hits it

## **Details**

The inputs and outputs of the outputs fo the methods are all handling simple to manage Numpy arrays.
This choice is due to two main considerations aimed to make the backend functions as broadly applicable as possible.

1. The Input can therefore stem from a (flat and regular) point grid or directly from an image.
2. The output can be used for further data driven analytics, comparing or storage without any additional data structure

To maintain close-to-realtime performance also at larger array sizes, the exposed methods for the analytics calculations include downscale and up sample functionality while keeping the returned values also scaled accordingly.
