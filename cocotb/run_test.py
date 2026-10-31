import os
import sys
from cocotb_test.simulator import run

def test_runner():
    proj_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    verilog_sources = [
        os.path.join(proj_path, "verilog", "rtl", "user_project_wrapper.v"),
        os.path.join(proj_path, "verilog", "rtl", "my_core.v")
    ]

    run(
        simulator="icarus",
        verilog_sources=verilog_sources,
        toplevel="user_project_wrapper",
        module="test_dut",
        includes=[os.path.join(proj_path, "verilog", "rtl")],
        compile_args=["-I" + os.path.join(proj_path, "verilog", "rtl")]
    )

if __name__ == "__main__":
    test_runner()
