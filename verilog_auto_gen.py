# V1.0: The code is nearly finished. Future update: 1. setting local variable when through out 2. change the file type
#       3. increase error annotation when through out. 2022-03-28
import pandas as pd
import re
from optparse import OptionParser
import os


def delete_last_blank(content):
    for i in range(len(content)):
        if i != len(content) - 1:
            content[i] = content[i].rstrip() + '\n'
        else:
            content[i] = content[i].rstrip()
    return content


def verilog_data_type_check(data_type):
    verilog_data_type_lst = [
        'integer',
        'float',
        'time',
        'wire',
        'reg'
    ]
    if data_type in verilog_data_type_lst:
        return True
    return False


def regular_expression_lst(regular_expression_lst, module_inst_name, variable_name):
    for item in regular_expression_lst:
        s_module_inst_name = item['regular_module_inst_expression'].search(module_inst_name)
        if s_module_inst_name != None:
            s_variable_name = item['regular_variable_expression'].search(variable_name)
            if s_variable_name != None:
                regular_connect_name = item['regular_connect_expression']
                for i in range(len(s_module_inst_name.regs) - 1):
                    regular_connect_name = regular_connect_name.replace(f'#{i}', s_module_inst_name.group(i + 1))
                for i in range(len(s_variable_name.regs) - 1):
                    regular_connect_name = regular_connect_name.replace(f'${i}', s_variable_name.group(i + 1))
                return regular_connect_name
    return None


def find_file_list(dir, recursion_flag, type=None):
    if dir[-1] != '/':
        file_name = dir.split(sep='/')[-1]
        file_name = file_name.replace('.', '\\.')
        file_name = file_name.replace('*', '.*')
        file_name = file_name + '$'

        input_root = ''
        for item in dir.split(sep='/')[:-1]:
            input_root = input_root + item + '/'

        r = re.compile(file_name)

        list = []
        for root, dirs, files in os.walk(input_root):
            # list = list.append((root + '/' + x) for x in files if r.search(x))
            for x in files:
                if r.search(x):
                    list.append(root + x)
            break
    else:
        input_root = dir
        if type == 'verilog':
            r = re.compile(r'.*\.(v|sv)$')
        elif type == 'excel':
            r = re.compile(r'.*\.(xls|xlsx)$')

        list = []
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

    return list


def find_first_str(content, pattern_text):
    for i in range(len(content)):
        match = re.search(pattern_text, content[i])
        if not match == None:
            row = i + 1
            break
    if not match == None:
        return row, match.span()
    else:
        return -1, None


def find_row(file_pt, row):  # file_pt in r+ mode
    file_pt.seek(0, 0)  # return to the beginning
    for i in range(row):
        file_pt.readline()
    # file_pt.seek(file_pt.tell(), 0)  # or the text will be written in the end
    return file_pt


def insert_text(file_pt, column, text):  # insert content start from the next row
    file_pt.write(' ' * column)
    file_pt.write(text + '\n')
    return file_pt


def content_lst_delete(content_lst, begin_txt, end_txt):
    begin_row = find_first_str(content_lst, begin_txt)[0]
    end_row = find_first_str(content_lst, end_txt)[0]
    if begin_row != -1 and end_row != -1:
        del content_lst[begin_row - 1:end_row]


def content_lst_insert(lst, row, text):
    lst.insert(row, text)
    row = row + 1
    return row


def module_list_find(module_list, module_name):
    for item in module_list:
        if item['module_name'] == module_name:
            return item
    return None


def find_max_str_len(module_port_column):
    max_len = 0
    for item in module_port_column:
        if isinstance(item, str):
            if max_len < len(item):
                max_len = len(item)
    return max_len


