import os
import glob
import socket
import re

from Gui_SF1P import Gui
from lib_gen_sf1p import Gen


"""
 ToDo list
 1. V Alt brl
 2. V Coms     
 3. V Mux
 4. gui_MuxMngIO
 5. fail if COM is already open by TeraTerm
"""


class MainTester:
    def __init__(self, gui_num):
        print(f'MainTester, self:{self}')
        self.gaSet = {}
        if gui_num == 'Demo':
            gui_num = 1
            demo = True
        else:
            gui_num = gui_num
            demo = False

        print(f'main0 {self.gaSet}')
        hw_dict = Gen.read_hw_init(Gen, gui_num)
        # 13:14 07/04/2024 ini_dict = Gen.read_init(Gen, gui_num)
        ini_dict = Gen.read_init(Gen, self, gui_num)
        print(f'main1 {self.gaSet}')
        for f in glob.glob("SW*.txt"):
            os.remove(f)

        # hw_dict = Gen.read_hw_init(Gen, self)
        # ini_dict = Gen.read_init(Gen, self)

        self.gaSet = {**hw_dict, **ini_dict}
        self.gaSet['gui_num'] = gui_num
        self.gaSet['demo'] = demo
        self.if_rad_net()
        self.gaSet['use_exist_barcode'] = 0
        self.gaSet['wifi_net'] = f'{socket.gethostname()}_{gui_num}'
        self.gaSet['id_mac_link'] = 0
        self.gaSet['chirp_stack_ip.9XX'] = '172.18.94.105'
        self.gaSet['chirp_stack_ip.8XX'] = '172.18.94.26'
        self.gaSet['lora_server_host'] = 'Jer-LoraSrv1-10'
        self.gaSet['lora_server_ip'] = '172.18.94.79'
        self.gaSet['lora_stay_connected_on_fail'] = 0
        print(f'main2 {self.gaSet}')
        Gui(self)


    def if_rad_net(self):
        rad_net = False
        res = socket.gethostbyname_ex(socket.gethostname())
        if re.search('192.115.243', str(res[2])) or \
                re.search('172.18.9', str(res[2])):
            rad_net = True
        self.gaSet['rad_net'] = rad_net

if __name__ == '__main__':
    print(f'Main sf1p')
    tester = MainTester(33)
    print(tester.gui_num)

    