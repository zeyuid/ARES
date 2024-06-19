from __future__ import division, absolute_import, print_function, unicode_literals
import re
import os
import numpy as np
from scipy.io import loadmat, savemat
import json

def sourceIsFlat(cls, sourceText):
    """Return whether the source is 'flat'.
    A flat source is one without block definitions and
    just plain AWL code."""
    haveDB = re.match(r'.*^\s*DATA_BLOCK\s+.*', sourceText,
                      re.DOTALL | re.MULTILINE)
    haveFB = re.match(r'.*^\s*FUNCTION_BLOCK\s+.*', sourceText,
                      re.DOTALL | re.MULTILINE)
    haveFC = re.match(r'.*^\s*FUNCTION\s+.*', sourceText,
                      re.DOTALL | re.MULTILINE)
    haveOB = re.match(r'.*^\s*ORGANIZATION_BLOCK\s+.*', sourceText,
                      re.DOTALL | re.MULTILINE)
    haveUDT = re.match(r'.*^\s*TYPE\s+.*', sourceText,
                       re.DOTALL | re.MULTILINE)

    return not bool(haveDB) and not bool(haveFB) and \
           not bool(haveFC) and not bool(haveOB) and \
           not bool(haveUDT)


def read_file_as_str(file_name):
    file_path = "./" + file_name
    if not os.path.isfile(file_path):
        raise TypeError(file_path + " does not exist")

    all_the_text = open(file_path).read()
    return all_the_text


def network_segmentation(sourcefile):
    # input STL sourcefile, output networks(functions) in it
    networks = re.split('\nNETWORK\nTITLE =\n\n', sourcefile, flags=re.M | re.I)
    if not networks:
        print("\nNo functions exists in given Block")

    return networks


def network_function_search(network_file):
    # using set to avoid multi-correlated
    factor_variable_set_directly = []  # set()
    factor_variable_set_indirectly = []  # set()
    network_induced_relation_directly = {}
    network_induced_relation_indirectly = {}

    line_seg = re.split('\n', network_file)

    for var in range(len(line_seg)):
        variable = re.split(r'=|S|R|T|MOVE|call', line_seg[var], flags=re.M | re.I)
        if len(variable) > 1:  # if the instrction exists
            induced_var = variable[1].replace(" ", "")
            induced_var_abs_A = re.search(r'(\s*[QIM]\d+\.[0-7])|(\s*[QIM][BWD]\d+\.[0-7])|(\s*[QIM][BWD]\d+)\s*',
                                          induced_var)
            induced_var_abs_B = re.search(r'(\s*DB\d+.DB[XBWD])(\d+\.[0-7])\s*', induced_var)
            induced_var_abs_C = re.search(r'(\s*(FC|OB)\d+)\s*', induced_var)

            if induced_var_abs_A:
                # match the QIM address
                network_induced_relation_directly[induced_var_abs_A.group()] = set(factor_variable_set_directly)
                network_induced_relation_indirectly[induced_var_abs_A.group()] = set(factor_variable_set_indirectly)
                # remove self correlation, if it exists
                if induced_var_abs_A.group() in factor_variable_set_indirectly:
                    network_induced_relation_indirectly[induced_var_abs_A.group()].remove(induced_var_abs_A.group())
            elif induced_var_abs_B:
                # match the DB address
                network_induced_relation_directly[induced_var_abs_B.group()] = set(factor_variable_set_directly)
                network_induced_relation_indirectly[induced_var_abs_B.group()] = set(factor_variable_set_indirectly)
                # remove self correlation, if it exists
                if induced_var_abs_B.group() in factor_variable_set_indirectly:
                    network_induced_relation_indirectly[induced_var_abs_B.group()].remove(induced_var_abs_B.group())
            elif induced_var_abs_C:
                # match the FC/OB block number
                network_induced_relation_directly[induced_var_abs_C.group()] = set(factor_variable_set_directly)
                network_induced_relation_indirectly[induced_var_abs_C.group()] = set(factor_variable_set_indirectly)
                # remove self correlation, if it exists
                if induced_var_abs_C.group() in factor_variable_set_indirectly:
                    network_induced_relation_indirectly[induced_var_abs_C.group()].remove(induced_var_abs_C.group())
        else:
            # if the instruction doesn't include the induced-variable, search the self-vabriation-variable.
            factor_var = variable[0].replace(" ", "")
            factor_var_abs = re.search(r'(\s*[I])([0-9]+\.[0-7])\s*', factor_var)
            if factor_var_abs:
                factor_variable_set_directly.append(factor_var_abs.group())
            else:
                factor_var_abs = re.search(r'(\s*[QM]\d+\.[0-7])|(\s*MD\d+\.[0-7])|(\s*MD\d+)\s*', factor_var)
                if factor_var_abs:
                    factor_variable_set_indirectly.append(factor_var_abs.group())
                else:
                    # at last, using DB to abstract address
                    factor_var_abs = re.search(r'(\s*DB\d+.DB[XBWD])(\d+\.[0-7])\s*', factor_var)
                    if factor_var_abs:
                        factor_variable_set_indirectly.append(factor_var_abs.group())
                    else:
                        pass

    return network_induced_relation_directly, network_induced_relation_indirectly


