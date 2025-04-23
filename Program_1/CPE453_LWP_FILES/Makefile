PLAT=$(shell uname -i)
LWP-EX=liblwp-$(PLAT).a
SN-EX=libsnakes-$(PLAT).a
LWP=liblwp.a

all: $(LWP)
examples: numbersmain-ex snakemain-ex hungrymain-ex
tests: numbersmain snakemain hungrymain numbersmain

snakemain: snakemain.c snakes.h $(LWP) $(SN-EX)
	cc -Wall -Werror -g -o $@ $< $(LWP) $(SN-EX) -L/usr/lib64 -lncurses


snakemain-ex: snakemain.c snakes.h $(LWP-EX) $(SN-EX)
	cc -Wall -Werror -g -o $@ $< $(LWP-EX) $(SN-EX) -L/usr/lib64 -lncurses

hungrymain: hungrymain.c snakes.h $(LWP) $(SN-EX)
	cc -Wall -Werror -g -m32 -o $@ $< $(LWP) $(SN-EX) -L/usr/lib64 -lncurses

hungrymain-ex: hungrymain.c snakes.h $(LWP-EX) $(SN-EX)
	cc -Wall -Werror -g -o $@ $< $(LWP-EX) $(SN-EX) -L/usr/lib64 -lncurses

numbersmain: numbersmain.c lwp.h $(LWP)
	cc -Wall -Werror -g -m32 -o $@ $< $(LWP)

numbersmain-ex: numbersmain.c lwp.h $(LWP-EX)
	cc -Wall -Werror -g -o $@ $< $(LWP-EX)

startThreads.o: startThreads.c lwp.h
	cc -Wall -Werror -g -m32 -c -o $@ $

startThreads: startThreads.o $(LWP)
	cc -g -o $@ $< $(LWP)
	

$(LWP): lwp.o
	ar r $@ lwp.o
	ranlib $@

lwp.o: lwp.c lwp.h
	cc -Wall -Werror -g -m32 -c -o $@ $<
	cc -S $<

clean:
	-rm -f numbersmain snakemain hungrymain $(LWP) lwp.o liblwp.o numbersmain-ex snakemain-ex hungrymain-ex
	-rm -f lwp.s
