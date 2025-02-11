set -e

# Function configurations
memory=512
timeout=60000

echo ""
echo "Deploying functions..."
echo ""



# Deep Learning Inference Function
cd deep-learning-inference
# pip install -r requirements.txt -t .
rm -rf build
mkdir build
cp -R src/* build
cd build
zip -r index.zip *
wsk -i action update dli --kind python:3 --main main --memory 512 --timeout 60000 index.zip



cd ../../image-processing
rm -rf build
mkdir build
cp -R src/* build
cd build
zip -r index.zip *
wsk -i action update ip --kind python:3 --main main --memory 512 --timeout 60000 index.zip


cd ../../memory-allocator
rm -rf build
mkdir build 
cp -R src/* build
cd build    
zip -r index.zip *
wsk -i action update ma --kind python:3 --main main --memory 512 --timeout 60000 index.zip


cd ../../video-processing 
rm -rf build
mkdir build 
cp -R src/* build
cd build
zip -r index.zip *
wsk -i action update vp --kind python:3 --main main --memory 512 --timeout 60000 index.zip


cd ../../image-resolution
rm -rf build
mkdir build 
cp -R src/* build
cd build
zip -r index.zip *
wsk -i action update ir --kind python:3 --main main --memory 512 --timeout 60000 index.zip





# # Image Processing Function
# cd image-processing
# # pip install -r requirements.txt -t .
# zip -r ip.zip .  # Zip the entire folder, including dependencies
# wsk -i action update ip ip.zip --kind python:3 --memory 512

# # Memory Allocator Function
# cd memory-allocator
# zip -r ma.zip .  # Zip the entire folder, including dependencies
# wsk -i action update ma ma.zip --kind python:3 --memory 512

# # Video Processing Function
# cd video-processing
# pip install -r requirements.txt -t .
# zip -r vp.zip .  # Zip the entire folder, including dependencies
# wsk -i action update vp vp.zip --kind python:3 --memory 512
