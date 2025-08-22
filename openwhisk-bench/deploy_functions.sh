# cd matmul

# rm -rf build
# mkdir build

# cp -R src/* build
# cd build
# zip -r index.zip *

# wsk -i action update mm --kind python:3.11 --main main --memory 512 --timeout 60000 index.zip


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

wsk -i action update video-process --kind python:3.11 --main main --memory 512 --timeout 60000 index.zip


# cd ../../

# cd highmem

# rm -rf build
# mkdir build

# cp -R src/* build
# cd build
# zip -r index.zip *

# wsk -i action update fc --kind python:3.11 --main main --memory 512 --timeout 60000 index.zip