def autoinoutparam(verilog_file_content, module_list, module_list_module, verilog_file_type, throughout_flag):
    pattern_text = r'/\*AUTOINOUTPARAM\*/'
    insert_row, span = find_first_str(verilog_file_content, pattern_text)
    if insert_row != -1:
        module_port = module_list_module['module_port']
        module_column = module_port.loc[:, 'type']
        parameter_max_index = module_column[(module_column == 'parameter') | (module_column == 'localparam')].index[
            -1]  # the last index of parameter
        insert_row = content_lst_insert(verilog_file_content, insert_row,
                                        ' ' * span[0] + '/*beginning of AUTOINOUTPARAM*/\n')
        # throughout
        sub_module_list = module_list_module['sub_module']
        parameter_lst = []
        r_connect_name = re.compile('//')  # for comment append
        # for alignment
        inst_parameter_lst = [[], [], [], [], [], [], []]  # type, data type, sign, width, name, default value, comment

        for i in range(module_port.shape[0]):
            module_port_line = module_port.loc[i, :]
            if (module_port_line['type'] == 'parameter') or (module_port_line['type'] == 'localparam'):
                inst_parameter_lst[0].append(module_port_line['type'])
                if isinstance(module_port_line['data type'], str):
                    inst_parameter_lst[1].append(module_port_line['data type'])
                else:
                    inst_parameter_lst[1].append('')
                if isinstance(module_port_line['sign'], str):
                    inst_parameter_lst[2].append(module_port_line['sign'])
                else:
                    inst_parameter_lst[2].append('')
                if verilog_file_type == 'sv':
                    if isinstance(module_port_line['width'], str):
                        inst_parameter_lst[3].append(module_port_line['width'])
                    else:
                        inst_parameter_lst[3].append('')
                else:
                    inst_parameter_lst[3].append('')
                if isinstance(module_port_line['name'], str):
                    inst_parameter_lst[4].append(module_port_line['name'])
                    parameter_lst.append(module_port_line['name'])
                else:
                    inst_parameter_lst[4].append('?')
                if isinstance(module_port_line['default value/instantiated variable'], str):
                    inst_parameter_lst[5].append(module_port_line['default value/instantiated variable'] + ',')
                else:
                    inst_parameter_lst[5].append('')
                inst_parameter_lst[6].append('')
        if throughout_flag:
            for sub_module_list_item in sub_module_list:
                sub_module = module_list_find(module_list, sub_module_list_item['sub_module_name'])
                sub_module_port = sub_module['module_port']
                sub_module_connect_port = sub_module_list_item['sub_module_port']

                for i in range(sub_module_port.shape[0]):
                    module_port_line = sub_module_port.loc[i, :]
                    regular_connect_name = regular_expression_lst(module_list_module['regular_expression'],
                                                                  sub_module_list_item['sub_module_inst_name'],
                                                                  module_port_line['name'])
                    if module_port_line['type'] == 'parameter':
                        row_index = sub_module_connect_port[
                            sub_module_connect_port['name'] == module_port_line['name']].index
                        if len(row_index) != 0:
                            connect_name = sub_module_connect_port['default value/instantiated variable'][row_index[0]]
                        elif regular_connect_name != None:
                            connect_name = regular_connect_name
                        else:
                            connect_name = module_port_line['name']
                        if connect_name in parameter_lst:
                            inst_parameter_index = inst_parameter_lst[4].index(connect_name)
                            sub_module_inst_name = sub_module_list_item['sub_module_inst_name']
                            if r_connect_name.search(inst_parameter_lst[6][inst_parameter_index]):
                                inst_parameter_lst[6][inst_parameter_index] = inst_parameter_lst[6][
                                                                                  inst_parameter_index][
                                                                              :-1] + f', {sub_module_inst_name}'
                            else:
                                inst_parameter_lst[6][inst_parameter_index] = inst_parameter_lst[6][
                                                                                  inst_parameter_index][
                                                                              :-1] + f'  // {sub_module_inst_name}'
                            continue

                        parameter_lst.append(connect_name)

                        inst_parameter_lst[0].append('parameter')
                        if isinstance(module_port_line['data type'], str):
                            if verilog_file_type == 'v':
                                if verilog_data_type_check(module_port_line['data type']):
                                    data_type = module_port_line['data type']
                                else:
                                    data_type = 'integer'
                            else:
                                data_type = module_port_line['data type']
                            inst_parameter_lst[1].append(data_type)
                        else:
                            inst_parameter_lst[1].append('')
                        if isinstance(module_port_line['sign'], str):
                            inst_parameter_lst[2].append(module_port_line['sign'])
                        else:
                            inst_parameter_lst[2].append('')
                        if isinstance(module_port_line['width'], str) and verilog_file_type == 'sv':
                            inst_parameter_lst[3].append(module_port_line['width'])
                        else:
                            inst_parameter_lst[3].append('')

                    inst_parameter_lst[4].append(connect_name)
                    # if isinstance(module_port_line['multiple dimension/connect bit'], str):
                    #     text = text + module_port_line['multiple dimension/connect bit']
                    if isinstance(module_port_line['default value/instantiated variable'], str):
                        inst_parameter_lst[5].append(module_port_line['default value/instantiated variable'] + ',')
                    else:
                        inst_parameter_lst[5].append('')
                    inst_parameter_lst[6].append("  // " + sub_module_list_item['sub_module_inst_name'])

        # print
        parameter_max_len = []
        if inst_parameter_lst[5][-1]:
            inst_parameter_lst[5][-1] = inst_parameter_lst[5][-1][:-1]  # delete the last ','
        for max_index in range(len(inst_parameter_lst)):
            parameter_max_len.append(find_max_str_len(inst_parameter_lst[max_index]))
        for lst_index in range(len(inst_parameter_lst[0])):
            text = ' ' * span[0]
            for index in range(4):
                if parameter_max_len[index] != 0:
                    text = text + inst_parameter_lst[index][lst_index].ljust(parameter_max_len[index]) + ' '
            if parameter_max_len[4] != 0:
                if inst_parameter_lst[5][lst_index]:
                    text = text + inst_parameter_lst[4][lst_index].ljust(parameter_max_len[4])
                else:
                    if lst_index != len(inst_parameter_lst[0]) - 1:
                        text = text + (inst_parameter_lst[4][lst_index] + ',').ljust(parameter_max_len[4])
                    else:
                        text = text + (inst_parameter_lst[4][lst_index]).ljust(parameter_max_len[4])
            if parameter_max_len[5] == 0:
                if lst_index != len(inst_parameter_lst[0]) - 1:
                    text = text + ','
            else:
                if inst_parameter_lst[5][lst_index]:
                    text = text + ' = ' + inst_parameter_lst[5][lst_index].ljust(parameter_max_len[5])
                else:
                    if len(inst_parameter_lst[4][lst_index]) + 1 > parameter_max_len[4]:
                        text = text + '  ' + ''.ljust(parameter_max_len[5])
                    else:
                        text = text + '   ' + ''.ljust(parameter_max_len[5])
            if parameter_max_len[6] != 0:
                text = text + inst_parameter_lst[6][lst_index]
            text = text + '\n'
            insert_row = content_lst_insert(verilog_file_content, insert_row, text)
        content_lst_insert(verilog_file_content, insert_row, ' ' * span[0] + '/*end of AUTOINOUTPARAM*/\n')

    return verilog_file_content


