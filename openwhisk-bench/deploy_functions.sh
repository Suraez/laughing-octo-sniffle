# cd matmul

# rm -rf build
# mkdir build

# cp -R src/* build
# cd build
# zip -r index.zip *

# wsk -i action update mm --kind python:3.11 --main main --memory 2048 --timeout 60000 index.zip


# # Chamelon
# cd ../../

# cd chamelon

# rm -rf build
# mkdir build

# cp -R src/* build
# cd build
# zip -r index.zip *

# wsk -i action update ch --kind python:3.11 --main main --memory 512 --timeout 60000 index.zip

#idle
# cd ../../

# cd idle

# rm -rf build
# mkdir build

# cp -R src/* build
# cd build
# zip -r index.zip *

# wsk -i action update idle --kind python:3.10 --main main --memory 2048 --timeout 60000 index.zip


# cd ../../
cd video-process

rm -rf build
mkdir build

cp -R src/* build
cd build
zip -r index.zip *

wsk -i action update video-process --kind python:3.11 --main main --memory 1024 --timeout 60000 index.zip --web true

# cd ../../

# cd highmem

# rm -rf build
# mkdir build

# cp -R src/* build
# cd build
# zip -r index.zip *

# wsk -i action update fc --kind python:3.11 --main main --memory 512 --timeout 60000 index.zip

cd ../../
cd bert

rm -rf build
mkdir build

cp -R src/* build
cd build
zip -r index.zip *

wsk -i action update bert --kind python:3.12 --main main --memory 1560 --timeout 60000 index.zip --web true

wsk -i action invoke bert -r
# cd ../..

# cd image-recognition

# rm -rf build
# mkdir build

# cp -R src/* build
# cd build
# zip -r index.zip *

# wsk -i action update ir --kind python:image --main main --memory 2048 --timeout 60000 index.zip --web true
