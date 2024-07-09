import re
import subprocess
import time
import inspect
import winsound

import Gui_SF1P
import lib_gen_sf1p as lgen
# from gui_sf1p import App
from RL import rl_com as rlcom

import rad_apps
from rad_apps import *


class Put:
    def __init__(self, main_obj):
        self.main_obj = main_obj
        # print(f'put init self:{self}')
        # App.__init__(self, self.gaSet['root'], gaSet)

    def login(self):
        if self.main_obj.gaSet['act'] == 0:
            return -2
        gen_obj = lgen.Gen(self.main_obj)
        print(f'\n{gen_obj.my_time()} Login ')
        self.main_obj.my_statusbar.sstatus('Login')

        ret = -1
        com = self.main_obj.gaSet['com_obj']
        self.login_buff = ''
        com.send("\r", 'stam', 0.25)
        self.login_buff += com.buffer
        com.send("\r", 'stam', 0.25)
        self.login_buff += com.buffer
        print(f'login_buff:<{self.login_buff}>')
        if self.main_obj.gaSet['act'] == 0:
            return -2

        if re.search('PCPE>', self.login_buff):
            print(f'login PCPE')
            com.send('boot\r', 'partitions')
            time.sleep(10)
            ret = -1

        if re.search('root@localhost', self.login_buff):
            print(f'login localhost')
            ret = com.send('exit\r\r', '-1p', 12)

        if re.search('-1p', com.buffer):
            print(f'login -1p')
            time.sleep(2)
            # com.send('\r', 'stam', 0.25)
            com.send('\r', '-1p')
            self.login_buff += com.buffer
            if re.search('-1p', com.buffer):
                ret = 0

        if re.search('CLI session is closed', com.buffer):
            print(f'login CLI session is closed')
            ret = -1
            com.send('\r')

        print(f'ret before loop:{ret}')
        if self.main_obj.gaSet['act'] == 0:
            return -2

        self.main_obj.gaSet['fail'] = 'Login fail'
        if ret != 0:
            start_sec = time.time()
            for i in range(1, 61):
                run_sec = int(time.time() - start_sec)
                self.main_obj.my_statusbar.runTime(f'{run_sec} sec')
                self.main_obj.gaSet['root'].update()
                if self.main_obj.gaSet['act'] == 0:
                    ret = -2
                    break

                try:
                    read_buff = str(com.read(), 'utf-8')
                    self.login_buff += read_buff
                    print(f'\nrun_sec:{run_sec}  read_buff:<{read_buff}>')
                except:
                    time.sleep(5)
                    continue

                if re.search(r'failed to achieve system info', self.login_buff) and \
                        re.search(r'command execute error:', self.login_buff):
                    return 'PowerOffOn'

                if re.search(r'user>', self.login_buff):  # rlcom.buffer
                    com.send('su\r', 'assword')
                    if com.send('1234\r', '-1p#', 3) == 0:
                        ret = 0
                        break
                    elif 'The password is not strong' in com.buffer:
                        com.send('4\r', 'again', 3)
                        ret = com.send('4\r', '-1p#', 3)
                    elif 'Login failed' in com.buffer:
                        com.send('su\r4\r', 'again', 3)
                        ret = com.send('4\r', '-1p#', 3)

                if re.search('-1p', read_buff):
                    return 0

                if re.search(r'PCPE>', read_buff):
                    com.send('boot\r', 'partitions')

                time.sleep(5)

        if ret == 0:
            self.main_obj.gaSet['fail'] = ''
        # else:
        #     self.gaSet['fail'] = 'Login fail'
        return ret

    def pwr_rst_login_2_app(self):
        # self.gaSet['puts_log'].info(f'pwr_rst_login_2_app')
        print(f'{lgen.my_time()} {inspect.stack()[0][3].upper()}')
        com = 'comDut'
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        if re.search('-1p#', rlcom.buffer):  # rlcom.buffer
            return 0
        if re.search('user>', rlcom.buffer):  # rlcom.buffer
            lgen.my_send(self.gaSet, com, 'su\r', 'assword')
            if lgen.my_send(self.gaSet, com, '1234\r', '-1p#') == 0:
                return 0

        lgen.power(self.gaSet, 1, 0)
        time.sleep(4)
        lgen.power(self.gaSet, 1, 1)
        return self.login_2_app()

    def pwr_rst_login_2_boot(self):
        # self.gaSet['puts_log'].info(f'pwr_rst_login_2_boot')
        gen_obj = lgen.Gen(self.main_obj)
        print(f'{gen_obj.my_time()} {inspect.stack()[0][3].upper()}')
        com = self.main_obj.gaSet['com_obj']
        com.send('\r', 'stam', 0.25)
        com.send('\r', 'stam', 0.25)
        if re.search('PCPE', com.buffer):  # rlcom.buffer
            return 0

        gen_obj.power(self.main_obj, 1, 0)
        time.sleep(4)
        gen_obj.power(self.main_obj, 1, 1)
        return self.login_2_boot()

    def login_2_app(self):
        # print(f'put login_2_app self:{self}')
        App.my_statusbar.sstatus('Login into Application')

        ret = -1
        com = 'comDut'
        login_buff = ''
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        login_buff += rlcom.buffer
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        login_buff += rlcom.buffer

        if re.search('-1p', rlcom.buffer):
            print(f'login_2_app -1p')
            ret = 0
        if re.search('PCPE>', rlcom.buffer):
            print(f'login_2_app PCPE')
            lgen.my_send(self.gaSet, com, 'boot\r', 'stam', 0.25)
            time.sleep(10)
            ret = -1
        if re.search('root@localhost', rlcom.buffer):
            print(f'login_2_app localhost')
            ret = lgen.my_send(self.gaSet, com, 'exit\r\r', '-1p', 12)

        print(f'login_2_app ret before loop:{ret}')
        self.gaSet['fail'] = 'Login to Application level fail'
        if ret != 0:
            start_sec = time.time()
            for i in range(1, 61):
                App.my_statusbar.runTime(i)
                self.gaSet['root'].update()
                if self.gaSet['act'] == 0:
                    ret = -2
                    break

                read_buff = lgen.my_read(self.gaSet, com)
                login_buff += read_buff
                print(f'Login to App {lgen.my_time()} run_sec:{int(time.time() - start_sec)}  read_buff:_{read_buff}_')

                if re.search('user>', login_buff):  # rlcom.buffer
                    lgen.my_send(self.gaSet, com, 'su\r', 'assword')
                    if lgen.my_send(self.gaSet, com, '1234\r', '-1p#') == 0:
                        ret = 0
                        break

                time.sleep(5)

        if ret == 0:
            self.gaSet['fail'] = ''
        else:
            self.gaSet['fail'] = 'Login fail'
        return ret

    def login_2_boot(self):
        self.main_obj.my_statusbar.sstatus('Login into Boot')

        ret = -1
        com = self.main_obj.gaSet['com_obj']
        self.login_buff = ''
        com.send('\r', 'stam', 0.25)
        self.login_buff += com.buffer
        com.send('\r', 'stam', 0.25)
        self.login_buff += com.buffer

        if re.search('\\]#', com.buffer):
            ret = 0

        # self.gaSet['fail'] = 'Login to Boot level fail'
        if ret != 0:
            start_sec = time.time()
            for i in range(1, 301):
                self.main_obj.my_statusbar.runTime(i)
                self.main_obj.gaSet['root'].update()
                if self.main_obj.gaSet['act'] == 0:
                    ret = -2
                    break

                read_buff = str(com.read(), 'utf-8')
                self.login_buff += read_buff
                print(
                    f'Login to Boot run_sec:{int(time.time() - start_sec)}  read_buff:<{read_buff}>')

                if re.search('to stop autoboot:', read_buff):  # rlcom.buffer
                    if com.send('\r\r', 'PCPE') == 0:
                        ret = 0
                        break
                if re.search('to stop PCPE:', read_buff):  # rlcom.buffer
                    ret = 0
                    break

                time.sleep(1)

        if ret == 0:
            self.main_obj.gaSet['fail'] = ''
        else:
            self.main_obj.gaSet['fail'] = 'Login fail'
        return ret

    def login_2_uboot(self):
        App.my_statusbar.sstatus('Login into Uboot')

        ret = -1
        com = 'comDut'
        login_buff = ''
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        login_buff += rlcom.buffer
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        login_buff += rlcom.buffer

        if re.search('PCPE', rlcom.buffer):
            ret = 0

        self.gaSet['fail'] = 'Login to Uboot level fail'
        if ret != 0:
            start_sec = time.time()
            for i in range(1, 61):
                App.my_statusbar.runTime(i)
                self.gaSet['root'].update()
                if self.gaSet['act'] == 0:
                    ret = -2
                    break

                read_buff = lgen.my_read(self.gaSet, com)
                login_buff += read_buff
                print(
                    f'Login to Uboot {lgen.my_time()} run_sec:{int(time.time() - start_sec)}  read_buff:_{read_buff}_')

                if re.search('PCPE', login_buff):  # rlcom.buffer
                    ret = 0
                    break

                time.sleep(1)

        if ret == 0:
            self.gaSet['fail'] = ''
        # else:
        #     gaSet['fail'] = 'Login fail'
        return ret

    def login_2_linux(self):
        self.main_obj.my_statusbar.sstatus('Login to Linux')
        ret = -1
        com = self.main_obj.gaSet['com_obj']
        login_buff = ''
        com.send('\r', 'stam', 0.25)
        login_buff += com.buffer

        if re.search('root@localhost', com.buffer):
            ret = 0
            return ret

        ret = self.logon_debug()
        print(f'ret after logon_debug:{ret}')
        if ret != 0:
            return ret

        ret = com.send('debug shell\r\r', '/\\]#')
        if ret == -1:
            self.main_obj.gaSet['fail'] = "Login to Linux Fail"

        return ret

    def logon_debug(self):
        self.main_obj.my_statusbar.sstatus('Logon Debug')

        ret = -1
        com = self.main_obj.gaSet['com_obj']
        com.send('exit all\r', 'stam', 0.25)
        com.send('logon debug\r', 'stam', 0.25)
        if re.search('command not recognized', com.buffer) is None:
            m = re.search('Key code:\s+(\d+)', com.buffer)
            if m:
                kc = m[1]
                # ate_decr = AteDecryptor()
                password = AteDecryptor().get_password(kc, "pass")
                print(f'logon_debug password:{password}')
                self.main_obj.gaSet['fail'] = 'Logon debug fail'
                ret = com.send(f'{password}\r', '-1p#')
            else:
                ret = -1
        else:
            ret = 0
        return ret

    def read_wan_lan_status(self):
        if self.main_obj.gaSet['act'] == 0:
            return -2
        gen_obj = lgen.Gen(self.main_obj)
        print(f'\n{gen_obj.my_time()} read_wan_lan_status')
        ret = 0
        sfp_ports = []
        utp_ports = []
        if self.main_obj.gaSet['wanPorts'] == '2U':
            sfp_ports = []
            utp_ports = ['3', '4']
        elif self.main_obj.gaSet['wanPorts'] == '4U2S':
            sfp_ports = ['1', '2']
            utp_ports = ['3', '4', '5', '6']
        elif self.main_obj.gaSet['wanPorts'] == '5U1S':
            sfp_ports = ['1']
            utp_ports = ['2', '3', '4', '5', '6']
        elif self.main_obj.gaSet['wanPorts'] == '1SFP1UTP':
            sfp_ports = ['wan1']
            utp_ports = ['wan2', 'lan1', 'lan2', 'lan3', 'lan4']

        print(f'read_wan_lan_status sfp_ports:<{sfp_ports}> utp_ports:<{utp_ports}>')

        ret = self.login()
        print(f'read_wan_lan_status ret of login:{ret}')
        if ret != 0:
            return ret

        for port in sfp_ports + utp_ports:
            ret = self.shut_down(port, 'no shutdown')
            print(f'read_wan_lan_status ret of shut_down:{ret} act:{self.main_obj.gaSet["act"]}')
            if self.main_obj.gaSet['act'] == 0:
                return -2

        for port in sfp_ports:
            ret = self.read_eth_port_status(port)
            print(f'ret of read_eth_port_status port {port}:{ret} act:{self.main_obj.gaSet["act"]}')
            if ret != 0:
                return ret
            if self.main_obj.gaSet['act'] == 0:
                return -2
        for port in utp_ports:
            ret = self.read_utp_port_status(port)
            print(f'ret of read_utp_port_status port {port}:{ret} act:{self.main_obj.gaSet["act"]}')
            if ret != 0:
                return ret
            if self.main_obj.gaSet['act'] == 0:
                return -2

        return ret

    def read_eth_port_status(self, port):
        self.main_obj.my_statusbar.sstatus(f'Read EthPort Status of {port}')
        if self.main_obj.gaSet['act'] == 0:
            return -2

        print(f'\nread_eth_port_status port:{port}')
        # ret = self.login()
        # print(f'read_eth_port_status ret of login:{ret}')
        # if ret != 0:
        #     return ret
        # self.main_obj.my_statusbar.sstatus(f'Read EthPort Status of {port}')

        self.main_obj.gaSet['fail'] = f'Show status of port {port} fail'
        com = self.main_obj.gaSet['com_obj']

        com.send('exit all\r', 'stam', 0.25)
        ret = com.send(f'config port ethernet {port}\r', f'\({port}\)')
        if ret != 0:
            return ret

        time.sleep(2)

        com.send('show status\r', 'more', 8)
        bu = com.buffer
        ret = com.send('\r', f'\({port}\)')
        if ret != 0:
            return ret
        bu += com.buffer

        # self.gaSet['puts_log'].info(f"ReadEthPortStatus bu:{bu}")
        print(f'ReadEthPortStatus bu:{bu}')

        m = re.search(r'SFP\+?\sIn', bu)
        print(f'm of SFP In:{m}')

        m = re.search(r'Operational Status[\s\:]+([\w]+)\s', bu)
        if m is None:
            self.main_obj.gaSet['fail'] = f'Read Operational Status of port {port} fail'
            return -1
        op_stat = m[1].strip(" ")
        # print(f'Op Stat:_{op_stat}_')
        # self.gaSet['puts_log'].info(f"Operational Status: {op_stat}")
        print(f'Operational Status: {op_stat}')
        if op_stat != "Up":
            self.main_obj.gaSet['fail'] = f'The Operational Status of port {port} is {op_stat}'
            return -1

        m = re.search(r'Administrative Status[\s\:]+([\w]+)\s', bu)
        if m is None:
            self.main_obj.gaSet['fail'] = f'Read Administrative Status of port {port} fail'
            return -1
        adm_stat = m[1].strip(" ")
        # print(f'Op Stat:_{adm_stat}_')
        # self.gaSet['puts_log'].info(f"Administrative Status: {adm_stat}")
        print(f'Administrative Status: {adm_stat}')
        # print(f'm of Adm Stat:{m}, m1:{m[1]}')
        if adm_stat != "Up":
            self.main_obj.gaSet['fail'] = f'The Administrative Status of port {port} is {adm_stat}'
            return -1

        return ret

    def read_utp_port_status(self, port):
        self.main_obj.my_statusbar.sstatus(f'Read EthPort Status of {port}')
        print(f'\nread_utp_port_status port:{port}')
        # ret = self.login()
        # print(f'read_utp_port_status ret of login:{ret}')
        # if ret != 0:
        #     return ret
        # self.main_obj.my_statusbar.sstatus(f'Read EthPort Status of {port}')

        self.main_obj.gaSet['fail'] = f'Show status of port {port} fail'
        com = self.main_obj.gaSet['com_obj']

        com.send('exit all\r', 'stam', 0.25)
        ret = com.send(f'config port ethernet {port}\r', f'\({port}\)')
        if ret != 0:
            return ret

        time.sleep(2)

        com.send('show status\r', f'\({port}\)')
        bu = com.buffer
        ret = com.send('\r', f'\({port}\)')
        if ret != 0:
            return ret
        bu += com.buffer

        # self.gaSet['puts_log'].info(f"ReadEthPortStatus bu:{bu}")
        print(f'ReadEthPortStatus bu:{bu}')

        m = re.search(r'Operational Status[\s\:]+([\w]+)\s', bu)
        if m is None:
            self.main_obj.gaSet['fail'] = f'Read Operational Status of port {port} fail'
            return -1
        op_stat = m[1].strip(" ")
        # print(f'Op Stat:_{op_stat}_')
        # self.gaSet['puts_log'].info(f"Operational Status: {op_stat}")
        print(f'Operational Status: {op_stat}')
        if op_stat != "Up":
            self.main_obj.gaSet['fail'] = f'The Operational Status of port {port} is {op_stat}'
            return -1

        m = re.search(r'Administrative Status[\s\:]+([\w]+)\s', bu)
        if m is None:
            self.main_obj.gaSet['fail'] = f'Read Administrative Status of port {port} fail'
            return -1
        adm_stat = m[1].strip(" ")
        # print(f'Op Stat:_{adm_stat}_')
        # self.gaSet['puts_log'].info(f"Administrative Status: {adm_stat}")
        print(f'Administrative Status: {adm_stat}')
        # print(f'm of Adm Stat:{m}, m1:{m[1]}')
        if adm_stat != "Up":
            self.main_obj.gaSet['fail'] = f'The Administrative Status of port {port} is {adm_stat}'
            return -1

        m = re.search(r'Connector Type[\s\:]+([\w]+)\s', bu)
        if m is None:
            self.main_obj.gaSet['fail'] = f'Read Connector Type of port {port} fail'
            return -1
        conn = m[1].strip(" ")
        # self.gaSet['puts_log'].info(f"Connector Type: {conn}")
        print(f'Connector Type: {conn}')
        if conn != "RJ45":
            self.main_obj.gaSet['fail'] = f'The Connector Type of port {port} is {conn}'
            return -1

        return ret

    def shut_down(self, port, state):
        gen_obj = lgen.Gen(self.main_obj)
        self.main_obj.my_statusbar.sstatus(f'ShutDown port {port} "{state}"')
        # self.main_obj.gaSet['root'].update()

        if self.main_obj.gaSet['act'] == 0:
            return -2

        print(f'{gen_obj.my_time()} shut_down port:{port}, state:{state}')
        # ret = self.login()
        # print(f'shut_down ret of login:{ret}')
        # if ret != 0:
        #     return ret
        # self.main_obj.my_statusbar.sstatus(f'ShutDown port {port} "{state}"')

        com = self.main_obj.gaSet['com_obj']
        ret = com.send('exit all\r', '-1p')
        if ret != 0:
            return ret
        ret = com.send(f'configure port ethernet {port}\r', 'stam', 1)
        ret = com.send(f'{state}\r', f'\({port}\)')
        return ret

    def usb_tree_perform(self):
        # self.gaSet['puts_log'].info(f'{inspect.stack()[0][3].upper()}')
        print(f'{lgen.my_time()} {inspect.stack()[0][3].upper()}')
        if self.gaSet['dut_fam']['cell']['cell'] != 0 and self.gaSet['dut_fam']['wifi'] == 0:
            ## LTE only
            bus0devs = '2'
            sec_vendor_spec = 12
        elif self.gaSet['dut_fam']['cell']['cell'] != 0 and self.gaSet['dut_fam']['wifi'] != 0:
            ## LTE and WiFi
            bus0devs = '2'
            sec_vendor_spec = 480
        elif self.gaSet['dut_fam']['cell']['cell'] == 0 and self.gaSet['dut_fam']['wifi'] == 0:
            ## no LTE, no WiFi
            bus0devs = '1'
            sec_vendor_spec = 'NA'
        elif self.gaSet['dut_fam']['cell']['cell'] == 0 and self.gaSet['dut_fam']['wifi'] != 0:
            ## WiFi only
            bus0devs = '1'
            sec_vendor_spec = 'NA'

        com = 'comDut'
        ret = lgen.my_send(self.gaSet, com, 'usb start\r', 'stam', 3)
        ret = lgen.my_send(self.gaSet, com, 'usb stop\r', 'stam', 1)
        ret = lgen.my_send(self.gaSet, com, 'usb start\r', 'stam', 3)
        if re.search('PCPE', rlcom.buffer):
            ret = 0

        if ret != 0:
            self.gaSet['fail'] = f'"usb start" fail'
            return ret

        m = re.search(r'scanning bus 0 for devices[\.\s]+(\d) USB Device\(s\) found', rlcom.buffer)
        if m is None:
            self.gaSet['fail'] = f'Retrieve from "scanning bus 0 for devices" fail'
            return -1
        val = m[1]
        # self.gaSet['puts_log'].info(f'UsbStartPerform val:{val} bus0devs:{bus0devs}')
        print(f'{lgen.my_time()} UsbStartPerform val:{val} bus0devs:{bus0devs}')
        # print(f'UsbStartPerform val:{type(val)} bus0devs:{type(bus0devs)}')
        if val != bus0devs:
            self.gaSet['fail'] = f'Found {val} devices on bus 0. Should be {bus0devs}'
            return -1

        ret = lgen.my_send(self.gaSet, com, 'usb tree\r', 'PCPE')
        if ret != 0:
            self.gaSet['fail'] = f'"usb tree" fail'
            return -1

        if sec_vendor_spec == 'NA':
            if re.search('2 Vendor specific', rlcom.buffer):
                self.gaSet['fail'] = f'"2 Vendor specific" is existing'
                return -1
            else:
                ret = 0
        else:
            if re.search(r'2\s+Vendor specific', rlcom.buffer) is None:
                self.gaSet['fail'] = f'No "2 Vendor specific"'
                return -1
            else:
                ret = 0

        if self.gaSet['dut_fam']['wifi'] != 0:
            ret = lgen.my_send(self.gaSet, com, 'pci\r', 'PCPE')
            if ret != 0:
                self.gaSet['fail'] = f'"pci" fail'
                return -1
            if re.search('Network controller', rlcom.buffer) is None:
                self.gaSet['fail'] = f'"Network controller" does not exist'
                return -1

        return ret

    def micro_sd_perform(self):
        # self.gaSet['puts_log'].info(f'{inspect.stack()[0][3].upper()}')
        print(f'{lgen.Gen.my_time(lgen)} {inspect.stack()[0][3].upper()}')
        com = self.main_obj.gaSet['com_obj']
        ret = com.send('mmc dev 0:1\r', 'PCPE')
        if ret != 0:
            time.sleep(0.5)
            ret = com.send('mmc dev 0:1\r', 'PCPE')
            if ret != 0:
                self.main_obj.gaSet['fail'] = f'"mmc dev 0:1" fail'
                return -1

        if re.search(r'switch to partitions #0, OK', com.buffer) is None:
            com.send('mmc dev 0:1\r', 'PCPE')
            if re.search(r'switch to partitions #0, OK', com.buffer) is None:
                self.main_obj.gaSet['fail'] = f'"switch to partitions 0" does not exist'
                return -1

        if re.search(r'mmc0 is current device', com.buffer) is None:
            com.send('mmc dev 0:1\r', 'PCPE')
            if re.search(r'mmc0 is current device', com.buffer) is None:
                self.main_obj.gaSet['fail'] = f'"mmc0 is current device" does not exist'
                return -1

        ret = com.send('mmc info\r', 'PCPE')
        if ret != 0:
            time.sleep(0.5)
            ret = com.send('mmc info\r', 'PCPE')
            if ret != 0:
                self.main_obj.gaSet['fail'] = f'"mmc info" fail'
                return -1
        if re.search(r'Capacity: 29.7 GiB', com.buffer) is None:
            self.main_obj.gaSet['fail'] = f'"Capacity: 29.7 GiB" does not exist'
            return -1

        return ret

    def soc_flash_perform(self):
        # self.gaSet['puts_log'].info(f'{inspect.stack()[0][3].upper()}')
        print(f'{lgen.Gen.my_time(lgen)} {inspect.stack()[0][3].upper()}')
        com = self.main_obj.gaSet['com_obj']
        ret = com.send('mmc dev 1:0\r', 'PCPE')
        if ret != 0:
            self.main_obj.gaSet['fail'] = f'"mmc dev 1:0" fail'
            return -1
        if re.search(r'switch to partitions #0, OK', com.buffer) is None:
            self.main_obj.gaSet['fail'] = f'"switch to partitions 0" does not exist'
            return -1
        if re.search(r'mmc1\(part 0\) is current device', com.buffer) is None:
            self.main_obj.gaSet['fail'] = f'"mmc1(part 0) is current device" does not exist'
            return -1

        ret = com.send('mmc info\r', 'PCPE')
        if ret != 0:
            time.sleep(0.5)
            ret = com.send('mmc info\r', 'PCPE')
            if ret != 0:
                self.main_obj.gaSet['fail'] = f'"mmc info" fail'
                return -1
        if re.search(r'HC WP Group Size: 8 MiB', com.buffer) is None:
            self.main_obj.gaSet['fail'] = f'"HC WP Group Size: 8 MiB" does not exist'
            return -1
        if re.search(r'Bus Width: 8-bit', com.buffer) is None:
            self.main_obj.gaSet['fail'] = f'"Bus Width: 8-bit" does not exist'
            return -1

        ret = com.send('mmc list\r', 'PCPE')
        if ret != 0:
            self.main_obj.gaSet['fail'] = f'"mmc list" fail'
            return -1
        if re.search(r'sdhci@d0000: 0', com.buffer) is None:
            self.main_obj.gaSet['fail'] = f'"sdhci@d0000: 0" does not exist'
            return -1
        if re.search(r'sdhci@d8000: 1 \(eMMC\)', com.buffer) is None:
            self.main_obj.gaSet['fail'] = f'"sdhci@d8000: 1 (eMMC)" does not exist'
            return -1

        return ret

    def soc_2ic_perform(self):
        # self.gaSet['puts_log'].info(f'{inspect.stack()[0][3].upper()}')
        print(f'{lgen.Gen.my_time(lgen)} {inspect.stack()[0][3].upper()}')
        com = self.main_obj.gaSet['com_obj']

        ret = com.send('i2c bus\r', 'PCPE')
        if ret != 0:
            self.main_obj.gaSet['fail'] = f'"i2c bus" fail'
            return -1
        if re.search(r'Bus 0:\s+i2c@11000', com.buffer) is None:
            self.main_obj.gaSet['fail'] = f'"Bus 0: i2c@11000" does not exist'
            return -1

        ret = com.send('i2c dev 0\r', 'PCPE')
        if ret != 0:
            self.main_obj.gaSet['fail'] = f'"i2c dev 0" fail'
            return -1
        ret = com.send('i2c probe\r', 'PCPE')
        if ret != 0:
            self.main_obj.gaSet['fail'] = f'"i2c probe" fail'
            return -1
        if re.search(r'20 21', com.buffer) is None:
            self.main_obj.gaSet['fail'] = f'"20 21" does not exist'
            return -1
        if re.search(r'7E 7F', com.buffer) is None:
            self.main_obj.gaSet['fail'] = f'"7E 7F" does not exist'
            return -1

        com.send('i2c mw 0x52 0.2 0xaa 0x1\r', 'PCPE')
        ret = com.send('i2c md 0x52 0.2 0x20\r', 'PCPE')
        if ret != 0:
            self.main_obj.gaSet['fail'] = f'"i2c md" fail'
        if re.search(r'0000: aa', com.buffer) is None:
            self.main_obj.gaSet['fail'] = f'"0000: aa" does not exist'
            return -1

        com.send('i2c mw 0x52 0.2 0xbb 0x1\r', 'PCPE')
        ret = com.send('i2c md 0x52 0.2 0x20\r', 'PCPE')
        if ret != 0:
            self.main_obj.gaSet['fail'] = f'"i2c md" fail'
        if re.search(r'0000: bb', com.buffer) is None:
            self.main_obj.gaSet['fail'] = f'"0000: bb" does not exist'
            return -1

        return ret

    def brd_eeprom_perform(self):
        # self.gaSet['puts_log'].info(f'{inspect.stack()[0][3].upper()}')
        print(f'{lgen.my_time()} {inspect.stack()[0][3].upper()}')
        com = 'comDut'
        ret = self.login_2_linux()
        print(f'brd_eeprom_perform ret after login_2_linux:{ret}')
        if ret != 0:
            ret = self.login()
            print(f'brd_eeprom_perform ret after login:{ret}')
            if ret != 0:
                return ret

        ret = self.build_eeprom_string("new_uut")
        print(f"brd_eeprom_perform (self.gaSet['eeprom'])")
        if ret != 0:
            return ret

        return ret

    def build_eeprom_string(self, mode):
        self.gaSet['eeprom'] = {}
        # self.gaSet['puts_log'].info(f'{inspect.stack()[0][3].upper()}')
        print(f'{lgen.my_time()} {inspect.stack()[0][3].upper()}')
        # self.gaSet['puts_log'].info(self.gaSet['dut_fam'])
        lgen.print_gaSet('build_eeprom_string:', self.gaSet, "dut_fam")

        if self.gaSet['dut_fam']['cell']['qty'] == 0 and self.gaSet['dut_fam']['wifi'] == 0:
            # no modems, no wifi
            self.gaSet['eeprom']['mod1man'] = ""
            self.gaSet['eeprom']['mod1type'] = ""
            self.gaSet['eeprom']['mod2man'] = ""
            self.gaSet['eeprom']['mod2type'] = ""
        elif self.gaSet['dut_fam']['cell']['qty'] == 1 and self.gaSet['dut_fam']['wifi'] == 0 and \
                self.gaSet['dut_fam']['lora']['lora'] == 0:
            # just modem 1, no modem 2 and no wifi
            self.gaSet['eeprom']['mod1man'] = self.mod_man(self.gaSet['dut_fam']['cell']['cell'])
            self.gaSet['eeprom']['mod1type'] = self.mod_type(self.gaSet['dut_fam']['cell']['cell'])
            self.gaSet['eeprom']['mod2man'] = ""
            self.gaSet['eeprom']['mod2type'] = ""
        elif self.gaSet['dut_fam']['cell']['qty'] == 1 and self.gaSet['dut_fam']['wifi'] == 'WF':
            # modem 1 and wifi instead of modem 2
            self.gaSet['eeprom']['mod1man'] = self.mod_man(self.gaSet['dut_fam']['cell']['cell'])
            self.gaSet['eeprom']['mod1type'] = self.mod_type(self.gaSet['dut_fam']['cell']['cell'])
            self.gaSet['eeprom']['mod2man'] = self.mod_man('wifi')
            self.gaSet['eeprom']['mod2type'] = self.mod_type('wifi')
        elif self.gaSet['dut_fam']['cell']['qty'] == 0 and self.gaSet['dut_fam']['wifi'] == 'WF':
            # no modem 1 and wifi instead of modem 2
            self.gaSet['eeprom']['mod1man'] = ""
            self.gaSet['eeprom']['mod1type'] = ""
            self.gaSet['eeprom']['mod2man'] = self.mod_man('wifi')
            self.gaSet['eeprom']['mod2type'] = self.mod_type('wifi')
        elif self.gaSet['dut_fam']['cell']['qty'] == 2:
            #  two modems are installed
            self.gaSet['eeprom']['mod1man'] = self.mod_man(self.gaSet['dut_fam']['cell']['cell'])
            self.gaSet['eeprom']['mod1type'] = self.mod_type(self.gaSet['dut_fam']['cell']['cell'])
            self.gaSet['eeprom']['mod2man'] = self.mod_man(self.gaSet['dut_fam']['cell']['cell'])
            self.gaSet['eeprom']['mod2type'] = self.mod_type(self.gaSet['dut_fam']['cell']['cell'])
        elif self.gaSet['dut_fam']['cell']['qty'] == 1 and self.gaSet['dut_fam']['lora']['lora'] != 0:
            # modem 1 and LoRa instead of modem 2
            self.gaSet['eeprom']['mod1man'] = self.mod_man(self.gaSet['dut_fam']['cell']['cell'])
            self.gaSet['eeprom']['mod1type'] = self.mod_type(self.gaSet['dut_fam']['cell']['cell'])
            self.gaSet['eeprom']['mod2man'] = self.mod_man('lora')
            self.gaSet['eeprom']['mod2type'] = self.mod_type('lora')

        if mode == "new_uut":
            ret = self.get_mac(1)
            if ret == -1 or ret == -2:
                return ret
            mac = ret
        else:
            mac = "no mac"
        self.gaSet['eeprom']['mac'] = mac

        part_number = self.gaSet['dutFullName'].replace(r'\.', "/")

        if self.gaSet['dut_fam']['ps'] == "12V":
            self.gaSet['eeprom']['ps'] = "WDC-12V"
        elif self.gaSet['dut_fam']['ps'] == "48V":
            self.gaSet['eeprom']['ps'] = "DC-48V"
        elif self.gaSet['dut_fam']['ps'] == "WDC":
            self.gaSet['eeprom']['ps'] = "WDC-20-60V"
        elif self.gaSet['dut_fam']['ps'] == "ACEX":
            self.gaSet['eeprom']['ps'] = "12V"
        elif self.gaSet['dut_fam']['ps'] == "DC":
            self.gaSet['eeprom']['ps'] = "12V"

        if self.gaSet['dut_fam']['serPort'] == 0:
            ser_1 = ""
            ser_2 = ""
            rs485_1 = ""
            rs485_2 = ""
            cts_2 = ""
        elif self.gaSet['dut_fam']['serPort'] == '2RS':
            ser_1 = "RS232"
            ser_2 = "RS232"
            rs485_1 = ""
            rs485_2 = ""
            cts_2 = "YES"
        elif self.gaSet['dut_fam']['serPort'] == '2RSM':
            ser_1 = "RS232"
            ser_2 = "RS485"
            rs485_1 = ""
            rs485_2 = "2W"
            cts_2 = "YES"
        elif self.gaSet['dut_fam']['serPort'] == '1RS':
            ser_1 = "RS232"
            ser_2 = ""
            rs485_1 = ""
            rs485_2 = ""
            cts_2 = ""
        self.gaSet['eeprom']['ser_1'] = ser_1
        self.gaSet['eeprom']['ser_2'] = ser_2
        self.gaSet['eeprom']['rs485_1'] = rs485_1
        self.gaSet['eeprom']['rs485_2'] = rs485_2

        if self.gaSet['dut_fam']['poe'] == '0':
            self.gaSet['eeprom']['poe'] = ""
        elif self.gaSet['dut_fam']['poe'] == '2PA':
            self.gaSet['eeprom']['poe'] = "2PA"
        elif self.gaSet['dut_fam']['poe'] == 'POE':
            self.gaSet['eeprom']['poe'] = "POE"

        if mode == 'new_uut':
            txt = 'aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeeeaaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeeeddeeeeeeeeeeaaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeeeaaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeeeaaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeeeaaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeeeaaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeeeaaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeeeaaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeeeaaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeee'
            txt += f"MODEM_1_MANUFACTURER={self.gaSet['eeprom']['mod1man']},"
            txt += f"MODEM_2_MANUFACTURER={self.gaSet['eeprom']['mod2man']},"
            txt += f"MODEM_1_TYPE={self.gaSet['eeprom']['mod1type']},"
            txt += f"MODEM_2_TYPE={self.gaSet['eeprom']['mod2type']},"
            txt += f"MAC_ADDRESS={self.gaSet['eeprom']['mac']},"
            txt += f"MAIN_CARD_HW_VERSION={self.gaSet['mainHW']},"
            txt += f"SUB_CARD_1_HW_VERSION=,"
            txt += f"CSL={self.gaSet['csl']},"
            txt += f"PART_NUMBER={part_number},"
            txt += f"PCB_MAIN_ID={self.gaSet['mainPcbId']},"
            txt += f"PCB_SUB_CARD_1_ID=,"
            txt += f"PS={self.gaSet['eeprom']['ps']},"
            txt += f"SD_SLOT=YES,"
            txt += f"SERIAL_1={self.gaSet['eeprom']['ser_1']},"
            txt += f"SERIAL_2={self.gaSet['eeprom']['ser_2']},"
            txt += f"SERIAL_1_CTS_DTR=YES,"
            txt += f"SERIAL_2_CTS_DTR={cts_2},"
            txt += f"RS485_1={rs485_1},"
            txt += f"RS485_2={rs485_2},"
            txt += f"DRY_CONTACT=2_2,"
            if self.gaSet['dut_fam']['wanPorts'] == '4U2S':
                txt += f"NNI_WAN_1=FIBER,"
                txt += f"NNI_WAN_2=FIBER,"
                txt += f"LAN_3_4=YES,"
            elif self.gaSet['dut_fam']['wanPorts'] == '2U':
                txt += f"NNI_WAN_1=,"
                txt += f"NNI_WAN_2=,"
                txt += f"LAN_3_4=,"
            txt += f"LIST_REF=0.0,"
            txt += f"END="

            # self.gaSet['puts_log'].info(f'build_eeprom_string txt:_{txt}_')
            print(f'{lgen.my_time()} build_eeprom_string txt:_{txt}_')
            self.gaSet['file_log'].info(f'{txt}')

            eep_file = 'c:\\download\\etx1p\\eeprom.cnt'
            if os.path.exists(eep_file) is True:
                os.remove(eep_file)
                time.sleep(0.5)

            with open(eep_file, 'w') as fi:
                fi.write(txt)

        return 0

    def mod_man(self, cell):
        if cell == "HSR" or "L1" or "L2" or "L3" or "L4":
            return 'QUECTEL'
        elif cell == "wifi":
            return 'AAZUREWAVE'
        elif cell == 'lora':
            return 'RAK'

    def mod_type(self, cell):
        if cell == "HSR":
            return 'UC20'
        elif cell == "L1":
            return 'EC25-E'
        elif cell == "L2":
            return 'EC25-A'
        elif cell == "L3":
            return 'EC25-AU'
        elif cell == "L4":
            return 'EC25-AFFD'
        elif cell == "wifi":
            return 'AW-CM276MA'
        elif cell == 'lora':
            return 'RAK-2247'

    def get_mac(self, qty):
        # self.gaSet['puts_log'].info(f'{inspect.stack()[0][3].upper()}')
        print(f'{lgen.my_time()} {inspect.stack()[0][3].upper()}')
        com = 'comDut'
        ret = self.login_2_linux()
        if ret != 0:
            return ret

        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.5)
        ret = lgen.my_send(self.gaSet, com, 'cat /USERFS/eeprom/MAC_ADDRESS\r', '/\]\#')
        if ret != 0:
            return ret
        if re.search('command not found', rlcom.buffer) is not None:
            ret = lgen.my_send(self.gaSet, com, 'cat /USERFS/eeprom/MAC_ADDRESS\r', '/\]\#')
            if ret != 0:
                return ret

        bb = re.sub(r'\s+', " ", rlcom.buffer)
        print(f'get_mac bb:_{bb}_')
        # for ch in bbb:
        #     print(ch, {ord(ch)})
        m = re.search(r'ADDRESS\s+([0-9A-F:]+)', bb)
        print(f'get_mac m:_{m}_ _{m[1].upper()}_')
        if m is None:
            dut_mac = "EmptyEEPROM"
            # self.gaSet['puts_log'].info(f'GetMac No User_eeprom')
            print(f'{lgen.my_time()} GetMac No User_eeprom')
        else:
            dut_mac = m[1].upper()  # ab:12:cd:34:ef:56 -> AB:12:CD:34:EF:56
            # self.gaSet['puts_log'].info(f'get_mac mac_match:{m[1]}, dut_mac:{dut_mac}')
            print(f'{lgen.my_time()} get_mac mac_match:{m[1]}, dut_mac:{dut_mac}')

        # self.gaSet['puts_log'].info(f'GetMac dut_mac:{dut_mac}')
        print(f'{lgen.my_time()} GetMac dut_mac:{dut_mac}')

        if dut_mac != 'EmptyEEPROM':
            return dut_mac
        else:
            # self.gaSet['puts_log'].info(f'GetMac MACServer.exe')
            print(f'{lgen.my_time()} GetMac MACServer.exe')
            state, mac = Lib_RadApps.macserver(10)
            if state is False:
                self.gaSet['fail'] = mac
                return -1
            # AB12CD34EF56 -> AB:12:CD:34:EF:56
            mac = ':'.join(format(s, '02x') for s in bytes.fromhex(mac)).upper()
            return mac

    def id_perform(self, mode):
        gen_obj = lgen.Gen(self.main_obj)
        # print(f'{lgen.Gen.my_time(lgen)} {inspect.stack()[0][3].upper()}')
        print(f'{gen_obj.my_time()} {inspect.stack()[0][3].upper()}')
        com = self.main_obj.gaSet['com_obj']
        ret = self.login()
        print(f'ret of login:{ret}')
        if ret == 'PowerOffOn':
            gen_obj.power(self.main_obj, 1, 0)
            time.sleep(4)
            gen_obj.power(self.main_obj, 1, 1)
            ret = self.login()

        if ret != 0:
            return ret

        ret = self.login_2_linux()
        if ret != 0:
            return ret

        com.send('\r', 'stam', 0.5)
        ret = com.send('cat /USERFS/eeprom/MAC_ADDRESS\r', '/\]\#')
        if ret != 0:
            return ret
        if re.search('command not found', com.buffer):
            ret = com.send('cat /USERFS/eeprom/MAC_ADDRESS\r', '/\]\#')
            if ret != 0:
                return ret

        bb = re.sub(r'\s+', " ", com.buffer)
        print(f'id_perform bb:_{bb}_')
        m = re.search(r'ADDRESS\s+([0-9A-F:]+)', bb)
        if m is None:
            dut_mac = "EmptyEEPROM"
            print(f'id_perform No User_eeprom')
        else:
            eeprom_mac = m[1]
            dut_mac = re.sub(r':+', "", m[1]).upper()  # ab:12:cd:34:ef:56 -> AB12CD34EF56
            self.main_obj.gaSet['mac'] = dut_mac
            print(f'get_mac mac_match:{m[1]}, dut_mac:{dut_mac}')

        ret = com.send('exit\r', '#')
        if ret != 0:
            return ret

        if mode == 'read_mac':
            return ret

        if dut_mac[:6] != "1806F5":
            if m is None:
                self.main_obj.gaSet['fail'] = "MAC Address is empty"
            else:
                self.main_obj.gaSet['fail'] = f"MAC Address is \'{m[1]}\'. It's out of RAD range"
            return -1

        ret = com.send('configure system\r', 'system#')
        if ret != 0:
            self.main_obj.gaSet['fail'] = "Configure System fail"
            return -1
        ret = com.send('show device-information\r', 'Engine Time')
        if ret != 0:
            self.main_obj.gaSet['fail'] = "Show device-information fail"
            return -1

        text = "".join([s for s in com.buffer.splitlines(True) if s.strip("\r\n")])
        # lgen.Gen.add_to_log(lgen.Gen, self.main_obj, text)
        gen_obj.add_to_log(self.main_obj, text)

        m = re.search(r'Sw:\s+([\d\.]+)\s', com.buffer)
        if m is None:
            self.main_obj.gaSet['fail'] = "Read Sw fail"
            return -1
        uut_sw = m[1].strip()
        print(f"gaSet['sw_app']:{self.main_obj.gaSet['sw_app']} uut_sw:{uut_sw}")
        if uut_sw != self.main_obj.gaSet['sw_app']:
            self.main_obj.gaSet['fail'] = f"The SW is \'{uut_sw}\'. Should be \'{self.main_obj.gaSet['sw_app']}\'"
            return -1

        m = re.search(r'Name\s+:\s+([a-zA-Z\d\-]+)\s', com.buffer)
        if m is None:
            self.main_obj.gaSet['fail'] = "Read Name fail"
            return -1
        uut_nam = m[1].strip()
        print(f"uut_nam:{uut_nam}")
        if uut_nam != "SF-1p":
            self.main_obj.gaSet['fail'] = f"The Name is \'{uut_nam}\'. Should be \'SF-1p\'"
            return -1

        m = re.search(r'Model\s+:\s+([a-zA-Z\d\-_\s]+)\s', com.buffer)
        if m is None:
            self.main_obj.gaSet['fail'] = "Read Model fail"
            return -1
        uut_model = m[1].strip()
        # print(f"{lgen.Gen.my_time(lgen)} uut_model:<{uut_model}>")
        # uut_model = uut_model.replace('_', '/')
        mainHW = self.main_obj.gaSet['mainHW']
        print(f"General uut_model:<{uut_model}> mainHW:{mainHW}")

        if (self.main_obj.gaSet['wanPorts'] == '4U2S' or self.main_obj.gaSet['wanPorts'] == '5U1S') \
                and mainHW < 0.6 and not re.search('SF-1P superset', uut_model):
            self.main_obj.gaSet['fail'] = f"The Model is \'{uut_model}\'. Should be \'SF-1P superset\'"
            return -1
        elif (self.main_obj.gaSet['wanPorts'] == '4U2S' or self.main_obj.gaSet['wanPorts'] == '5U1S') \
                and mainHW >= 0.6 and not re.search('SF-1P superset CP_2', uut_model):
            self.main_obj.gaSet['fail'] = f"The Model is \'{uut_model}\'. Should be \'SF-1P superset CP_2\'"
            return -1
        elif self.main_obj.gaSet['wanPorts'] == '2U' and not re.search('SF-1P', uut_model):
            self.main_obj.gaSet['fail'] = f"The Model is \'{uut_model}\'. Should be \'SF-1P\'"
            return -1
        elif self.main_obj.gaSet['wanPorts'] == '1SFP1UTP' and not re.search('ETX-1P', uut_model):
            self.main_obj.gaSet['fail'] = f"The Model is \'{uut_model}\'. Should be \'ETX-1P\'"
            return -1

        m = re.search(r'Address\s+:\s+([A-F\d\-]+)\s', com.buffer)
        if m is None:
            self.main_obj.gaSet['fail'] = "Read MAC Address fail"
            return -1
        uut_mac = m[1].strip()
        print(f"uut_mac:{uut_mac}")
        u0_mac = uut_mac.replace('-', ':')
        print(f"uut_mac:{uut_mac} u0_mac:{u0_mac} eeprom_mac:{eeprom_mac}")
        if u0_mac != eeprom_mac:
            mac_minus1 = hex(int(uut_mac.replace('-', ''), base=16) - 1).upper()[
                         2:]  # 18:06:F5:E2:4B:B3 -> 1806F5E24BB2
            uut_mac = ':'.join(mac_minus1[i:i + 2] for i in range(0, 12, 2))  # 18:06:F5:E2:4B:B2
            print(f"uut_mac:{uut_mac} eeprom_mac:{eeprom_mac}")
            if uut_mac != eeprom_mac:
                self.main_obj.gaSet['fail'] = f"The MAC is \'{uut_mac}\'. Should be \'{eeprom_mac}\'"
                return -1

        ret = com.send('show summary-inventory\r', 'CPU')
        if ret != 0:
            self.main_obj.gaSet['fail'] = "Show summary-inventory fail"
            return -1

        text = "".join([s for s in com.buffer.splitlines(True) if s.strip("\r\n")])
        gen_obj.add_to_log(self.main_obj, text)
        m = re.search(r'\.\d+\s+([\w\-/]+)\s', com.buffer)
        if m is None:
            self.main_obj.gaSet['fail'] = "Read FW Ver fail"
            return -1
        mrkt = self.main_obj.gaSet['mrkt_name']
        fw_ver = m.group(1)
        print(f'sum_inv fw_ver:<{fw_ver}> mrkt:<{mrkt}>')
        if mrkt != fw_ver:
            self.main_obj.gaSet['fail'] = f"The FW Ver is \'{fw_ver}\'. Should be \'{mrkt}\'"
            return -1

        return 0

    def power_off_on_perf(self):
        gen_obj = lgen.Gen(self.main_obj)
        print(f'{gen_obj.my_time()} {inspect.stack()[0][3].upper()}')
        com = self.main_obj.gaSet['com_obj']

        for i in range(1, 3):
            gen_obj.power(self.main_obj, 1, 0)
            self.main_obj.my_statusbar.sstatus(f"Power OFF {i}")
            time.sleep(4)
            gen_obj.power(self.main_obj, 1, 1)
            self.main_obj.my_statusbar.sstatus(f"Power ON {i}")
            com.send("\r", 'stam', 2)

            buffer = com.buffer
            print(f'buffer_len:<{len(buffer)}>')
            if len(buffer) > 100:
                ret = 0
            else:
                self.main_obj.gaSet['fail'] = f"UUT doesn't respond after {i} OFF-ON"
                ret = -1
                break

        return ret

    def dry_contact_perf(self):
        gen_obj = lgen.Gen(self.main_obj)
        print(f'{gen_obj.my_time()} {inspect.stack()[0][3].upper()}')
        com = self.main_obj.gaSet['com_obj']
        ret = self.login()
        print(f'ret of login:{ret}')
        if ret == 0:
            ret = self.login_2_linux()
            print(f'ret of login_2_linux:{ret}')
        if ret == 0:
            ret = self.dry_contact_config()
            print(f'ret of dry_contact_config:{ret}\n')

        if ret == 0:
            for gr2st, gr1st, sb in zip([0, 1, 0, 1], [0, 0, 1, 1], ['00', '10', '11', '11']):
                gen_obj.mux_switch_box(self.main_obj, 1, gr1st)
                gen_obj.mux_switch_box(self.main_obj, 2, gr2st)
                time.sleep(0.25)
                com.send(f'cat $DC_IN1_DIR/value > $DC_OUT1_DIR/value\r', 'stam', 0.2)
                com.send(f'cat $DC_IN1_DIR/value\r', 'stam', 0.2)
                com.send(f'cat $DC_OUT1_DIR/value\r', 'stam', 0.2)
                com.send(f'cat $DC_IN2_DIR/value > $DC_OUT2_DIR/value\r', 'stam', 0.2)
                com.send(f'cat $DC_IN2_DIR/value\r', 'stam', 0.2)
                com.send(f'cat $DC_OUT2_DIR/value\r', 'stam', 0.2)
                time.sleep(0.25)
                buffer = gen_obj.read_pio(self.main_obj, 7)[6:]
                print(f"dry_contact_perf after gr2st:{gr2st} gr1st:{gr1st} buffer:{buffer} sb:{sb}\n")
                if buffer != sb:
                    self.main_obj.gaSet['fail'] = f'I/O Alarm is {buffer}. Should be {sb}'
                    ret = -1
                    break

        return ret

    def dry_contact_config(self):
        print(f'{lgen.Gen.my_time(lgen)} {inspect.stack()[0][3].upper()}')
        com = self.main_obj.gaSet['com_obj']
        ret = 0
        com.send('cd / \r', 'stam', 0.1)

        print(f"mainHW:{self.main_obj.gaSet['mainHW']}")
        if self.main_obj.gaSet['mainHW'] < 0.6:
            scr = 'dry2in2out.2021.sh'
        else:
            scr = 'dry2in2out.sh'

        print(f'\nDownload dry_contact script:{scr}')
        self.main_obj.my_statusbar.sstatus(f"Download dry_contact script:{scr}")
        with open(scr, 'r') as file:
            for line in file:
                lin = line.rstrip()
                if len(lin) > 0 and lin[0:2] != '#!':
                    com.send(f'{lin}\r', 'stam', 0.2)
                    if re.search('write error', com.buffer):
                        self.main_obj.gaSet['fail'] = "\'write error\' during Config DryContact"
                        ret = -1
                        break

        com.send('\r', 'stam', 0.25)
        return ret

    def read_boot_params(self):
        gen_obj = lgen.Gen(self.main_obj)
        print(f'\n{gen_obj.my_time()} read_boot_params ')
        # ret = self.login()
        # print(f'read_boot_params ret of login:{ret}')
        # if ret != 0:
        #     return ret

        gen_obj.power(1, 0)
        time.sleep(4)
        gen_obj.power(1, 1)

        ret = self.login_2_boot()
        print(f'read_boot_params ret of login_2_boot:{ret}')

        # self.main_obj.my_statusbar.sstatus(f'ShutDown port {port} "{state}"')

        com = self.main_obj.gaSet['com_obj']
        print(f'\nbuffer:<{self.login_buff}>\n')

        dbrBootSwVer = self.main_obj.gaSet['sw_boot'].lstrip('B')
        # m = re.search(f'VER({dbrBootSwVer})', self.login_buff)
        # print(f'm: <{m}>')
        if f'VER{dbrBootSwVer}' not in self.login_buff:
            gen_obj.power(1, 0)
            time.sleep(4)
            gen_obj.power(1, 1)

            ret = self.login_2_boot()
            print(f'read_boot_params ret of login_2_boot:{ret}')
            print(f'\nbuffer:<{self.login_buff}>\n')
            # m = re.search(f'VER({dbrBootSwVer})', self.login_buff)
            if f'VER{dbrBootSwVer}' not in self.login_buff:
                self.main_obj.gaSet['fail'] = f'No "{dbrBootSwVer}" in Boot'
                return -1
        print(f'Boot VER:{dbrBootSwVer}')

        if f'DRAM:  {self.main_obj.gaSet["mem"]} GiB' not in self.login_buff:
            self.main_obj.gaSet['fail'] = f'No DRAM: {self.main_obj.gaSet["mem"]} GiB in Boot'
            return -1
        print(f'DRAM:  {self.main_obj.gaSet["mem"]} GiB')

        if 'HL' in self.main_obj.gaSet['dbr_name']:
            com.send('printenv fdt_name\r', 'PCPE')
            if 'armada-3720-SF1p_superSet_hl.dtb' not in com.buffer:
                self.main_obj.gaSet['fail'] = f'No "armada-3720-SF1p_superSet_hl.dtb" in Boot'
                return -1

        return 0

    def hl_security_perf(self):
        gen_obj = lgen.Gen(self.main_obj)
        print(f'\nhl_security_perf')
        com = self.main_obj.gaSet['com_obj']
        # print(f'\nbuffer:<{self.login_buff}>\n')
        # self.main_obj.my_statusbar.sstatus(f'ShutDown port {port} "{state}"')

        ret = self.login()
        print(f'hl_security_perf ret of login:{ret}')
        if ret == 0:
            ret = self.login_2_linux()
            print(f'ret of login_2_linux:{ret}')
        if ret == 0:
            self.main_obj.my_statusbar.sstatus(f'Read Docker')
            com.send("cd /USERFS/docker/internal\r", 'stam', 1)
            com.send("docker load -i gateway-mfr-rs.tar\r", "Loaded image")
            if re.search('no such file or directory', com.buffer):
                self.main_obj.gaSet['fail'] = 'Load gateway-mfr-rs.tar tp Docker Fail'
                ret = -1

            if ret == 0:
                com.send(
                    "docker run --rm -it --privileged gateway-mfr-rs:latest /gateway_mfr --device ecc://i2c-5:0xc0?slot=0 provision\r",
                    'stam', 3)
                if re.search('Error', com.buffer):
                    self.main_obj.gaSet['fail'] = 'Check INFO returns Error'
                    ret = -1

        return ret

    def cellularLte_RadOS_Sim12(self):
        gen_obj = lgen.Gen(self.main_obj)
        com = self.main_obj.gaSet['com_obj']
        l4 = 0
        if 'L4' in self.main_obj.gaSet['cellType']:
            l4 = 1
        print(f'\ncellularLte_RadOS_Sim12 L4:{l4}')

        ret = self.login()
        print(f'cellularLte_RadOS_Sim12 ret of login:{ret}')
        if ret == 0:
            self.main_obj.my_statusbar.sstatus(f'Configuration Cellular')
            ret = com.send("exit all\r", "-1p")
            ret = com.send("configure\r", "-1p>conf")
        if ret == 0:
            ret = com.send("port\r", "fig>port")
        if ret == 0:
            ret = com.send("cellular lte\r", "\(lte\)")
        if ret == 0:
            ret = com.send("sim 1\r", "\(1\)")
        if ret == 0:
            ret = com.send('apn-name "statreal"\r', "\(1\)")
        if l4 == 1:
            if ret == 0:
                ret = com.send('pdp-type relayed-ppp\r', "\(1\)")
        if ret == 0:
            ret = com.send("exit\r", "\(lte\)")
        if ret == 0:
            ret = com.send("sim 2\r", "\(2\)")
        if ret == 0:
            ret = com.send('apn-name "statreal"\r', "\(2\)")
        if l4 == 1:
            if ret == 0:
                ret = com.send('pdp-type relayed-ppp\r', "\(2\)")

        if ret == 0:
            ret = com.send("exit all\r", "-1p")
        if ret == 0:
            ret = com.send("configure\r", "-1p")
        if ret == 0:
            ret = com.send("router 1\r", "er\(1\)")
        if ret == 0:
            ret = com.send("interface 1\r", "ace\(1\)")
        if ret == 0:
            ret = com.send("shutdown\r", "ace\(1\)")
        if ret == 0:
            ret = com.send("bind cellular lte\r", "ace\(1\)")
        if l4 == 1:
            if ret == 0:
                ret = com.send('no shutdown\r', "ace\(1\)")
        else:
            if ret == 0:
                ret = com.send('dhcp\r', "ace\(1\)")
            if ret == 0:
                ret = com.send('dhcp-client\r', "ace\(1\)")
            if ret == 0:
                ret = com.send('client-id mac\r', "ace\(1\)")
            if ret == 0:
                ret = com.send("exit\r", "er\(1\)")
                ret = com.send("no shutdown\r", "er\(1\)")
        if ret != 0:
            self.main_obj.gaSet['fail'] = "Configuration Cellular Lte fail"

        return ret

    def cellularModemPerf_RadOS_Sim12(self, act_sim):
        print(f'\ncellularModemPerf_RadOS_Sim12 act_sim:{act_sim}')
        buf = ''
        gen_obj = lgen.Gen(self.main_obj)
        com = self.main_obj.gaSet['com_obj']
        ret = self.login()
        print(f'cellularModemPerf_RadOS_Sim12 ret of login:{ret}')
        if ret == 0:
            self.main_obj.my_statusbar.sstatus(f'Configuration Mode to SIM-{act_sim}')
            ret = gen_obj.com_send("exit all\r", "-1p")
            ret = gen_obj.com_send("configure\r", "-1p>conf")
        if ret == 0:
            ret = gen_obj.com_send("port\r", "fig>port")
        if ret == 0:
            ret = gen_obj.com_send("cellular lte\r", "\(lte\)")
        if ret == 0:
            ret = gen_obj.com_send("shutdown\r", "\(lte\)")
        if ret == 0:
            ret = gen_obj.wait(self.main_obj, "Wait for LTE shutdown", 10, 'white')
        if ret == 0:
            ret = gen_obj.com_send(f"mode sim {act_sim}\r", "\(lte\)")
        if ret == 0:
            ret = gen_obj.com_send("no shutdown\r", "\(lte\)")
        if ret != 0:
            self.main_obj.gaSet['fail'] = f"Config Mode to SIM-{act_sim} fail"

        for i in range(1, 36):
            self.main_obj.gaSet['root'].update()
            self.main_obj.my_statusbar.sstatus(f'Read SIM-{act_sim} status ({i})')
            buf = ''
            ret = gen_obj.com_send("show status\r", "stam", 2)
            buf += com.buffer
            if ret == -2:
                return -2
            ret = gen_obj.com_send("\r", "stam", 2)
            buf += com.buffer
            if ret == -2:
                return -2
            ret = gen_obj.com_send("\r", "stam", 2)
            buf += com.buffer
            if ret == -2:
                return -2
            ret = gen_obj.com_send("\r", "stam", 2)
            buf += com.buffer
            if ret == -2:
                return -2
            ret = gen_obj.com_send("\r", "\(lte\)")
            buf += com.buffer
            if ret == -2:
                return -2

            print(f'\ni:<{i}>, buf:<{buf}>\n')
            m = re.search(r'Operationa?l? Status\s+:\s+(\w+)', buf)
            if not m:
                self.main_obj.gaSet['fail'] = f"Read Operational Status of SIM-{act_sim} fail"
                ret = -1
                break
            op_stat = m.group(1)

            m = re.search(r'Mode\s+:\s+(sim-\d)', buf)
            if not m:
                self.main_obj.gaSet['fail'] = f"Read Mode of SIM-{act_sim}fail"
                ret = -1
                break
            mode = m.group(1)

            m = re.search(r'Cellular network connection\s+:\s+(\w+)', buf)
            if not m:
                self.main_obj.gaSet['fail'] = f"Read Cellular network connection of SIM-{act_sim} fail"
                ret = -1
                break
            cel_conn = m.group(1)

            m = re.search(r'Administrative Status\s+:\s+(\w+)', buf)
            if not m:
                self.main_obj.gaSet['fail'] = f"Read Administrative Status of SIM-{act_sim} fail"
                ret = -1
                break
            adm_stat = m.group(1)

            m = re.search(r'RSSI \(dBm\)\s+:\s+([\-\d]+)', buf)
            if not m:
                self.main_obj.gaSet['fail'] = f"Read RSSI of SIM-{act_sim} fail"
                ret = -1
                break
            rssi = int(m.group(1))

            m = re.search(r'SIM Status\s+:\s+(\w+)', buf)
            if not m:
                self.main_obj.gaSet['fail'] = f"Read SIM Status of SIM-{act_sim} fail"
                ret = -1
                break
            sim_stat = m.group(1)

            print(f'\n({i}) op_stat:{op_stat} mode:{mode} cel_conn:{cel_conn} adm_stat:{adm_stat} '
                  f'rssi:{rssi} sim_stat:{sim_stat}')
            if op_stat == 'Up' and mode == f'sim-{act_sim}' and cel_conn == 'Connected' and -75 < rssi < -50 \
                    and sim_stat == 'ready':
                ret = 0
                break
            else:
                time.sleep(3)

        gen_obj.add_to_log(self.main_obj, f"Operational Status: {op_stat}")
        gen_obj.add_to_log(self.main_obj, f"Mode: {mode}")
        gen_obj.add_to_log(self.main_obj, f"Cellular network connection: {cel_conn}")
        gen_obj.add_to_log(self.main_obj, f"RSSI: {rssi}")
        gen_obj.add_to_log(self.main_obj, f"SIM Status: {sim_stat}")
        if op_stat != "Up":
            self.main_obj.gaSet['fail'] = f"Operational Status of SIM-{act_sim} is {op_stat}. Should be Up"
            ret = -1
        if ret == 0:
            if mode != f"sim-{act_sim}":
                self.main_obj.gaSet['fail'] = f"Mode of SIM-{act_sim} is {mode}. Should be sim-{act_sim}"
                ret = -1
        if ret == 0:
            if cel_conn != 'Connected':
                self.main_obj.gaSet['fail'] = (f"Cellular network connection of SIM-{act_sim} is {cel_conn}. Should be "
                                               f"Connected")
                ret = -1
        if ret == 0:
            if sim_stat != "ready":
                self.main_obj.gaSet['fail'] = f"SIM Status of SIM-{act_sim} is {sim_stat}. Should be ready"
                ret = -1

        if ret == 0:
            m = re.search(r'Firmware : Revision:\s+(\w+)', buf)
            if not m:
                m = re.search(r'Firmware : Revision:\s+([\w._/]+)', buf)
                if not m:
                    self.main_obj.gaSet['fail'] = f"Read Firmware Revision of SIM-{act_sim} fail"
                    ret = -1
            if m:
                fw_rev = m.group(1)
                fw_rev_rad = self.main_obj.gaSet['fw_dict'][self.main_obj.gaSet['cellType']]
                gen_obj.add_to_log(self.main_obj, f'Firmware : Revision: {fw_rev}')
                print(fw_rev_rad, fw_rev)
                if fw_rev != fw_rev_rad:
                    self.main_obj.gaSet[
                        'fail'] = f"Firmware Revision of SIM-{act_sim} is {fw_rev}. Should be {fw_rev_rad}"
                    ret = -1

        if ret == 0:
            gen_obj.wait(self.main_obj, 'Wait 5 sec for Network', 5)
            for i in range(1, 6):
                self.main_obj.gaSet['root'].update()
                if self.main_obj.gaSet['act'] == 0:
                    return -2
                print(f'Ping try {i}')
                self.main_obj.my_statusbar.sstatus(f'Ping try {i}')
                ret = gen_obj.com_send('ping 8.8.8.8\r', '-1p', 25)
                if ret != 0:
                    self.main_obj.gaSet['fail'] = f"Send ping to 8.8.8.8 from SIM-{act_sim} fail"
                    break
                if '5 packets transmitted. 5 packets received, 0% packet loss' in com.buffer:
                    gen_obj.add_to_log(self.main_obj, 'Ping to 8.8.8.8: 5 packets transmitted. 5 packets received, '
                                                      '0% packet loss')
                    ret = 0
                    break
                else:
                    ret = -1
                    self.main_obj.gaSet['fail'] = f"Send ping to 8.8.8.8 from SIM-{act_sim} fail"
                    time.sleep(10)

        return ret

    def cellularLte_RadOS_Sim12_dual(self):
        gen_obj = lgen.Gen(self.main_obj)
        com = self.main_obj.gaSet['com_obj']
        l4 = 0
        if 'L4' in self.main_obj.gaSet['cellType']:
            l4 = 1
        print(f'\ncellularLte_RadOS_Sim12_dual L4:{l4}')

        ret = self.login()
        print(f'cellularLte_RadOS_Sim12_dual ret of login:{ret}')

        if ret == 0:
            self.main_obj.my_statusbar.sstatus(f'Configuration Cellular')
            ret = gen_obj.com_send("exit all\r", "-1p")
            ret = gen_obj.com_send("configure\r", "-1p>config")
        if ret == 0:
            ret = gen_obj.com_send("port\r", "fig>port")
        if ret == 0:
            ret = gen_obj.com_send("cellular lte-1\r", "\(lte-1\)")
        if ret == 0:
            ret = gen_obj.com_send("sim 1\r", "\(1\)")
        if ret == 0:
            ret = gen_obj.com_send('apn-name \"statreal\"\r', "\(1\)")
        if ret == 0:
            ret = gen_obj.com_send("exit\r", "\(lte-1\)")
        if ret == 0:
            ret = gen_obj.com_send("no shutdown\r", "\(lte-1\)")
        if ret == 0:
            ret = gen_obj.com_send("exit\r", "fig>port")

        if ret == 0:
            ret = gen_obj.com_send("cellular lte-2\r", "\(lte-2\)")
        if ret == 0:
            ret = gen_obj.com_send("sim 1\r", "\(1\)")
        if ret == 0:
            ret = gen_obj.com_send('apn-name \"statreal\"\r', "\(1\)")
        if l4 == 1:
            if ret == 0:
                ret = gen_obj.com_send('pdp-type relayed-ppp\r', "\(1\)")
        if ret == 0:
            ret = gen_obj.com_send("exit\r", "\(lte-2\)")
        if ret == 0:
            ret = gen_obj.com_send("no shutdown\r", "\(lte-2\)")

        if ret == 0:
            ret = gen_obj.com_send("exit all\r", "-1p")
        if ret == 0:
            ret = com.send("configure\r", "-1p")
        if ret == 0:
            ret = com.send("router 1\r", "er\(1\)")
        if ret == 0:
            ret = com.send("interface 1\r", "ace\(1\)")
        if ret == 0:
            ret = com.send("shutdown\r", "ace\(1\)")
        if ret == 0:
            ret = com.send("bind cellular lte-1\r", "ace\(1\)")
        if ret == 0:
            ret = com.send("dhcp\r", "ace\(1\)")
        if ret == 0:
            ret = com.send("dhcp-client\r", "ace\(1\)")
        if ret == 0:
            ret = com.send("client-id mac\r", "ace\(1\)")
        if ret == 0:
            ret = com.send("exit\r", "ace\(1\)")
        if ret == 0:
            ret = com.send("no shutdown\r", "ace\(1\)")
        if ret == 0:
            ret = com.send("exit\r", "er\(1\)")

        if ret == 0:
            ret = com.send("interface 2\r", "ace\(2\)")
        if ret == 0:
            ret = com.send("shutdown\r", "ace\(2\)")
        if ret == 0:
            ret = com.send("bind cellular lte-2\r", "ace\(2\)")
        if ret == 0:
            ret = com.send("dhcp\r", "ace\(2\)")
        if ret == 0:
            ret = com.send("dhcp-client\r", "ace\(2\)")
        if ret == 0:
            ret = com.send("client-id mac\r", "ace\(2\)")
        if ret == 0:
            ret = com.send("exit\r", "ace\(2\)")
        if ret == 0:
            ret = com.send("no shutdown\r", "ace\(2\)")
        if ret == 0:
            ret = com.send("exit all\r", "-1p#")

        # if l4 == 1:
        #     if ret == 0:
        #         ret = com.send('no shutdown\r', "-1p")

        if ret == -2:
            return -2
        if ret != 0:
            self.main_obj.gaSet['fail'] = 'Configuration Cellular Lte fail'
        return ret

    def cellularModemPerf_RadOS_Sim12_dual(self, act_lte):
        print(f'\ncellularModemPerf_RadOS_Sim12_dual act_sim:{act_lte}')
        buf = ''
        gen_obj = lgen.Gen(self.main_obj)
        com = self.main_obj.gaSet['com_obj']
        ret = self.login()
        print(f'cellularModemPerf_RadOS_Sim12_dual ret of login:{ret}')
        if ret == 0:
            self.main_obj.my_statusbar.sstatus(f'Configuration Mode to LTE-{act_lte}')
            ret = gen_obj.com_send("exit all\r", "-1p")
            ret = gen_obj.com_send("configure\r", "-1p>conf")
        if ret == 0:
            ret = gen_obj.com_send(f"port\r", 'fig>port')
        if ret == 0:
            ret = gen_obj.com_send(f"cellular lte-{act_lte}\r", f'-{act_lte}')

        if ret == -2:
            return -2
        if ret != 0:
            self.main_obj.gaSet['fail'] = f'Configuration Mode to LTE-{act_lte} fail'

        for i in range(1, 36):
            self.main_obj.gaSet['root'].update()
            self.main_obj.my_statusbar.sstatus(f'Read LTE-{act_lte} status ({i})')
            buf = ''
            ret = gen_obj.com_send("show status\r", "stam", 2)
            buf += com.buffer
            if ret == -2:
                return -2
            ret = gen_obj.com_send("\r", "stam", 2)
            buf += com.buffer
            if ret == -2:
                return -2
            ret = gen_obj.com_send("\r", "stam", 2)
            buf += com.buffer
            if ret == -2:
                return -2
            ret = gen_obj.com_send("\r", "stam", 2)
            buf += com.buffer
            if ret == -2:
                return -2
            ret = gen_obj.com_send("\r", f'-{act_lte}')
            buf += com.buffer
            if ret == -2:
                return -2

            print(f'\ni:<{i}>, buf:<{buf}>\n')
            m = re.search(r'Operationa?l? Status\s+:\s+(\w+)', buf)
            if not m:
                self.main_obj.gaSet['fail'] = f"Read Operational Status of LTE-{act_lte} fail"
                ret = -1
                break
            op_stat = m.group(1)

            m = re.search(r'Mode\s+:\s+(sim-1)', buf)
            if not m:
                self.main_obj.gaSet['fail'] = f"Read Mode of LTE-{act_lte} fail"
                ret = -1
                break
            mode = m.group(1)

            m = re.search(r'Cellular network connection\s+:\s+(\w+)', buf)
            if not m:
                self.main_obj.gaSet['fail'] = f"Read Cellular network connection of LTE-{act_lte} fail"
                ret = -1
                break
            cel_conn = m.group(1)

            m = re.search(r'Administrative Status\s+:\s+(\w+)', buf)
            if not m:
                self.main_obj.gaSet['fail'] = f"Read Administrative Status of LTE-{act_lte} fail"
                ret = -1
                break
            adm_stat = m.group(1)

            m = re.search(r'RSSI \(dBm\)\s+:\s+([\-\d]+)', buf)
            if not m:
                self.main_obj.gaSet['fail'] = f"Read RSSI of LTE-{act_lte} fail"
                ret = -1
                break
            rssi = int(m.group(1))

            m = re.search(r'SIM Status\s+:\s+(\w+)', buf)
            if not m:
                self.main_obj.gaSet['fail'] = f"Read SIM Status of LTE-{act_lte} fail"
                ret = -1
                break
            sim_stat = m.group(1)

            print(f'\n({i}) op_stat:{op_stat} mode:{mode} cel_conn:{cel_conn} adm_stat:{adm_stat} '
                  f'rssi:{rssi} sim_stat:{sim_stat}')
            if op_stat == 'Up' and mode == f'sim-1' and cel_conn == 'Connected' and -75 < rssi < -50 \
                    and sim_stat == 'ready':
                ret = 0
                break
            else:
                time.sleep(3)

        gen_obj.add_to_log(self.main_obj, f"Operational Status: {op_stat}")
        gen_obj.add_to_log(self.main_obj, f"Mode: {mode}")
        gen_obj.add_to_log(self.main_obj, f"Cellular network connection: {cel_conn}")
        gen_obj.add_to_log(self.main_obj, f"RSSI: {rssi}")
        gen_obj.add_to_log(self.main_obj, f"SIM Status: {sim_stat}")
        if op_stat != "Up":
            self.main_obj.gaSet['fail'] = f"Operational Status of LTE-{act_lte} is {op_stat}. Should be Up"
            ret = -1
        if ret == 0:
            if mode != f"sim-1":
                self.main_obj.gaSet['fail'] = f"Mode of LTE-{act_lte} is {mode}. Should be sim-1"
                ret = -1
        if ret == 0:
            if cel_conn != 'Connected':
                self.main_obj.gaSet['fail'] = (f"Cellular network connection of LTE-{act_lte} is {cel_conn}. Should be "
                                               f"Connected")
                ret = -1
        if ret == 0:
            if sim_stat != "ready":
                self.main_obj.gaSet['fail'] = f"SIM Status of LTE-{act_lte} is {sim_stat}. Should be ready"
                ret = -1

        if ret == 0:
            m = re.search(r'Firmware : Revision:\s+(\w+)', buf)
            if not m:
                m = re.search(r'Firmware : Revision:\s+([\w._/]+)', buf)
                if not m:
                    self.main_obj.gaSet['fail'] = f"Read Firmware Revision of LTE-{act_lte} fail"
                    ret = -1
            if m:
                fw_rev = m.group(1)
                fw_rev_rad = self.main_obj.gaSet['fw_dict'][self.main_obj.gaSet['cellType']]
                gen_obj.add_to_log(self.main_obj, f'Firmware : Revision: {fw_rev}')
                print(fw_rev_rad, fw_rev)
                if fw_rev != fw_rev_rad:
                    self.main_obj.gaSet[
                        'fail'] = f"Firmware Revision of LTE-{act_lte} is {fw_rev}. Should be {fw_rev_rad}"
                    ret = -1

        if ret == 0:
            gen_obj.wait(self.main_obj, 'Wait 5 sec for Network', 5)
            for i in range(1, 6):
                self.main_obj.gaSet['root'].update()
                if self.main_obj.gaSet['act'] == 0:
                    return -2
                print(f'Ping try {i}')
                self.main_obj.my_statusbar.sstatus(f'Ping try {i}')
                ret = gen_obj.com_send('ping 8.8.8.8\r', '-1p', 25)
                if ret != 0:
                    self.main_obj.gaSet['fail'] = f"Send ping to 8.8.8.8 from LTE-{act_lte} fail"
                    break
                if '5 packets transmitted. 5 packets received, 0% packet loss' in com.buffer:
                    gen_obj.add_to_log(self.main_obj, 'Ping to 8.8.8.8: 5 packets transmitted. 5 packets received, '
                                                      '0% packet loss')
                    ret = 0
                    break
                else:
                    ret = -1
                    self.main_obj.gaSet['fail'] = f"Send ping to 8.8.8.8 from LTE-{act_lte} fail"
                    time.sleep(10)

        if ret == 0 and act_lte == 2:
            ret = self.login_2_linux()
            print(f'cellularModemPerf_RadOS_Sim12_dual ret of login_2_linux:{ret}')
            if ret == 0:
                for wwan in ['wwan0', 'wwan1']:
                    for i in range(1, 6):
                        self.main_obj.gaSet['root'].update()
                        if self.main_obj.gaSet['act'] == 0:
                            return -2
                        print(f'Ping from {wwan} try {i}')
                        self.main_obj.my_statusbar.sstatus(f'Ping try {i}')
                        ret = gen_obj.com_send(f'ping 8.8.8.8 -I {wwan} -c 5\r', '/]#', 25)
                        if ret != 0:
                            self.main_obj.gaSet['fail'] = f"Send ping to 8.8.8.8 from {wwan} fail"
                            break
                        if '5 packets transmitted, 5 received, 0% packet loss' in com.buffer:
                            gen_obj.add_to_log(self.main_obj,
                                               f'Ping to 8.8.8.8 from {wwan} : 5 packets transmitted, 5 received, 0% packet loss')
                            ret = 0
                            break
                        else:
                            ret = -1
                            self.main_obj.gaSet['fail'] = f"Send ping to 8.8.8.8 from {wwan} fail"
                            time.sleep(1)

        return ret

    def data_transmission_setup(self):
        print(f'\ndata_transmission_setup')
        gen_obj = lgen.Gen(self.main_obj)
        # com = self.main_obj.gaSet['com_obj']
        gen_obj.com_send('exit\r', '-1p#', 2)
        gen_obj.com_send('exit\r', '-1p#', 2)
        ret = self.login()
        print(f'data_transmission_setup ret of login:{ret}')

        if ret == 0:
            ret = self.login_2_linux()
            print(f'data_transmission_setup ret of login_2_linux:{ret}')

        if ret == 0:
            for i in range(0, 6):
                ret = gen_obj.com_send('\r', '/\\]#', 2)
                if ret == 0:
                    break

        cmds = []
        cmds.append("brctl addbr br0\r")
        cmds.append("brctl addif br0 wan1\r")
        cmds.append("brctl addif br0 wan2\r")
        cmds.append("ifconfig wan1 up\r")
        cmds.append("ifconfig wan2 up\r")
        cmds.append("ifconfig br0 up\r")

        cmds.append("brctl addbr br1\r")
        cmds.append("brctl addif br1 lan0\r")
        cmds.append("brctl addif br1 lan1\r")
        cmds.append("ifconfig lan0 up\r")
        cmds.append("ifconfig lan1 up\r")
        cmds.append("ifconfig br1 up\r")

        cmds.append("brctl addbr br2\r")
        cmds.append("brctl addif br2 lan3\r")
        cmds.append("brctl addif br2 lan2\r")
        cmds.append("ifconfig lan2 up\r")
        cmds.append("ifconfig lan3 up\r")
        cmds.append("ifconfig br2 up\r")
        if ret == 0:
            self.main_obj.my_statusbar.sstatus(f"Configuring for Data Transmission")
            for cmd in cmds:
                last_word = cmd.split(" ")[-1]
                print(last_word)
                ret = gen_obj.com_send(cmd, f'/\\]#')
                if ret != 0:
                    break
        return ret

    def serial_ports_perf(self):
        print(f'\nserial_ports_perf')
        gen_obj = lgen.Gen(self.main_obj)
        # com = self.main_obj.gaSet['com_obj']
        gen_obj.com_send('exit\r', '-1p#', 2)
        gen_obj.com_send('exit\r', '-1p#', 2)
        com_ser1 = rlcom.RLCom(self.main_obj.gaSet['comSer1'], 115200)
        com_ser1.open()
        ret = self.login()
        print(f'serial_ports_perf ret of login:{ret}')

        if ret == 0:
            ret = self.login_2_linux()
            print(f'serial_ports_perf ret of login_2_linux:{ret}')

        self.main_obj.my_statusbar.sstatus(f"Configuration Serial Ports")
        ret = gen_obj.com_send('echo \"1\" > /sys/class/gpio/gpio484/value\r', 'stam', 0.5)  # f'/\\]#'
        ret = gen_obj.com_send('stty -F /dev/ttyMV1 115200\r', 'stam', 0.5)
        ret = gen_obj.com_send('cat /dev/ttyMV1 &\r', 'stam', 0.5)

        ret = 0
        if ret == 0:
            txt1 = "ABCD_1234 7890"
            self.main_obj.my_statusbar.sstatus(f"Send {txt1} from Serial-2 to Serial-1")
            ret = -1
            for i in range(1, 3):
                ret = gen_obj.com_send(f'echo \"{txt1}\" > /dev/ttyMV1\r', 'stam', 0.5)
                buff = str(com_ser1.read(), 'utf-8')
                print(f'ser1 buff:<{buff}>')
                if txt1 in buff:
                    ret = 0
                    break
        if ret == -1:
            self.main_obj.gaSet['fail'] = f'Read \'{txt1}\' on Serial-1 fail'

        if ret == 0:
            txt2 = "10987_abcd6543"
            self.main_obj.my_statusbar.sstatus(f"Send {txt2} from Serial-2 to Serial-1")
            ret = -1
            for i in range(1, 3):
                com_ser1.send(f'{txt2}\r\r', 'stam', 1)
                buff = str(self.main_obj.gaSet['com_obj'].read(), 'utf-8')
                print(f'ser2 buff:<{buff}>')
                if txt2 in buff:
                    ret = 0
                    break
        if ret == -1:
            self.main_obj.gaSet['fail'] = f'Read \'{txt2}\' on Serial-2 fail'

        return ret

    def gps_perf(self):
        print(f'\ngps_perf')
        com = self.main_obj.gaSet['com_obj']
        gen_obj = lgen.Gen(self.main_obj)
        max_wait = 6
        admin_st = oper_st = track_st = -1

        ret = self.login()
        print(f'gps_perf ret of login:{ret}')

        if ret == 0:
            ret = gen_obj.com_send('configure system clock gnss 1\r', 'ock>gnss')
            if ret == -1:
                self.main_obj.gaSet['fail'] = 'Configure clock gnss 1 fail'
        if ret == 0:
            time.sleep(5)
            ret = gen_obj.com_send('secondary-system glonass galileo beido\r', 'ock>gnss')
            if ret == -1:
                self.main_obj.gaSet['fail'] = 'Configure secondary-system glonass fail'

        if ret == 0:
            ret = gen_obj.com_send('no shutdown\r', 'ock>gnss')
            if ret == -1:
                self.main_obj.gaSet['fail'] = 'Enable gnss 1 fail'

        if ret == 0:
            sec1 = time.time()
            for i in range(1, 60 * max_wait, 10):
                buf = ''
                sec2 = time.time()
                aft = int(sec2 - sec1)
                ret = gen_obj.wait(self.main_obj, f'Wait for GPS sync ({aft} sec past)', 10)
                if ret == -1:
                    break
                gen_obj.com_send('show status\r', 'more', 2)
                buf += com.buffer
                ret = gen_obj.com_send('\r', 'ock>gnss')
                buf += com.buffer
                print(f'gps_perf i:<{i}> aft:<{aft}> buf:<{buf}>')
                if ret == -2:
                    break

                ret = -1
                m = re.search(r'Operational Status[\s:]+(\w+)\s', buf)
                if not m:
                    self.main_obj.gaSet['fail'] = 'Read Operational Status fail'
                    break
                oper_st = m.group(1).strip()
                print(f'oper_st:{oper_st}')

                m = re.search(r'Administrative Status[\s:]+(\w+)\s', buf)
                if not m:
                    self.main_obj.gaSet['fail'] = 'Read Administrative Status fail'
                    break
                admin_st = m.group(1).strip()
                print(f'admin_st:{admin_st}')

                if oper_st == "Up":
                    m = re.search(r'Tracking Status[\s:]+(\w+)\s+Latitude', buf)
                    if m:
                        track_st = m.group(1).strip()
                        print(f'track_st:{track_st}')

                        if track_st == 'GNSS Locked':
                            ret = 0
                            break

            print(admin_st, oper_st, track_st)
            if ret == -1:
                self.main_obj.gaSet['fail'] = f'GPS did not synchronized after {max_wait} minutes'

        return ret

    def lte_leds_perf(self):
        print(f'\nlte_leds_perf')
        gen_obj = lgen.Gen(self.main_obj)
        # com = self.main_obj.gaSet['com_obj']
        gen_obj.com_send('exit\r', '-1p#', 2)
        gen_obj.com_send('exit\r', '-1p#', 2)
        ret = self.login()
        print(f'lte_leds_perf ret of login:{ret}')

        if ret == 0:
            ret = self.login_2_linux()
            print(f'lte_leds_perf ret of login_2_linux:{ret}')

        self.main_obj.my_statusbar.sstatus(f"Configuration Cell Bar")

        gen_obj.com_send('cd / \r', 'stam', 0.5)
        gen_obj.com_send('stty icrnl \r', 'stam', 0.5)

        gen_obj.com_send('cat > lte_ledtest.sh\r', 'stam', 0.5)
        with open('lte_ledtest.sh') as scr:
            for line in scr:
                gen_obj.com_send(f'{line}\r', 'stam', 0.5)
        gen_obj.com_send('\4\r', 'stam', 0.5)

        gen_obj.com_send('cat > lte_ledbar_test.sh\r', 'stam', 0.5)
        with open('lte_ledbar_test.sh') as scr:
            for line in scr:
                gen_obj.com_send(f'{line}\r', 'stam', 0.5)
        gen_obj.com_send('\4\r', 'stam', 0.5)

        gen_obj.com_send('chmod 777 lte_ledtest.sh\r', 'stam', 0.5)
        gen_obj.com_send('chmod 777 lte_ledbar_test.sh\r', 'stam', 0.5)
        gen_obj.com_send('cd / \r', 'stam', 0.5)

        while True:
            ret = self.login()
            print(f'lte_leds_perf ret of login:{ret}')

            if ret == 0:
                ret = self.login_2_linux()
                print(f'lte_leds_perf ret of login_2_linux:{ret}')
            if ret != 0:
                break

            wav = "C:\\RLFiles\\Sound\\Wav\\info.wav"
            winsound.PlaySound(wav, winsound.SND_FILENAME)
            db_dict = {
                "title": "CellBar Test",
                "message": "Press \'OK\' and verify LTE Bar Leds is changing in the following order:\n\nall OFF -> 1 and "
                           "3 -> 2 and 4 -> all ON -> all OFF",
                "type": ["OK"],
                "icon": "::tk::icons::information",
                'default': 0
            }
            string, res_but, ent_dict = Gui_SF1P.DialogBox(self.main_obj.gaSet['root'], db_dict).show()
            print(string, res_but)

            for leds in [0, 5, 10, 15, 0]:
                gen_obj.com_send(f'./lte_ledtest.sh {leds}\r', 'stam', 0.5)
                time.sleep(0.25)

            wav = "C:\\RLFiles\\Sound\\Wav\\info.wav"
            winsound.PlaySound(wav, winsound.SND_FILENAME)
            db_dict = {
                "title": "LTE Led Bar Test",
                "message": "Does the LTE Led Bar work well?",
                "type": ["Yes", "No", "Repeat"],
                "icon": "::tk::icons::information",
                'default': 0
            }
            string, res_but, ent_dict = Gui_SF1P.DialogBox(self.main_obj.gaSet['root'], db_dict).show()
            print(string, res_but)
            if res_but == 'No':
                self.main_obj.gaSet['fail'] = 'CellBar Test Fail'
                ret = -1
                break
            elif res_but == 'Yes':
                ret = 0
                break

        return ret

    def front_leds_perf(self):
        print(f'\nfront_leds_perf')
        gen_obj = lgen.Gen(self.main_obj)
        com = self.main_obj.gaSet['com_obj']
        ret = 0

        if 'ETX-1P_SFC' in self.main_obj.gaSet['dbr_name']:
            gen_obj.power(self.main_obj, 1, 0)
            time.sleep(4)
            gen_obj.power(self.main_obj, 1, 1)
            time.sleep(1)

        wav = "C:\\RLFiles\\Sound\\Wav\\info.wav"
        winsound.PlaySound(wav, winsound.SND_FILENAME)
        db_dict = {
            "title": "Front Leds Test",
            "type": ["Ok", "Cancel"],
            "icon": "::tk::icons::information",
            'default': 0
        }
        mess = "Please disconnect all ETH cables\nRemove the SD-card and the SIMs (if exists)"
        if self.main_obj.gaSet['cellQty'] != 'NotExists':
            mess += '\nDisconnect the antenna from \'LTE MAIN\' and mount it on the \'LTE AUX\''
        db_dict['message'] = mess
        string, res_but, ent_dict = Gui_SF1P.DialogBox(self.main_obj.gaSet['root'], db_dict).show()
        print(string, res_but)
        if res_but == 'Cancel':
            # self.main_obj.gaSet['fail'] = "\'LTE AUX\' Test fail"
            ret = -2

        if ret == 0:
            gen_obj.com_send('exit\r\r', 'stam', 3)
            gen_obj.com_send('\33', 'stam', 1)
            ret = self.login()
            print(f'front_leds_perf ret of login:{ret}')

        if ret == 0:
            gen_obj.com_send('\r', 'stam', 1)
            buff1 = com.buffer  # str(com.read(), 'utf-8')
            print(f'Buffer before FD: :<{buff1}>')
            wav = "C:\\RLFiles\\Sound\\Wav\\info.wav"
            winsound.PlaySound(wav, winsound.SND_FILENAME)
            db_dict = {
                "title": "FD button Test",
                "type": ["Yes", "No"],
                "icon": "::tk::icons::information",
                'default': 0,
                "message": "Press the FD button for 10-15 sec and verify the UUT is reboting (Front side's LEDs are "
                           "blinking one time).\n\nReset has been performed??"
            }
            string, res_but, ent_dict = Gui_SF1P.DialogBox(self.main_obj.gaSet['root'], db_dict).show()
            print(string, res_but)
            if res_but == 'No':
                self.main_obj.gaSet['fail'] = "FD button Test fail"
                ret = -1

        if ret == 0:
            gen_obj.com_send('\r', 'stam', 1)
            buff2 = com.buffer  # str(com.read(), 'utf-8')
            print(f'Buffer after FD: :<{buff2}>')
            if 'actory-default-config' not in buff2:
                print(f'No \'factory-default-config\' message (FD button)')

            if buff1 == buff2:
                self.main_obj.gaSet['fail'] = "Reset by FD button was not performed"
                ret = -1

        if ret == 0:
            ret = self.login_2_boot()
            print(f'front_leds_perf ret of login_2_boot:{ret}')

        if ret == 0:
            ret = gen_obj.com_send('\r\r', 'PCPE', 1)
            if ret == -1:
                gen_obj.power(self.main_obj, 1, 0)
                time.sleep(4)
                gen_obj.power(self.main_obj, 1, 1)
                ret = self.login_2_boot()
                print(f'front_leds_perf ret of login_2_boot:{ret}')

        if ret == 0:
            ret = gen_obj.com_send('mmc dev 0:1\r', 'PCPE', 1)
            if ret == -1:
                self.main_obj.gaSet['fail'] = "Read \'mmc dev 0:1\' fail"

        if ret == 0:
            if 'ot found' not in com.buffer:
                self.main_obj.gaSet['fail'] = "SD card is not pulled out"

            wav = "C:\\RLFiles\\Sound\\Wav\\info.wav"
            winsound.PlaySound(wav, winsound.SND_FILENAME)
            db_dict = {
                "title": "ALM and RUN Led Test",
                "type": ["Yes", "No"],
                "icon": "::tk::icons::information",
                'default': 0,
                "message": "Verify the ALM and RUN Leds are OFF"
            }
            string, res_but, ent_dict = Gui_SF1P.DialogBox(self.main_obj.gaSet['root'], db_dict).show()
            print(string, res_but)
            if res_but == 'No':
                self.main_obj.gaSet['fail'] = "ALM and RUN Leds are not OFF"
                ret = -1

        if ret == 0:
            ret = gen_obj.com_send('gpio toogle GPIO112\r', 'PCPE', 1)
            if ret == -1:
                self.main_obj.gaSet['fail'] = "Set gpio toogle GPIO112 fail"
        if ret == 0:
            wav = "C:\\RLFiles\\Sound\\Wav\\info.wav"
            winsound.PlaySound(wav, winsound.SND_FILENAME)
            db_dict = {
                "title": "RUN and PWR Green Led Test",
                "type": ["Yes", "No"],
                "icon": "::tk::icons::information",
                'default': 0,
                "message": "Verify the RUN and PWR Green Leds are ON"
            }
            string, res_but, ent_dict = Gui_SF1P.DialogBox(self.main_obj.gaSet['root'], db_dict).show()
            print(string, res_but)
            if res_but == 'No':
                self.main_obj.gaSet['fail'] = "RUN and/or PWR Green Led are not ON"
                ret = -1
            gen_obj.com_send('gpio toogle GPIO112\r', 'PCPE', 1)

        if ret == 0:
            ret = gen_obj.com_send('gpio toogle GPIO113\r', 'PCPE', 1)
            if ret == -1:
                self.main_obj.gaSet['fail'] = "Set gpio toogle GPIO113 fail"

        if ret == 0:
            wav = "C:\\RLFiles\\Sound\\Wav\\info.wav"
            winsound.PlaySound(wav, winsound.SND_FILENAME)
            db_dict = {
                "title": "ALM Red Led Test",
                "type": ["Yes", "No"],
                "icon": "::tk::icons::information",
                'default': 0,
                "message": "Verify the ALM Red Led is ON"
            }
            string, res_but, ent_dict = Gui_SF1P.DialogBox(self.main_obj.gaSet['root'], db_dict).show()
            print(string, res_but)
            if res_but == 'No':
                self.main_obj.gaSet['fail'] = "ALM Red Led is not ON"
                ret = -1
            gen_obj.com_send('gpio toogle GPIO113\r', 'PCPE', 1)

        if ret == 0:
            gen_obj.com_send('mii write 1 1 0x80fe\r', 'PCPE', 1)
            gen_obj.com_send('mii write 1 0 0x9656\r', 'PCPE', 1)

            wav = "C:\\RLFiles\\Sound\\Wav\\info.wav"
            winsound.PlaySound(wav, winsound.SND_FILENAME)
            db_dict = {
                "title": "AUX Green Led Test",
                "type": ["Yes", "No"],
                "icon": "::tk::icons::information",
                'default': 0,
                "message": "Verify the AUX Green Led is ON, if exists"
            }
            string, res_but, ent_dict = Gui_SF1P.DialogBox(self.main_obj.gaSet['root'], db_dict).show()
            print(string, res_but)
            if res_but == 'No':
                self.main_obj.gaSet['fail'] = "AUX Green Led is not ON"
                ret = -1
            gen_obj.com_send('mii write 1 1 0x80ee\r', 'PCPE', 1)
            gen_obj.com_send('mii write 1 0 0x9656\r', 'PCPE', 1)

            # all ON
            gen_obj.com_send('mii write 2 1 0x80ff\r', 'PCPE', 1)
            gen_obj.com_send('mii write 2 0 0x96b6\r', 'PCPE', 1)
            if 'ETX-1P_SFC' in self.main_obj.gaSet['dbr_name']:
                # WAN2 led
                gen_obj.com_send('mii write 2 0 0x9676\r', 'PCPE', 1)

            for reg1 in ['0x80ff', '0x90ff']:
                for reg2 in ['0x9636', '0x9656', '0x9676', '0x9696']:
                    gen_obj.com_send(f'mii write 1 1 {reg1}\r', 'PCPE', 1)
                    gen_obj.com_send(f'mii write 1 0 {reg2}\r', 'PCPE', 1)

            wav = "C:\\RLFiles\\Sound\\Wav\\info.wav"
            winsound.PlaySound(wav, winsound.SND_FILENAME)
            mess = ("Verify Green Leds are ON on the following ports:\nETH 1-6, S1 TX and RX, S2 TX and RX, SIM 1 and "
                    "2\n\nVerify Red Led is ON on the AUX port\n\nDo the Leds work well?")
            db_dict = {
                "title": "Boot Leds Test",
                "type": ["Yes", "No"],
                "icon": "::tk::icons::information",
                'default': 0,
                "message": mess
            }
            string, res_but, ent_dict = Gui_SF1P.DialogBox(self.main_obj.gaSet['root'], db_dict).show()
            print(string, res_but)
            if res_but == 'No':
                self.main_obj.gaSet['fail'] = "Boot Leds Test fail"
                ret = -1

        if ret == 0:
            # all OFF
            gen_obj.com_send('mii write 2 1 0x80ee\r', 'PCPE', 1)
            gen_obj.com_send('mii write 2 0 0x96b6\r', 'PCPE', 1)
            if 'ETX-1P_SFC' in self.main_obj.gaSet['dbr_name']:
                # WAN2 led
                gen_obj.com_send('mii write 2 0 0x9676\r', 'PCPE', 1)

            for reg1 in ['0x80ee', '0x90ee']:
                for reg2 in ['0x9636', '0x9656', '0x9676', '0x9696']:
                    gen_obj.com_send(f'mii write 1 1 {reg1}\r', 'PCPE', 1)
                    gen_obj.com_send(f'mii write 1 0 {reg2}\r', 'PCPE', 1)

            wav = "C:\\RLFiles\\Sound\\Wav\\info.wav"
            winsound.PlaySound(wav, winsound.SND_FILENAME)
            db_dict = {
                "title": "Boot Leds Test",
                "type": ["Yes", "No"],
                "icon": "::tk::icons::information",
                'default': 0,
                "message": "Verify all the leds, except PWR, are OFF"
            }
            string, res_but, ent_dict = Gui_SF1P.DialogBox(self.main_obj.gaSet['root'], db_dict).show()
            print(string, res_but)
            if res_but == 'No':
                self.main_obj.gaSet['fail'] = "Boot Leds Test fail"
                ret = -1

        return ret

    def read_imei(self):
        com = self.main_obj.gaSet['com_obj']
        self.main_obj.gaSet['imei1'] = "NotExists"
        self.main_obj.gaSet['imei2'] = "NotExists"
        if self.main_obj.gaSet['act'] == 0:
            return -2
        gen_obj = lgen.Gen(self.main_obj)
        print(f'\nread_imei')
        ret = self.login()
        print(f'read_imei ret of login:{ret}')
        if ret == 0:
            gen_obj.com_send('exit all\r', '-1p')
            if self.main_obj.gaSet['cellQty'] == 1:
                self.main_obj.my_statusbar.sstatus("Read IMEI")
                ret = gen_obj.com_send('configure port cellular lte\r', 'lar\(lte')
                if ret == 0:
                    ret = gen_obj.com_send('no shutdown\r', 'lar\(lte')
                if ret == 0:
                    for i in range(1, 11):
                        if self.main_obj.gaSet['act'] == 0:
                            break
                        self.main_obj.my_statusbar.sstatus(f"Read LTE status ({i})")
                        ret = gen_obj.com_send('show status\r', 'more')
                        buf = com.buffer
                        ret = gen_obj.com_send('\r', 'lar\(lte', 1)
                        buf += com.buffer
                        if 'more' in com.buffer:
                            ret = gen_obj.com_send('\r', 'lar\(lte')
                            buf += com.buffer
                        m = re.search('IMEI\s+:\s+(\d+)', buf)
                        if not m:
                            time.sleep(3)
                        else:
                            self.main_obj.gaSet['imei1'] = m.group(1)
                            ret = 0
                            break

            elif self.main_obj.gaSet['cellQty'] == 2:
                for lte in ['1', '2']:
                    self.main_obj.my_statusbar.sstatus(f"Read IMEI of LTE {lte}")
                    ret = gen_obj.com_send('exit all\r', '-1p')
                    ret = gen_obj.com_send(f'configure port cellular lte-{lte}\r', 'lar\(lte')
                    if ret == 0:
                        ret = gen_obj.com_send('no shutdown\r', 'lar\(lte')
                    if ret == 0:
                        for i in range(1, 11):
                            if self.main_obj.gaSet['act'] == 0:
                                break
                            self.main_obj.my_statusbar.sstatus(f"Read LTE {lte} status ({i})")
                            ret = gen_obj.com_send('show status\r', 'more')
                            buf = com.buffer
                            ret = gen_obj.com_send('\r', 'more', 1)
                            buf += com.buffer
                            for mor in range(1, 4):
                                if 'more' in com.buffer:
                                    ret = gen_obj.com_send('\r', 'lar\(lte', 2)
                                    buf += com.buffer
                            m = re.search('IMEI\s+:\s+(\d+)', buf)
                            if not m:
                                time.sleep(3)
                            else:
                                self.main_obj.gaSet[f'imei{lte}'] = m.group(1)
                                ret = 0
                                break

        if ret == -1:
            self.main_obj.gaSet['fail'] = 'Read IMEI fail'

        print(self.main_obj.gaSet['imei1'], self.main_obj.gaSet['imei2'])

        return ret

    def check_sim_out(self):
        com = self.main_obj.gaSet['com_obj']
        if self.main_obj.gaSet['act'] == 0:
            return -2
        gen_obj = lgen.Gen(self.main_obj)
        print(f'\ncheck_sim_out')
        ret = self.login()
        print(f'check_sim_out ret of login:{ret}')
        if ret == 0:
            gen_obj.com_send('exit all\r', '-1p')
            if self.main_obj.gaSet['cellQty'] == 1:
                ret = self.cellularLte_RadOS_Sim12()

                if ret == 0:
                    self.main_obj.my_statusbar.sstatus("Read IMEI")
                    ret = gen_obj.com_send('configure port cellular lte\r', 'lar\(lte')
                if ret == 0:
                    for sim in ['1', '2']:
                        ret = gen_obj.com_send('shutdown\r', 'lar\(lte')
                        ret = gen_obj.com_send(f'mode sim {sim}\r', 'lar\(lte')
                        if ret == 0:
                            ret = gen_obj.com_send('no shutdown\r', 'lar\(lte')
                            if sim == '2':
                                ret = gen_obj.wait(self.main_obj, 'Wait for SIM-2 activation', 60)

                            if ret == 0:
                                for i in range(1, 41):
                                    if self.main_obj.gaSet['act'] == 0:
                                        break
                                    self.main_obj.my_statusbar.sstatus(f"Read LTE status of SIM {sim} ({i})")
                                    ret = gen_obj.com_send('show status\r', 'more')
                                    buf = com.buffer
                                    ret = gen_obj.com_send('\r', 'lar\(lte', 1)
                                    buf += com.buffer
                                    if 'more' in com.buffer:
                                        ret = gen_obj.com_send('\r', 'lar\(lte')
                                        buf += com.buffer
                                    m = re.search(r'SIM Information[\s-]+SIM([\w\s\d\:]+)Status', buf)
                                    if not m:
                                        time.sleep(2)
                                    else:
                                        if sim == '1' and m.group(1) == "SIM 2":
                                            continue
                                        if sim == '2' and m.group(1) == "SIM 1":
                                            continue

                                        m = re.search(r'SIM Status\s+:\s+([\w\-]+)', buf)
                                        if not m:
                                            time.sleep(2)
                                        else:
                                            ret = 0
                                            break

                                print(f'val:{m.group(1)}')
                                if m.group(1) == 'ready':
                                    self.main_obj.gaSet['fail'] = f'The SIM {sim} is not pulled out'
                                    ret = -1

            elif self.main_obj.gaSet['cellQty'] == 2:
                ret = self.cellularLte_RadOS_Sim12_dual()
                if ret == 0:
                    for lte in ['1', '2']:
                        self.main_obj.my_statusbar.sstatus(f"Read IMEI of LTE {lte}")
                        ret = gen_obj.com_send('exit all\r', '-1p')
                        ret = gen_obj.com_send(f'configure port cellular lte-{lte}\r', 'lar\(lte')
                        if ret == 0:
                            ret = gen_obj.com_send('no shutdown\r', 'lar\(lte')
                        if ret == 0:
                            for i in range(1, 11):
                                if self.main_obj.gaSet['act'] == 0:
                                    break
                                self.main_obj.my_statusbar.sstatus(f"Read LTE {lte} status ({i})")
                                ret = gen_obj.com_send('show status\r', 'more')
                                buf = com.buffer
                                ret = gen_obj.com_send('\r', 'more', 1)
                                buf += com.buffer
                                for mor in range(1, 4):
                                    if 'more' in com.buffer:
                                        ret = gen_obj.com_send('\r', 'lar\(lte', 2)
                                        buf += com.buffer
                                m = re.search('SIM Status\s+:\s+([\w\-]+)', buf)
                                if not m:
                                    time.sleep(2)
                                else:
                                    ret = 0
                                    break
                            print(f'val:{m.group(1)}')
                            if m.group(1) == 'ready':
                                self.main_obj.gaSet['fail'] = f'The SIM of LTE {lte} is not pulled out'
                                ret = -1
                                break

        return ret

    def inform_about_sim(self):
        wav = "C:\\RLFiles\\Sound\\Wav\\info.wav"
        winsound.PlaySound(wav, winsound.SND_FILENAME)
        db_dict = {
            "title": "SIM inside",
            "type": ["Ok", "Stop"],
            "icon": "::tk::icons::error",
            'default': 0,
            "message": "Pull out SIM/s and press OK"
        }
        string, res_but, ent_dict = Gui_SF1P.DialogBox(self.main_obj.gaSet['root'], db_dict).show()
        print(string, res_but)
        return res_but

    def fact_sett_perf(self):
        com = self.main_obj.gaSet['com_obj']
        if self.main_obj.gaSet['act'] == 0:
            return -2
        gen_obj = lgen.Gen(self.main_obj)
        print(f'\nfact_sett_perf')
        ret = self.login()
        print(f'fact_sett_perf ret of login:{ret}')
        if ret == 0:
            ret = gen_obj.com_send('exit all\r', '-1p')
            ret = gen_obj.com_send('admin factory-default\r', 'yes/no')
            if ret == -1:
                self.main_obj.gaSet['fail'] = 'Perform factory-default fail'
        if ret == 0:
            ret = gen_obj.com_send('yes\r', 'startup-config successfully', 20)
            if ret == -1:
                self.main_obj.gaSet['fail'] = 'Restarting system fail'
        return ret

    def ssh_perf(self):
        com = self.main_obj.gaSet['com_obj']
        if self.main_obj.gaSet['act'] == 0:
            return -2
        gen_obj = lgen.Gen(self.main_obj)
        print(f'\nssh_perf')
        ret = self.login()
        print(f'ssh_perf ret of login:{ret}')
        if ret == 0:
            # ssh = subprocess.Popen('plink -ssh su@169.254.1.1 -pw 1234', bufsize=0, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # read = ssh.stdout.read(10).decode('utf-8')
            # print(f'ssh_perf ret of read1:<{read}>')
            # if 'SF-1p' not in read:
            #     ret = -1
            # ssh.stdin.write(b'\n\r')
            # ssh.stdin.flush()
            # read = ssh.stdout.read(2).decode('utf-8')
            # print(f'ssh_perf ret of read2:<{read}>')

            if self.main_obj.gaSet['wanPorts'] in ['2U', '1SFP1UTP']:
                ssh_port = 4
            else:
                ssh_port = 6
            wav = "C:\\RLFiles\\Sound\\Wav\\info.wav"
            winsound.PlaySound(wav, winsound.SND_FILENAME)
            db_dict = {
                "title": "SSH Test",
                "type": ["Ok", "Cancel"],
                "icon": "::tk::icons::information",
                'default': 0,
                "message": f"Please connect the SSH cable to port {ssh_port}\nRemove the J21 jumper to 2-3 position"
            }
            string, res_but, ent_dict = Gui_SF1P.DialogBox(self.main_obj.gaSet['root'], db_dict).show()
            if res_but == 'Cancel':
                return -2

            ssh = SSH()
            data = ''
            for i in range(1, 6):
                if self.main_obj.gaSet['act'] == 0:
                    return -2
                self.main_obj.my_statusbar.sstatus(f'SSH Login ({i})')
                ret = ssh.connect_to(host='169.254.1.1', port=22, username='su', password='1234')
                if ret != 0:
                    ret = ssh.connect_to(host='169.254.1.1', port=22, username='su', password='4')
                    if ret != 0:
                        self.main_obj.gaSet['fail'] = ret
                        ret = -1
                if ret == 0:
                    ret, data = ssh.do_command(b'show config system device-inf\n')
                    print(f'ssh_perf ret of ret:<{ret}> data:<{data}>')
                    if ret == -1:
                        self.main_obj.gaSet['fail'] = data

                if ret == 0:
                    if not 'Engine Time' in data:
                        ret = -1
                    else:
                        break

                if ret != 0:
                    time.sleep(2)

            if ret == 0 and 'ETX-1P_SFC' in self.main_obj.gaSet['dbr_name']:
                Gui_SF1P.DialogBox(self.main_obj.gaSet['root'],
                                   {'title': "SSH Test for Safaricom", "type": ["Ok"], "icon": "::tk::icons"
                                                                                               "::information",
                                    "message": "Remove the J21"}).show()

        return ret

    def read_mac(self):
        com = self.main_obj.gaSet['com_obj']
        self.main_obj.gaSet['mac'] = "NotExists"
        if self.main_obj.gaSet['act'] == 0:
            return -2
        gen_obj = lgen.Gen(self.main_obj)
        print(f'\nread_mac')
        ret = self.login()
        print(f'read_mac ret of login:{ret}')
        if ret == 0:
            gen_obj.com_send('exit all\r', '-1p')
            ret = gen_obj.com_send('show config system device-inf\r', 'Engine Time')
            if ret != 0:
                self.main_obj.gaSet['fail'] = "Show config system device-infoC fail"
        if ret == 0:
            m = re.search('MAC Address[:\s]+([-\d\w]+)\s+Engine', com.buffer)
            if not m:
                self.main_obj.gaSet['fail'] = "Read MAC fail"
                ret = -1
            else:
                self.main_obj.gaSet['mac'] = m.group(1)
                ret = 0
        return ret



