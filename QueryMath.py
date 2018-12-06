def minus(dict, operand1, operand2):
    op_dict01 = dict[operand1]
    op_dict02 = dict[operand2]
    temp_dict = {}
    if op_dict01:
        for pinv in list(op_dict01):
            if pinv in op_dict02:
                temp_dict[pinv] = op_dict01[pinv] - op_dict02[pinv]
            else:
                temp_dict[pinv] = op_dict01[pinv]
    return temp_dict


def positive_num(dict, operand):
    op_dict = dict[operand]
    temp_dict = {}
    if op_dict:
        for pinv in op_dict:
            if op_dict[pinv] < 0:
                temp_dict[pinv] = float(0)
            else:
                temp_dict[pinv] = op_dict[pinv]
    return temp_dict
