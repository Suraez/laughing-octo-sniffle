#include <linux/bpf.h>
#include <bpf/libbpf.h>
#include <unistd.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <linux/perf_event.h>  // ✅ Include perf_event struct definitions
#include <sys/ioctl.h>         // ✅ Include ioctl function declaration
#include <string.h>
#include <stdlib.h>

int main() {
    struct bpf_object *obj;
    int prog_fd, perf_fd;

    obj = bpf_object__open_file("sched_switch_kern.o", NULL);
    if (!obj) {
        perror("Failed to open eBPF object");
        return 1;
    }

    if (bpf_object__load(obj)) {
        perror("Failed to load eBPF object");
        return 1;
    }

    struct bpf_program *prog = bpf_object__find_program_by_name(obj, "sched_switch_pr");
    if (!prog) {
        perror("Failed to find program");
        return 1;
    }

    prog_fd = bpf_program__fd(prog);
    if (prog_fd < 0) {
        perror("Failed to get program FD");
        return 1;
    }

    // Setup perf_event_attr structure
    struct perf_event_attr attr;
    memset(&attr, 0, sizeof(attr));
    attr.type = PERF_TYPE_TRACEPOINT;
    attr.size = sizeof(attr);
    attr.config = 58;  // sched:sched_switch event ID (verify this)
    attr.sample_period = 1;

    // Attach to the perf event
    perf_fd = syscall(__NR_perf_event_open, &attr, -1, 0, -1, 0);
    if (perf_fd < 0) {
        perror("perf_event_open failed");
        return 1;
    }

    if (ioctl(perf_fd, PERF_EVENT_IOC_SET_BPF, prog_fd)) {
        perror("Failed to attach BPF program");
        return 1;
    }

    printf("eBPF program successfully attached to sched:sched_switch\n");

    while (1) sleep(1);
    return 0;
}
