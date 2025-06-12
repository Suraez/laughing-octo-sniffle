Preprocessing scripts for Azure Function invocation dataset

Sampled Azure Function Invocation traces are present in the invocation_dataset directory.

High-mem-func-benchmarks folder contains benchmarks that could create memory pressure when being deployed on 
OpenWhisk


Inside the `monitoring` folder, the script for tracing page_free and page_alloc can be run <br>
using `sudo bpftrace trace_pages.bt`


### Scirpts Folder

`invoke_functions.sh` it randomly invokes functions specified in deploy_functions.sh inside the _**applications**_ folder



### OpenFaas-High-Mem

sebs/video-processing

To invoke this function, you need to be inside the video-processing directory where you have the video stored
and then hit

`curl -X POST http://127.0.0.1:8080/function/video-processing \
  --data-binary "@input.mp4"`