# FSBS 


Fetal Structural Brain Segmentation (FSBS) 

This segmentation tool is meant to segment super resolution reconstructed fetal T2 images. This pipeline is built using python v=3.7, nipype, and docker. The template used is Ali Gholipour et. al 2017 [Fetal Brain Atlas](http://crl.med.harvard.edu/research/fetal_brain_atlas/). 


## Usage 

The program is designed to run entirely within a docker container. Prior to running this tool for the first time, docker needs to be installed and the docker image needs to be built using the docker build command. 


### Docker Install 

To install Docker on your computer, follow these steps. [Docker Install Instructions](https://docs.docker.com/engine/install/)


### Docker Build Command

Following installation of the Docker engine, the image must be build before it can be run the first time. 

To build the docker image, navigate to the folder which contains the Dockerfile (This will be the folder cloned from GitHub). Then run the following command in a terminal or WSL for windows machines. 

```bash
docker build -t fsbs:latest .
```


### Running FSBS

FSBS can be run on a single subject or a batch of subjects. 


