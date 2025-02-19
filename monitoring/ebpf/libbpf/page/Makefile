all:
	clang -O2 -target bpf -c page_trace_kern.c -o page_trace_kern.o
	clang -o attach_page_trace attach_page_trace.c -lbpf -lelf
	sudo ./attach_page_trace


clean:
	rm -f attach_page_trace page_trace_kern.o