`default_nettype none

module my_core (
    input  wire        clk,
    input  wire        reset,
    input  wire [31:0] data_in,
    output reg  [31:0] data_out
);

    always @(posedge clk or posedge reset) begin
        if (reset) begin
            data_out <= 32'h00000000;
        end else begin
            data_out <= ~data_in;
        end
    end

endmodule

`default_nettype wire
