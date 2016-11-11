.PHONY: all clean install uninstall

version := 1.4.1
gsl_flags := $(shell pkg-config --libs --cflags gsl)
ifeq ($(gsl_flags),)
$(error Failed to query GSL complilation flags from pkg-config)
endif
gsl_flags += -DHAVE_INLINE
commonflags := -Wall -Wextra -std=c99 -pedantic -Wno-unknown-pragmas -Wshadow -Wpointer-arith
commonflags += $(CFLAGS)
commonflags += -g -DEEMD_DEBUG=0
commonflags += -fopenmp
PREFIX ?= /usr

SONAME = -soname
ifeq ($(shell uname -s),Darwin)
    SONAME = -install_name
endif

define uninstall_msg
If you used $(PREFIX) as the prefix when running `make install`,
you can undo the install by removing these files:
$(PREFIX)/include/eemd.h
$(PREFIX)/lib/libeemd.a
$(PREFIX)/lib/libeemd.so
$(PREFIX)/lib/libeemd.so.$(version)
endef
export uninstall_msg

all: libeemd.so.$(version) libeemd.a eemd.h

clean:
	rm -f libeemd.so libeemd.so.$(version) libeemd.a eemd.h obj/eemd.o
	rm -rf obj

install:
	install -d $(PREFIX)/include
	install -d $(PREFIX)/lib
	install -m644 eemd.h $(PREFIX)/include
	install -m644 libeemd.a $(PREFIX)/lib
	install libeemd.so.$(version) $(PREFIX)/lib
	cp -Pf libeemd.so $(PREFIX)/lib

uninstall:
	@echo "$$uninstall_msg"

obj:
	mkdir -p obj

obj/eemd.o: src/eemd.c src/eemd.h | obj
	gcc $(commonflags) -c $< $(gsl_flags) -o $@

libeemd.a: obj/eemd.o
	$(AR) rcs $@ $^

libeemd.so.$(version): src/eemd.c src/eemd.h
	gcc $(commonflags) $< -fPIC -shared -Wl,$(SONAME),$@ $(gsl_flags) -o $@
	ln -sf $@ libeemd.so

eemd.h: src/eemd.h
	cp $< $@
