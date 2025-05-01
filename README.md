Preprocessing scripts for Azure Function invocation dataset

Sampled Azure Function Invocation traces are present in the invocation_dataset directory.

And benchmarks (functions) that could possibly create memory pressure on the system are available in the
high-mem-func-benchmarks


Inside the `monitoring` folder , the script for tracing page_free and page_alloc can be run <br>
using `sudo bpftrace trace_pages.bt`


### Scirpts Folder

`invoke_functions.sh` it randomly invokes functions specified in deploy_functions.sh inside the _**applications**_ folder