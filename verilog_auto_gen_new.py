# V0.0: jkhuang 2022-04-01 Code initialization
# V0.1: jkhuang 2022-04-02 finish data preparation
# V0.2: jkhuang 2022-04-03 finish verilog generation function

import pandas as pd
import re
from optparse import OptionParser
import os
import warnings
import numpy as np


def find_file_list(dir, recursion_flag, type=None, gen_dir=None):
    list = []
    if os.path.isdir(dir):
        input_root = dir
        if type == 'verilog':
            r = re.compile(r'\w+\.(v|sv)$')
        elif type == 'excel':
            r = re.compile(r'\w+\.(xls|xlsx)$')

        for root, dirs, files in os.walk(input_root):
            # list = list.append((root + '/' + x) for x in files if r.search(x))
            for x in files:
                if r.search(x):
                    if root == './':
                        list.append(root + x)
                    else:
                        list.append(root + '/' + x)
            if not recursion_flag:
                break
    else:
        file_name = dir.split(sep='/')[-1]
        file_name = file_name.replace('.', r'\.')  # replace all the .
        file_name = file_name.replace('*', r'\w+')  # replace all the *
        file_name = file_name + '$'

        input_root = ''
        for item in dir.split(sep='/')[:-1]:
            input_root = input_root + item + '/'

        r = re.compile(file_name)

        for root, dirs, files in os.walk(input_root):
            # list = list.append((root + '/' + x) for x in files if r.search(x))
            for x in files:
                if r.search(x):
                    list.append(root + x)
            break

    if list == []:
        if type == 'excel':
            raise RuntimeError(f'No {type} file is found.')
        elif type == 'verilog' and not gen_dir:
            raise RuntimeError(f'No {type} file is found and no generate dir is specified')

    return list


