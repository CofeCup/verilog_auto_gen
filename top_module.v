module top_module #(
  /*AUTOINOUTPARAM*/
  /*beginning of AUTOINOUTPARAM*/
  parameter integer unsigned Parameter1      = 16,           // sub_module_inst, sub_module_inst, sub_module_inst45
  parameter integer unsigned Parameter2      = 8'hAB,        // sub_module_inst, sub_module_inst, sub_module_inst45
  parameter integer unsigned Parameter3,
  parameter integer unsigned Parameter4      = 8'b11110000,
  parameter integer unsigned LocalParameter3,                // sub_module_inst1
  parameter integer unsigned LocalParameter2 = 8'b00000001,  // sub_module_inst1
  parameter integer unsigned LocalParameter2 = 128,          // sub_module_inst1
  /*end of AUTOINOUTPARAM*/
)(
  /*AUTOARG*/
  /*beginning of AUTOARG*/
  input  wire signed   [7:0]  input_variable_1[0:7][0:15],
  input  wire unsigned [15:0] input_variable_2,
  input  wire unsigned        input_variable_3,
  input  wire unsigned [7:0]  input_variable_4[0:7][0:15],                       // sub_module_inst, sub_module_inst3
  input  wire unsigned [15:0] local_variable_2,                                  // sub_module_inst1
  input  wire unsigned        input_variable_6,                                  // sub_module_inst, sub_module_inst3
  input  wire unsigned [15:0] input_variable_5,                                  // sub_module_inst, sub_module_inst3
  input  wire unsigned        local_variable_5,                                  // sub_module_inst2
  input  wire unsigned [7:0]  i_sub_module_inst45_regular_variable4[0:7][0:15],  // sub_module_inst45
  input  wire unsigned [15:0] i_sub_module_inst45_regular_variable5,             // sub_module_inst45
  input  wire unsigned        i_sub_module_inst45_regular_variable6              // sub_module_inst45
  output wire unsigned [7:0]  output_variable_1[0:7][0:15],                      // sub_module_inst45
  output reg  unsigned [7:0]  output_variable_2,                                 // sub_module_inst45
  output wire unsigned        output_variable_3,                                 // sub_module_inst45
  output wire unsigned [7:0]  o_sub_module_inst1_regular_variable1[0:7][0:15],   // sub_module_inst1
  output wire unsigned [7:0]  local_variable_3,                                  // sub_module_inst1 (***not sure***) , sub_module_inst2 (***not sure***)
  output wire unsigned        local_variable_4,                                  // sub_module_inst1 (***not sure***)
  output wire unsigned [7:0]  local_variable_6[0:7][0:15],                       // sub_module_inst2
  output wire unsigned [7:0]  local_variable_7,                                  // sub_module_inst2
  output wire unsigned        o_sub_module_inst2_regular_variable3,              // sub_module_inst2
  output wire unsigned [7:0]  o_sub_module_inst3_regular_variable1[0:7][0:15],   // sub_module_inst3
  output wire unsigned [7:0]  o_sub_module_inst3_regular_variable2,              // sub_module_inst3
  output wire unsigned        o_sub_module_inst3_regular_variable3,              // sub_module_inst3
  /*end of AUTOARG*/
);

  /*AUTOVARIABLE*/
  /*beginning of AUTOVARIABLE*/
  /*error parameter*/
  /*error variable*/
  /*local parameter*/
  /*local variable*/
  /*end of AUTOVARIABLE*/

  /*AUTOINST*/
  /*beginning of AUTOINST*/
  sub_module #(
    .Parameter1(LocalParameter3),
    .Parameter2(LocalParameter2),
    .Parameter5(Parameter5)
  ) sub_module_inst1 (
    .input_variable_4 (input_variable_4),
    .input_variable_5 (local_variable_2),
    .input_variable_6 (input_variable_6),
    .output_variable_1(o_sub_module_inst1_regular_variable1),
    .output_variable_2(local_variable_3[15:8]),
    .output_variable_3(local_variable_4[7:0])
  );
  sub_module #(
    .Parameter1(Parameter1),
    .Parameter2(Parameter2),
    .Parameter5(Parameter5)
  ) sub_module_inst2 (
    .input_variable_4 (local_variable_3[7:0]),
    .input_variable_5 (input_variable_5),
    .input_variable_6 (local_variable_5),
    .output_variable_1(local_variable_6),
    .output_variable_2(local_variable_7),
    .output_variable_3(o_sub_module_inst2_regular_variable3)
  );
  sub_module #(
    .Parameter1(Parameter1),
    .Parameter2(Parameter2),
    .Parameter5(Parameter5)
  ) sub_module_inst3 (
    .input_variable_4 (input_variable_4),
    .input_variable_5 (input_variable_5),
    .input_variable_6 (input_variable_6),
    .output_variable_1(o_sub_module_inst3_regular_variable1),
    .output_variable_2(o_sub_module_inst3_regular_variable2),
    .output_variable_3(o_sub_module_inst3_regular_variable3)
  );
  sub_module #(
    .Parameter1(Parameter1),
    .Parameter2(Parameter2),
    .Parameter5(Parameter5)
  ) sub_module_inst45 (
    .input_variable_4 (i_sub_module_inst45_regular_variable4),
    .input_variable_5 (i_sub_module_inst45_regular_variable5),
    .input_variable_6 (i_sub_module_inst45_regular_variable6),
    .output_variable_1(output_variable_1),
    .output_variable_2(output_variable_2),
    .output_variable_3(output_variable_3)
  );
  /*end of AUTOINST*/
endmodule