# cocotb Makefile for Caravel Harness Verification

SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Paths relative to the cocotb/ directory
PROJECT_ROOT = $(shell pwd)/..
VERILOG_SOURCES = $(PROJECT_ROOT)/verilog/rtl/user_project_wrapper.v \
                  $(PROJECT_ROOT)/verilog/rtl/my_core.v

# Top-level module inside the simulator
TOPLEVEL = user_project_wrapper

# Python testbench module name (test_dut.py -> test_dut)
MODULE = test_dut

# Simulator compilation flags
COMPILE_ARGS += -I$(PROJECT_ROOT)/verilog/rtl

include $(shell cocotb-config --makefiles)/Makefile.sim
