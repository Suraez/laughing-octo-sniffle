cd matmul

rm -rf build
mkdir build

cp -R src/* build
cd build
zip -r index.zip *

wsk -i action update $name --kind python:3 --main main --memory 512 --timeout 60000 index.zip


cd ../../

# Chamelon

cd chameleon
rm -rf build
mkdir build
cp -R src/* build
