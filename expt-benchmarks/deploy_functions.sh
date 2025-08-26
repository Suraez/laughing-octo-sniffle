cd image-recognition

# Destroy and prepare build folder.
rm -rf build
mkdir build

# Copy files to build folder.
cp -R src/* build
cd build && npm install
zip -r index.zip *

wsk -i action update ir --kind nodejs:14 --main main --memory 512 --timeout 60000 --web true index.zip



# cd ../..

# cd video-process

# # video processing
# rm -rf build
# mkdir build

# cp -R src/* build
# cd build
# zip -r index.zip *

# wsk -i action update vp --kind python:3.11 --main main --memory 512 --timeout 60000 --web true index.zip


cd ../..
#python bfs

cd python-bfs

rm -rf build
mkdir build

cp -R src/* build
cd build
zip -r index.zip *

wsk -i action update bfs --kind python:3.11 --main main --memory 256 --timeout 60000 --web true index.zip


# cd ../..
# #python graph pagerank
# cd python-graphpagerank

# rm -rf build
# mkdir build

# cp -R src/* build
# cd build
# zip -r index.zip *

# wsk -i action update gp --kind python:3.11 --main main --memory 256 --timeout 60000 --web true index.zip
