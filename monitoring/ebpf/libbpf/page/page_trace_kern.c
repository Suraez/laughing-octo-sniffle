#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

SEC("tracepoint/kmem/mm_page_alloc")
int on_page_alloc(void *ctx) {
    bpf_printk("Page allocated by PID %d\n", bpf_get_current_pid_tgid() >> 32);
    return 0;
}

SEC("tracepoint/kmem/mm_page_free")
int on_page_free(void *ctx) {
    bpf_printk("Page freed by PID %d\n", bpf_get_current_pid_tgid() >> 32);
    return 0;
}

char _license[] SEC("license") = "GPL";
