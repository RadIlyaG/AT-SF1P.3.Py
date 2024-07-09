import os
import time
from pathlib import Path
import requests
import subprocess
import re
import socket
from lib_gen_sf1p import Gen
from lib_put_sf1p import Put


class Lora(Gen, Put):
    def __init__(self, main_obj):
        Gen.__init__(self, main_obj)
        Put.__init__(self, main_obj)
        self.main_obj = main_obj
        self.server_poll_fld = os.path.join('//', self.main_obj.gaSet['lora_server_host'], '/c$/LoraDirs/LoraServerPoll')
        self.server_chirpStack_logs_fld = os.path.join('//', self.main_obj.gaSet['lora_server_host'],
                                            '/c$/LoraDirs/ChirpStackLogs')
        self.chirpStack_ip_gw = '1806f5fffeb80'

    def lora_module_conf(self):
        print(f'\nlora_module_conf')
        buf = ''
        gen_obj = Gen(self.main_obj)
        put_obj = Put(self.main_obj)
        com = self.main_obj.gaSet['com_obj']
        ret = put_obj.login()
        print(f'lora_module_conf ret of login:{ret}')
        if ret == 0:
            self.main_obj.my_statusbar.sstatus(f'Configuration LoRa Module')
            ret = com.send("exit all\r", "-1p#")

        if ret == 0:
            ret = com.send("configure\r", "-1p>conf")
        if ret == 0:
            ret = com.send("router 1\r", "er\(1\)")
        if ret == 0:
            ret = com.send("interface 32\r", "ace\(32\)")
        if ret == 0:
            ret = com.send("shutdown\r", "ace\(32\)", 44)
        if ret == 0:
            ret = com.send("no address 169.254.1.1/16\r", "ace\(32\)")
        if ret == 0:
            ret = com.send(f'address {self.main_obj.gaSet["ip4lora"]}/24\r", "ace\(32\)')
        if ret == 0:
            ret = com.send("no shutdown\r", "ace\(32\)", 44)
            if ret == 0:
                ret = com.send("\r", "ace\(32\)", 44)

        if ret == -1:
            self.main_obj.gaSet["fail"] = 'Configuration LoRa Module fail'

        if ret == 0:
            obt = 0
            self.main_obj.my_statusbar.sstatus(f'Configuration LoRa Module"')
            max_wait = 300
            gen_obj.mux_mng_io(self.main_obj, '6_PC')
            start_sec = time.time()
            for i in range(1,101):
                if self.main_obj.gaSet["act"] == 0:
                    return -2
                #  now_sec = time.time()
                wait_sec = time.time() - start_sec
                if wait_sec > max_wait:
                    self.main_obj.gaSet["fail"] = f'DHCP IP not Obtained after {max_wait} seconds'
                    ret = -1
                    break
                print(f'Wait for DHCP: <{wait_sec}>, i:<{i}>')
                ret = com.send("show status\r", "ace\(32\)", 44)
                if 'Lease Obtained' in com.buffer and 'Admin:Up' in com.buffer and 'Oper: Up' in com.buffer :
                    ret =com.send("\r", "ace\(32\)")
                    obt = 1
                    break
                if i == 20 or i == 40 or i == 60 or i == 80:
                        gen_obj.mux_mng_io(self.main_obj, 'nc_PC')
                        time.sleep(3)
                        gen_obj.mux_mng_io(self.main_obj, '6_PC')
                if ret == -1:
                    self.main_obj.gaSet["fail"] = f'Read Status fail'
                    break
                time.sleep(3)
            if obt == 0:
                self.main_obj.gaSet["fail"] = f'DHCP IP not Obtained'

        if ret == 0:
            ret = com.send("exit\r", "fig>router")
            ret = com.send("dns-name-server 8.8.8.8\r", "fig>router")
        if ret == 0:
            ret = com.send("exit\r", "ofig")
        if ret == 0:
            ret = com.send("system\r", "ofig>system")
        if ret == 0:
            ret = com.send("date-and-time ntp\r", "time>ntp")
        if ret == 0:
            ret = com.send("server 1\r", "ver\(1\)")
        if ret == 0:
            ipc = subprocess.run('ipconfig.exe',
                                 shell=False, check=True, stdout=subprocess.PIPE, universal_newlines=True,
                                 stderr=subprocess.PIPE)
            m = re.search('172.18.9.*[\w\s\d\:\.]+', str(ipc.stdout))
            if not m:
                self.main_obj.gaSet["fail"] = f'Read ipconfig fail'
                ret = -1
            else:
                mg = re.search('Gateway[.:\s]+([\d\.]+)', m.group(0))
                dg = mg.group(1)

        if ret == 0:
            ret = com.send(f"address {dg}\r", "ver\(1\)")
        if ret == 0:
            ret = com.send(f"no shutdown\r", "ver\(1\)")
        if ret == 0:
            ret = com.send("exit all\r", "-1p#")
        if ret == 0:
            ret = com.send("configure\r", "-1p>conf")
        if ret == 0:
            ret = com.send("port lora\r", "lora\(1\)")
        if ret == 0:
            ret = com.send(f"frequency plan {self.main_obj.gaSet['lora_region']}\r", "lora\(1\)")
        if ret == 0:
            ret = com.send(f"gateway\r", "lora-gateway")
        if ret == 0:
            ret = com.send(f"shutdown\r", "lora-gateway")
        if ret == 0:
            srvr_ip = self.main_obj.gaSet[f'chirp_stack_ip.{self.main_obj.gaSet["lora_fam"]}']
            ret = com.send(f"server ip-address {srvr_ip} port 1700\r", "lora-gateway")
        if ret == 0:
            lora_type = self.main_obj.gaSet["lora"][-1].lower()
            self.chirpStack_ip_gw += lora_type
            self.chirpStack_ip_gw += socket.gethostname().split('-')[-2]   # at-sf1p-1-10 -> 1
            self.chirpStack_ip_gw += self.main_obj.gaSet['gui_num']
            print(f'LoraModuleConf gateway-id:<{self.chirpStack_ip_gw}>')
            ret = com.send(f"gateway-id string {self.chirpStack_ip_gw}\r", "lora-gateway")
        if ret == -1:
            self.main_obj.gaSet["fail"] = f'Configuration LoRa Module fail'

        return ret

    def lora_gw_mode(self, mode):
        print(f'\nlora_gw_mode mode:{mode}')
        buf = ''
        gen_obj = Gen(self.main_obj)
        com = self.main_obj.gaSet['com_obj']
        ret = self.login()
        print(f'lora_gw_mode ret of login:{ret}')
        if ret == 0:
            self.main_obj.my_statusbar.sstatus(f'Set Lora GateWay Mode to {mode}')
            ret = com.send("exit all\r", "-1p#")
        if ret == 0:
            ret = com.send("configure\r", "-1p>config")
        if ret == 0:
            ret = com.send("port lora 1\r", "\(1\)")
        if ret == 0:
            ret = com.send("gateway\r", "lora-gateway")
        if ret == 0:
            ret = com.send(f"{mode}\r", "lora-gateway")
        if ret == -1:
            self.main_obj.gaSet["fail"] = f'Set Lora GateWay Mode to {mode} fail'
        return ret

    def lora_server_polling(self):
        print(f'\n{self.my_time()}lora_server_polling')
        self.main_obj.my_statusbar.sstatus(f'Polling Lora Server')

        start_sec = time.time()
        max_wait = 30
        while True:
            if self.main_obj.gaSet['act'] == 0:
                return -2
            flags = os.listdir(self.server_poll_fld)
            if len(flags)> 1:
                for flag in flags:
                    os.remove(flag)
                time.sleep(0.2)

            flags = os.listdir(self.server_poll_fld)
            flags_qty = len(flags)
            flag = Path(flags[0]).name
            wait_sec = int(time.time() - start_sec)
            print(f'LoraServerPolling flag:<{flag}> flags_qty:{flags_qty} wifi_net:<{self.main_obj.gaSet["wifi_net"]}> wait_sec:{wait_sec} sec')
            if wait_sec > max_wait:
                self.main_obj.gaSet["fail"] = "Can't get Enqueue to ChirpStack"
                ret = -1
                break

            if flags_qty == 0:
                with open(os.path.join(self.server_poll_fld, self.main_obj.gaSet["wifi_net"]), 'w+'):
                    time.sleep(1)
                ret = 0
                break
            else:
                print(1)
                if flag == self.main_obj.gaSet["wifi_net"]:
                    print(2)
                    ret = 0
                    break
                else:
                    print(3)
                    self.main_obj.gaSet['root'].update()
            time.sleep(5)
        return ret

    def lora_server_release(self):
        print(f'\n{self.my_time()}lora_server_release')
        self.main_obj.my_statusbar.sstatus(f'Release Lora Server')
        try:
            os.remove(os.path.join(self.server_poll_fld, self.main_obj.gaSet["wifi_net"]))
            ret = 0
        except Exception as exp:
            self.main_obj.gaSet['fail'] = exp
            ret = -1
        return ret

    def lora_ping_to_chirpStack(self):
        print(f'\n{self.my_time()}lora_ping_to_chirpStack')
        com = self.main_obj.gaSet['com_obj']
        ip = self.main_obj.gaSet[f'chirp_stack_ip.{self.main_obj.gaSet["lora_fam"]}']
        gen = Gen(self.main_obj)
        gen.wait(self.main_obj, "Wait 5 seconds for Network", 5)
        ret = -1
        for i in range(1,5):
            print(f'Ping {i}')
            ret = gen.com_send(f"ping {ip}\r", '-1p', 15)
            if ret == -2:
                return ret
            elif ret == -1:
                self.main_obj.gaSet['fail'] = f'Send ping to ChirpStack {ip} fail'
                return ret

            ret = -1
            if '5 packets transmitted. 5 packets received, 0% packet loss' in com.buffer:
                ret = 0
                break
            else:
                self.main_obj.gaSet['fail'] = f'Ping to ChirpStack {ip} fail'
                time.sleep(0.5)
        return ret

    def lora_ping(self, to, ip):
        print(f'\n{self.my_time()}lora_ping to:{to}, ip:{ip}')
        com = self.main_obj.gaSet['com_obj']
        gen = Gen(self.main_obj)
        gen.wait(self.main_obj, "Wait 5 seconds for Network", 5)
        ret = -1
        for i in range(1,5):
            print(f'Ping {i}')
            ret = gen.com_send(f"ping {ip}\r", '-1p', 15)
            if ret == -2:
                return ret
            elif ret == -1:
                self.main_obj.gaSet['fail'] = f'Send ping to:{to}, ip:{ip} fail'
                return ret

            ret = -1
            if '5 packets transmitted. 5 packets received, 0% packet loss' in com.buffer:
                ret = 0
                break
            else:
                self.main_obj.gaSet['fail'] = f'Ping to:{to}, ip:{ip} fail'
                time.sleep(0.5)
        return ret

    def config_lora_device(self):
        print(f'\n{self.my_time()}config_lora_device')
        self.main_obj.my_statusbar.sstatus(f'Config Lora Device')
        ret = 0
        dev_rate = ''
        if self.main_obj.gaSet['lora_region'] == 'eu433':
            dev_rate = 'EU433'
        elif self.main_obj.gaSet['lora_region'] == 'eu868':
            dev_rate = 'EU868'
        elif self.main_obj.gaSet['lora_region'] == 'au915' or 'us902' or 'us915':
            dev_rate = 'US915'
        elif self.main_obj.gaSet['lora_region'] == 'as923':
            dev_rate = 'AS923'
        else:
                self.main_obj.gaSet['fail'] = 'RATE is not defined'
                ret = -1
        if ret == 0:
            self.clear_chirpStack_logs()
            url = f"http://{self.main_obj.gaSet['lora_server_ip']}:5000/sendToLora"
            data = {"ConfigLoraDev": dev_rate}
            try:
                requests.post(url, data=data, timeout=10)
                ret = 0
            except Exception as exp:
                print(f'config_lora_device error:{exp}')
                ret = -1
        if ret == 0:
            ret = self.read_chirpStack_logs()

        return ret

    def clear_chirpStack_logs(self):
        print(f'\n{self.my_time()}clear_chirpStack_logs')
        logs = os.listdir(self.server_chirpStack_logs_fld)
        print(f'ClearChirpStackLogs before delete: {logs}')
        for log in logs:
            os.remove(log)
        print(f'ClearChirpStackLogs after delete: {os.listdir(self.server_chirpStack_logs_fld)}')
        return 0

    def read_chirpStack_logs(self, max_wait=20):
        print(f'\n{self.my_time()}read_chirpStack_logs')
        start_sec = time.time()
        while True:
            if self.main_obj.gaSet['act'] == 0:
                return -2
            wait_sec = time.time()
            if wait_sec > max_wait:
                self.main_obj.gaSet['fail'] = 'No result from ChirpStack'
                return -1

            logs = os.listdir(self.server_chirpStack_logs_fld)
            print(f'ClearChirpStackLogs after {wait_sec} sec: {logs}')
            ret = 'na'
            for log in logs:
                tail = Path(log).name
                print(f'ClearChirpStackLogs log:<{log}> tail:<{tail}>')
                if tail == 'OK':
                    ret = 0
                    break
                elif tail == 'FAIL':
                    ret = -1
                    break

            if ret != 'na':
                for log in os.listdir(self.server_chirpStack_logs_fld):
                    os.remove(log)
                break

            time.sleep(2)

        return ret

    def join_lora_device(self):
        print(f'\n{self.my_time()}join_lora_device')
        self.main_obj.my_statusbar.sstatus(f'Join Lora Device')

        self.clear_chirpStack_logs()
        url = f"http://{self.main_obj.gaSet['lora_server_ip']}:5000/sendToLora"
        data = {"JoinLoraDev": ''}
        try:
            requests.post(url, data=data, timeout=10)
            ret = 0
        except Exception as exp:
            print(f'join_lora_device error:{exp}')
            ret = -1

        if ret == 0:
            ret = self.read_chirpStack_logs()
        elif ret == -1:
            self.main_obj.gaSet['fail'] = 'Join LoRa Device fail'

        return ret

    def send_data_to_lora_device(self, data='aabbccdd'):
        print(f'\n{self.my_time()}send_data_to_lora_device {data}')
        self.main_obj.my_statusbar.sstatus(f'Send Data {data} to Lora Device')

        self.clear_chirpStack_logs()
        url = f"http://{self.main_obj.gaSet['lora_server_ip']}:5000/sendToLora"
        data = {"SendDataToLoraDev": data}
        try:
            requests.post(url, data=data, timeout=10)
            ret = 0
        except Exception as exp:
            print(f'send_data_to_lora_device error:{exp}')
            ret = -1

        if ret == 0:
            ret = self.read_chirpStack_logs()
        elif ret == -1:
            self.main_obj.gaSet['fail'] = 'Send_Receive to LoRa Device fail'

        return ret

    def lora_perf(self, data):
        print(f'\n{self.my_time()}lora_perf {data}')
        log = os.path.join(self.server_chirpStack_logs_fld, self.chirpStack_ip_gw, f'{data}.txt')
        print(f'delete log:{log}')
        try:
            os.remove(log)
            ret = 0
        except Exception as exp:
            ret = -1
            self.main_obj.gaSet['fail'] = f'Delete log {log} fail'
        if ret == 0:
            ret = self.send_data_to_lora_device(data)
        if ret == 0:
            print(f'lora_perf after Send <{os.listdir(self.server_chirpStack_logs_fld)}>')
            if os.path.exists(log):
                ret = 0
                self.add_to_log(self.main_obj, f'LogFile: {Path(log).name}')
                try:
                    os.remove(log)
                    res = 0
                except Exception as exp:
                    res = exp
                print(f'LoraPerf res after delete logFile: <{res}>')
            else:
                ret = -1
                self.main_obj.gaSet['fail'] = f"Log File for {self.chirpStack_ip_gw} doesn't exist"

        return ret

