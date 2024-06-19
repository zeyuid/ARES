import OpenOPC
import adodbapi
import pywintypes

class opc(object):
    def __init__(self):
        pywintypes.datetime = pywintypes.TimeType
        self.wincc = "OPCServer.WinCC.1"
        self.loadMapping()

    def loadMapping(self):
        sql_server= sqlserver()
        sql_server.connect()
        self.names = sql_server.fetchName()
        # print(self.names)
    
    def connect(self):
        self.opcItem = OpenOPC.client()
        self.opcItem.connect(self.wincc)
        print("OPC client start connection")
    
    def readVars(self):
        result = self.opcItem.read(self.names)
        # print(dir(result))
        # print(hasattr(result, 'value'))
        self.readLt = [1 if item[1] else 0 for item in result]
        # print(self.readLt)
        return self.readLt
    
    def close(self):
        self.opcItem.close()
        print("OPC client close connection")
        
class sqlserver(object):
    def __init__(self):
        self.conn_str = "Provider=%(provider)s;Integrated Security=SSPI;Persist Security Info=False;Initial Catalog=%(database)s;Data Source=%(host)s"
        self.provider = "SQLOLEDB.1"
        self.database = "CC_wincc_20_11_03_21_26_04R"
        self.host = "WIN-SABDP768LOD\WINCC"
        self.query = "SELECT ValueName FROM Archive WHERE ValueID>34 and ValueID <82"

    def connect(self):
        self.conn = adodbapi.connect(self.conn_str, \
            provider=self.provider, host=self.host, database=self.database)
        self.cursor = self.conn.cursor()
        
    def fetchName(self):
        self.cursor.execute(self.query)
        result = self.cursor.fetchall()
        name_lt = [name['valuename'] for name in result]
        # format the name string
        name_format_lt = [name.split("\\")[-1].strip() for name in name_lt]
        # print(name_format_lt)
        # give the exact same order with mapping
        names = []
        names += name_format_lt[0:25][::-1]
        names += name_format_lt[-7:][::-1]
        names += name_format_lt[-16:-8][::-1]
        names += name_format_lt[-18:-16]
        names += name_format_lt[-22:-18][::-1]
        return names

if __name__ == "__main__":
    wincc_opc = opc()
    import time
    wincc_opc.connect()
    start = time.time()
    for i in range(100):
        wincc_opc.readVars()
    end = time.time()
    print(str(end-start))
    wincc_opc.close()
