import adodbapi as adod
from scipy.io import savemat, loadmat
import time



class WinccServer(object):
    def __init__(self):
        self.conn_str = "Provider=WinCCOLEDBProvider.1;Catalog=CC_wincc_20_11_03_21_26_04R;Data Source=WIN-SABDP768LOD\WINCC"
        self.readAll = "TAG:R,(59;58;57;56;55;54;53;52;51;50;49;48;47;46;45;44;43;42;41;40;39;38;37;36;35;81;80;79;78;77;76;75;73;72;71;70;69;68;67;66;64;65;63;62;61;60),'0000-00-00 00:00:00.400',\
                        '0000-00-00 00:00:00.000'"
        self.logRegistered = False
        self.record_all = []
        self.init = False

    def read(self):
        if self.init == False:
            self.conn = adod.connect(self.conn_str)
            self.cursor = self.conn.cursor()
        self.cursor.execute(self.readAll)
        result = self.cursor.fetchall()
        # for i in result:
        #     print(i)
        bool_result_all = [int(result_line['realvalue']) for result_line in result]
        self.record_all.append(bool_result_all)
        # self.conn.close()

        # if self.logRegistered == True:
        # print(bool_result_all)
        return bool_result_all
    
    def logRegister(self, iflog):
        if iflog:
            self.logRegistered = True
        else:
            self.logRegistered = False

    def export(self):
        for i in self.record_all:
            print(i)
        self.conn.close()
        a = loadmat("all_read.mat")
        a["all"] = self.record_all
        savemat("all_read.mat", a)

if __name__ == "__main__":
    winserver = WinccServer()
    winserver.logRegister(iflog=True)
    for i in range(15):
        print(i)
        a = winserver.read()
        print(a)
        time.sleep(0.1)
    winserver.export()
    print("done")