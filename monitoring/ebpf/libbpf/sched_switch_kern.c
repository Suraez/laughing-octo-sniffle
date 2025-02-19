#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

SEC("tracepoint/sched/sched_switch")
int sched_switch_pr(void *ctx) {
    bpf_printk("Context switch detected\n");
    return 0;
}


char _license[] SEC("license") = "GPL";