def STL_function_search(networks, Blk_name="OB 1"):
    # do network_function_search for each network
    # find the embedded functions in STL_functions, via network_function_search
    Blk = Blk_name.replace(" ", "")

    Block_STL_induced_relation = {}
    Block_STL_induced_relation_indirectly = {}

    for net in range(0, len(networks)):
        network_relation_directly, network_relation_indirectly = network_function_search(networks[net])
        # case1: one network may exist multiple assignment instruction
        for var in network_relation_directly:
            # case2: Q exists in multiple network
            if not var in Block_STL_induced_relation:
                # case 3: indirectly correlated variables exist;
                if network_relation_indirectly[var]:
                    # add indirectly correlated variables to network_relation_directly,
                    # and update STL_induced_relation
                    network_relation_directly[var] = network_relation_directly[var].union(
                        network_relation_indirectly[var])
                Block_STL_induced_relation[var] = network_relation_directly[var]
                Block_STL_induced_relation_indirectly[var] = network_relation_indirectly[var]
                if not Blk == "OB1":
                    Block_STL_induced_relation[var].add(Blk)
                    Block_STL_induced_relation_indirectly[var].add(Blk)
            else:
                # case 3: indirectly correlated variables exist;
                if network_relation_indirectly[var]:
                    # add indirectly correlated variables to network_relation_directly,
                    # and update STL_induced_relation
                    network_relation_directly[var] = network_relation_directly[var].union(
                        network_relation_indirectly[var])

                Block_STL_induced_relation[var] = Block_STL_induced_relation[var].union(network_relation_directly[var])
                Block_STL_induced_relation_indirectly[var] = Block_STL_induced_relation_indirectly[var].union(
                    network_relation_indirectly[var])

                if not Blk == "OB1":
                    Block_STL_induced_relation[var].add(Blk)
                    Block_STL_induced_relation_indirectly[var].add(Blk)

    return Block_STL_induced_relation, Block_STL_induced_relation_indirectly


