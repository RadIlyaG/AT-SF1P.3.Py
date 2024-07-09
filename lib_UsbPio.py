import ctypes
from ctypes.wintypes import DWORD
import pathlib
import os
import time
import ftd2xx
from ftd2xx import FTD2XX
import subprocess
from subprocess import CalledProcessError, check_output
import re


class UsbPio:
    def __init__(self):
        self.pio_port_id = {}

    def retrive_usb_channel(self, box):
        arr = str(
            check_output(r'c:\\tcl\\bin\\wish86.exe pio_usb_scr.tcl RetriveUsbChannel'),
            'utf-8')
        lst = arr.split(" ")
        it_lst = iter(lst)
        channel = None
        for a in it_lst:
            if re.search('SerialNumber', a) and next(it_lst) == box:
                channel = a.split(',')[0]
                # print(f'a:{a} channel:{channel}')
                break
        return channel

    def osc_pio(self, channel, port, group, value, state='00000000'):
        # print(f'rlusbpio osc_pio self:{self} channel:{channel} port:{port} group:{group} value:{value} state:{state}')
        lin = f'c:\\tcl\\bin\\wish86.exe pio_usb_scr.tcl OpenSetClose {channel} {port} {group} "{value}" {state}'
        ret = str(check_output(lin), 'utf-8')
        # print(f'rlusbpio osc_pio ret:{ret}')
        return ret

    ''''''
    def mmux(self, channel, port, group, mode, chs=''):
        print(f'mmmux, mode:{mode}, chs:{chs}')
        values = []

        if mode == "AllNC":
            values += ['10000000']
            values += self.bus_state("A B C D")
        elif mode == "ChsCon":
            values = self.channels_con(chs)
        elif mode == "ChOnly":
            values += ['10000000']
            values += self.bus_state("A B C D")
            values += self.channels_con(chs)
        elif mode == "BusState":
            values += self.bus_state(chs)

        #return values

        lin = f'c:\\tcl\\bin\\wish86.exe pio_usb_scr.tcl MultiMux {channel} {port} {group} {values} "00000000"'
        ret = str(check_output(lin), 'utf-8')
        return ret

    def bus_state(self, bus):
        a = b = ''
        pio_bits = []
        wl = []
        if bus == "A,B,C,D":
            wl = ("011101", "011110", "011111")  # close relays 1,2 and 3
        elif bus == "A,B C D":
            wl = ("011101", "111110", "111111")  # close relay 1, open relays 2 and 3
        elif bus == "A B,C D":
            wl = ("111101", "011110", "111111")  # close relay 2, open relays 1 and 3
        elif bus == "A B C,D":
            wl = ("111101", "111110", "011111")  # close relay 3, open relays 1 and 2
        elif bus == "A,B,C D":
            wl = ("011101", "011110", "111111")  # close relays 1 and 2, open relay 3
        elif bus == "A B,C,D":
            wl = ("111101", "011110", "011111")  # close relays 2 and 3, open relay 1
        elif bus == "A,B C,D":
            wl = ("011101", "111110", "011111")  # close relays 1 and 3, open relay 2
        elif bus == "A B C D":
            wl = ("111101", "111110", "111111")  # open relays  1,2 and 3
      
        for w in wl:
            pio_bits += ["11" + w]
            pio_bits += ["01" + w]
            pio_bits += ["11" + w]

        return pio_bits
        
    def ch_to_pio(self, ch):
        gr_bits = ''
        if ch <= 7:
            gr_bits = '00'
        elif 7 < ch <= 15:
            gr_bits = '01'
        elif 15 < ch <= 23:
            gr_bits = '10'
        else:
            gr_bits = '11'

        return gr_bits + self.ch_to_chBits(ch)

    def ch_to_chBits(self, ch):
        return f'{(ch + 8) % 8:03b}'

    def channel_con(self, ch):
        ret_list = []
        pio_bits = self.ch_to_pio(ch)
        ret_list.append('111' + pio_bits)
        ret_list.append('011' + pio_bits)
        ret_list.append('111' + pio_bits)
        return ret_list

    def channels_con(self, chs):
        pio_bits = []
        for ch in chs:
            pio_bits += self.channel_con(ch)
        return pio_bits

if __name__ == '__main__':
    pio_obj = UsbPio()
    #print(pio_obj.bus_state("A B C D"))

    for mode, chs in [["AllNC", 'nc'], ['ChsCon', [1,3]],
                      ['ChsCon', [1]], ['ChOnly', [1]], ['BusState', "A,B C,D"]]:
        print(f'{mode},{pio_obj.mmux(1,2,3, mode, chs)}')



