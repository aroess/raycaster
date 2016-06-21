gcc -fPIC -c engine.c
ld -shared -soname enigne.so.1 -o engine.so.1.0 -lc engine.o
