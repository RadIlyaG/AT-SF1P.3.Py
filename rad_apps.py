import socket
import ssl
import requests
import json
import os
import re
import subprocess
import sqlite3
from sqlite3 import Error
import paramiko
import time
from subprocess import CalledProcessError, check_output


class RetriveIdTraceData:
    def __init__(self):
        self.hostname = 'ws-proxy01.rad.com'
        self.port = '10211'  # '8445'

    def get_value(self, barcode, command):
        barc = barcode[0:11]
        if command == "CSLByBarcode" or command == "MKTItem4Barcode" or command == "OperationItem4Barcode":
            barcode = barc
            traceabilityID = "null"
        elif command == "PCBTraceabilityIDData":
            barcode = "null"
            traceabilityID = barc

        context = ssl.create_default_context()
        url = 'http://' + self.hostname + ':' + self.port + '/ATE_WS/ws/rest/'
        param = command + "?" + "barcode=" + barcode + "&" + "traceabilityID=" + traceabilityID
        url = url + param
        headers = {'Authorization': 'Basic d2Vic2VydmljZXM6cmFkZXh0ZXJuYWw='}
        payload = {'TraceID': traceabilityID}
        print(f'url:{url}')
        try:
            with socket.create_connection((self.hostname, self.port)) as sock:
                r = requests.get(url, headers=headers, params=payload, verify=False)
                #print(f'status_code:{r.status_code} txt:{r.text}')
                data = json.loads(r.text)
                #print(f'data:{data}')
                inside_data = data[command][0]
                #print(f'inside_data:{inside_data}')
                return inside_data

        except Exception as error:
            gMessage = f'Error during conn: {error}'
            print(f'gMessage:{gMessage}')
            return False

class GetDbrSW:
    def __init__(self):
        pass

    def getDbrSw(self, barcode):
        pa = os.path.join('c:/radapps', 'SWVersions4IDnumber.jar')
        print(f'pa:{pa} BARCODE:{barcode}')
        try:
            process = subprocess.run("java.exe -jar " + pa + " " + barcode,
                                     shell=False, check=True, stdout=subprocess.PIPE, universal_newlines=True,
                                     stderr=subprocess.PIPE)
            stdout = process.stdout.rstrip()
            # print(f'stdout: {stdout}')
            returncode = process.returncode
            # print(f'returncode: {returncode}')
            return stdout
        except Exception as error:
            print(f'error: {error}')
            return False