def autoarg(verilog_file_content, module_list, module_list_module, verilog_file_type, throughout_flag):
    pattern_text = r'/\*AUTOARG\*/'
    insert_row, span = find_first_str(verilog_file_content, pattern_text)
    if insert_row != -1:
        module_port = module_list_module['module_port']
        module_column = module_port.loc[:, 'type']
        max_index = module_column[(module_column != 'parameter') & (module_column != 'localparam') & (
                module_column != 'local variable')].index[
            -1]  # the last index of parameter
        insert_row = content_lst_insert(verilog_file_content, insert_row, ' ' * span[0] + '/*beginning of AUTOARG*/\n')

        # throughout
        sub_module_list = module_list_module['sub_module']
        variable_lst = []
        r_connect_name = re.compile('//')  # for comment append
        # for alignment
        inst_variable_lst = [[], [], [], [], [], []]  # type, data type, sign, width, name, comment

        for i in range(module_port.shape[0]):
            module_port_line = module_port.loc[i, :]
            if module_port_line['type'] != 'parameter' and module_port_line['type'] != 'localparam' and \
                    module_port_line['type'] != 'local variable':
                if isinstance(module_port_line['type'], str):
                    inst_variable_lst[0].append(module_port_line['type'])
                else:
                    inst_variable_lst[0].append('')
                if isinstance(module_port_line['data type'], str):
                    if verilog_file_type == 'sv':  # systemverilog
                        inst_variable_lst[1].append(module_port_line['data type'])
                    else:  # verilog
                        if module_port_line['data type'] != 'logic':
                            inst_variable_lst[1].append(module_port_line['data type'])
                        else:
                            inst_variable_lst[1].append('wire')
                else:
                    if verilog_file_type == 'sv':  # systemverilog
                        inst_variable_lst[1].append('logic')
                    else:  # verilog
                        inst_variable_lst[1].append('wire')
                if isinstance(module_port_line['sign'], str):
                    inst_variable_lst[2].append(module_port_line['sign'])
                else:
                    inst_variable_lst[2].append('')
                if isinstance(module_port_line['width'], str):
                    inst_variable_lst[3].append(module_port_line['width'])
                else:
                    inst_variable_lst[3].append('')
                if isinstance(module_port_line['name'], str):
                    text = module_port_line['name']
                    variable_lst.append(module_port_line['name'])
                else:
                    text = '?'
                if isinstance(module_port_line['multiple dimension/connect bit'], str):
                    text = text + module_port_line['multiple dimension/connect bit']
                text = text + ','
                inst_variable_lst[4].append(text)
                inst_variable_lst[5].append('')
        if throughout_flag:
            for sub_module_list_item in sub_module_list:
                sub_module = module_list_find(module_list, sub_module_list_item['sub_module_name'])
                sub_module_port = sub_module['module_port']
                sub_module_connect_port = sub_module_list_item['sub_module_port']

                for i in range(sub_module_port.shape[0]):
                    module_port_line = sub_module_port.loc[i, :]
                    regular_connect_name = regular_expression_lst(module_list_module['regular_expression'],
                                                                  sub_module_list_item['sub_module_inst_name'],
                                                                  module_port_line['name'])
                    if module_port_line['type'] != 'parameter' and module_port_line['type'] != 'localparam' and \
                            module_port_line['type'] != 'local variable':
                        row_index = sub_module_connect_port[
                            sub_module_connect_port['name'] == module_port_line['name']].index
                        if len(row_index) != 0:
                            connect_name = sub_module_connect_port['default value/instantiated variable'][row_index[0]]
                            connect_bit = sub_module_connect_port['multiple dimension/connect bit'][row_index[0]]
                        elif regular_connect_name != None:
                            connect_name = regular_connect_name
                            connect_bit = None
                        elif isinstance(module_port_line['name'], str):
                            connect_name = module_port_line['name']
                            connect_bit = None
                        else:
                            connect_name = '?'
                            connect_bit = None
                        if connect_name in variable_lst:
                            s_temp = '^' + connect_name + r'(\[|,)'
                            r_temp = re.compile(s_temp)
                            inst_variable_index = None
                            for lst_item in inst_variable_lst[4]:
                                if r_temp.match(lst_item):
                                    inst_variable_index = inst_variable_lst[4].index(lst_item)
                                    break
                            sub_module_inst_name = sub_module_list_item['sub_module_inst_name']
                            if isinstance(connect_bit, str):
                                warning_text = ' (***not sure***)  '
                            else:
                                warning_text = ''
                            if r_connect_name.search(inst_variable_lst[5][inst_variable_index]):
                                inst_variable_lst[5][inst_variable_index] = inst_variable_lst[5][
                                                                                inst_variable_index][
                                                                            :-1] + f', {sub_module_inst_name}' + warning_text
                            else:
                                inst_variable_lst[5][inst_variable_index] = inst_variable_lst[5][
                                                                                inst_variable_index][
                                                                            :-1] + f'  // {sub_module_inst_name}' + warning_text
                            continue
                        variable_lst.append(connect_name)

                        inst_variable_lst[0].append(module_port_line['type'])
                        if verilog_file_type == 'sv':  # systemverilog
                            data_type = module_port_line['data type']
                        else:  # verilog
                            data_type = 'wire'
                        inst_variable_lst[1].append(data_type)
                        if isinstance(module_port_line['sign'], str):
                            inst_variable_lst[2].append(module_port_line['sign'])
                        else:
                            inst_variable_lst[2].append('')
                        if isinstance(module_port_line['width'], str):
                            inst_variable_lst[3].append(module_port_line['width'])
                        else:
                            inst_variable_lst[3].append('')
                        if isinstance(module_port_line['multiple dimension/connect bit'], str):
                            connect_name = connect_name + module_port_line['multiple dimension/connect bit']
                        connect_name = connect_name + ','
                        inst_variable_lst[4].append(connect_name)
                        if isinstance(connect_bit, str):
                            inst_variable_lst[5].append(
                                "  // " + sub_module_list_item['sub_module_inst_name'] + ' (***not sure***)  ')
                        else:
                            inst_variable_lst[5].append(
                                "  // " + sub_module_list_item['sub_module_inst_name'])

        # print
        variable_max_len = []
        inst_variable_lst[4][-1] = inst_variable_lst[4][-1][:-1]  # delete the last ','
        for max_index in range(len(inst_variable_lst)):
            variable_max_len.append(find_max_str_len(inst_variable_lst[max_index]))
        for lst_index in range(len(inst_variable_lst[0])):
            if inst_variable_lst[0][lst_index] == 'input':
                text = ' ' * span[0]
                for index in range(4):
                    if variable_max_len[index] != 0:
                        text = text + inst_variable_lst[index][lst_index].ljust(variable_max_len[index]) + ' '
                text = text + inst_variable_lst[4][lst_index].ljust(variable_max_len[4])
                if variable_max_len[5] != 0:
                    text = text + inst_variable_lst[5][lst_index]
                text = text + '\n'
                insert_row = content_lst_insert(verilog_file_content, insert_row, text)
        for lst_index in range(len(inst_variable_lst[0])):
            if inst_variable_lst[0][lst_index] == 'output':
                text = ' ' * span[0]
                for index in range(4):
                    if variable_max_len[index] != 0:
                        text = text + inst_variable_lst[index][lst_index].ljust(variable_max_len[index]) + ' '
                text = text + inst_variable_lst[4][lst_index].ljust(variable_max_len[4])
                if variable_max_len[5] != 0:
                    text = text + inst_variable_lst[5][lst_index]
                text = text + '\n'
                insert_row = content_lst_insert(verilog_file_content, insert_row, text)
        for lst_index in range(len(inst_variable_lst[0])):
            if inst_variable_lst[0][lst_index] == 'inout':
                text = ' ' * span[0]
                for index in range(4):
                    if variable_max_len[index] != 0:
                        text = text + inst_variable_lst[index][lst_index].ljust(variable_max_len[index]) + ' '
                text = text + inst_variable_lst[4][lst_index].ljust(variable_max_len[4])
                if variable_max_len[5] != 0:
                    text = text + inst_variable_lst[5][lst_index]
                text = text + '\n'
                insert_row = content_lst_insert(verilog_file_content, insert_row, text)
        content_lst_insert(verilog_file_content, insert_row, ' ' * span[0] + '/*end of AUTOARG*/\n')
    return verilog_file_content