class Module:
    'consist of the information of one module'

    def __init__(self):
        self.module_name = None
        self.module_verilog_file_type = None  # 'v' or 'sv'
        self.module_port = None
        self.module_parameter = None
        self.module_ioport = None
        self.module_input = None
        self.module_output = None
        self.module_ioput = None
        self.module_localparam = None
        self.module_localvariable = None
        self.sub_module = []
        self.regular_expression = []
        self.vfile_content = None
        self.vfile_dir = None

    def type_check(self, type_series):
        type_lst = [
            'parameter',
            'localparam',
            'input',
            'output',
            'inout',
        ]
        for i in type_series.index:
            if type_series[i] not in type_lst:
                if isinstance(type_series[i], str):
                    raise RuntimeError(
                        f'Error: Excel type error in row index {i}, content:\n module name {self.module_name} \n {self.module_port.loc[i, :]}')

    def v_parameter_data_type_check(self, data_type_series):
        verilog_data_type_lst = [
            'integer',
            'real',
            'time',
        ]
        for i in data_type_series.index:
            if data_type_series[i] not in verilog_data_type_lst:
                if isinstance(data_type_series[i], str):
                    raise RuntimeError(
                        f'Error: Excel parameter data type error in row index {i}, content:\n module name {self.module_name} \n {self.module_port.loc[i, :]}')

    def v_variable_data_type_check(self, data_type_series):
        verilog_data_type_lst = [
            'wire',
            'reg',
        ]
        for i in data_type_series.index:
            if data_type_series[i] not in verilog_data_type_lst:
                if isinstance(data_type_series[i], str):
                    raise RuntimeError(
                        f'Error: Excel variable data type error in row index {i}, content:\n module name {self.module_name} \n {self.module_port.loc[i, :]}')

    def sv_parameter_data_type_check(self, data_type_series):
        verilog_data_type_lst = [
            'integer',
            'real',
            'time',
            'longint',
            'int',
            'shortint',
            'byte',
            'bit',
        ]
        for i in data_type_series.index:
            if data_type_series[i] not in verilog_data_type_lst:
                if isinstance(data_type_series[i], str):
                    raise RuntimeError(
                        f'Error: Excel parameter data type error in row index {i}, content:\n module name {self.module_name} \n {self.module_port.loc[i, :]}')

    def sv_variable_data_type_check(self, data_type_series):
        verilog_data_type_lst = [
            'wire',
            'reg',
            'logic',
        ]
        for i in data_type_series.index:
            if data_type_series[i] not in verilog_data_type_lst:
                if isinstance(data_type_series[i], str):
                    raise RuntimeError(
                        f'Error: Excel variable data type error in row index {i}, content:\n module name {self.module_name} \n {self.module_port.loc[i, :]}')

    def sign_check(self, sign_series):
        sign_lst = [
            'signed',
            'unsigned',
        ]
        for i in sign_series.index:
            if sign_series[i] not in sign_lst:
                if isinstance(sign_series[i], str):
                    raise RuntimeError(
                        f'Error: Excel sign error in row index {i}, content:\n module name {self.module_name} \n {self.module_port.loc[i, :]}')

    def width_check(self, width_series):
        s = r'^\[\w+:\w+\]$'
        re_str = re.compile(s)
        for i in width_series.index:
            if isinstance(width_series[i], str):
                if not re_str.search(width_series[i]):
                    raise RuntimeError(
                        f'Error: Excel width error in row index {i}, content:\n module name {self.module_name} \n {self.module_port.loc[i, :]}')

    def name_check(self, name_series):
        s = r'^\w+$'
        re_str = re.compile(s)
        for i in name_series.index:
            if not re_str.search(name_series[i]):
                raise RuntimeError(
                    f'Error: Excel name error in row index {i}, content:\n module name {self.module_name} \n {self.module_port.loc[i, :]}')

    def sub_module_port_check(self):  # only check name and connect bit
        for item in self.sub_module:
            s = r'^\w+$'
            re_str = re.compile(s)
            sub_module_name = item['sub_module_name']
            sub_module_inst_name = item['sub_module_inst_name']
            sub_module_port = item['sub_module_port']
            for i in sub_module_port['name'].index:
                if isinstance(sub_module_port['name'][i], str):
                    if not re_str.search(sub_module_port['name'][i]):
                        raise RuntimeError(
                            f'Error: Excel name of sub module port error in row index {i}, content:\n module name {self.module_name} \nsub module name is {sub_module_name}, sub module inst name is {sub_module_inst_name} \n{sub_module_port.loc[i, :]}')
            for i in sub_module_port['default value/instantiated variable'].index:
                if isinstance(sub_module_port['default value/instantiated variable'][i], str):
                    if not re_str.search(sub_module_port['default value/instantiated variable'][i]):
                        raise RuntimeError(
                            f'Error: Excel instantiated variable of sub module port error in row index {i}, content:\n module name {self.module_name} \nsub module name is {sub_module_name}, sub module inst name is {sub_module_inst_name} \n{sub_module_port.loc[i, :]}')

            s = r'^(\[\w+:\w+\])+$'
            re_str = re.compile(s)
            for i in sub_module_port['multiple dimension/connect bit'].index:
                if isinstance(sub_module_port['multiple dimension/connect bit'][i], str):
                    if not re_str.search(sub_module_port['multiple dimension/connect bit'][i]):
                        raise RuntimeError(
                            f'Error: Excel connect bit of sub module port error in row index {i}, content:\n module name {self.module_name} \n  sub module name is {sub_module_name}, sub module inst name is {sub_module_inst_name} \n {sub_module_port.loc[i, :]}')

    def default_value_check(self, default_value_series):
        for i in default_value_series.index:
            if not isinstance(default_value_series[i], str):
                warnings.warn(
                    f'Warning: Excel default value is empty in row index {i}, content:\n module name {self.module_name} \n {self.module_port.loc[i, :]}')

    def multiple_dimension_check(self, multiple_dimension_series):
        s = r'^(\[\w+:\w+\])+$'
        re_str = re.compile(s)
        for i in multiple_dimension_series.index:
            if isinstance(multiple_dimension_series[i], str):
                if not re_str.search(multiple_dimension_series[i]):
                    raise RuntimeError(
                        f'Error: Excel multiple dimension error in row index {i}, content:\n module name {self.module_name} \n {self.module_port.loc[i, :]}')

    # def not_blank_check(self):
    #     if self.module_parameter['multiple dimension/connect bit'].notnull():
    #         warnings.warn('Warning: the data in column multiple dimension/connect bit of parameter row is useless.')
    #     if self.module_localparam['multiple dimension/connect bit'].notnull():
    #         warnings.warn('Warning: the data in column multiple dimension/connect bit of parameter row is useless.')
    #     if self.module_ioport['default value/instantiated variable'].notnull():
    #         warnings.warn('Warning: the data in column multiple dimension/connect bit of parameter row is useless.')
    #     if self.module_localvariable['default value/instantiated variable'].notnull():
    #         warnings.warn('Warning: the data in column multiple dimension/connect bit of parameter row is useless.')

    def module_name_check(self):
        if self.module_verilog_file_type == None:
            raise RuntimeError(f'Error: the module name {self.module_name} is not correct, eg. module(v)')

    def sub_module_name_check(self):
        for item in self.sub_module:
            if item['sub_module_inst_name'] == None:
                sub_module_name = item['sub_module_name']
                raise RuntimeError(
                    f'Error: the sub module name or inst name is not correct:\n module name {self.module_name} \n {sub_module_name}')

    def regular_expression_check(self):
        for item in self.regular_expression:
            regular_module_name_expression = item['regular_module_name_expression']
            regular_module_inst_expression = item['regular_module_inst_expression']
            regular_variable_expression = item['regular_variable_expression']
            regular_connect_expression = item['regular_connect_expression']
            regular_connect_bit_expression = item['regular_connect_bit_expression']
            if regular_module_inst_expression == None:
                raise RuntimeError(
                    f'Error: the regular expression is not correct:\n module name {self.module_name} \n {item}')
            try:
                item['regular_module_name_expression'] = re.compile(regular_module_name_expression)
            except:
                raise RuntimeError(
                    f'Error: the regular expression can\'t be compiled:\n module name {self.module_name} \n {item}')
            try:
                item['regular_module_inst_expression'] = re.compile(regular_module_inst_expression)
            except:
                raise RuntimeError(
                    f'Error: the regular expression can\'t be compiled:\n module name {self.module_name} \n {item}')
            try:
                item['regular_variable_expression'] = re.compile(regular_variable_expression)
            except:
                raise RuntimeError(
                    f'Error: the regular expression can\'t be compiled:\n module name {self.module_name} \n {item}')
            try:
                item['regular_connect_expression'] = re.compile(regular_connect_expression)
            except:
                raise RuntimeError(
                    f'Error: the regular expression can\'t be compiled:\n module name {self.module_name} \n {item}')
            if isinstance(regular_connect_bit_expression, str):  # regular_connect_bit_expression can be empty
                try:
                    item['regular_connect_bit_expression'] = re.compile(regular_connect_bit_expression)
                except:
                    raise RuntimeError(
                        f'Error: the regular expression can\'t be compiled:\n module name {self.module_name} \n {item}')
            # regular_variable_type_lst = [
            #     'ioport',
            #     'parameter',
            # ]
            # if item['regular_variable_type'] not in regular_variable_type_lst:
            #     raise RuntimeError(
            #         f'Error: the regular variable type is not correct:\n {item}')

    # def sub_module_port_check(self):
    #     for item in self.sub_module:

    def data_check(self):
        self.module_name_check()
        self.sub_module_name_check()
        self.regular_expression_check()
        self.sub_module_port_check()  # check the syntax
        # check data type
        if self.module_verilog_file_type == 'v':  # v
            # check parameter
            self.v_parameter_data_type_check(self.module_parameter['data type'])
            # check ioport
            self.v_variable_data_type_check(self.module_ioport['data type'])
            # check localparam
            self.v_parameter_data_type_check(self.module_localparam['data type'])
            # check local variable
            self.v_variable_data_type_check(self.module_localvariable['data type'])
        else:  # sv
            # check parameter
            self.sv_parameter_data_type_check(self.module_parameter['data type'])
            # check ioport
            self.sv_variable_data_type_check(self.module_ioport['data type'])
            # check localparam
            self.sv_parameter_data_type_check(self.module_localparam['data type'])
            # check local variable
            self.sv_variable_data_type_check(self.module_localvariable['data type'])
        # check sign
        self.sign_check(self.module_port['sign'])
        # check width
        self.width_check(self.module_port['width'])
        # check name
        self.name_check(self.module_port['name'])
        # check default value
        self.default_value_check((self.module_parameter['default value/instantiated variable']))
        self.default_value_check((self.module_localparam['default value/instantiated variable']))
        # check multiple dimension
        self.multiple_dimension_check(self.module_ioport['multiple dimension/connect bit'])
        self.multiple_dimension_check(self.module_localvariable['multiple dimension/connect bit'])
        # check if there is not necessary information
        # self.not_blank_check()

    def port_completion(self):
        if self.module_verilog_file_type == 'v':
            self.module_parameter.loc[:, 'data type'][self.module_parameter.loc[:, 'data type'].isnull()] = 'integer'
            self.module_parameter.loc[:, 'sign'][self.module_parameter.loc[:, 'sign'].isnull()] = 'unsigned'
            self.module_localparam.loc[:, 'data type'][self.module_localparam.loc[:, 'data type'].isnull()] = 'integer'
            self.module_localparam.loc[:, 'sign'][self.module_localparam.loc[:, 'sign'].isnull()] = 'unsigned'
            self.module_ioport.loc[:, 'data type'][self.module_ioport.loc[:, 'data type'].isnull()] = 'wire'
            self.module_ioport.loc[:, 'sign'][self.module_ioport.loc[:, 'sign'].isnull()] = 'unsigned'
            self.module_localvariable.loc[:, 'data type'][
                self.module_localvariable.loc[:, 'data type'].isnull()] = 'wire'
            self.module_localvariable.loc[:, 'sign'][self.module_localvariable.loc[:, 'sign'].isnull()] = 'unsigned'
        elif self.module_verilog_file_type == 'sv':
            self.module_parameter.loc[:, 'data type'][self.module_parameter.loc[:, 'data type'].isnull()] = 'int'
            self.module_parameter.loc[:, 'sign'][self.module_parameter.loc[:, 'sign'].isnull()] = 'unsigned'
            self.module_localparam.loc[:, 'data type'][self.module_localparam.loc[:, 'data type'].isnull()] = 'int'
            self.module_localparam.loc[:, 'sign'][self.module_localparam.loc[:, 'sign'].isnull()] = 'unsigned'
            self.module_ioport.loc[:, 'data type'][self.module_ioport.loc[:, 'data type'].isnull()] = 'logic'
            self.module_ioport.loc[:, 'sign'][self.module_ioport.loc[:, 'sign'].isnull()] = 'unsigned'
            self.module_localvariable.loc[:, 'data type'][
                self.module_localvariable.loc[:, 'data type'].isnull()] = 'logic'
            self.module_localvariable.loc[:, 'sign'][self.module_localvariable.loc[:, 'sign'].isnull()] = 'unsigned'
        else:
            raise RuntimeError(f'module {self.module_name} verilog file type {self.module_verilog_file_type} error')


