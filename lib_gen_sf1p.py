import os
import re
import webbrowser
from pathlib import Path
import json
from datetime import datetime
import time
import glob
from rad_apps import *
import lib_UsbPio
from RL import rl_com
import Gui_SF1P


class Gen:
    def __init__(self, main_obj):
        self.main_obj = main_obj

    def open_history(self):
        new = 2  # open in a new tab, if possible
        url = "history.html"
        webbrowser.open(url, new=new)

    def my_time(self):
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")

    def get_dbr_name(self, id_number, *event):
        # print(f'\n{self.my_time(Gen)} get_dbr_name barcode:{id_number}')
        retrIdTra = RetriveIdTraceData()
        data = retrIdTra.get_value(id_number, "OperationItem4Barcode")
        self.dbr_name = None
        if data:
            self.dbr_name = data['item']
            # print(f'dbrName:{dbr_name}')
        else:
            print(f'No dbrName for {id_number}')
        print(f'{Gen.my_time(Gen)} get_dbr_name dbrName:{self.dbr_name}')
        return self.dbr_name

    def get_mrkt_name(self, id_number, *event):
        # print(f'\n{self.my_time(Gen)} get_mrkt_name barcode:{id_number}')
        retrIdTra = RetriveIdTraceData()
        data = retrIdTra.get_value(id_number, "MKTItem4Barcode")
        self.mrkt_name = None
        if data:
            self.mrkt_name = data['MKT Item']
            # print(f'mrkt_name:{mrkt_name}')
        else:
            print(f'No mrkt_name for {id_number}')
        print(f'{Gen.my_time(Gen)} get_mrkt_name mrkt_name:{self.mrkt_name}')
        return self.mrkt_name

    def get_csl(self, id_number, *event):
        # print(f'\n{self.my_time(Gen)} get_csl barcode:{id_number}')
        retrIdTra = RetriveIdTraceData()
        data = retrIdTra.get_value(id_number, "CSLByBarcode")
        self.csl = None
        if data:
            self.csl = data['CSL']
            # print(f'csl:{csl}')
        else:
            print(f'No csl for {id_number}')
        print(f'{Gen.my_time(Gen)}get_csl csl:{self.csl}')
        # print(f'getcsl, {self}')
        return self.csl

        gaSet['dutFullName'] = dbr_name
        gaSet['dutInitName'] = re.sub('/', '.', dbr_name) + '.json'
        gaSet['id_number'] = id_number
        gaSet['root'].title(f"{gaSet['gui_num']}: {dbr_name}")
        di = Gen.read_unit_init(self, gaSet)
        # print(di)

        # print(f'get_dbr_name self: {self}') # DA1000835558
        # Gen.retrive_dut_fam(self, gaSet) ## done in build_tests

        Gen.build_tests(Gen, gaSet)
        gui_sf1p.App.my_statusbar.sstatus("Ready")

    def retrive_dut_fam(self, main_obj):
        print(f'\n{Gen.my_time(Gen)} retrive_dut_fam')
        fields = main_obj.gaSet['dbr_name'].split('/')
        dbr_name = main_obj.gaSet['dbr_name'] + '/'
        print(main_obj.gaSet['dbr_name'], dbr_name)
        # print(f'retrive_dut_fam, {self}')

        if 'HL' in fields:
            fields.remove('HL')

        sf_ma = re.search(r'([A-Z0-9\-\_]+)/E?', dbr_name)
        sf = sf_ma.group(1)
        # print(f'sf:{sf}')
        if sf in ['SF-1P', 'ETX-1P', 'SF-1P_ICE', 'ETX-1P_SFC', 'SF-1P_ANG']:
            main_obj.gaSet['prompt'] = '-1p#'
        elif sf == 'VB-101V':
            main_obj.gaSet['prompt'] = 'VB101V#'
        else:
            return f'Wrong product: {main_obj.gaSet["dbr_name"""]}'
        fields.remove(sf)

        if sf in ['ETX-1P', 'ETX-1P_SFC']:
            box = 'etx'
            ps_ma = re.search(r'1P/([A-Z0-9]+)/', dbr_name)
            if ps_ma is None:
                ps_ma = re.search(r'1P_SFC/([A-Z0-9]+)/', dbr_name)
            ps = ps_ma.group(1)
            wanPorts = "1SFP1UTP"
            lanPorts = "4UTP"
        else:
            box = re.search(r'P[_A-Z]*/(E\d)/', dbr_name).group(1)
            ps = re.search(r'E\d/([A-Z0-9]+)/', dbr_name).group(1)

            wanPorts_ma = re.search(r'/(2U)/', dbr_name)
            if wanPorts_ma is None:
                wanPorts_ma = re.search(r'/(4U2S)/', dbr_name)
                if wanPorts_ma is None:
                    wanPorts_ma = re.search(r'/(5U1S)/', dbr_name)
            wanPorts = wanPorts_ma.group(1)
            lanPorts = "NotExists"

        main_obj.gaSet['box'] = box
        main_obj.gaSet['ps'] = ps
        main_obj.gaSet['wanPorts'] = wanPorts
        main_obj.gaSet['lanPorts'] = lanPorts
        if box in fields:
            fields.remove(box)
        fields.remove(ps)
        if wanPorts in fields:
            fields.remove(wanPorts)
        if lanPorts in fields:
            fields.remove(lanPorts)

        serPort_ma = re.search(r'/(2RS)/', dbr_name)
        if serPort_ma is None:
            serPort_ma = re.search(r'/(2RSM)/', dbr_name)
            if serPort_ma is None:
                serPort_ma = re.search(r'/(1RS)/', dbr_name)
                if serPort_ma is None:
                    serPort_ma = re.search(r'/(2RMI)/', dbr_name)
                    if serPort_ma is None:
                        serPort_ma = re.search(r'/(2RSI)/', dbr_name)
        if serPort_ma is None:
            main_obj.gaSet['serPort'] = 'NotExists'
        else:
            main_obj.gaSet['serPort'] = serPort_ma.group(1)
        if main_obj.gaSet['serPort'] in fields:
            fields.remove(main_obj.gaSet['serPort'])

        serPortCsp = re.search(r'/(CSP)/', dbr_name)
        if serPortCsp is None:
            main_obj.gaSet['serPortCsp'] = 'NotExists'
        else:
            main_obj.gaSet['serPortCsp'] = serPortCsp.group(1)
        if main_obj.gaSet['serPortCsp'] in fields:
            fields.remove(main_obj.gaSet['serPortCsp'])

        main_obj.gaSet['poe'] = 'NotExists'
        if main_obj.gaSet['poe'] in fields:
            fields.remove(main_obj.gaSet['poe'])

        main_obj.gaSet['plc'] = 'NotExists'
        if main_obj.gaSet['plc'] in fields:
            fields.remove(main_obj.gaSet['plc'])

        main_obj.gaSet['cellType'] = 'NotExists'
        main_obj.gaSet['cellQty'] = 'NotExists'
        for cell in ['HSP', 'L1', 'L2', 'L3', 'L4']:  # 'L450A', '5G']
            qty = len([i for i, x in enumerate(dbr_name.split('/')) if x == cell])
            # print(f'cell{cell}, qty:{qty}')
            if qty > 0:
                main_obj.gaSet['cellType'] = cell
                main_obj.gaSet['cellQty'] = qty
        if main_obj.gaSet['cellType'] in fields:
            fields.remove(main_obj.gaSet['cellType'])
        if main_obj.gaSet['cellType'] in fields:
            fields.remove(main_obj.gaSet['cellType'])

        gps = re.search(r'/(G)/', dbr_name)
        if gps is None:
            main_obj.gaSet['gps'] = 'NotExists'
        else:
            main_obj.gaSet['gps'] = gps.group(1)
        if main_obj.gaSet['gps'] in fields:
            fields.remove(main_obj.gaSet['gps'])

        wifi_ma = re.search(r'/(WF)/', dbr_name)
        if wifi_ma is not None:
            main_obj.gaSet['wifi'] = 'WF'
        else:
            wifi_ma = re.search(r'/(WFH)/', dbr_name)
            if wifi_ma is not None:
                main_obj.gaSet['wifi'] = 'WH'
            else:
                wifi_ma = re.search(r'/(WH)/', dbr_name)
                if wifi_ma is not None:
                    main_obj.gaSet['wifi'] = 'WH'
                else:
                    main_obj.gaSet['wifi'] = 'NotExists'
        if main_obj.gaSet['wifi'] in fields:
            fields.remove(main_obj.gaSet['wifi'])

        dryCon_ma = re.search(r'/(GO)/', dbr_name)
        if dryCon_ma is not None:
            main_obj.gaSet['dryCon'] = 'GO'
        else:
            main_obj.gaSet['dryCon'] = 'FULL'

        rg = re.search(r'/(RG)/', dbr_name)
        if rg is None:
            main_obj.gaSet['rg'] = 'NotExists'
        else:
            main_obj.gaSet['rg'] = 'RG'
        if main_obj.gaSet['rg'] in fields:
            fields.remove(main_obj.gaSet['rg'])

        lora_ma = re.search(r'/(LR[1-6AB])/', dbr_name)
        if lora_ma is None:
            main_obj.gaSet['lora'] = 'NotExists'
            main_obj.gaSet['lora_region'] = 'NotExists'
            main_obj.gaSet['lora_fam'] = 'NotExists'
            main_obj.gaSet['lora_band'] = 'NotExists'
        else:
            lora = lora_ma.group(1)
            main_obj.gaSet['lora'] = lora
            if lora == 'LR1':
                main_obj.gaSet['lora_region'] = 'eu433'
                main_obj.gaSet['lora_fam'] = '4XX'
                main_obj.gaSet['lora_band'] = 'EU 433'
            elif lora == 'LR2':
                main_obj.gaSet['lora_region'] = 'eu868'
                main_obj.gaSet['lora_fam'] = '8XX'
                main_obj.gaSet['lora_band'] = 'EU 863-870'
            elif lora == 'LR3':
                main_obj.gaSet['lora_region'] = 'au915'
                main_obj.gaSet['lora_fam'] = '9XX'
                main_obj.gaSet['lora_band'] = 'AU 915-928 Sub-band 2'
            elif lora == 'LR4':
                main_obj.gaSet['lora_region'] = 'us902'
                main_obj.gaSet['lora_fam'] = '9XX'
                main_obj.gaSet['lora_band'] = 'US 902-928 Sub-band 2'
            elif lora == 'LR6':
                main_obj.gaSet['lora_region'] = 'as923'
                main_obj.gaSet['lora_fam'] = '9XX'
                main_obj.gaSet['lora_band'] = 'AS 923-925'
            elif lora == 'LRA':
                main_obj.gaSet['lora_region'] = 'us915'
                main_obj.gaSet['lora_fam'] = '9XX'
                main_obj.gaSet['lora_band'] = 'US 902-928 Sub-band 2'
            elif lora == 'LRB':
                main_obj.gaSet['lora_region'] = 'eu868'
                main_obj.gaSet['lora_fam'] = '8XX'
                main_obj.gaSet['lora_band'] = 'EU 863-870'
        if main_obj.gaSet['lora'] in fields:
            fields.remove(main_obj.gaSet['lora'])

        mem = re.search(r'/2R/', dbr_name)
        if mem is not None:
            main_obj.gaSet['mem'] = 2
            fields.remove('2R')
        else:
            main_obj.gaSet['mem'] = 1

        main_obj.gaSet['fields'] = fields
        print(f'retrive dut fam {main_obj.gaSet}')
        print(f'dbr_name:{dbr_name} fields:{fields}')


        return True

    def get_dbr_sw(self, main_obj):
        get_dbr_sw_obj = GetDbrSW()
        id_number = main_obj.gaSet['id_number']
        sws = get_dbr_sw_obj.getDbrSw(id_number)
        main_obj.gaSet['sw_boot'] = None
        main_obj.gaSet['sw_app'] = None
        # print(vars(gen_obj.main_tester))
        for lin in sws.split('\n'):
            # print(f'aaa {lin}')
            sw_fields = list(lin.split(' '))
            # print(f'aaa sw_fields {sw_fields}')
            if sw_fields[0][0:2] == 'SW':
                # print(f'fff {sw_fields}')
                sw_val = sw_fields[2]
                # print(f'bbb sw_val {sw_val}_{sw_val[0]}_')
                if sw_val[0] == 'B':
                    main_obj.gaSet['sw_boot'] = sw_val
                else:
                    main_obj.gaSet['sw_app'] = sw_val

        # print(f'get_dbr_sw {vars(gen_obj.main_tester)}')
        print(f'get dbr sw {main_obj.gaSet}')

    def edit_mdm_file(self):
        mdm_name = 'CellularModemFWs.json'
        pa = os.path.join(os.getcwd(), 'TeamLeaderFiles')
        fn = os.path.join(pa, mdm_name)

        try:
            process = subprocess.run("notepad.exe " + fn,
                                     shell=False, check=True, stdout=subprocess.PIPE, universal_newlines=True,
                                     stderr=subprocess.PIPE)
            stdout = process.stdout.rstrip()
            # print(f'stdout: {stdout}')
            returncode = process.returncode
            # print(f'returncode: {returncode}')
            return True
        except Exception as error:
            print(f'error at edit_mdm_file: {error}')
            return False

    def loadModemsFWfile(self):
        fn = Path(os.path.join(os.getcwd(), 'TeamLeaderFiles', 'CellularModemFWs.json'))
        try:
            with open(fn, 'r') as fi:
                fw_dict = json.load(fi)
        except Exception as e:
            raise Exception("e")
        return fw_dict

    def read_hw_init(self, gui_num):
        print(f'read_hw_init')
        host = socket.gethostname()
        Path(host).mkdir(parents=True, exist_ok=True)
        hw_file = Path(os.path.join(host, f"HWinit.{gui_num}.json"))
        if not os.path.isfile(hw_file):
            hw_dict = {
                'comDut': 'COM8',
                'comSer1': 'COM2',
                'comSer2': 'COM6',
                'comSer485': 'COM6',
                'pioBoxSerNum': "FT31CTG9",
            }
            # di = {**hw_dict, **dict2}

            with open(hw_file, 'w') as fi:
                # json.dump(hw_dict, fi, indent=2, sort_keys=True)
                json.dump(hw_dict, fi, indent=2, sort_keys=True)

        try:
            with open(hw_file, 'r') as fi:
                hw_dict = json.load(fi)
        except Exception as e:
            # print(e)
            # raise(e)
            raise Exception("e")

        return hw_dict

    def read_init(self, main_obj, gui_num):
        print(f'read_init')
        # print(f'read_init script_dir {os.path.dirname(__file__)}')
        host = socket.gethostname()
        Path(host).mkdir(parents=True, exist_ok=True)        
        ini_file = Path(os.path.join(host, "init." + str(gui_num) + ".json"))
        # print(f'read_init Path(host) {Path(host)}')
        if os.path.isfile(ini_file) is False:
            dicti = {
                'geom': '+210+210'
            }
            self.save_init(dicti, main_obj, gui_num)

        try:
            with open(ini_file, 'r') as fi:
                dicti = json.load(fi)
        except Exception as e:
            # print(e)
            # raise(e)
            raise Exception("e")

        # print(f'read_init {ini_file} {dicti}')
        return dicti

    def save_init(self, main_obj, gui_num):
        print(f'save_init, main_obj:{main_obj}, gui_num:{gui_num}')
        host = socket.gethostname()
        Path(host).mkdir(parents=True, exist_ok=True)
        ini_file = Path(os.path.join(host, "init." + str(gui_num) + ".json"))

        di = {}
        try:
            # di['geom'] = "+" + str(dicti['root'].winfo_x()) + "+" + str(dicti['root'].winfo_y())
            di['geom'] = self.get_xy(main_obj.gaSet['root'])
        except:
            di['geom'] = "+230+233"

        try:
            with open(ini_file, 'w') as fi:
                json.dump(di, fi, indent=2, sort_keys=True)
                # json.dump(gaSet, fi, indent=2, sort_keys=True)
        except Exception as e:
            print(e)
            raise (e)

    def get_xy(top):
        return str("+" + str(top.winfo_x()) + "+" + str(top.winfo_y()))

    def power(self, main_obj, ps, state):
        # print(f'{self.my_time(Gen)} Power PS- main_obj:{main_obj}  ps:{ps}, state:{state}, args:{args}')
        print(f'Power ps:{ps}, state:{state}')
        pio = lib_UsbPio.UsbPio()
        channel = pio.retrive_usb_channel(main_obj.gaSet['pioBoxSerNum'])
        print(f'gen power channel:{channel}')

        group = 'RBA'
        ret = lib_UsbPio.UsbPio.osc_pio(pio, channel, ps, group, state)
        return 0

    def gui_Power(self, main_obj, ps, state):
        print(f"gui_Power main_obj:{main_obj} ps:{ps}, state:{state}")
        self.power(self, main_obj, ps, state)

    def gui_PowerOffOn(self, main_obj, ps):
        self.gui_Power(self, main_obj, ps, 0)
        time.sleep(2)
        self.gui_Power(self, main_obj, ps, 1)

    def gui_MuxMngIO(self, main_jbj, mode):
        print(f"gui_MuxMngIO mode:{mode}")

    def read_pio(self, main_obj, port):
        #print(f"read_pio port:{port}")
        pio = lib_UsbPio.UsbPio()
        channel = pio.retrive_usb_channel(main_obj.gaSet['pioBoxSerNum'])
        group = 'PORT'
        ret = lib_UsbPio.UsbPio.osc_pio(pio, channel, port, group, 'GET').split('.')[2].split('_')[2]
        #print(f"read_pio ret:{ret}")
        return ret

    def mux_switch_box(self, main_obj, relay, state):
        # print(f"mux_switch_box relay:{relay} state:{state}")
        pio = lib_UsbPio.UsbPio()
        channel = pio.retrive_usb_channel(main_obj.gaSet['pioBoxSerNum'])
        group = 'SPDT'
        ret = lib_UsbPio.UsbPio.osc_pio(pio, channel, relay, group, state)
        # print(f"mux_switch_box relay:{relay} state:{state} ret:{ret}")

    def mux_mng_io(self, main_obj, mode):
        """ mode src(1-6, nc)_dst(Pc): '6_Gen', '1_PC' """
        print(f"mux_mng_io mode:{mode}")
        pio = lib_UsbPio.UsbPio()
        channel = pio.retrive_usb_channel(main_obj.gaSet['pioBoxSerNum'])
        group = 'PORT'

        chs = []
        src = int(mode.split('To')[0]) # chs 1 - 6, nc
        dst = mode.split('To')[1] # PC (ch 14) or Gen (ch 13)
        if dst == "Pc":
            chs = [src, 14]
        elif dst == 'Gen':
            chs = [src, 13]

        ret1 = lib_UsbPio.UsbPio.mmux(pio, channel, 1, group, "AllNC")
        ret2 = lib_UsbPio.UsbPio.mmux(pio, channel, 1, group, "BusState", "A,B C D")
        if src == 'nc':
            # do nothing, already disconnected
            ret3 = 0
        else:
            ret3 = lib_UsbPio.UsbPio.mmux(pio, channel, 1, group, "ChsCon", chs)
        print(f'mux_mng_io mode:{mode}, ret1:{ret1}, ret2:{ret2}, ret3:{ret3}')

    def open_teraterm(main_obj, comName):
        com = main_obj.gaSet[comName][3:]  # COM8 -> 8 (cut off COM)
        print(f"open_teraterm comName:{comName}, com:{com}")

        command = os.path.join('C:/Program Files (x86)', 'teraterm', 'ttermpro.exe')
        command = str(command) + ' /c=' + str(com) + ' /baud=115200'
        # os.startfile(command)
        subprocess.Popen(command)
        print(command)

    def add_to_log(self, main_obj, txt):
        with open(main_obj.gaSet['log'], 'a') as log:
            if txt == '':
                text = f'\n'
            else:
                text = f'{self.my_time()}..{txt}\n'
            log.write(text)

    def open_rl(self, main_obj):
        com = rl_com.RLCom(main_obj.gaSet['comDut'], 115200)
        main_obj.gaSet['com_obj'] = com
        return com.open()

    def close_rl(self, main_obj):
        if main_obj.gaSet['com_obj']:
            main_obj.gaSet['com_obj'].close()

    def wait(self, main_obj, txt, dly, color='white'):
        """wait main_obj, 'txt', dly, color"""
        print(f'\n{self.my_time()} Start wait {txt} {dly} sec')
        main_obj.my_statusbar.sstatus(txt, color)
        for i in range(dly, 0, -1):
            self.main_obj.gaSet['root'].update()
            if main_obj.gaSet['act'] == 0:
                return -2
            main_obj.my_statusbar.runTime(i)
            time.sleep(1)
        main_obj.my_statusbar.runTime('')
        main_obj.my_statusbar.sstatus('')
        print(f'{self.my_time()} Finish wait {txt} {dly} sec\n')
        return 0

    def com_send(self, sent, exp='', timeout=10):
        self.main_obj.gaSet['root'].update()
        if self.main_obj.gaSet['act'] == 0:
            return -2
        com = self.main_obj.gaSet['com_obj']
        return com.send(f"{sent}", exp, timeout)

    def toggle_comDut(self):
        dut_name = self.main_obj.gaSet['dbr_name']
        print(f'\n{self.my_time()} ToggleComDut {dut_name}')
        if self.main_obj.gaSet['box'] == 'etx' or self.main_obj.gaSet['serPort']=='1RS':
            self.main_obj.gaSet['comDut'] = self.main_obj.gaSet['comSer1']
        else:
            self.main_obj.gaSet['comDut'] = self.main_obj.gaSet['comSer2']
        print(f"comDut:{self.main_obj.gaSet['comDut']}")
        Gui_SF1P.MenuBar.termmenu.entryconfigure(0, label=f'UUT: {self.main_obj.gaSet["comDut"]}')




if __name__ == '__main__':
    for id in ['DC1002313829', "DA1000878872", 'DC1002313485']:
        dbr_name = Gen.get_dbr_name(Gen, id)
        Gen.retrive_dut_fam(Gen)
