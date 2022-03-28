// -------------------------------------------------------------------------------------------------
//                            Copyright (c) 2022 TJ IClab.
//                                          ALL RIGHTS RESERVED
// -------------------------------------------------------------------------------------------------
// Filename      : sub_module.sv
// Author        : jkhuang
// Created On    : 2022-03-24
// Version 1.1   : initial RTL, by jkhuang 2022-03-24
// -------------------------------------------------------------------------------------------------
// Description   :
// -------------------------------------------------------------------------------------------------


module sub_module #(
  /*AUTOINOUTPARAM*/
  /*beginning of AUTOINOUTPARAM*/
  parameter  integer unsigned Parameter1,
  parameter  integer unsigned Parameter2 = 8'b00000001,
  localparam integer unsigned Parameter3 = 128,
  parameter  integer unsigned Parameter5
  /*end of AUTOINOUTPARAM*/
)(
  /*AUTOARG*/
  /*beginning of AUTOARG*/
  input  wire unsigned [7:0]  input_variable_4[0:7][0:15],
  input  wire unsigned [15:0] input_variable_5,
  input  wire unsigned        input_variable_6,
  output wire unsigned [7:0]  output_variable_1[0:7][0:15],
  output reg  unsigned [7:0]  output_variable_2,
  output wire unsigned        output_variable_3
  /*end of AUTOARG*/
);

  /*AUTOVARIABLE*/
  /*beginning of AUTOVARIABLE*/
  /*error parameter*/
  /*error variable*/
  /*local parameter*/
  /*local variable*/
  wire unsigned [15:0] local_variable_3;  // local variable
  /*end of AUTOVARIABLE*/

  /*AUTOINST*/
  /*beginning of AUTOINST*/
  /*end of AUTOINST*/

endmodule