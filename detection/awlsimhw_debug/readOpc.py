import OpenOPC
import adodbapi
import pywintypes

class opc(object):
    def __init__(self):
        pywintypes.datetime = pywintypes.TimeType
        # The name of WinCC project is customized. Here is our case 
        self.wincc = "OPCServer.WinCC.xxx"
        self.loadMapping()

    def loadMapping(self):
        sql_server= sqlserver()
        sql_server.connect()
        self.names = sql_server.fetchName()
    
    def connect(self):
        self.opcItem = OpenOPC.client()
        self.opcItem.connect(self.wincc)
        print("OPC client start connection")
    
    def readVars(self):
        result = self.opcItem.read(self.names)
        self.readLt = [1 if item[1] else 0 for item in result]
        return self.readLt
    
    def close(self):
        self.opcItem.close()
        print("OPC client close connection")
        
class sqlserver(object):
    def __init__(self):
        self.conn_str = "Provider=%(provider)s;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=%(database)s;Data Source=%(host)s"
        self.provider = "SQLOLEDB.1"
        # The name of database for WinCC project is customized. Here is our case 
        self.database = "CC_wincc_XX_XX_XX_XX_XX_XX"
        # The host of database for WinCC project depends on the workstation, and is customized. Here is our case 
        self.host = "WIN-XXXXXXXX\XXX"
        self.query = "SELECT ValueName FROM Archive WHERE ValueID>34 and ValueID <82"
        self.query_attr = "SELECT ValueName FROM Archive WHERE ValueID>93 and ValueID<115"

    def connect(self):
        self.conn = adodbapi.connect(self.conn_str, \
            provider=self.provider, host=self.host, database=self.database)
        self.cursor = self.conn.cursor()
        
    def fetchName(self):
        self.cursor.execute(self.query)
        result = self.cursor.fetchall()
        name_lt = [name['valuename'] for name in result]
        name_format_lt = [name.split("\\")[-1].strip() for name in name_lt]
        # give the exact same order with mapping
        names = []
        names += name_format_lt[0:25][::-1]
        names += name_format_lt[-7:][::-1]
        names += name_format_lt[-16:-8][::-1]
        names += name_format_lt[-18:-16]
        names += name_format_lt[-22:-18][::-1]

        self.cursor.execute(self.query_attr)
        result = self.cursor.fetchall()
        name_lt = [name['valuename'] for name in result]
        # format the name string
        name_format_lt = [name.split("\\")[-1].strip() for name in name_lt]
        atts = name_format_lt[::-1]

        names = names + atts
        print (names)
        return names

if __name__ == "__main__":
    wincc_opc = opc()
    import time
    wincc_opc.connect()
    start = time.time()
    for i in range(10):
        a = wincc_opc.readVars()
        print(a)
    end = time.time()
    print(str(end-start))
    wincc_opc.close()
