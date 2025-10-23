
#! /bin/bash

set -e

# Function configurations
memory=600
timeout=60000

cd image-recognition

# Destroy and prepare build folder.
rm -rf build
mkdir build

# Copy files to build folder.
cp -R src/* build
cd build
zip -r index.zip *

wsk -i action update ir --kind python:3.9 --main main --memory 530 --timeout 120000 index.zip --web true

# cd ../..

# cd video-process

# # video processing
# rm -rf build
# mkdir build

# cp -R src/* build
# cd build
# zip -r index.zip *

# wsk -i action update vp --kind python:3.11 --main main --memory 256 --timeout 60000 --web true index.zip


# cd ../..
# #python bfs

# cd python-bfs

# rm -rf build
# mkdir build

# cp -R src/* build
# cd build
# zip -r index.zip *

# wsk -i action update bfs --kind python:3.11 --main main --memory 20 --timeout 60000 --web true index.zip


# cd ../..
# #python graph pagerank
# cd python-graphpagerank

# rm -rf build
# mkdir build

# cp -R src/* build
# cd build
# zip -r index.zip *

# wsk -i action update gp --kind python:3.11 --main main --memory 256 --timeout 60000 --web true index.zip

cd ../..

cd bert

rm -rf build
mkdir build
    
cp -R src/* build
cd build
zip -r index.zip *

wsk -i action update bert --kind python:3.12 --main main --memory 950 --timeout 200000 --web true index.zip


# cd ../..

# cd image-recognition

# # Destroy and prepare build folder.
# rm -rf build
# mkdir build

# # Copy files to build folder.
# cp -R src/* build
# cd build
# zip -r index.zip *

# wsk -i action update ir2 --kind python:3.9 --main main --memory 600 --timeout 120000 index.zip --web true