def autovariable(verilog_file_content, module_list, top_module_name, verilog_file_type, throughout_flag):
    pattern_text = r'/\*AUTOVARIABLE\*/'
    insert_row, span = find_first_str(verilog_file_content, pattern_text)
    module_list_module = module_list_find(module_list, top_module_name)
    module_list_module_port = module_list_module['module_port']
    parameter_lst = []
    variable_lst = []

    # store the parameter and variable of top_module
    for i in range(module_list_module_port.shape[0]):
        top_module_port_line = module_list_module_port.loc[i, :]
        if (top_module_port_line['type'] == 'parameter') or (top_module_port_line['type'] == 'localparam'):
            parameter_lst.append(top_module_port_line['name'])
        elif top_module_port_line['type'] != 'local variable':
            variable_lst.append(top_module_port_line['name'])

    if insert_row != -1:
        insert_row = content_lst_insert(verilog_file_content, insert_row,
                                        ' ' * span[0] + '/*beginning of AUTOVARIABLE*/\n')
        parameter_insert_row = content_lst_insert(verilog_file_content, insert_row,
                                                  ' ' * span[0] + '/*local parameter*/\n')
        variable_insert_row = content_lst_insert(verilog_file_content, parameter_insert_row,
                                                 ' ' * span[0] + '/*local variable*/\n')
        sub_module_list = module_list_module['sub_module']

        # for alignment
        inst_parameter_lst = [[], [], [], [], [], [], []]  # type, data type, sign, width, name, default value, comment
        inst_variable_lst = [[], [], [], [], []]  # data type, sign, width, name, comment
        r_connect_name = re.compile('//')  # for comment append

        # insert local variable of top module
        for i in module_list_module_port[module_list_module_port['type'] == 'local variable'].index:
            module_port_line = module_list_module_port.loc[i, :]
            if module_port_line['name'] in variable_lst:
                continue
            if isinstance(module_port_line['data type'], str):
                if verilog_file_type == 'sv':  # systemverilog
                    data_type = module_port_line['data type']
                else:  # verilog
                    if module_port_line['data type'] != 'logic':
                        data_type = module_port_line['data type']
                    else:
                        data_type = 'wire'
            else:
                if verilog_file_type == 'sv':  # systemverilog
                    data_type = 'logic'
                else:  # verilog
                    data_type = 'wire'
            inst_variable_lst[0].append(data_type)
            if isinstance(module_port_line['sign'], str):
                inst_variable_lst[1].append(module_port_line['sign'])
            else:
                inst_variable_lst[1].append('')
            if isinstance(module_port_line['width'], str):
                inst_variable_lst[2].append(module_port_line['width'])
            else:
                inst_variable_lst[2].append('')
            if isinstance(module_port_line['name'], str):
                text = module_port_line['name']
            if isinstance(module_port_line['multiple dimension/connect bit'], str):
                text = text + module_port_line['multiple dimension/connect bit']
            text = text + ';'
            inst_variable_lst[3].append(text)
            inst_variable_lst[4].append('  // local variable\n')
            variable_lst.append(module_port_line['name'])
        if not throughout_flag:
            # insert inst parameter and variable
            for sub_module_list_item in sub_module_list:
                sub_module = module_list_find(module_list, sub_module_list_item['sub_module_name'])
                sub_module_port = sub_module['module_port']
                sub_module_connect_port = sub_module_list_item['sub_module_port']

                for i in range(sub_module_port.shape[0]):
                    module_port_line = sub_module_port.loc[i, :]
                    regular_connect_name = regular_expression_lst(module_list_module['regular_expression'],
                                                                  sub_module_list_item['sub_module_inst_name'],
                                                                  module_port_line['name'])
                    if module_port_line['type'] == 'parameter':
                        row_index = sub_module_connect_port[
                            sub_module_connect_port['name'] == module_port_line['name']].index
                        if len(row_index) != 0:
                            connect_name = sub_module_connect_port['default value/instantiated variable'][row_index[0]]
                        elif regular_connect_name != None:
                            connect_name = regular_connect_name
                        else:
                            connect_name = module_port_line['name']
                        if connect_name in parameter_lst:
                            sub_module_inst_name = sub_module_list_item['sub_module_inst_name']
                            if connect_name in inst_parameter_lst[4]:  # can't use find_first_str()
                                inst_parameter_index = inst_parameter_lst[4].index(connect_name)
                                inst_parameter_lst[6][inst_parameter_index] = inst_parameter_lst[6][
                                                                                  inst_parameter_index][
                                                                              :-1] + f', {sub_module_inst_name}\n'
                            else:
                                row_connect_name = find_first_str(verilog_file_content, connect_name)[0]
                                if r_connect_name.search(verilog_file_content[row_connect_name - 1]):
                                    verilog_file_content[row_connect_name - 1] = verilog_file_content[
                                                                                     row_connect_name - 1][
                                                                                 :-1] + f', {sub_module_inst_name}\n'
                                else:
                                    verilog_file_content[row_connect_name - 1] = verilog_file_content[
                                                                                     row_connect_name - 1][
                                                                                 :-1] + f'  // {sub_module_inst_name}\n'
                            continue

                        parameter_lst.append(connect_name)

                        inst_parameter_lst[0].append('localparam')
                        if isinstance(module_port_line['data type'], str):
                            if verilog_file_type == 'v':
                                if verilog_data_type_check(module_port_line['data type']):
                                    data_type = module_port_line['data type']
                                else:
                                    data_type = 'integer'
                            else:
                                data_type = module_port_line['data type']
                            inst_parameter_lst[1].append(data_type)
                        else:
                            inst_parameter_lst[1].append('')
                        if isinstance(module_port_line['sign'], str):
                            inst_parameter_lst[2].append(module_port_line['sign'])
                        else:
                            inst_parameter_lst[2].append('')
                        if isinstance(module_port_line['width'], str) and verilog_file_type == 'sv':
                            inst_parameter_lst[3].append(module_port_line['width'])
                        else:
                            inst_parameter_lst[3].append('')

                        inst_parameter_lst[4].append(connect_name)
                        # if isinstance(module_port_line['multiple dimension/connect bit'], str):
                        #     text = text + module_port_line['multiple dimension/connect bit']
                        if isinstance(module_port_line['default value/instantiated variable'], str):
                            inst_parameter_lst[5].append(module_port_line['default value/instantiated variable'] + ';')
                        else:
                            inst_parameter_lst[5].append(';')
                        inst_parameter_lst[6].append("  // " + sub_module_list_item['sub_module_inst_name'] + '\n')

                    elif module_port_line['type'] != 'localparam' and module_port_line['type'] != 'local variable':
                        row_index = sub_module_connect_port[
                            sub_module_connect_port['name'] == module_port_line['name']].index
                        if len(row_index) != 0:
                            connect_name = sub_module_connect_port['default value/instantiated variable'][row_index[0]]
                            connect_bit = sub_module_connect_port['multiple dimension/connect bit'][row_index[0]]
                        elif regular_connect_name != None:
                            connect_name = regular_connect_name
                            connect_bit = None
                        elif isinstance(module_port_line['name'], str):
                            connect_name = module_port_line['name']
                            connect_bit = None
                        else:
                            connect_name = '?'
                            connect_bit = None
                        if connect_name in variable_lst:
                            s_temp = '^' + connect_name + r'(\[|;)'
                            r_temp = re.compile(s_temp)
                            inst_variable_index = None
                            for lst_item in inst_variable_lst[3]:
                                if r_temp.match(lst_item):
                                    inst_variable_index = inst_variable_lst[3].index(lst_item)
                                    break
                            sub_module_inst_name = sub_module_list_item['sub_module_inst_name']
                            if inst_variable_index != None:
                                inst_variable_lst[4][inst_variable_index] = inst_variable_lst[4][
                                                                                inst_variable_index][
                                                                            :-1] + f', {sub_module_inst_name}\n'
                            else:
                                row_connect_name = find_first_str(verilog_file_content, connect_name)[0]
                                if r_connect_name.search(verilog_file_content[row_connect_name - 1]):
                                    verilog_file_content[row_connect_name - 1] = verilog_file_content[
                                                                                     row_connect_name - 1][
                                                                                 :-1] + f', {sub_module_inst_name}\n'
                                else:
                                    verilog_file_content[row_connect_name - 1] = verilog_file_content[
                                                                                     row_connect_name - 1][
                                                                                 :-1] + f'  // {sub_module_inst_name}\n'
                            continue
                        variable_lst.append(connect_name)
                        if verilog_file_type == 'sv':  # systemverilog
                            data_type = 'logic'
                        else:  # verilog
                            data_type = 'wire'
                        inst_variable_lst[0].append(data_type)
                        if isinstance(module_port_line['sign'], str):
                            inst_variable_lst[1].append(module_port_line['sign'])
                        else:
                            inst_variable_lst[1].append('')
                        if isinstance(module_port_line['width'], str):
                            inst_variable_lst[2].append(module_port_line['width'])
                        else:
                            inst_variable_lst[2].append('')
                        if isinstance(module_port_line['multiple dimension/connect bit'], str):
                            connect_name = connect_name + module_port_line['multiple dimension/connect bit']
                        connect_name = connect_name + ';'
                        inst_variable_lst[3].append(connect_name)
                        if isinstance(connect_bit, str):
                            inst_variable_lst[4].append(
                                "  // " + sub_module_list_item['sub_module_inst_name'] + ' (***not sure***) \n')
                        else:
                            inst_variable_lst[4].append(
                                "  // " + sub_module_list_item['sub_module_inst_name'] + '\n')
        # print
        parameter_max_len = []
        variable_max_len = []
        comment_r = re.compile(r'\(\*\*\*not sure\*\*\*\)')
        parameter_error_insert_row = insert_row
        variable_error_insert_row = insert_row
        parameter_error_insert_row = content_lst_insert(verilog_file_content, parameter_error_insert_row,
                                                        ' ' * span[0] + '/*error parameter*/\n')
        variable_error_insert_row = variable_error_insert_row + 1
        variable_error_insert_row = content_lst_insert(verilog_file_content, variable_error_insert_row,
                                                       ' ' * span[0] + '/*error variable*/\n')
        parameter_insert_row = parameter_insert_row + 2
        variable_insert_row = variable_insert_row + 2
        for max_index in range(len(inst_parameter_lst)):
            parameter_max_len.append(find_max_str_len(inst_parameter_lst[max_index]))
        for max_index in range(len(inst_variable_lst)):
            variable_max_len.append(find_max_str_len(inst_variable_lst[max_index]))
        for lst_index in range(len(inst_parameter_lst[0])):
            text = ' ' * span[0]
            for index in range(4):
                if parameter_max_len[index] != 0:
                    text = text + inst_parameter_lst[index][lst_index].ljust(parameter_max_len[index]) + ' '
            if parameter_max_len[4] != 0:
                text = text + inst_parameter_lst[4][lst_index].ljust(parameter_max_len[4])
            if parameter_max_len[5] == 0:
                text = text + ';'
            else:
                text = text + ' = ' + inst_parameter_lst[5][lst_index].ljust(parameter_max_len[5])
            if parameter_max_len[6] != 0:
                text = text + inst_parameter_lst[6][lst_index]
            if inst_parameter_lst[5][lst_index] != ';':
                parameter_insert_row = content_lst_insert(verilog_file_content, parameter_insert_row, text)
                variable_insert_row = variable_insert_row + 1
            else:
                parameter_error_insert_row = content_lst_insert(verilog_file_content, parameter_error_insert_row, text)
                variable_error_insert_row = variable_error_insert_row + 1
                parameter_insert_row = parameter_insert_row + 1
                variable_insert_row = variable_insert_row + 1
        for lst_index in range(len(inst_variable_lst[0])):
            text = ' ' * span[0]
            for index in range(3):
                if variable_max_len[index] != 0:
                    text = text + inst_variable_lst[index][lst_index].ljust(variable_max_len[index]) + ' '
            text = text + inst_variable_lst[3][lst_index].ljust(variable_max_len[3])
            text = text + inst_variable_lst[4][lst_index]
            if comment_r.search(text):
                variable_error_insert_row = content_lst_insert(verilog_file_content, variable_error_insert_row, text)
                parameter_insert_row = parameter_insert_row + 1
                variable_insert_row = variable_insert_row + 1
            else:
                variable_insert_row = content_lst_insert(verilog_file_content, variable_insert_row, text)

        content_lst_insert(verilog_file_content, variable_insert_row, ' ' * span[0] + '/*end of AUTOVARIABLE*/\n')
    return verilog_file_content