class ContentIndentLst:
    def __init(self, dataframe):
        content_indet_lst = []
        for i in range(dataframe.shape[1]):
            content_indet_lst.append([])  # continue from here



class ModuleList:
    'consist of all the information of module'

    def __init__(self, vfile_list, xfile_list, throughout_flag, completion_flag, gen_dir):
        self.module_list = []  # module specified in excel
        self.throughout_flag = throughout_flag
        self.completion_flag = completion_flag
        self.iter_num = 0
        self.vfile_list = vfile_list
        self.xfile_list = xfile_list
        self.gen_dir = gen_dir

        # check input
        if not os.path.isdir(self.gen_dir):
            raise RuntimeError(f'Error: generate directory {self.gen_dir} is not a directory!')

        self.module_list_gen()
        self.module_list_check()
        self.module_list_completion()

    # insert the xfile information into vfile
    def change_vfile(self):
        0

    def generate_vfile(self):
        if self.gen_dir:
            not_exist_flag = 1
            path = None
            index = None
            gen_content = [
                '  /*AUTOINOUTPARAM*/\n',
                ')(\n',
                '  /*AUTOARG*/\n',
                ');\n',
                '\n',
                '  /*AUTOVARIABLE*/\n',
                '\n',
                '  /*AUTOINST*/\n',
                '\n',
                'endmodule\n',
            ]
            for module_list_item in self.module_list:
                if not module_list_item.vfile_dir:
                    path = os.path.join(self.gen_dir,
                                        module_list_item.module_name + '.' + module_list_item.module_verilog_file_type)
                    verilog_file = open(path, 'w+')
                    verilog_file.write(f"module {module_list_item.module_name} #(\n" + "".join(gen_content))
                    verilog_file.close()
                    self.module_list[self.module_list.index(module_list_item)].vfile_dir = path

    def module_list_gen(self):
        module_name_str = r'^(\w+)\((v|sv)\)$'
        re_module_name_str = re.compile(module_name_str)
        sub_module_str = r'^(\w+)--(\w+)$'
        re_sub_module_str = re.compile(sub_module_str)
        regular_expression_str = r'\(r\)(.+)--(.+)'
        re_regular_expression_str = re.compile(regular_expression_str)

        # read in the xfile_list
        for index in range(len(self.xfile_list)):
            # skip the file
            xfile_name = self.xfile_list[index].split(sep='/')[-1]
            xfile_type = xfile_name.split(sep='.')[-1]
            if xfile_name[0] == '~':  # skip the temporary Excel file
                break
            if xfile_type != 'xls' and xfile_type != 'xlsx':
                break

            table_dict = pd.read_excel(self.xfile_list[index],
                                       converters={0: str, 1: str, 2: str, 3: str, 4: str, 5: str, 6: str, 7: str},
                                       sheet_name=None, usecols=list(range(8)))
            for table in table_dict.values():  # step into the sheet
                module = Module()
                # find all the significant row
                table_module_series = table['module']
                module_name = table_module_series[0]
                if module_name in self.get_module_name_lst():  # drop the excel if the module name is used
                    break
                table_module_index = list(table_module_series.dropna().index)
                table_module_index.append(
                    table.index[-1] + 1)  # the last item of table_module_index is the row number of table

                # rename the column name
                table.columns = ['module', 'type', 'data type', 'sign', 'width', 'name',
                                 'default value/instantiated variable', 'multiple dimension/connect bit']
                # set the unused box to null
                if len(table_module_index) > 2:
                    table.loc[table_module_index[1]:table_module_index[-1] - 1, 'type':'width'] = np.nan
                # delete all the black row
                table = table.dropna(axis=0, how='all')

                for i in range(len(table_module_index)):
                    if i == 0:  # the first row must be top module

                        m = re_module_name_str.search(table_module_series[i])
                        if m:
                            module.module_name = m.group(1)
                            module.module_verilog_file_type = m.group(2)
                        else:
                            module.module_name = table_module_series[i]
                            module.module_verilog_file_type = None

                        # find vfile directory
                        vfile_str = module.module_name + '\\.' + module.module_verilog_file_type + '$'
                        re_vfile_str = re.compile(vfile_str)
                        for vfile_list_item in self.vfile_list:
                            if re_vfile_str.search(vfile_list_item):
                                module.vfile_dir = vfile_list_item
                                break

                        setattr(module, 'module_port', table.loc[
                                                       table_module_index[0]:table_module_index[1] - 1,
                                                       'type':'multiple dimension/connect bit'])
                        setattr(module, 'sub_module', [])
                        setattr(module, 'regular_expression', [])
                        setattr(module, 'module_parameter',
                                module.module_port[module.module_port['type'] == 'parameter'])
                        setattr(module, 'module_ioport',
                                module.module_port[(module.module_port['type'] == 'input') | (module.module_port[
                                                                                                  'type'] == 'output') | (
                                                           module.module_port['type'] == 'inout')])
                        setattr(module, 'module_input',
                                module.module_port[module.module_port['type'] == 'input'])
                        setattr(module, 'module_output',
                                module.module_port[module.module_port['type'] == 'output'])
                        setattr(module, 'module_inout',
                                module.module_port[module.module_port['type'] == 'inout'])
                        setattr(module, 'module_localparam',
                                module.module_port[module.module_port['type'] == 'localparam'])
                        setattr(module, 'module_localvariable',
                                module.module_port[(module.module_port['type'] != 'input') & (
                                        module.module_port['type'] != 'output') & (
                                                           module.module_port['type'] != 'inout') & (
                                                           module.module_port['type'] != 'parameter') & (
                                                           module.module_port['type'] != 'localparam')])

                    elif not i == (len(table_module_index) - 1):
                        # regular expression
                        if table_module_series[table_module_index[i]][0:3] == '(r)':
                            m = re_regular_expression_str.search(table_module_series[table_module_index[i]])

                            regular_module_name = m.group(1)
                            regular_module_inst_expression = m.group(2)
                            # regular_variable_type = table.loc[table_module_index[i], 'type']
                            regular_variable_expression = table.loc[table_module_index[i], 'name']
                            regular_connect_expression = table.loc[
                                table_module_index[i], 'default value/instantiated variable']
                            regular_connect_bit_expression = table.loc[
                                table_module_index[i], 'multiple dimension/connect bit']

                            regular_expression_dict = {}
                            regular_expression_dict['regular_module_name_expression'] = regular_module_name
                            regular_expression_dict['regular_module_inst_expression'] = regular_module_inst_expression
                            # regular_expression_dict['regular_variable_type'] = regular_variable_type
                            regular_expression_dict['regular_variable_expression'] = regular_variable_expression
                            regular_expression_dict['regular_connect_expression'] = regular_connect_expression
                            regular_expression_dict['regular_connect_bit_expression'] = regular_connect_bit_expression
                            module.regular_expression.append(regular_expression_dict)
                        else:
                            sub_module_dict = {}
                            module_inst_port = table.loc[table_module_index[i]:table_module_index[i + 1] - 1,
                                               'name':'multiple dimension/connect bit']
                            m = re_sub_module_str.search(table_module_series[table_module_index[i]])
                            if m:
                                sub_module_dict['sub_module_name'] = m.group(1)
                                sub_module_dict['sub_module_inst_name'] = m.group(2)
                            else:
                                sub_module_dict['sub_module_name'] = table_module_series[table_module_index[i]]
                                sub_module_dict['sub_module_inst_name'] = None
                            sub_module_dict['sub_module_port'] = module_inst_port
                            module.sub_module.append(sub_module_dict)
                self.module_list.append(module)

    def module_list_completion(self):
        if self.completion_flag:
            for module_list_item in self.module_list:
                module_list_item.port_completion()

    def module_list_check(self):
        # read in the vfile_list
        for vfile in self.vfile_list:
            verilog_file_name = vfile.split(sep='/')[-1]
            module_name = verilog_file_name.split(sep='.')[0]
            verilog_file_type = verilog_file_name.split(sep='.')[1]  # sv or v
            # skip the file
            if verilog_file_name[0] == '~':  # skip the temporary verilog file
                break
            if verilog_file_type != 'v' and verilog_file_type != 'sv':  # not v or sv file
                break
            if module_name not in self.get_module_name_lst():
                warnings.warn(f'Warning: can\'t find module {module_name} in excel')

        # check the data
        for module_list_item in self.module_list:
            module_list_item.data_check()  # only check the sntax of the sub module port

        # check if the sub module in excel, and there may be redundancy in the sub module port
        self.sub_module_check()

    def get_module(self, module_name):
        for module_list_item in self.module_list:
            if module_list_item.module_name == module_name:
                return module_list_item
        return None

    def get_module_name_lst(self):
        lst = []
        for module_list_item in self.module_list:
            lst.append(module_list_item.module_name)
        return lst

    def find_module_verilog_type(self, module_name):
        module = self.get_module(module_name)
        return module.module_verilog_file_type

    # check sub module name and sub module port
    def sub_module_check(self):
        for module_list_item in self.module_list:
            for sub_module_item in module_list_item.sub_module:
                sub_module_top = self.get_module(
                    sub_module_item['sub_module_name'])  # sub_module_top is the module information of the sub module
                sub_module_name = sub_module_item['sub_module_name']
                if not sub_module_top:
                    raise RuntimeError(
                        f'Error: sub module {sub_module_name} of module {module_list_item.module_name} is not in excel!')
                else:
                    for sub_module_port_name_item in sub_module_item['sub_module_port']['name']:
                        if isinstance(sub_module_port_name_item, str):
                            if (sub_module_port_name_item not in sub_module_top.module_ioport['name'].values) and (
                                    sub_module_port_name_item not in sub_module_top.module_parameter['name'].values):
                                raise RuntimeError(
                                    f'Error: sub module variable {sub_module_port_name_item} of sub module {sub_module_name} of module {module_list_item.module_name} is not correct!')

    def __len__(self):
        return len(self.module_list)

    def __getitem__(self, item):
        return self.module_list[item]

    def __iter__(self):
        return self

    def __next__(self):
        if self.iter_num < len(self):
            module_list = self.module_list[self.iter_num]
            self.iter_num = self.iter_num + 1
            return module_list
        else:
            self.iter_num = 0
            raise StopIteration


