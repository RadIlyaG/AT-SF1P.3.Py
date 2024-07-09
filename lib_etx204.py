import time

import lib_gen_sf1p
import rl_etx204


class Etx204Gen:
    def __init__(self, main_obj):
        self.main_obj = main_obj
        self.e204 = rl_etx204.Etx204()
        self.id = {}

    def OpenGen(self):
        for gen in [1, 2]:
            com = self.main_obj.gaSet[f'comGen{gen}'][3:]
            print(f'\n{lib_gen_sf1p.Gen.my_time(lib_gen_sf1p.Gen)} OpenGen {gen}')
            ret = self.e204.open(com)
            print(f'ret of etx204 OpenGen {gen}:<{ret}>')
            if ret.isnumeric() and int(ret)> 0:
                self.id[gen] = ret
            else:
                self.main_obj.gaSet['fail'] = f"Open Generator-{gen} fail"
                return -1

        return self.id

    def CloseGen(self):
        print(f'\n{lib_gen_sf1p.Gen.my_time(lib_gen_sf1p.Gen)} CloseGen {self.id}')
        ret = self.e204.close()
        print(f'ret of etx204 close:<{ret}>')
        return 0

    def PortsDown(self):
        ret = 0
        for gen in [1, 2]:
            self.main_obj.my_statusbar.sstatus(f"Ports down of Generator-{gen}")
            print(f'\n{lib_gen_sf1p.Gen.my_time(lib_gen_sf1p.Gen)} PortsDown {gen}')
            ret += int(self.e204.ports_config(self.id[gen],  "-updGen all", "-admStatus down"))
            print(f'ret of PortsDown {gen}: <{ret}>')
        return ret

    def PortsUp(self):
        ret = 0
        for gen in [1, 2]:
            self.main_obj.my_statusbar.sstatus(f"Ports up of Generator-{gen}")
            id = self.id[gen]
            print(f'\n{lib_gen_sf1p.Gen.my_time(lib_gen_sf1p.Gen)} PortsUp {gen}')
            ret += int(self.e204.ports_config(self.id[gen],  "-updGen all", "-admStatus up"))
            print(f'ret of PortsUp {gen}: <{ret}>')
        return ret

    def InitEtxGen(self):
        ret = 0
        for gen in [1, 2]:
            self.main_obj.my_statusbar.sstatus(f"Init Generator-{gen}")
            id = self.id[gen]
            print(f'\n{lib_gen_sf1p.Gen.my_time(lib_gen_sf1p.Gen)} InitEtxGen {gen}')
            ret += int(self.e204.ports_config(id, "-admStatus down", "-updGen all", '-autoneg enbl', '-maxAdvertize 1000-f'))
            ret += int(self.e204.gen_config(id, "-updGen all", "-factory yes", '-genMode GE', '-chain 1', '-packRate 115000'))
            ret += int(self.e204.packet_config(id, 'MAC', "-updGen 1", f"-SA 0000000000{gen}1",
                                           f"-DA 0000000000{gen}2"))
            ret += int(self.e204.packet_config(id, 'MAC', "-updGen 2", f"-SA 0000000000{gen}2",
                                           f"-DA 0000000000{gen}1"))
            if gen == 1:
                ret += int(self.e204.packet_config(id, 'MAC', "-updGen 3", f"-SA 0000000000{gen}3",
                                               f"-DA 0000000000{gen}4"))
                ret += int(self.e204.packet_config(id, 'MAC', "-updGen 4", f"-SA 0000000000{gen}4",
                                               f"-DA 0000000000{gen}3"))

            print(f'InitEtxGen {gen} ret:<{ret}>')
        return ret

    def GenConfig(self):
        ret = 0
        for gen in [1, 2]:
            self.main_obj.my_statusbar.sstatus(f"GenConfig of Generator-{gen}")
            id = self.id[gen]
            print(f'\n{lib_gen_sf1p.Gen.my_time(lib_gen_sf1p.Gen)} GenConfig {gen}')
            ret += int(self.e204.gen_config(id, "-updGen all", "-factory yes", '-genMode GE', '-chain 1', '-packRate 115000'))
            print(f'GenConfig {gen} ret:<{ret}>')
        return ret

    def Start(self):
        ret = 0
        for gen in [1, 2]:
            self.main_obj.my_statusbar.sstatus(f"Start Generator-{gen}")
            id = self.id[gen]
            print(f'\n{lib_gen_sf1p.Gen.my_time(lib_gen_sf1p.Gen)} Start {gen}')
            self.e204.start(id)
            time.sleep(0.5)
            self.e204.clear(id)
            time.sleep(0.5)
            self.e204.start(id)
            time.sleep(0.5)
            self.e204.clear(id)
        return ret

    def Check(self):
        ret = 0
        for gen in [1, 2]:
            if gen == 2 and self.main_obj.gaSet['wanPorts'] == '2U':
                break
            self.main_obj.my_statusbar.sstatus(f"Check Generator-{gen}")
            id = self.id[gen]
            print(f'\n{lib_gen_sf1p.Gen.my_time(lib_gen_sf1p.Gen)} Check {gen}')
            dict_res = self.e204.get_statistics(id)
            #print(dict_res)
            ret = 0
            for key, val in dict_res.items():
                box_id, par, port_name = key.split(',')
                box = box_id[2:]
                port = port_name[3:]
                print(gen, id, box, par, port, val)
                if self.main_obj.gaSet['wanPorts'] == '2U' and gen == 1 and (port == '3' or port == '4'):
                    print(f'2U gen=1, port={port}, continue')
                    continue
                elif gen == 2 and (port == '3' or port == '4'):
                    print(f'gen=2, port={port}, continue')
                    continue
                else:
                    print('check')
                if id == box and par in ['ERR_CNT', 'FRAME_ERR', 'PRBS_ERR', 'SEQ_ERR']:
                    if val != '0':
                        self.main_obj.gaSet['fail'] = f'The {par} in Generator-{gen} Port-{port} is {val}. Should be 0'
                        ret = -1
                        break
                if id == box and par in ['PRBS_OK', 'RCV_BPS', 'RCV_PPS']:
                    if val == '0':
                        self.main_obj.gaSet['fail'] = f'The {par} in Generator-{gen} Port-{port} is 0. Should be more'
                        ret = -1
                        break

            if ret != 0:
                print(f"gaSet['fail']:{self.main_obj.gaSet['fail']}")
        return ret

