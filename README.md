@'
# EEGR 471 Caravel SoC Verification with cocotb

## 1. System Architecture & Dataflow
This project implements a co-verification testbench for custom digital blocks integrated into the Caravel `user_project_wrapper`.
The flow uses a dual-driver / passive-monitor architecture:
* **Firmware Stimulus Driver**: Simulates in-system firmware execution and coordinates synchronization pulses via GPIO handshake pins.
* **cocotb Monitor & Checker**: An event-driven Python testbench running coroutines to sample output pins and assert equality against an independent mathematical reference model.  
bash
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