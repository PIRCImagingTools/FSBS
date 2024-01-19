# FSBS 

Fetal Structural Brain Segmentation (FSBS) 

This segmentation tool is meant to segment super-resolution reconstructed fetal T2 images. This pipeline is built using Python v=3.7, Advanced Normalization Tools (ANTs) v2.5.0, Nipype, and Docker. This software usees the IMAGINE Fetal T2-weighted MRI Atlas from Ali Gholipour et. al 2017 [Fetal Brain Atlas](http://crl.med.harvard.edu/research/fetal_brain_atlas/). 
If you publish any work using this software, please cite our paper and paper for the IMAGINE Fetal T2-weighted MRI Atlas.

  1. Rajagopalan V, Reynolds WT, Zepeda J, Lopez J, Ponrartana S, Wood J, Ceschin R, Panigrahy A. Impact of COVID-19 Related Maternal Stress on Fetal Brain Development: A Multimodal MRI Study. J Clin Med. 2022 Nov 9;11(22):6635. doi: 10.3390/jcm11226635. PMID: 36431112; PMCID: PMC9695517. [Pubmed](https://pubmed.ncbi.nlm.nih.gov/36431112/)
  3. Gholipour A, Rollins CK, Velasco-Annis C, Ouaalam A, Akhondi-Asl A, Afacan O, Ortinau CM, Clancy S, Limperopoulos C, Yang E, Estroff JA, Warfield SK. A normative spatiotemporal MRI atlas of the fetal brain for automatic segmentation and analysis of early brain growth. Sci Rep. 2017 Mar 28;7(1):476. doi: 10.1038/s41598-017-00525-w. PMID: 28352082; PMCID: PMC5428658. [Pubmed](https://pubmed.ncbi.nlm.nih.gov/28352082/)
## Setup  

The program is designed to run entirely within a docker container. Before using this tool docker needs to be installed and the docker image needs to be built using the docker build command below. 

### Docker Install 

To install Docker on your computer, follow these steps. [Docker Install Instructions](https://docs.docker.com/engine/install/)

### Docker Build Command

Following installation of the Docker engine, the image must be built before it can be run the first time. 

To build the docker image, navigate to the folder that contains the Dockerfile (This will be the folder cloned from GitHub). Then run the following command in a terminal or WSL for Windows machines. 

```bash
docker build -t fsbs:latest . 
```
>[!Tip]
>During the build process, ANTs is compiled from source. This can be sped up by increasing the default value of the build-arg `COMPILER_THREADS=<val>` to > 4. If your computer has limited resources, the value can be lowered from 4. The code below can be used to run the altered command.
>
>```bash
>docker build --build-arg COMPILER_THREADS=<thread number> -t fsbs:latest .
>```

Before running FSBS for the first time. The location of the FSBS script should be added to your path. To accomplish this run the following command from the FSBS directory:
```bash
echo "export PATH=${PATH}:$(pwd)" >> ~/.profile && source ~/.profile
```

>[!NOTE]
>If the `./FSBS` script does not function for your system, the script may be replaced with
>```bash
>docker run -it fsbs:latest --user $UID -v $(pwd):/data
>```
## Running FSBS

FSBS can be run in three different ways. 
  <ol type="I">
  <li>Single</li>
  <li>Batch via a directory of subject directories containing image files</li>
  <li>Batch via a CSV/Excel giving explicit paths</li>
  </ol>



### I. Running FSBS in Single Mode
To run FSBS in single mode four pieces of information are needed:
  1. Subject ID
  2. Gestational Age
  3. Reconstruction File
  4. Mask File of Brain

To run in single mode, run the command below with your arguments inserted. 

```bash
./FSBS single <Subject ID> <Gestational Age> <Reconstruction File> <Mask File>
```
>[!NOTE]
>The reconstruction file and the mask file must be within the current folder, or a folder that is downstream of your current folder for Docker to access the files correctly.

### II. Running FSBS in Batch Directory Mode
To run FSBS in batch directory mode, two pieces of information are required, but adding additional parameters may help. 
  1. File directory - Location where subject images are located
  2. Excel file Path - Excel file containing subject IDs and their gestational ages.

Additional Arguments which help: 
  1. Search Directory - If for whatever reason you only want to run files in a specific directory, adding this term will only process files within this folder.
  2. Exclude Directory - Similar to above, but will not process any files contained in this directory.
  3. Search Term - This is the term the program uses to search for reconstruction files to process.
  4. Exclude Term - Similar to above, but will ignore any files with this term in the filename.

```bash
./FSBS batch_dir <File Directory> <Excel File Path> 
```
If running with additional parameters, run the command below with your arguments inserted

```bash
./FSBS batch_dir <File Directory> <Excel File Path>
  --search_dir <Search Directory>
  --exclude_dir <Exclude Directory>
  --search_term <Search Term>
  --exclude_term <Exclude Term>
```

Lastly, if you only want to test how many subjects would be run with a specific combination of search/exclude directories/terms, you can add the flag `--dry_run` to accomplish that. The command below would be an example. 

```bash
./FSBS batch_dir <File Directory> <Excel File Path>
  --search_dir <Search Directory>
  --exclude_dir <Exclude Directory>
  --search_term <Search Term>
  --exclude_term <Exclude Term>
  --dry_run
```

>[!NOTE]
> The file directory and Excel file must be within the current folder, or a folder that is downstream of your current folder for Docker to access the files correctly.

### III. Running FSBS in Batch CSV Mode
To run FSBS in batch CSV mode, one piece of information is required, but adding additional parameters may help.
  1. CSV or Excel file Path - CSV or Excel file containing subject IDs and their gestational ages.

Additional Arguments which help: 
  1. Subject Label - Column label for the column containing the subject IDs in the CSV/Excel file. 
  2. GA Label - Column label for the column containing the subject Gestational Ages. 
  3. Recon Label - Column label for the column containing the path to the reconstruction file.
  4. Mask Label - Column label for the column containing the path to the mask file. 

This method also can take a `--dry_run` flag. Below is an example command:
```bash
./FSBS batch_csv <File Directory> <CSV/Excel File Path>
  --subject_label <Subject Label>
  --ga_label <GA Label>
  --recon_label <Recon Label>
  --mask_label <Mask Label>
  --dry_run
```
>[!NOTE]
>NOTE: The CSV or Excel file and files referenced in the CSV/Excel must be contained within the current folder, or a folder that is downstream of your current folder for Docker to access the files correctly.
