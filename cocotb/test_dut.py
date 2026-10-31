import cocotb
from cocotb.triggers import Timer, ClockCycles
from cocotb.clock import Clock

class CaravelDUTEnv:
    def __init__(self, dut):
        self.dut = dut
        self.sync_pin = 37

    def monitor_outputs(self) -> int:
        val = self.dut.io_out.value.binstr
        data_bits = val[-32:]
        return int(data_bits, 2)

    def check_result(self, step: int, observed: int, expected: int):
        assert observed == expected, (
            f"\n[FAIL] Step {step} Mismatch!\n"
            f"  Expected: {hex(expected)}\n"
            f"  Observed: {hex(observed)}"
        )
        cocotb.log.info(f"[PASS] Step {step}: Matches {hex(observed)}")

@cocotb.test()
async def test_my_core_baseline(dut):
    env = CaravelDUTEnv(dut)

    cocotb.start_soon(Clock(dut.wb_clk_i, 100, unit="ns").start())

    dut.wb_rst_i.value = 1
    dut.la_data_in.value = 0
    await ClockCycles(dut.wb_clk_i, 5)
    dut.wb_rst_i.value = 0
    await ClockCycles(dut.wb_clk_i, 2)

    test_vectors = [0x00000000, 0xAAAAAAAA, 0x55555555, 0xFFFFFFFF, 0x12345678]
    expected_outputs = [(~v) & 0xFFFFFFFF for v in test_vectors]

    # --- PART 9 BUG INJECTION ---
    # Intentionally corrupt the expected value for step 0 to prove self-checking
    # bug reverted 

    cocotb.log.info("Starting Caravel baseline verification with intentional bug...")

    for idx, (vec, expected) in enumerate(zip(test_vectors, expected_outputs)):
        dut.la_data_in.value = vec | (1 << 37)
        await ClockCycles(dut.wb_clk_i, 2)

        observed = env.monitor_outputs()
        env.check_result(idx, observed, expected)

        dut.la_data_in.value = vec & ~(1 << 37)
        await ClockCycles(dut.wb_clk_i, 2)
