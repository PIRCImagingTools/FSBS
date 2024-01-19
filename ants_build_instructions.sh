#!/bin/bash

antsBuildInstructions="https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS"

# Number of threads used by make
buildThreads="$1"
workingDir=${PWD}

echo "Building ANTs using ${buildThreads} threads."

# Clone the repo
git clone https://github.com/ANTsX/ANTs.git --branch v2.5.0

# Where to build, should be an empty directory
buildDir=${workingDir}/build
installDir=${workingDir}/install
mkdir $buildDir $installDir
cd $buildDir

# USE_VTK must be turned on to build antsSurf
cmake \
    -DCMAKE_INSTALL_PREFIX=$installDir \
    -DBUILD_SHARED_LIBS=OFF \
    -DUSE_VTK=OFF \
    -DBUILD_TESTING=OFF \
    -DRUN_LONG_TESTS=OFF \
    -DRUN_SHORT_TESTS=OFF \
    ${workingDir}/ANTs 2>&1 | tee cmake.log


make -j $buildThreads 2>&1 | tee build.log


cd ANTS-build
make install 2>&1 | tee install.log

antsRegExe="${installDir}/bin/antsRegistration"
echo "Installation complete, running ${antsRegExe}"

${antsRegExe} --version

echo "
Binaries and scripts are located in 

  $installDir

Please see post installation instructions at 

  $antsBuildInstructions

"