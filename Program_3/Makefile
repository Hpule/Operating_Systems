# Makefile for memSim.py

all: memSim

memSim: memSim.py
	tr -d '\r' < memSim.py > memSim.tmp && mv memSim.tmp memSim.py 
	chmod +x memSim.py
	ln -sf memSim.py memSim

# Clean up
clean:
	rm -f memSim

install: memSim
	@echo "You can manually copy 'memSim' to a directory in your PATH if desired"

# Help target
help:
	@echo "Makefile for memSim.py"
	@echo ""
	@echo "Usage:"
	@echo "  make           - Make memSim.py executable and create a symlink named 'memSim'"
	@echo "  make clean     - Remove the memSim symlink"
	@echo "  make test      - Run basic tests"
	@echo "  make help      - Show this help message"
	@echo ""

test: memSim
	@echo "Running basic tests..."
	./memSim addresses.txt 10 FIFO
	./memSim addresses.txt 10 LRU
	./memSim addresses.txt 20 CLOCK
	@echo "Tests completed."

.PHONY: all clean install help test