def autoinst(verilog_file_content, module_list, top_module_name):
    pattern_text = r'/\*AUTOINST\*/'
    insert_row, span = find_first_str(verilog_file_content, pattern_text)
    module_list_module = module_list_find(module_list, top_module_name)
    if insert_row != -1:
        insert_row = content_lst_insert(verilog_file_content, insert_row,
                                        ' ' * span[0] + '/*beginning of AUTOINST*/\n')
        sub_module_list = module_list_module['sub_module']
        # insert inst param
        for sub_module_list_item in sub_module_list:
            insert_row = content_lst_insert(verilog_file_content, insert_row,
                                            ' ' * span[0] + sub_module_list_item['sub_module_name'] + ' #(\n')
            sub_module = module_list_find(module_list, sub_module_list_item['sub_module_name'])

            sub_module_port = sub_module['module_port']
            sub_module_connect_port = sub_module_list_item['sub_module_port']
            module_column = sub_module_port.loc[:, 'type']
            # param_count = len(module_column[module_column == 'parameter'].index)  # the last index of parameter
            # inout_count = len(module_column[(module_column != 'parameter') & (module_column != 'localparam')].index)  # the last index of inout

            inst_module_lst = [[], [], [], []]  # parameter, inst_parameter, variable, inst_variable

            for i in range(sub_module_port.shape[0]):
                module_port_line = sub_module_port.loc[i, :]
                regular_connect_name = regular_expression_lst(module_list_module['regular_expression'],
                                                              sub_module_list_item['sub_module_inst_name'],
                                                              module_port_line['name'])
                if module_port_line['type'] == 'parameter':
                    if isinstance(module_port_line['name'], str):
                        inst_module_lst[0].append(module_port_line['name'])
                    row_index = sub_module_connect_port[
                        sub_module_connect_port['name'] == module_port_line['name']].index
                    if len(row_index) != 0:
                        connect_name = sub_module_connect_port['default value/instantiated variable'][row_index[0]]
                    elif regular_connect_name != None:  # find the regular expression
                        connect_name = regular_connect_name
                    else:
                        connect_name = module_port_line['name']
                    # if isinstance(module_port_line['multiple dimension/connect bit'], str):
                    #     connect_name = connect_name + module_port_line['multiple dimension/connect bit']
                    inst_module_lst[1].append(connect_name)
                elif module_port_line['type'] != 'localparam' and module_port_line['type'] != 'local variable':
                    if isinstance(module_port_line['name'], str):
                        inst_module_lst[2].append(module_port_line['name'])
                    row_index = sub_module_connect_port[
                        sub_module_connect_port['name'] == module_port_line['name']].index
                    if len(row_index) != 0:
                        connect_name = sub_module_connect_port['default value/instantiated variable'][row_index[0]]
                        if isinstance(sub_module_connect_port['multiple dimension/connect bit'][row_index[0]], str):
                            connect_name = connect_name + sub_module_connect_port['multiple dimension/connect bit'][
                                row_index[0]]
                    elif regular_connect_name != None:  # find the regular expression
                        connect_name = regular_connect_name
                    else:
                        connect_name = module_port_line['name']
                    inst_module_lst[3].append(connect_name)
            parameter_max_len = find_max_str_len(inst_module_lst[0])
            # parameter_inst_max_len = find_max_str_len(inst_module_lst[1])
            variable_max_len = find_max_str_len(inst_module_lst[2])
            # variable_inst_max_len = find_max_str_len(inst_module_lst[3])
            for lst_index in range(len(inst_module_lst[0])):
                text = ' ' * (span[0] + 2) + '.' + inst_module_lst[0][lst_index].ljust(parameter_max_len) + '(' + \
                       inst_module_lst[1][lst_index] + ')'
                if not lst_index == len(inst_module_lst[0]) - 1:
                    text = text + ',\n'
                else:
                    text = text + '\n'
                insert_row = content_lst_insert(verilog_file_content, insert_row, text)
            text = ' ' * span[0] + ') ' + sub_module_list_item['sub_module_inst_name'] + ' (\n'
            insert_row = content_lst_insert(verilog_file_content, insert_row, text)
            for lst_index in range(len(inst_module_lst[2])):
                text = ' ' * (span[0] + 2) + '.' + inst_module_lst[2][lst_index].ljust(variable_max_len) + '(' + \
                       inst_module_lst[3][lst_index] + ')'
                if not lst_index == len(inst_module_lst[2]) - 1:
                    text = text + ',\n'
                else:
                    text = text + '\n' + ' ' * span[0] + ');\n'
                insert_row = content_lst_insert(verilog_file_content, insert_row, text)
        content_lst_insert(verilog_file_content, insert_row, ' ' * span[0] + '/*end of AUTOINST*/\n')
    return verilog_file_content


