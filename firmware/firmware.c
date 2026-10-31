#include <defs.h>

#define SYNC_PIN 37

void set_sync(uint32_t val) {
    if (val)
        reg_mprj_datal |= (1 << (SYNC_PIN - 32));
    else
        reg_mprj_datal &= ~(1 << (SYNC_PIN - 32));
}

void main() {
    // 1. Configure Pin 37 as Management Output for Handshake
    reg_mprj_io_37 = GPIO_MODE_MGMT_STD_OUTPUT;

    // 2. Configure Pins [31:0] as User Output to expose student RTL
    // (In full tests, iterate over all reg_mprj_io_0 through 31)
    reg_mprj_xfer = 1;
    while (reg_mprj_xfer == 1); // Wait for shift register transfer

    // 3. Signal initialization complete
    set_sync(0);

    // Test vector list
    uint32_t test_vectors[5] = {
        0x00000000,
        0xAAAAAAAA,
        0x55555555,
        0xFFFFFFFF,
        0x12345678
    };

    // Drive stimulus via Logic Analyzer probes
    for (int i = 0; i < 5; i++) {
        set_sync(0);
        reg_la0_data = test_vectors[i];

        // Allow cycles for DUT register transition
        for (volatile int d = 0; d < 20; d++);

        // Signal cocotb that output is ready
        set_sync(1);
        for (volatile int d = 0; d < 20; d++);
    }
}