def Recursively_loop(STL_induced_relation, STL_induced_relation_indirectly, STL_false_address, cycle=1):
    _Iaddress = re.compile(r'(\s*[I]\d+\.[0-7])\s*')
    _Qaddress = re.compile(r'(\s*[Q]\d+\.[0-7])\s*')
    _Maddress = re.compile(r'(\s*[M]\d+\.[0-7])|(\s*MD\d+\.[0-7])|(\s*MD\d+)\s*')
    _DBaddress = re.compile(r'(\s*DB\d+.DB[XBWD])(\d+\.[0-7])\s*')

    # new an updated table to correlate indirected variable (M/DB) with input address
    invar_updated_table = {}
    induced_updated_table = {}

    for var in STL_induced_relation_indirectly:
        induced_var_update = STL_induced_relation[var]
        # remove self correlation
        if var in induced_var_update:
            induced_var_update.remove(var)

        indir_var_update = set([])
        indir_var = STL_induced_relation_indirectly[var]

        if cycle == 1 and ("FC" not in var):
            # in the first cyclic loop, update address with padding addresses
            Addr_Padding = address_padding(var)
            for addr_pad in Addr_Padding:
                if addr_pad in STL_induced_relation:
                    # if the in_var is in the invar_updated_table, then do query; else, search
                    for var_up in STL_induced_relation[addr_pad]:
                        if not _Iaddress.search(var_up):
                            indir_var_update.add(var_up)
                        else:
                            induced_var_update.add(var_up)

        # update correlations in invar_updated_table, including in_var in indir_var, and in_var correlated padding address
        # for each in_var in indir_var, update the indirectly relation
        for in_var in indir_var:
            induced_var_update.remove(in_var)
            if not in_var == "False":
                # find in_var itself's variable
                if in_var in STL_induced_relation:
                    # if the in_var is in the invar_updated_table, then do query; else, search
                    # add .union(induced_updated_table[in_var]) 
                    induced_variables = STL_induced_relation[in_var]

                    for var_up in induced_variables:
                        if not _Iaddress.search(var_up):
                            indir_var_update.add(var_up)
                        else:
                            induced_var_update.add(var_up)
                else:
                    # if the indirectly variable doesn't have a mapping in STL_induced_relation,
                    # then set as the initial state -- "false"
                    indir_var_update.add("False")
                    induced_updated_table[in_var] = {"False"}
                    STL_false_address[in_var] = {"False"}
            else:
                pass

        induced_var_update = induced_var_update.union(indir_var_update)
        # update the STL_induced_relation_indirectly
        invar_updated_table[var] = set(indir_var_update)

        if var in invar_updated_table[var]:
            invar_updated_table[var].remove(var)

        # update the STL_induced_relation
        induced_updated_table[var] = induced_var_update

    return induced_updated_table, invar_updated_table, STL_false_address


def address_padding(addr):
    # input: a variable address
    # output: a set consists of all addresses that can impact input address, without itself

    B_off = range(1)
    W_off = range(2)
    D_off = range(4)

    correlated_addr = set([])

    Addr_X_tmp = re.compile(r"(?P<Area>.)(?P<Byte>\d+)(?P<Bit>\.[0-7])", re.S)
    AddrObj = Addr_X_tmp.search(addr)
    if AddrObj:
        for off in B_off:
            correlated_addr.add(AddrObj["Area"] + "B" + str(max(0, int(AddrObj["Byte"]) - off)))
        for off in W_off:
            correlated_addr.add(AddrObj["Area"] + "W" + str(max(0, int(AddrObj["Byte"]) - off)))
        for off in D_off:
            correlated_addr.add(AddrObj["Area"] + "D" + str(max(0, int(AddrObj["Byte"]) - off)))
    else:
        X_off = range(8)
        Addr_B_tmp = re.compile(r"(?P<Area>.)B(?P<Byte>\d+)", re.S)
        AddrObj = Addr_B_tmp.search(addr)
        if AddrObj:
            for off in W_off:
                correlated_addr.add(AddrObj["Area"] + "W" + str(max(0, int(AddrObj["Byte"]) - off)))
            for off in D_off:
                correlated_addr.add(AddrObj["Area"] + "D" + str(max(0, int(AddrObj["Byte"]) - off)))
        else:
            X_off = range(16)
            Addr_W_tmp = re.compile(r"(?P<Area>.)W(?P<Byte>\d+)", re.S)
            AddrObj = Addr_W_tmp.search(addr)
            if AddrObj:
                for off in W_off:
                    correlated_addr.add(AddrObj["Area"] + "W" + str(max(0, int(AddrObj["Byte"]) - off)))
                for off in D_off:
                    correlated_addr.add(AddrObj["Area"] + "D" + str(max(0, int(AddrObj["Byte"]) - off)))
            else:
                X_off = range(32)
                Addr_D_tmp = re.compile(r"(?P<Area>.)D(?P<Byte>\d+)", re.S)
                AddrObj = Addr_D_tmp.search(addr)
                if AddrObj:
                    for off in D_off:
                        correlated_addr.add(AddrObj["Area"] + "D" + str(max(0, int(AddrObj["Byte"]) - off)))
                else:
                    print("Wrong address format!!")

    if addr in correlated_addr:
        correlated_addr.remove(addr)

    return correlated_addr


