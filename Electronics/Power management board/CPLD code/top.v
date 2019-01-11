`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date:    14:15:46 08/01/2016 
// Design Name:    cosi_pwr_cpld
// Module Name:    top 
// Project Name:   cosi_pwr
// Target Devices: XC2C64A
// Tool versions:  ISE 14.7
// Description:    This circuit accepts two button inputs as the control signals for the
//                 relays. A short press activates the relay; A long press deactivates the relay.
//
// Dependencies: 
//
// Revision: 
// Revision 0.01 - File Created
// Additional Comments: 
//
//////////////////////////////////////////////////////////////////////////////////
module top(
    input pushBtnPin109,
    input pushBtnPin104,
    //input pushBtnPin216,
    input clkPin106,
    output ledPin100,
    output ledPin200,
	 output relayDCPin115,
    output relayACPin215
    );

wire pushBtnPin104_db;
reg pushBtnPin104_db1=0,pushBtnPin104_db2=0;
wire pushBtnPin109_db;
reg pushBtnPin109_db1=0,pushBtnPin109_db2=0;
reg [24:0] cnt=0;
reg cnt_en=1'b0;
reg relayDC=1'b0;
reg relayAC=1'b0;
Debouncer u0(
    .clk(clkPin106),
    .PB(pushBtnPin104), 
    .PB_state(pushBtnPin104_db)
);
Debouncer u1(
    .clk(clkPin106),
    .PB(pushBtnPin109), 
    .PB_state(pushBtnPin109_db)
);

always @ (posedge clkPin106)
begin
	 if (cnt_en == 1'b1)
    begin
	     cnt <= cnt + 1;  
    end
	 else cnt <= 25'h0;
end 

always @ (posedge clkPin106)
begin
	 pushBtnPin104_db1 <= pushBtnPin104_db;
	 pushBtnPin104_db2 <= pushBtnPin104_db1;
	 if (pushBtnPin104_db1 == 1'b1 && pushBtnPin104_db2 == 1'b0)
	 begin
	     relayDC <= 1'b1;
		  cnt_en <= 1'b1;
	 end
	 if(cnt[24] == 1'b1)
	 begin
	     cnt_en <= 1'b0;
	     if(pushBtnPin104_db2 == 1'b1)
		  begin
		      relayDC  <= 1'b0;
		  end
	 end
	 pushBtnPin109_db1 <= pushBtnPin109_db;
	 pushBtnPin109_db2 <= pushBtnPin109_db1;
	 if (pushBtnPin109_db1 == 1'b1 && pushBtnPin109_db2 == 1'b0)
	 begin
	     relayAC <= 1'b1;
		  cnt_en <= 1'b1;
	 end
	 if(cnt[24] == 1'b1)
	 begin
	     cnt_en <= 1'b0;
	     if(pushBtnPin109_db2 == 1'b1)
		  begin
		      relayAC  <= 1'b0;
		  end
	 end
end

assign relayDCPin115 = relayDC ;
assign relayACPin215 = relayAC & relayDC;
assign ledPin100 = relayDC;
assign ledPin200 = relayAC;

endmodule

module Debouncer(
    input clk,
    input PB,  
    output reg PB_state
);

reg PB_sync_0; 
reg PB_sync_1;  
reg [10:0] PB_cnt;
wire PB_idle = (PB_state==PB_sync_1);
wire PB_cnt_max = &PB_cnt;	

always @(posedge clk)
begin
	PB_sync_0 <= PB; 
	PB_sync_1 <= PB_sync_0;
	if(PB_idle)
		 PB_cnt <= 0;  
	else
	begin
		 PB_cnt <= PB_cnt + 11'd1;  
		 if(PB_cnt_max) PB_state <= ~PB_state; 
	end
end

endmodule
