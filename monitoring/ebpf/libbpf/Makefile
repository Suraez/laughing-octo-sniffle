all:
	clang -O2 -target bpf -c sched_switch_kern.c -o sched_switch_kern.o
	clang -o attach_sched attach_sched.c -lbpf -lelf
	sudo ./attach_sched


clean:
	rm -f hello_kern.o hello_user trace_user openat_kern.o