parser = OptionParser()
parser.add_option("-v", "--vfile", default="./*.v", help="verilog file directory, in linux format", dest="verilog_dir",
                  type="string")
parser.add_option("-x", "--xfile", default="./*.xlsx", help="xls/xlsx file directory, in linux format",
                  dest="module_dir", type="string")
parser.add_option("-d", "--delete", default=False, action="store_true", help="only delelte the auto gen code",
                  dest="delete_flag")
parser.add_option("-r", "--recursion", default=False, action="store_true",
                  help="recursivly find files in the vfile and xfile dir",
                  dest="recursion_flag")
parser.add_option("-t", "--throughout", default=False, action="store_true",
                  help="connect the variable to the top module port directly",
                  dest="throughout_flag")
parser.add_option("-c", "--complete", default=True, action="store_true",
                  help="auto complete the default data type and sign",
                  dest="complete_flag")  # change default in the future
parser.add_option("-g", "--gen_dir", default='./gen',
                  help="auto generate verilog file if not exists",
                  dest="gen_dir")
(option, args) = parser.parse_args()
verilog_dir = option.verilog_dir
module_dir = option.module_dir
delete_flag = option.delete_flag
recursion_flag = option.recursion_flag
throughout_flag = option.throughout_flag
completion_flag = option.complete_flag
gen_dir = option.gen_dir

vfile_list = find_file_list(verilog_dir, recursion_flag, type='verilog', gen_dir=gen_dir)
xfile_list = find_file_list(module_dir, recursion_flag, type='excel', gen_dir=gen_dir)
module_list = ModuleList(vfile_list, xfile_list, throughout_flag, completion_flag, gen_dir)
module_list.generate_vfile()
0
