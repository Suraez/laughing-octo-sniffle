#include <stdio.h>
#include <stdlib.h>
#include <bpf/libbpf.h>
#include <bpf/bpf.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <linux/perf_event.h>

int main() {
    struct bpf_object *obj;
    int prog_fd;
    int ret;

    // Load the compiled eBPF program
    obj = bpf_object__open("hello_kern.o");
    if (!obj) {
        fprintf(stderr, "Failed to open eBPF object\n");
        return 1;
    }

    ret = bpf_object__load(obj);
    if (ret) {
        fprintf(stderr, "Failed to load eBPF object: %s\n", strerror(-ret));
        return 1;
    }

    // Get the program FD
    prog_fd = bpf_program__fd(bpf_object__find_program_by_name(obj, "hello"));
    if (prog_fd < 0) {
        fprintf(stderr, "Failed to find eBPF program\n");
        return 1;
    }

    // Attach the eBPF program to the tracepoint
    int tracepoint_fd = bpf_raw_tracepoint_open("sys_enter_execve", prog_fd);
    if (tracepoint_fd < 0) {
        fprintf(stderr, "Failed to attach eBPF program: %s\n", strerror(-tracepoint_fd));
        return 1;
    }

    printf("eBPF program loaded and attached successfully. Check dmesg for output.\n");

    // Keep the program running to allow the eBPF program to execute
    while (1) {
        sleep(1);
    }

    // Cleanup
    close(tracepoint_fd);
    bpf_object__close(obj);
    return 0;
}