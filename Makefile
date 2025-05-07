# Makefile for schedSim.py

# Default target
all: schedSim

# Make schedSim.py executable
schedSim: schedSim.py
	chmod +x schedSim.py
	ln -sf schedSim.py schedSim

# Clean up
clean:
	rm -f schedSim

# Install - This is optional, can place the script in a directory on your PATH
install: schedSim
	@echo "You can manually copy 'schedSim' to a directory in your PATH if desired"

# Help target
help:
	@echo "Makefile for schedSim.py"
	@echo ""
	@echo "Usage:"
	@echo "  make           - Make schedSim.py executable and create a symlink named 'schedSim'"
	@echo "  make clean     - Remove the schedSim symlink"
	@echo "  make test      - Run basic tests"
	@echo "  make help      - Show this help message"
	@echo ""

# Test target - Add your test cases here
test: schedSim
	@echo "Running basic tests..."
	./schedSim jobs.txt -p FIFO
	./schedSim jobs.txt -p SRTN
	./schedSim jobs.txt -p RR -q 2
	@echo "Tests completed."

.PHONY: all clean install help test