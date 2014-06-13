.PHONY: all
gsl_flags := $(shell pkg-config --libs --cflags gsl) -DHAVE_INLINE
commonflags := -Wall -Wextra -std=c99 -pedantic -Wno-unknown-pragmas -Wshadow -Wpointer-arith
commonflags += $(CFLAGS)

all: eemd_example ceemdan_example

eemd_example: eemd_example.c
	gcc $(commonflags) $(gsl_flags) -I../src -L.. -Wl,-rpath,.. -leemd $^ -o $@

ceemdan_example: ceemdan_example.c
	gcc $(commonflags) $(gsl_flags) -I../src -L.. -Wl,-rpath,.. -leemd $^ -o $@
