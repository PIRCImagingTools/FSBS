FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

ARG COMPILER_THREADS=4

RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-utils=2.4.11 \
    wget=1.21.2-2ubuntu1 \
    gnupg=2.2.27-3ubuntu2.1 \
    vim=2:8.2.3995-1ubuntu2.15 \
    git-all=1:2.34.1-1ubuntu1.10 \
    cmake=3.22.1-1ubuntu1.22.04.1 \
    g++=4:11.2.0-1ubuntu1 \
    zlib1g-dev=1:1.2.11.dfsg-2ubuntu9.2 \
    software-properties-common=0.99.22.9

RUN add-apt-repository ppa:deadsnakes/ppa -y && apt-get install -y --no-install-recommends \
    python3.7=3.7.17-1+jammy1 \
    python2.7=2.7.18-13ubuntu1.1 \ 
    python3-pip \
    python3.7-distutils 

RUN mkdir /fsl_install && wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py -P /fsl_install

RUN python2.7 /fsl_install/fslinstaller.py -d /usr/local/fsl

RUN apt-get update && apt-get install -y --no-install-recommends make

COPY ./ants_build_instructions.sh /ants/

RUN cd /ants && chmod 777 -R /ants \
    && ./ants_build_instructions.sh ${COMPILER_THREADS}

ENV PATH=${PATH}:/ants/install/bin:/usr/local/fsl/bin

RUN python3.7 -m pip install \
    numpy==1.21.6 \ 
    pandas==1.3.5 \ 
    nipype==1.8.6 \
    scikit-learn==1.0.2 \ 
    SimpleITK==2.2.1 \
    matplotlib==3.5.3 \
    openpyxl==3.1.2 \
    tqdm==4.66.1 \
    psutil==5.9.7

RUN mkdir -p /.config/matplotlib && chmod 777 -R /.config/

RUN echo "alias python=python3.7" >> /etc/bash.bashrc && /bin/bash -c 'source /etc/bash.bashrc'

ENV MPLCONFIGDIR='/.config/matplotlib'

COPY /app/ /app/

ENV FSLOUTPUTTYPE='NIFTI_GZ'

SHELL ["/bin/bash", "-c"]

Run echo "alias python=python3.7" >> ~/.bashrc && \
    echo "alias python=python3.7" >> /etc/profile && source /etc/profile

COPY .vimrc /root/.vimrc

ENV HOME=/home

RUN chmod -R 777 /home

RUN mkdir /data && chmod -R 777 /data

ENTRYPOINT ["/bin/bash", "/app/autorun.sh"]