parser = OptionParser()
parser.add_option("-v", "--vfile", default="./*v", help="verilog file directory, in linux format", dest="verilog_dir",
                  type="string")
parser.add_option("-x", "--xfile", default="./*xlsx", help="xls/xlsx file directory, in linux format",
                  dest="module_dir", type="string")
parser.add_option("-d", "--delete", default=False, action="store_true", help="only delelte the auto gen code",
                  dest="delete_flag")
parser.add_option("-r", "--recursion", default=False, action="store_true",
                  help="recursivly find files in the vfile and xfile dir",
                  dest="recursion_flag")
parser.add_option("-t", "--throughout", default=True, action="store_true",
                  help="connect the variable to the top module port directly",
                  dest="throughout_flag")
(option, args) = parser.parse_args()
verilog_dir = option.verilog_dir
module_dir = option.module_dir
delete_flag = option.delete_flag
recursion_flag = option.recursion_flag
throughout_flag = option.throughout_flag

vfile_list = find_file_list(verilog_dir, recursion_flag, type='verilog')
xfile_list = find_file_list(module_dir, recursion_flag, type='excel')

module_list = []
index_s = 0
for index in range(len(xfile_list)):

    # skip the file
    xfile_name = xfile_list[index].split(sep='/')[-1]
    xfile_type = xfile_name.split(sep='.')[-1]
    if xfile_name[0] == '~':  # skip the temporary Excel file
        break
    if xfile_type != 'xls' and xfile_type != 'xlsx':
        break

    table_dict = pd.read_excel(xfile_list[index], converters={'default value/instantiated variable': str},
                               sheet_name=None)
    for table in table_dict.values():
        table_module_series = table['module']
        table_row = table.shape[0]
        table_column = table.shape[1]
        table_module_index = []

        for i in range(table_module_series.shape[0]):
            if isinstance(table_module_series.values[i], str):
                table_module_index.append(i)
        table_module_index.append(table_row)  # the last item of table_module_index is the row number of table

        module_list.append({})
        for i in range(len(table_module_index)):
            if i == 0:
                module_list[index_s]['module_name'] = table_module_series[0]
                module_list[index_s]['module_port'] = table.loc[table_module_index[0]:table_module_index[1] - 1,
                                                      'type':'multiple dimension/connect bit']
                module_list[index_s]['sub_module'] = []
                module_list[index_s]['regular_expression'] = []
            elif not i == (len(table_module_index) - 1):
                # regular expression
                if table_module_series[table_module_index[i]][0:3] == '(r)':
                    regular_module_name = table_module_series[table_module_index[i]].split(sep='--')[0][3:]
                    regular_module_inst_expression = ''.join(
                        table_module_series[table_module_index[i]].split(sep='--')[1:])
                    regular_variable_expression = table.loc[table_module_index[i], 'name']
                    regular_connect_expression = table.loc[table_module_index[i], 'default value/instantiated variable']

                    regular_expression_dict = {}
                    regular_expression_dict['regular_module_inst_expression'] = re.compile(
                        regular_module_inst_expression)
                    regular_expression_dict['regular_variable_expression'] = re.compile(regular_variable_expression)
                    regular_expression_dict['regular_connect_expression'] = regular_connect_expression
                    module_list[index_s]['regular_expression'].append(regular_expression_dict)
                else:
                    module_list[index_s]['sub_module'].append({})
                    module_inst_port = table.loc[table_module_index[i]:table_module_index[i + 1] - 1,
                                       'name':'multiple dimension/connect bit']
                    module_list[index_s]['sub_module'][i - 1]['sub_module_name'] = \
                        table_module_series.values[table_module_index[i]].split(sep='--')[0]
                    module_list[index_s]['sub_module'][i - 1]['sub_module_inst_name'] = \
                        table_module_series.values[table_module_index[i]].split(sep='--')[1]
                    module_list[index_s]['sub_module'][i - 1]['sub_module_port'] = module_inst_port
        index_s = index_s + 1

