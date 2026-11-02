@'
# EEGR 471 Caravel SoC Verification with cocotb

## 1. System Architecture & Dataflow
This project implements a co-verification testbench for custom digital blocks integrated into the Caravel `user_project_wrapper`.
The flow uses a dual-driver / passive-monitor architecture:
* **Firmware Stimulus Driver**: Simulates in-system firmware execution and coordinates synchronization pulses via GPIO handshake pins.
* **cocotb Monitor & Checker**: An event-driven Python testbench running coroutines to sample output pins and assert equality against an independent mathematical reference model.

```text
       +-------------------------------------------------------+
       |             Caravel user_project_wrapper              |
       |                                                       |
       |   wb_clk_i ----> Clock Input                          |
       |   wb_rst_i ----> Active-High Reset                    |
       |   la_data_in[31:0] ---> DUT Stimulus Input            |
       |   la_data_in[37]   ---> Handshake Strobe              |
       |                                                       |
       |            +----------------------+                   |
       |            |       my_core        |                   |
       |            | (Bitwise Inverter)   |                   |
       |            +----------+-----------+                   |
       |                       |                               |
       |   io_out[31:0] <------+ DUT Processed Output          |
       |   io_out[37]   <------- Firmware Sync Handshake       |
       +-------------------------------------------------------+
   ```
   ---

## 2. Interface Pin Mapping
| Signal Name | Wrapper Pin | Direction | Description |
| :--- | :--- | :--- | :--- |
| `clk` | `wb_clk_i` | Input | Master SoC simulation clock (10 MHz) |
| `reset` | `wb_rst_i` | Input | Active-high system reset |
| `data_in[31:0]` | `la_data_in[31:0]` | Input | 32-bit stimulus bus driven via Logic Analyzer |
| `sync_pulse` | `la_data_in[37]` / `io_out[37]` | Pass-through | Handshake strobe signaling valid output |
| `data_out[31:0]` | `io_out[31:0]` | Output | 32-bit processed data output observed by cocotb |

---

## 3. Firmware Synchronization Mechanism
To eliminate race conditions between the stimulus provider and the monitor, synchronization is enforced via `io_out[37]`:
1. The driver asserts stimulus on `la_data_in[31:0]` and raises `io_out[37] = 1`.
2. The cocotb monitor waits for `io_out[37] == 1` before latching `io_out[31:0]`.
3. The driver clears `io_out[37] = 0` to acknowledge transfer completion.

---

## 4. Testbench Architecture (Parts 5–8)
* **Part 5 (Stimulus Driver)**: Firmware/stimulus sequencing drives boundary vectors.
* **Part 6 (Test Vectors)**: Validates boundary patterns (`0x00000000`, `0xAAAAAAAA`, `0x55555555`, `0xFFFFFFFF`, `0x12345678`).
* **Part 7 (Independent Reference Model)**: Derives expected outputs in Python using `(~v) & 0xFFFFFFFF` independently of the DUT.
* **Part 8 (Modular Testbench)**: Implemented in `CaravelDUTEnv` separating signal drivers, monitors, and assertion checkers.

---

## 5. Part 9: Self-Checking & Failure Injection Analysis
To verify that the testbench detects hardware faults:
1. An intentional error was injected by forcing `expected_outputs[0] = 0xDEADBEEF`.
2. The simulation failed on Step 0:
   ```text
   AssertionError: [FAIL] Step 0 Mismatch!
     Expected: 0xdeadbeef
     Observed: 0xffffffff
     ```
   Execution halted immediately, confirming that errors cannot pass silently.
## 6. Analysis Questions
* **Q1: What is the role of the Caravel Management Processor?**
```text
Answer:

A Caravel Management Processor acts as the in-system host master and stimulus driver. 
It configures GPIO multiplexing registers, initializes the harness, asserts reset release, and 
drives transaction stimuli to the student RTL via Wishbone or Logic Analyzer interfaces.
```

* **Q2: Why is synchronization required?**
```text
Answer:

Firmware executes inside the simulated core, while cocotb runs asynchronously in simulation time. 
Synchronization prevents race conditions (reading uninitialized/floating states) and guarantees that 
outputs are stable before assertion checks occur.
```

* **Q3: What are the advantages of a self-checking testbench?**
```text
Answer:

It enables automated continuous integration regressions, scales across thousands of test cycles 
without manual waveform scanning, and eliminates human error during boundary evaluation.
```

* **Q4: Compare: Stimulus vs. Monitoring vs. Checking**
```text
Answer:

- Stimulus: Active generation of control and input vectors to the DUT.

- Monitoring: Passive sampling of bus lines upon clock or sync triggers without mutating pin states.

- Checking: Evaluation comparing monitored data against an independent golden reference model.
```

* **Q5: Why must expected vectors remain independent of firmware?**
```text
Answer:

Coupling expected outputs directly to firmware introduces common-mode verification errors. 
If firmware contains a bug, a coupled checker could validate the erroneous behavior. 
Independent reference models guarantee the actual specification is enforced.
```

* **Q6: What are the consequences of changing firmware inputs before sampling?**
```text
Answer:

The DUT state transitions prematurely, causing cocotb to sample stale or invalid intermediate 
values, resulting in false-positive assertion failures.
```

* **Q7: Architecture Adjustments for Bus Protocols (APB, AXI, SPI, UART)?**
```text
Answer:

Requires transitioning to a Transaction-Level Modeling (TLM) architecture: utilizing Bus 
Functional Models (BFMs) to manage valid/ready handshakes, bus monitors to serialize packets 
into queues, and scoreboards to compare transaction structures.
```

* **Q8: What are some challenges when moving from RTL to gate-level simulation (GLS)?**
```text
Answer:

- Standard cell delays and timing annotations (SDF) expose setup/hold violations.

- X-propagation occurs if flip-flops are not properly reset.

- Internal RTL wire visibility is lost due to logic synthesis flattening.

- Execution speeds are significantly slower than behavioral simulation.
```