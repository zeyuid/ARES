import OpenOPC
import logging

class Opc():
    def __init__(self, name, driver, read_name_list=None, write_name_list=None):
        self.name = name
        self.driver = driver
        self.read_name_list = read_name_list
        self.write_name_list = write_name_list

    def connect(self):
        self.opc = OpenOPC.client()
        self.opc.connect(self.driver)
    
    def close(self):
        self.opc.close()

    # return list for read names 
    def read(self):
        if self.read_name_list == None:
            logging.error("Give specific read grp first")
            return None
        result_temp = self.opc.read(self.read_name_list)
        result = [item[1] for item in result_temp]
        return result
      
    def write(self, value_list):
        if self.write_name_list == None:
            logging.error("Give specific write grp first")
            return None
        if len(self.write_name_list) != len(value_list):
            logging.error("Error with unmatched list length between write name list and write values")
        write_tuple_list = []
        for name, value in zip(self.write_name_list, value_list):
            write_tuple_list.append((name, value))
        self.opc.write(write_tuple_list)
    
    def set_read_list(self, read_name_list):
        self.read_name_list = read_name_list
    
    def set_write_list(self, write_name_list):
        self.write_name_list = write_name_list