# correct the data base
for vfile in vfile_list:
    verilog_file_name = vfile.split(sep='/')[-1]
    module_name = verilog_file_name.split(sep='.')[0]
    verilog_file_type = verilog_file_name.split(sep='.')[1]  # sv or v

    # skip the file
    if verilog_file_name[0] == '~':  # skip the temporary verilog file
        break
    if verilog_file_type != 'v' and verilog_file_type != 'sv':  # not v or sv file
        break

    if verilog_file_type == 'v':
        default_type = 'wire'
        for i in range(len(module_list)):
            if module_list[i]['module_name'] == module_name:
                for l in range(len(module_list[i]['module_port']['data type'])):
                    if (not isinstance(module_list[i]['module_port']['data type'][l], str) or
                        module_list[i]['module_port']['data type'][l] == 'logic') and \
                            module_list[i]['module_port']['type'][l] != 'parameter' and \
                            module_list[i]['module_port']['type'][l] != 'localparam':
                        module_list[i]['module_port'].loc[l, 'data type'] = default_type
                    if module_list[i]['module_port']['type'][l] == 'parameter' or module_list[i]['module_port']['type'][
                        l] == 'localparam':
                        if module_list[i]['module_port']['data type'][l] != 'integer' and \
                                module_list[i]['module_port']['data type'][l] != 'real' and \
                                module_list[i]['module_port']['data type'][l] != 'time':
                            module_list[i]['module_port'].loc[l, 'data type'] = 'integer'  # in verilog, default integer
                break
    elif verilog_file_type == 'sv':
        default_type = 'logic'
        for i in range(len(module_list)):
            if module_list[i]['module_name'] == module_name:
                for l in range(len(module_list[i]['module_port']['data type'])):
                    if not isinstance(module_list[i]['module_port']['data type'][l], str):
                        if module_list[i]['module_port']['type'][l] != 'parameter' and \
                                module_list[i]['module_port']['type'][l] != 'localparam':
                            module_list[i]['module_port'].loc[l, 'data type'] = default_type
                        else:
                            if isinstance(module_list[i]['module_port']['width'][l], str):
                                module_list[i]['module_port'].loc[l, 'data type'] = 'bit'
                            else:
                                module_list[i]['module_port'].loc[l, 'data type'] = 'int'
                break
