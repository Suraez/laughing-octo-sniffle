#include <linux/bpf.h>
#include <bpf/libbpf.h>
#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main() {
    struct bpf_object *obj;
    struct bpf_program *prog_alloc, *prog_free;

    obj = bpf_object__open_file("page_trace_kern.o", NULL);
    if (!obj) {
        perror("Failed to open eBPF object");
        return 1;
    }

    if (bpf_object__load(obj)) {
        perror("Failed to load eBPF object");
        return 1;
    }

    // Attach to kmem_page_alloc
    prog_alloc = bpf_object__find_program_by_name(obj, "on_page_alloc");
    if (!prog_alloc) {
        perror("Failed to find on_page_alloc program");
        return 1;
    }
    if (bpf_program__attach_tracepoint(prog_alloc, "kmem", "mm_page_alloc") < 0) {
        perror("Failed to attach to kmem_page_alloc");
        return 1;
    }

    // Attach to kmem_page_free
    prog_free = bpf_object__find_program_by_name(obj, "on_page_free");
    if (!prog_free) {
        perror("Failed to find on_page_free program");
        return 1;
    }
    if (bpf_program__attach_tracepoint(prog_free, "kmem", "mm_page_free") < 0) {
        perror("Failed to attach to kmem_page_free");
        return 1;
    }

    printf("eBPF program attached to kmem_page_alloc and kmem_page_free.\n");

    while (1) sleep(1);
    return 0;
}