def Recursively_search(STL_induced_relation, STL_induced_relation_indirectly, STL_false_address={}):
    condition = True
    cycle = 1
    while condition:
        STL_induced_relation, STL_induced_relation_indirectly, STL_false_address = Recursively_loop(
            STL_induced_relation, STL_induced_relation_indirectly, STL_false_address, cycle=cycle)
        
        sets = list(STL_induced_relation_indirectly.values())
        condition = any([s if (len(s) > 0) else False for s in sets])
        cycle = cycle + 1

    print("\nIO map obtained, \nSearch times: {}".format(cycle))

    if STL_false_address:
        print("\nThe listed addresses are set as \"False\"")
        for k, v in STL_false_address.items():
            print(k, v)
    else:
        print("\nNO false address exists!")

    return STL_induced_relation, STL_induced_relation_indirectly, STL_false_address


def Block_segmentation(sourcefile):
    STL_blocks = {}
    FC_Blocks = re.findall(r"FUNCTION (.+?)END_FUNCTION", sourcefile, re.DOTALL | re.MULTILINE)
    for FC in range(len(FC_Blocks)):
        FCObj = re.search(r"(?P<Block>FC \d+)(.+)BEGIN\n(?P<NETs>.+)", FC_Blocks[FC], re.M | re.S)
        STL_blocks[FCObj["Block"]] = FCObj["NETs"]

    Orga_Blocks = re.findall(r"ORGANIZATION_BLOCK (.+?)END_ORGANIZATION_BLOCK", sourcefile, re.DOTALL | re.MULTILINE)
    for OB in range(len(Orga_Blocks)):
        OBObj = re.search(r"(?P<Block>OB \d+)(.+)BEGIN\n(?P<NETs>.+)", Orga_Blocks[OB], re.M | re.S)
        STL_blocks[OBObj["Block"]] = OBObj["NETs"]

    return STL_blocks


def STL_function_search_init(sourcefile):
    STL_induced_relation = {}
    STL_induced_relation_indirectly = {}
    STL_induced_relation_init = {}

    STL_blocks = Block_segmentation(sourcefile)
    # for each STL_block in STL_blocks, do network segmentation
    for blk in STL_blocks:
        block_networks = network_segmentation(STL_blocks[blk])
        block_induced_relation, block_induced_relation_indirectly = STL_function_search(block_networks, Blk_name=blk)
        STL_induced_relation.update(block_induced_relation)
        STL_induced_relation_indirectly.update(block_induced_relation_indirectly)

    print("\nObtaining the initial IO mapping ...  \nSTL_induced_relation:")
    for k, v in STL_induced_relation.items():
        print("Output {} : Input {}".format(k, v))
    print("\n")

    return STL_induced_relation, STL_induced_relation_indirectly


def save_mapping_file(dictionary, STL_indirectly_relation_init, file_path="./example/", file_name="test.json"):

    _Iaddress = re.compile(r'(\s*[I]\d+\.[0-7])\s*')
    _Qaddress = re.compile(r'(\s*[Q]\d+\.[0-7])\s*')
    _Maddress = re.compile(r'(\s*[M]\d+\.[0-7])|(\s*MD\d+\.[0-7])|(\s*MD\d+)\s*')
    _DBaddress = re.compile(r'(\s*DB\d+.DB[XBWD])(\d+\.[0-7])\s*')

    diction = {}
    print("\nSTL_induced_relation:")
    for k, v in dictionary.items():
        if _Qaddress.search(k):
            variables = v
            indirectly_relation = STL_indirectly_relation_init[k]
            for var_indirect in indirectly_relation:
                if var_indirect in dictionary:
                    variables = variables.union(dictionary[var_indirect])

            diction[k] = list(variables)
            print("Output {} : Input {}".format(k, diction[k]))

    with open(file_path + file_name + ".json", 'w') as f:
        json.dump(diction, f)

    print("\nIO_mapping saved in path {}{}.json".format(file_path, file_name))


file_name = "{}.awl".format("elevator_project")
sourcefile = read_file_as_str(file_name)

STL_induced_relation, STL_induced_relation_indirectly = STL_function_search_init(sourcefile)

IO_Map, STL_relation_indirectly, constant_variables_map = Recursively_search(STL_induced_relation, STL_induced_relation_indirectly)


save_mapping_file(IO_Map, STL_induced_relation_indirectly, file_path="./examples/", file_name="{}_{}".format("elevator_project", "IO"))

