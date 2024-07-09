import re
import time
import inspect
import os

import lib_gen_sf1p as lgen
from gui_sf1p import App
from RL import rl_com as rlcom
from RL import Lib_RadApps


class Put(App):
    def __init__(self, gaSet):
        self.gaSet = gaSet
        # print(f'put init self:{self}')
        # App.__init__(self, self.gaSet['root'], gaSet)

    def login(self):
        App.my_statusbar.sstatus('Login')

        ret = -1
        com = 'comDut'
        login_buff = ''
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        login_buff += rlcom.buffer
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        login_buff += rlcom.buffer

        if re.search('PCPE>', login_buff):
            print(f'login PCPE')
            lgen.my_send(self.gaSet, com, 'boot\r', 'partitions')
            time.sleep(10)
            ret = -1

        if re.search('root@localhost', login_buff):
            print(f'login localhost')
            ret = lgen.my_send(self.gaSet, com, 'exit\r\r', '-1p', 12)

        if re.search('-1p', rlcom.buffer):
            print(f'login -1p')
            time.sleep(2)
            lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
            login_buff += rlcom.buffer
            if re.search('-1p', rlcom.buffer):
                ret = 0

        if re.search('CLI session is closed', rlcom.buffer):
            print(f'login CLI session is closed')
            ret = -1
            rlcom.send(self.gaSet['id'][com], '\r')

        print(f'login ret before loop:{ret}')
        self.gaSet['fail'] = 'Login fail'
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
                print(f'Login {lgen.my_time()} run_sec:{int(time.time() - start_sec)}  read_buff:_{read_buff}_')

                if re.search(r'failed to achieve system info', login_buff) and \
                        re.search(r'command execute error:', login_buff):
                    return 'PowerOffOn'

                if re.search(r'user>', login_buff):  # rlcom.buffer
                    lgen.my_send(self.gaSet, com, 'su\r', 'assword')
                    if lgen.my_send(self.gaSet, com, '1234\r', '-1p#') == 0:
                        ret = 0
                        break

                if re.search('-1p', rlcom.buffer):
                    return 0

                if re.search(r'PCPE>', rlcom.buffer):
                    lgen.my_send(self.gaSet, com, 'boot\r', 'partitions')

                time.sleep(5)

        if ret == 0:
            self.gaSet['fail'] = ''
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
        print(f'{lgen.my_time()} {inspect.stack()[0][3].upper()}')
        com = 'comDut'
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        if re.search('PCPE', rlcom.buffer):  # rlcom.buffer
            return 0

        lgen.power(self.gaSet, 1, 0)
        time.sleep(4)
        lgen.power(self.gaSet, 1, 1)
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
        App.my_statusbar.sstatus('Login into Boot')

        ret = -1
        com = 'comDut'
        login_buff = ''
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        login_buff += rlcom.buffer
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        login_buff += rlcom.buffer

        if re.search('\\]#', rlcom.buffer):
            ret = 0

        self.gaSet['fail'] = 'Login to Boot level fail'
        if ret != 0:
            start_sec = time.time()
            for i in range(1, 301):
                App.my_statusbar.runTime(i)
                self.gaSet['root'].update()
                if self.gaSet['act'] == 0:
                    ret = -2
                    break

                read_buff = lgen.my_read(self.gaSet, com)
                login_buff += read_buff
                print(
                    f'Login to 2Boot {lgen.my_time()} run_sec:{int(time.time() - start_sec)}  read_buff:_{read_buff}_')

                if re.search('to stop autoboot:', login_buff):  # rlcom.buffer
                    if lgen.my_send(self.gaSet, com, '\r\r', 'PCPE') == 0:
                        ret = 0
                        break
                if re.search('to stop PCPE:', login_buff):  # rlcom.buffer
                    ret = 0
                    break

                time.sleep(1)

        if ret == 0:
            self.gaSet['fail'] = ''
        # else:
        #     gaSet['fail'] = 'Login fail'
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
        App.my_statusbar.sstatus('Login to Linux')

        ret = -1
        com = 'comDut'
        login_buff = ''
        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.25)
        login_buff += rlcom.buffer

        if re.search('root@localhost', rlcom.buffer):
            return 0

        ret = self.logon_debug()
        print(f'ret after logon_debug:{ret}')
        if ret != 0:
            return ret

        ret = lgen.my_send(self.gaSet, com, 'debug shell\r\r', '/\\]#')
        return ret

    def logon_debug(self):
        App.my_statusbar.sstatus('Logon Debug')

        ret = -1
        com = 'comDut'
        lgen.my_send(self.gaSet, com, 'exit all\r', 'stam', 0.25)
        lgen.my_send(self.gaSet, com, 'logon debug\r', 'stam', 0.25)
        if re.search('command not recognized', rlcom.buffer) is None:
            m = re.search('Key code:\s+(\d+)', rlcom.buffer)
            if m:
                kc = m[1]
                password = Lib_RadApps.ate_decryptor(kc, "pass")
                print(f'logon_debug password:{password}')
                self.gaSet['fail'] = 'Logon debug fail'
                ret = lgen.my_send(self.gaSet, com, f'{password}\r', '-1p#')
            else:
                ret = -1
        else:
            ret = 0
        return ret

    def read_wan_lan_status(self):
        ret = 0
        if self.gaSet['dut_fam']['wanPorts'] == '2U':
            sfp_ports = []
            utp_ports = [3, 4]
        elif self.gaSet['dut_fam']['wanPorts'] == '4U1S':
            sfp_ports = [1, 2]
            utp_ports = [3, 4, 5, 6]

        for port in sfp_ports:
            ret = self.shut_down(port, 'no shutdown')
        for port in utp_ports:
            ret = self.shut_down(port, 'no shutdown')

        for port in sfp_ports:
            ret = self.read_eth_port_status(port)
            if ret != 0:
                return ret
        for port in utp_ports:
            ret = self.read_utp_port_status(port)
            if ret != 0:
                return ret

        return ret

    def read_eth_port_status(self, port):
        ret = self.login()
        if ret != 0:
            return ret

        App.my_statusbar.sstatus(f'Read EthPort Status of {port}')

        self.gaSet['fail'] = f'Show status of port {port} fail'
        com = 'comDut'

        lgen.my_send(self.gaSet, com, 'exit all\r', 'stam', 0.25)
        ret = lgen.my_send(self.gaSet, com, f'config port ethernet {port}\r', f'({port})')
        if ret != 0:
            return ret

        time.sleep(2)

        lgen.my_send(self.gaSet, com, 'show status\r', 'more', 8)
        bu = rlcom.buffer
        ret = lgen.my_send(self.gaSet, com, '\r', f'({port})')
        if ret != 0:
            return ret
        bu += rlcom.buffer

        # self.gaSet['puts_log'].info(f"ReadEthPortStatus bu:{bu}")
        print(f'{lgen.my_time()} ReadEthPortStatus bu:{bu}')

        m = re.search(r'SFP\+?\sIn', bu)
        print(f'm of SFP In:{m}')

        m = re.search(r'Operational Status[\s\:]+([\w]+)\s', bu)
        if m is None:
            self.gaSet['fail'] = f'Read Operational Status of port {port} fail'
            return -1
        op_stat = m[1].strip(" ")
        # print(f'Op Stat:_{op_stat}_')
        # self.gaSet['puts_log'].info(f"Operational Status: {op_stat}")
        print(f'{lgen.my_time()} Operational Status: {op_stat}')
        if op_stat != "Up":
            self.gaSet['fail'] = f'The Operational Status of port {port} is {op_stat}'
            return -1

        m = re.search(r'Administrative Status[\s\:]+([\w]+)\s', bu)
        if m is None:
            self.gaSet['fail'] = f'Read Administrative Status of port {port} fail'
            return -1
        adm_stat = m[1].strip(" ")
        # print(f'Op Stat:_{adm_stat}_')
        # self.gaSet['puts_log'].info(f"Administrative Status: {adm_stat}")
        print(f'{lgen.my_time()} Administrative Status: {adm_stat}')
        # print(f'm of Adm Stat:{m}, m1:{m[1]}')
        if adm_stat != "Up":
            self.gaSet['fail'] = f'The Administrative Status of port {port} is {adm_stat}'
            return -1

        return ret

    def read_utp_port_status(self, port):
        ret = self.login()
        if ret != 0:
            return ret

        App.my_statusbar.sstatus(f'Read EthPort Status of {port}')

        self.gaSet['fail'] = f'Show status of port {port} fail'
        com = 'comDut'

        lgen.my_send(self.gaSet, com, 'exit all\r', 'stam', 0.25)
        ret = lgen.my_send(self.gaSet, com, f'config port ethernet {port}\r', f'({port})')
        if ret != 0:
            return ret

        time.sleep(2)

        lgen.my_send(self.gaSet, com, 'show status\r', f'({port})')
        bu = rlcom.buffer
        ret = lgen.my_send(self.gaSet, com, '\r', f'({port})')
        if ret != 0:
            return ret
        bu += rlcom.buffer

        # self.gaSet['puts_log'].info(f"ReadEthPortStatus bu:{bu}")
        print(f'{lgen.my_time()} ReadEthPortStatus bu:{bu}')

        m = re.search(r'Operational Status[\s\:]+([\w]+)\s', bu)
        if m is None:
            self.gaSet['fail'] = f'Read Operational Status of port {port} fail'
            return -1
        op_stat = m[1].strip(" ")
        # print(f'Op Stat:_{op_stat}_')
        # self.gaSet['puts_log'].info(f"Operational Status: {op_stat}")
        print(f'{lgen.my_time()} Operational Status: {op_stat}')
        if op_stat != "Up":
            self.gaSet['fail'] = f'The Operational Status of port {port} is {op_stat}'
            return -1

        m = re.search(r'Administrative Status[\s\:]+([\w]+)\s', bu)
        if m is None:
            self.gaSet['fail'] = f'Read Administrative Status of port {port} fail'
            return -1
        adm_stat = m[1].strip(" ")
        # print(f'Op Stat:_{adm_stat}_')
        # self.gaSet['puts_log'].info(f"Administrative Status: {adm_stat}")
        print(f'{lgen.my_time()} Administrative Status: {adm_stat}')
        # print(f'm of Adm Stat:{m}, m1:{m[1]}')
        if adm_stat != "Up":
            self.gaSet['fail'] = f'The Administrative Status of port {port} is {adm_stat}'
            return -1

        m = re.search(r'Connector Type[\s\:]+([\w]+)\s', bu)
        if m is None:
            self.gaSet['fail'] = f'Read Connector Type of port {port} fail'
            return -1
        conn = m[1].strip(" ")
        # self.gaSet['puts_log'].info(f"Connector Type: {conn}")
        print(f'{lgen.my_time()} Connector Type: {conn}')
        if conn != "RJ45":
            self.gaSet['fail'] = f'The Connector Type of port {port} is {conn}'
            return -1

        return ret

    def shut_down(self, port, state):
        # self.gaSet['puts_log'].info(f'{inspect.stack()[0][3].upper()}')
        print(f'{lgen.my_time()} {inspect.stack()[0][3].upper()}')
        ret = self.login()
        if ret != 0:
            return ret
        App.my_statusbar.sstatus('ShutDown port {port} "{state}"')

        com = 'comDut'
        ret = lgen.my_send(self.gaSet, com, 'exit all\r', '-1p')
        if ret != 0:
            return ret
        ret = lgen.my_send(self.gaSet, com, f'configure port ethernet {port} {state}\r', '-1p')
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
        print(f'{lgen.my_time()} {inspect.stack()[0][3].upper()}')
        com = 'comDut'
        ret = lgen.my_send(self.gaSet, com, 'mmc dev 0:1\r', 'PCPE')
        if ret != 0:
            self.gaSet['fail'] = f'"mmc dev 0:1" fail'
            return -1
        if re.search(r'dev 0:1\s+switch to partitions #0, OK', rlcom.buffer) is None:
            self.gaSet['fail'] = f'"dev 0:1 switch to partitions 0" does not exist'
            return -1
        if re.search(r'mmc0 is current device', rlcom.buffer) is None:
            self.gaSet['fail'] = f'"mmc0 is current device" does not exist'
            return -1

        ret = lgen.my_send(self.gaSet, com, 'mmc info\r', 'PCPE')
        if ret != 0:
            self.gaSet['fail'] = f'"mmc info" fail'
            return -1
        if re.search(r'Bus Width: 4-bit', rlcom.buffer) is None:
            self.gaSet['fail'] = f'"Bus Width: 4-bit" does not exist'
            return -1

        return ret

    def soc_flash_perform(self):
        # self.gaSet['puts_log'].info(f'{inspect.stack()[0][3].upper()}')
        print(f'{lgen.my_time()} {inspect.stack()[0][3].upper()}')
        com = 'comDut'
        ret = lgen.my_send(self.gaSet, com, 'mmc dev 1:0\r', 'PCPE')
        if ret != 0:
            self.gaSet['fail'] = f'"mmc dev 1:0" fail'
            return -1
        if re.search(r'dev 1:0\s+switch to partitions #0, OK', rlcom.buffer) is None:
            self.gaSet['fail'] = f'"dev 1:0 switch to partitions 0" does not exist'
            return -1
        if re.search(r'mmc1\(part 0\) is current device', rlcom.buffer) is None:
            self.gaSet['fail'] = f'"mmc1(part 0) is current device" does not exist'
            return -1

        ret = lgen.my_send(self.gaSet, com, 'mmc info\r', 'PCPE')
        if ret != 0:
            self.gaSet['fail'] = f'"mmc info" fail'
            return -1
        if re.search(r'HC WP Group Size: 8 MiB', rlcom.buffer) is None:
            self.gaSet['fail'] = f'"HC WP Group Size: 8 MiB" does not exist'
            return -1

        ret = lgen.my_send(self.gaSet, com, 'mmc list\r', 'PCPE')
        if ret != 0:
            self.gaSet['fail'] = f'"mmc list" fail'
            return -1
        if re.search(r'sdhci@d0000: 0', rlcom.buffer) is None:
            self.gaSet['fail'] = f'"sdhci@d0000: 0" does not exist'
            return -1
        if re.search(r'sdhci@d8000: 1 \(eMMC\)', rlcom.buffer) is None:
            self.gaSet['fail'] = f'"sdhci@d8000: 1 (eMMC)" does not exist'
            return -1

        return ret

    def soc_2ic_perform(self):
        # self.gaSet['puts_log'].info(f'{inspect.stack()[0][3].upper()}')
        print(f'{lgen.my_time()} {inspect.stack()[0][3].upper()}')
        com = 'comDut'
        ret = lgen.my_send(self.gaSet, com, 'i2c bus\r', 'PCPE')
        if ret != 0:
            self.gaSet['fail'] = f'"i2c bus" fail'
            return -1
        if re.search(r'Bus 0:\s+i2c@11000', rlcom.buffer) is None:
            self.gaSet['fail'] = f'"Bus 0: i2c@11000" does not exist'
            return -1

        ret = lgen.my_send(self.gaSet, com, 'i2c dev 0\r', 'PCPE')
        if ret != 0:
            self.gaSet['fail'] = f'"i2c dev 0" fail'
            return -1
        ret = lgen.my_send(self.gaSet, com, 'i2c probe\r', 'PCPE')
        if ret != 0:
            self.gaSet['fail'] = f'"i2c probe" fail'
            return -1
        if re.search(r'20 21', rlcom.buffer) is None:
            self.gaSet['fail'] = f'"20 21" does not exist'
            return -1
        if re.search(r'7E 7F', rlcom.buffer) is None:
            self.gaSet['fail'] = f'"7E 7F" does not exist'
            return -1

        lgen.my_send(self.gaSet, com, 'i2c mw 0x52 0.2 0xaa 0x1\r', 'PCPE')
        ret = lgen.my_send(self.gaSet, com, 'i2c md 0x52 0.2 0x20\r', 'PCPE')
        if ret != 0:
            self.gaSet['fail'] = f'"i2c md" fail'
        if re.search(r'0000: aa', rlcom.buffer) is None:
            self.gaSet['fail'] = f'"0000: aa" does not exist'
            return -1

        lgen.my_send(self.gaSet, com, 'i2c mw 0x52 0.2 0xbb 0x1\r', 'PCPE')
        ret = lgen.my_send(self.gaSet, com, 'i2c md 0x52 0.2 0x20\r', 'PCPE')
        if ret != 0:
            self.gaSet['fail'] = f'"i2c md" fail'
        if re.search(r'0000: bb', rlcom.buffer) is None:
            self.gaSet['fail'] = f'"0000: bb" does not exist'
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
        print(f'{lgen.my_time()} {inspect.stack()[0][3].upper()}')
        com = 'comDut'
        ret = self.login()
        if ret == 'PowerOffOn':
            lgen.power(self.gaSet, 1, 0)
            time.sleep(4)
            lgen.power(self.gaSet, 1, 1)
            ret = self.login()

        if ret != 0:
            return ret

        ret = self.login_2_linux()
        if ret != 0:
            return ret

        lgen.my_send(self.gaSet, com, '\r', 'stam', 0.5)
        ret = lgen.my_send(self.gaSet, com, 'cat /USERFS/eeprom/MAC_ADDRESS\r', '/\]\#')
        if ret != 0:
            return ret
        if re.search('command not found', rlcom.buffer):
            ret = lgen.my_send(self.gaSet, com, 'cat /USERFS/eeprom/MAC_ADDRESS\r', '/\]\#')
            if ret != 0:
                return ret

        bb = re.sub(r'\s+', " ", rlcom.buffer)
        print(f'id_perform bb:_{bb}_')
        m = re.search(r'ADDRESS\s+([0-9A-F:]+)', bb)
        if m is None:
            dut_mac = "EmptyEEPROM"
            print(f'{lgen.my_time()} id_perform No User_eeprom')
        else:
            eeprom_mac = m[1]
            dut_mac = re.sub(r':+', "", m[1]).upper()  # ab:12:cd:34:ef:56 -> AB12CD34EF56
            self.gaSet['mac'] = dut_mac
            print(f'{lgen.my_time()} get_mac mac_match:{m[1]}, dut_mac:{dut_mac}')

        ret = lgen.my_send(self.gaSet, com, 'exit\r', '#')
        if ret != 0:
            return ret

        if mode == 'read_mac':
            return ret

        if dut_mac[:6] != "1806F5":
            if m is None:
                self.gaSet['fail'] = "MAC Address is empty"
            else:
                self.gaSet['fail'] = f"MAC Address is \'{m[1]}\'. It's out of RAD range"
            return -1

        ret = lgen.my_send(self.gaSet, com, 'configure system\r', 'system')
        if ret != 0:
            self.gaSet['fail'] = "Configure System fail"
            return -1
        ret = lgen.my_send(self.gaSet, com, 'show device-information\r', 'system')
        if ret != 0:
            self.gaSet['fail'] = "Show device-information fail"
            return -1

        self.gaSet['file_log'].info(rlcom.buffer.replace("\n", ""))

        m = re.search(r'Sw:\s+([\d\.]+)\s', rlcom.buffer)
        if m is None:
            self.gaSet['fail'] = "Read Sw fail"
            return -1
        uut_sw = m[1].strip()
        print(f"{lgen.my_time()} gaSet['SWver']:{self.gaSet['SWver']} uut_sw:{uut_sw}")
        if uut_sw != self.gaSet['SWver']:
            self.gaSet['fail'] = f"The SW is \'{uut_sw}\'. Should be \'{self.gaSet['SWver']}\'"
            return -1

        m = re.search(r'Name\s+:\s+([a-zA-Z\d\-]+)\s', rlcom.buffer)
        if m is None:
            self.gaSet['fail'] = "Read Name fail"
            return -1
        uut_nam = m[1].strip()
        print(f"{lgen.my_time()} uut_nam:{uut_nam}")
        if uut_nam != "SF-1p":
            self.gaSet['fail'] = f"The Name is \'{uut_nam}\'. Should be \'SF-1p\'"
            return -1

        m = re.search(r'Model\s+:\s+([a-zA-Z\d\-/_]+)\s', rlcom.buffer)
        if m is None:
            self.gaSet['fail'] = "Read Model fail"
            return -1
        uut_model = m[1].strip()
        print(f"{lgen.my_time()} uut_model:{uut_model}")

        if lgen.parse_sw(self.gaSet) == "Safari" and uut_model != "SF-1P":
            self.gaSet['fail'] = f"The Model is \'{uut_model}\'. Should be \'SF-1P\'"
            return -1
        else:
            uut_model = uut_model.replace('_', '/')
            print(f"{lgen.my_time()} General uut_model:{uut_model}")
            if self.gaSet['dut_fam']['wanPorts'] == '4U2S' and re.search('SF-1P/superset_fallback', uut_model):
                uut_model = self.gaSet['dutFullName']
            elif self.gaSet['dut_fam']['wanPorts'] == '2U' and re.search('SF-1P/fallback', uut_model):
                uut_model = self.gaSet['dutFullName']
            if uut_model != self.gaSet['dutFullName']:
                self.gaSet['fail'] = f"The Model is \'{uut_model}\'. Should be \'{self.gaSet['dutFullName']}\'"
                return -1

        m = re.search(r'Address\s+:\s+([A-F\d\-]+)\s', rlcom.buffer)
        if m is None:
            self.gaSet['fail'] = "Read MAC Address fail"
            return -1
        uut_mac = m[1].strip()
        print(f"{lgen.my_time()} uut_mac:{uut_mac}")
        u0_mac = uut_mac.replace('-', ':')
        print(f"{lgen.my_time()} uut_mac:{uut_mac} u0_mac:{u0_mac} eeprom_mac:{eeprom_mac}")
        if u0_mac != eeprom_mac:
            mac_minus1 = hex(int(uut_mac.replace('-', ''), base=16) - 1).upper()[2:]  # 18:06:F5:E2:4B:B3 -> 1806F5E24BB2
            uut_mac = ':'.join(mac_minus1[i:i + 2] for i in range(0, 12, 2))       # 18:06:F5:E2:4B:B2
            print(f"{lgen.my_time()} uut_mac:{uut_mac} eeprom_mac:{eeprom_mac}")
            if uut_mac != eeprom_mac:
                self.gaSet['fail'] = f"The MAC is \'{uut_mac}\'. Should be \'{eeprom_mac}\'"
                return -1

        return 0