class EmplName:
    def __init__(self):
        pass

    def sqlite_create_connection(db_file):
        """ create a database connection to the SQLite database
            specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(f'sqlite_create_connection error: {e}')

        return conn

    def sqlite_get_empl_name(self, dbFile, empId):
        conn = self.sqlite_create_connection(dbFile)
        # print(f'conn: {conn}')
        with conn:
            c = conn.cursor()
            c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='tbl' ''')
            if c.fetchone()[0] == 0:
                c.execute("""CREATE TABLE tbl(EmpID, EmpName)""")
                return None

            s = "select EmpName from tbl where EmpID glob " + empId
            print(f's: {s}')
            cur = c.execute(s)
            for row in cur:
                na = row[0]
                return (f'{na}')

    def sqlite_add_empl_name(self, dbFile, empId, empName):
        conn = self.sqlite_create_connection(dbFile)
        with conn:
            s = "INSERT INTO tbl VALUES (" + empId + "," + "\'" + empName + "\'" + ")"
            print(f'sqlite_add_empl_name: {s}')
            c = conn.cursor()
            c.execute(s)
            conn.commit()
            return True

    def get_operator(emp_id):
        radAppsPath = r'c:/RadApps'
        pa = os.path.join(radAppsPath, 'GetEmpName.exe')
        print(f'pa:{pa} EmplID:{emp_id}')
        try:
            process = subprocess.run(pa + " " + emp_id,
                                     shell=False, check=True, stdout=subprocess.PIPE, universal_newlines=True,
                                     stderr=subprocess.PIPE)
            res_file = os.path.join(radAppsPath, emp_id + '.txt')
            print(f'res_file: {res_file}')
            try:
                with open(res_file) as empNaF:
                    emp_name = empNaF.read()
            except Exception as err:
                emp_name = err
            finally:
                os.remove(res_file)
            return str(emp_name).rstrip()
        except Exception as error:
            print(f'get_operator error: {error}')
            return False


class Mac:
    def __init__(self):
        self.hostname = 'ws-proxy01.rad.com'
        self.port = '10211'

    def check_mac(b, m):
        """ check_mac
        Inputs: ID barcode
                MAC address
        Outputs: True, if the ID barcode has not link to any MAC or if the ID barcode and the MAC are connected
                "BARCODE already connected to MAC, if the Id barcode already connected to other MAC"
                 """
        # FB1000F5815 0020D2268EAA

        radAppsPath = r'c:/RadApps'
        pa = os.path.join(radAppsPath, 'CheckMAC.jar')
        # print(f'RadAppsPath:{RadAppsPath}  pa:{pa}')
        process = subprocess.run("java.exe -jar  " + pa + " " + b + " " + m,
                                 shell=False, check=True, stdout=subprocess.PIPE, universal_newlines=True,
                                 stderr=subprocess.PIPE)
        stdout = process.stdout.rstrip()
        # returncode = process.returncode
        # print(f'output: {b}, {m}')
        # print(f'process: {process}')
        # print(f'stdout: {stdout}')
        # print(f'returncode: {returncode}')#, end='_'
        stderr = process.stderr.rstrip()
        # print(f'stderr: "{stderr}"')
        # if stdout == "":
        #     return True
        if stderr != '0' and stderr != "":
            return "Error"
        if stdout == "" and stderr == '0':
            # return(f'OK, or the {b} has no any MAC, or it has {m}')
            return "noLink"
        else:
            m = re.search('(\w+$)', stdout)  # $ at the end Anchors a match at the end of a string, also \Z
            #     # print(f'm is {m}')
            if m:
                ma = m.group(1)
                # print(f'{barcode} already connectred to {ma}')
                # return(f'{b} already connected to {ma}')
                return (ma)
            return False

    def mac_reg(*args):
        # mac1, barcode, mac2="", sp1="DISABLE", sp2="DISABLE", sp3="DISABLE", sp4="DISABLE",
        #                 sp5="DISABLE", sp6="DISABLE", sp7="DISABLE", sp8="DISABLE", imei1="", imei2=""
        radAppsPath = r'c:/RadApps'
        cmd = os.path.join(radAppsPath, 'MACReg_2Mac_2IMEI.exe')

        print(f'cmd:{cmd} *args:{args}')
        arg = args[0]
        cmd += f" /{arg['mac1']}"
        cmd += f" /{arg['mac2']}"
        cmd += f" /{arg['barcode']}"
        cmd += f" /DISABLE"
        cmd += f" /DISABLE"
        cmd += f" /DISABLE"
        cmd += f" /DISABLE"
        cmd += f" /DISABLE"
        cmd += f" /DISABLE"
        cmd += f" /DISABLE"
        cmd += f" /DISABLE"
        if arg['imei1'] != 'NotExists':
            cmd += f" /{arg['imei1']}"
        if arg['imei2'] != 'NotExists':
            cmd += f" /{arg['imei2']}"
        print(f'cmd:{cmd}')
        try:
            process = subprocess.run(cmd, shell=False, check=True, stdout=subprocess.PIPE, universal_newlines=True,
                stderr=subprocess.PIPE)
            return True
        except Exception as error:
            print(f'mac_reg error: {error}')
            return False

    def mac_unreg(self, barcode, mac=''):
        barc = barcode[0:11]
        # context = ssl.create_default_context()
        url = 'http://' + self.hostname + ':' + self.port + '/ATE_WS/ws/rest/'
        param = 'DisconnectBarcode?mac=' + mac + '&idNumber=' + barcode
        url = url + param
        headers = {'Authorization': 'Basic d2Vic2VydmljZXM6cmFkZXh0ZXJuYWw='}
        print(f'url:{url}')
        try:
            with socket.create_connection((self.hostname, self.port)) as sock:
                r = requests.get(url, headers=headers, verify=True)
                # print(f' status_code:{r.status_code} txt:{r.text}')
                return r.text

        except Exception as error:
            gMessage = f'Error during conn: {error}'
            print(f'gMessage:{gMessage}')
            return error


class AteDecryptor:
    def __init__(self):
        pass

    def get_password(self, kc, type):
        pa = os.path.join('c:/radapps', 'atedecryptor.exe')
        print(f'get_password kc:{kc} type:{type}')
        try:
            process = subprocess.run(pa + " " + kc + " " + type,
                                     shell=False, check=True, stdout=subprocess.PIPE, universal_newlines=True,
                                     stderr=subprocess.PIPE)
            return process.stdout.rstrip()
        except Exception as err:
            print(f'get_password err:{err}')
            return None

class SSH:
    def __init__(self):
        self.ssh = None
        self.chan = None

    def connect_to(self, host='169.254.1.1', port=22, username='su', password='1234'):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.timeout = 5
        try:
            self.ssh.connect(hostname=host, port=port, username=username, password=password, timeout=3)
            self.chan = self.ssh.invoke_shell()
            self.chan.timeout = 5
            # print(f'ssh_perf ret of connect_to chan :{chan}')
            try:
                self.chan.send(b'\n\r')
                return 0
            except Exception as err:
                return err

        except Exception as err:
            return err

    def do_command(self, cmd):
        self.chan.send(cmd)
        try:
            for i in range(1, 11):
                if self.chan.recv_ready():
                    break
                else:
                    print(f'Not ready {i}, {self.chan.timeout}')
                    time.sleep(0.21)

            data = self.chan.recv(100000).decode('utf-8')
            print(f'{len(data)} data:<{data}>')
            return 0, data
        except Exception as err:
            return -1, err

    def close_ch(self):
        try:
            self.chan.close()
            self.ssh.close()
            ret = 0
        except Exception as ex:
            print(ex)
            ret = -1
        return ret

if __name__ == '__main__':
    # mac = Mac()
    # ret = mac.mac_unreg('EA100463652')
    # print(f'ret:{ret}')

    ssh = SSH()
    ssh.connect_to()

    if False:
        retrIdTra = RetriveIdTraceData()
        data = retrIdTra.get_value('DF100148093', "OperationItem4Barcode")
        if data:
            dbr_name = data['item']
            print(f'dbr_name:{dbr_name}')
        else:
            print(f'No dbr_name for DF10014809')

    if False:
        data = retrIdTra.get_value('DF1001480939', "CSLByBarcode")
        csl = data['CSL']
        print(f'csl:{csl}')

        data = retrIdTra.get_value('DF1001480939', "MKTItem4Barcode")
        mrktName = data['MKT Item']
        print(f'mrktName:{mrktName}')

        data = retrIdTra.get_value('21181408', "PCBTraceabilityIDData")
        for par in ['rownum', 'po number', 'sub_po_number', 'pdn', 'product', 'pcb_pdn', 'pcb']:
            print(f'value of {par}:{data[par]}')
