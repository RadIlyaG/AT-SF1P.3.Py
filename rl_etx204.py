import time
import tkinter
from tkinter import messagebox

class Etx204:
    def __init__(self):
        self.tkl = tkinter.Tk()
        self.tkl.eval('source lib_etx204_scr.tcl')
        
    def open(self, com):
        print(f'Etx204 open com:<{com}>')
        return self.tkl.eval(f'RLEtxGen::Open {com} -package RLCom')
        
    def close(self):
        return self.tkl.eval(f'RLEtxGen::CloseAll')

    def ports_config(self, id, *args):
        #print(f'ports_config args:<{args}>')
        cmd = f'RLEtxGen::PortsConfig {id} '
        for arg in args:
            cmd += f' {arg}'
        print(cmd)
        return self.tkl.eval(cmd)

    def gen_config(self, id, *args):
        #print(f'gen_config args:<{args}>')
        cmd = f'RLEtxGen::GenConfig {id} '
        for arg in args:
            cmd += f' {arg}'
        print(cmd)
        return self.tkl.eval(cmd)

    def packet_config(self, id, *args):
        #print(f'gen_config args:<{args}>')
        cmd = f'RLEtxGen::PacketConfig {id} '
        for arg in args:
            cmd += f' {arg}'
        print(cmd)
        return self.tkl.eval(cmd)

    def start(self, id):
        cmd = f'RLEtxGen::Start {id} '
        print(cmd)
        return self.tkl.eval(cmd)

    def stop(self, id):
        cmd = f'RLEtxGen::Stop {id} '
        print(cmd)
        return self.tkl.eval(cmd)

    def clear(self, id):
        cmd = f'RLEtxGen::Clear {id} '
        print(cmd)
        return self.tkl.eval(cmd)

    def get_statistics(self, id):
        cmd = f'RLEtxGen::GetStatistics {id} ares'
        print(cmd)
        self.tkl.eval(cmd)
        time.sleep(2)
        # print(f'ares:<{self.tkl.eval("array get ares")}>')
        dict_res = {}
        lres = self.tkl.eval("array get ares").split(" ")
        for key, val in zip(lres[0::2], lres[1::2]):
            dict_res[key] = val
        print(dict_res)
        return dict_res


        