for i in range(len(module_list)):
    for l in range(len(module_list[i]['module_port']['sign'])):
        if not isinstance(module_list[i]['module_port']['sign'][l], str):
            module_list[i]['module_port'].loc[l, 'sign'] = 'unsigned'

for vfile in vfile_list:
    verilog_file_name = vfile.split(sep='/')[-1]
    verilog_file = open(vfile, 'r+')
    module_name = verilog_file_name.split(sep='.')[0]
    verilog_file_type = verilog_file_name.split(sep='.')[1]  # sv or v
    verilog_file_content = verilog_file.readlines()

    # skip the file
    if verilog_file_name[0] == '~':  # skip the temporary verilog file
        break
    if verilog_file_type != 'v' and verilog_file_type != 'sv':  # not v or sv file
        break

    # delete content first
    content_lst_delete(verilog_file_content, r'/\*beginning of AUTOINOUTPARAM\*/', r'/\*end of AUTOINOUTPARAM\*/')
    content_lst_delete(verilog_file_content, r'/\*beginning of AUTOARG\*/', r'/\*end of AUTOARG\*/')
    content_lst_delete(verilog_file_content, r'/\*beginning of AUTOVARIABLE\*/', r'/\*end of AUTOVARIABLE\*/')
    content_lst_delete(verilog_file_content, r'/\*beginning of AUTOINST\*/', r'/\*end of AUTOINST\*/')

    # generate content
    if not delete_flag:
        verilog_file_content = autoinoutparam(verilog_file_content, module_list,
                                              module_list_find(module_list, module_name),
                                              verilog_file_type, throughout_flag)
        verilog_file_content = autoarg(verilog_file_content, module_list, module_list_find(module_list, module_name),
                                       verilog_file_type, throughout_flag)
        verilog_file_content = autovariable(verilog_file_content, module_list, module_name, verilog_file_type,
                                            throughout_flag)
        verilog_file_content = autoinst(verilog_file_content, module_list, module_name)
    verilog_file_content = delete_last_blank(verilog_file_content)
    # write into the file
    verilog_file.seek(0, 0)
    verilog_file.close()
    verilog_file = open(vfile, 'w+')
    verilog_file.write(''.join(verilog_file_content))

    verilog_file.close()

t = 0
