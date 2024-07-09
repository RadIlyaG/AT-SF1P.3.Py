import re
import time
import datetime
import winsound

from packaging import version

import Gui_SF1P
import lib_barcode
import lib_gen_sf1p
import lib_put_sf1p
import lib_etx204
import lib_lora


class AllTests:
    def __init__(self):
        self.test_names_lst = []

    def build_tests(self, main_obj):
        dbr_name = main_obj.gaSet['dbr_name'] + '/'
        test_names_lst = []
        box = main_obj.gaSet['box']
        if False:
            test_names_lst += ['PowerOffOn']

            if box != 'etx':
                test_names_lst += ['MicroSD']

            test_names_lst += ['SOC_Flash_Memory', 'SOC_i2C']

            if box != 'etx':
                test_names_lst += ['DryContactAlarm']

            test_names_lst += ['ID']

            for field in main_obj.gaSet['fields']:
                test_names_lst += [field]

            if re.search(r'/HL/', dbr_name):
                test_names_lst += ['HL_Security']


            if re.search(r'/WH/', dbr_name):
                test_names_lst += ['Halow_WiFi']

            sw_app = main_obj.gaSet['sw_app']
            print(f'sw_app:{sw_app}')
            if main_obj.gaSet['cellType'] != 'NotExists':
                if version.parse(sw_app) == version.parse("5.0.1.229.5"):
                    test_names_lst += ['CellularModem']
                else:
                    test_names_lst += ['CellularModem_SIM1', 'CellularModem_SIM2']

            test_names_lst += ['DataTransmissionConf']

            test_names_lst += ['DataTransmission']

            if main_obj.gaSet['serPort'] != 'NotExists' and main_obj.gaSet['serPort'] != '1RS':
                test_names_lst += ['SerialPorts']

            if main_obj.gaSet['gps'] != 'NotExists':
                test_names_lst += ['GPS']

        if False:


            if main_obj.gaSet['wifi'] != 'NotExists':
                test_names_lst += ['WiFi_2G']
        if True:

            if main_obj.gaSet['lora'] != 'NotExists':
                test_names_lst += ['LoRa']
        if False:

            if main_obj.gaSet['poe'] != 'NotExists':
                test_names_lst += ['POE']

            if main_obj.gaSet['plc'] != 'NotExists':
                test_names_lst += ['PLC']


            if main_obj.gaSet['cellType'] != 'NotExists':
                test_names_lst += ['LteLeds']

            test_names_lst += ['FrontPanelLeds']

        if False:
            test_names_lst += ['Factory_Settings']


            test_names_lst += ['SSH']



            if main_obj.gaSet['demo'] is False:
                test_names_lst += ['Mac_BarCode']

        ind = 1
        for te in test_names_lst:
            self.test_names_lst.append(f'{ind}..{te}')
            ind += 1
        print(f'Tests.AllTests.test_names_lst:{self.test_names_lst}')

    def PowerOffOn(self, main_obj):
        # ::sendSlow 0
        put = lib_put_sf1p.Put(main_obj)
        return put.power_off_on_perf()

    def MicroSD(self, main_obj):
        com = main_obj.gaSet['com_obj']
        put = lib_put_sf1p.Put(main_obj)

        com.send("\r", 'stam', 0.25)
        com.send("\r", 'stam', 0.25)

        if re.search('PCPE>', com.buffer):
            ret = 0
        else:
            ret = put.pwr_rst_login_2_boot()

        if ret == 0:
            ret = put.micro_sd_perform()

        return ret

    def SOC_Flash_Memory(self, main_obj):
        com = main_obj.gaSet['com_obj']
        put = lib_put_sf1p.Put(main_obj)
        com.send("\r", 'stam', 0.25)
        com.send("\r", 'stam', 0.25)
        # put = Put(self.gaSet)
        if re.search('PCPE>', com.buffer):
            ret = 0
        else:
            ret = put.pwr_rst_login_2_boot()

        if ret == 0:
            ret = put.soc_flash_perform()

        return ret

    def SOC_i2C(self, main_obj):
        com = main_obj.gaSet['com_obj']
        put = lib_put_sf1p.Put(main_obj)
        com.send("\r", 'stam', 0.25)
        com.send("\r", 'stam', 0.25)
        # put = Put(self.gaSet)
        if re.search('PCPE>', com.buffer):
            ret = 0
        else:
            ret = put.pwr_rst_login_2_boot()

        if ret == 0:
            ret = put.soc_2ic_perform()

        return ret

    def DryContactAlarm(self, main_obj):
        # ::sendSlow 0
        put = lib_put_sf1p.Put(main_obj)
        ret = put.dry_contact_perf()
        return ret

    def ID(self, main_obj):
        put = lib_put_sf1p.Put(main_obj)
        ret = put.id_perform("ID")
        if ret != 0:
            return ret

        ret = put.read_wan_lan_status()
        if ret != 0:
            return ret

        ret = put.read_boot_params()
        return ret

    def HL_Security(self, main_obj):
        # ::sendSlow 0
        put = lib_put_sf1p.Put(main_obj)
        ret = put.hl_security_perf()
        return ret

    def CellularModem_SIM1(self, main_obj):
        # ::sendSlow 0
        put = lib_put_sf1p.Put(main_obj)
        if main_obj.gaSet['cellQty'] == 1:
            ret = put.cellularLte_RadOS_Sim12()
            if ret == 0:
                ret = put.cellularModemPerf_RadOS_Sim12(1)
        else:
            ret = put.cellularLte_RadOS_Sim12_dual()
            if ret == 0:
                ret = put.cellularModemPerf_RadOS_Sim12_dual(1)

        return ret

    def CellularModem_SIM2(self, main_obj):
        # ::sendSlow 0
        put = lib_put_sf1p.Put(main_obj)
        if main_obj.gaSet['cellQty'] == 1:
            ret = put.cellularLte_RadOS_Sim12()
            if ret == 0:
                ret = put.cellularModemPerf_RadOS_Sim12(2)
        else:
            ret = put.cellularLte_RadOS_Sim12_dual()
            if ret == 0:
                ret = put.cellularModemPerf_RadOS_Sim12_dual(2)

        return ret

    def DataTransmissionConf(self, main_obj):
        self.gen = lib_etx204.Etx204Gen(main_obj)
        ret = self.gen.OpenGen()
        print(f'ret of OpenGen:<{ret}>')
        if ret == -1:
            return -1

        ret = self.gen.PortsDown()
        print(f'ret of PortsDown:<{ret}>')

        put = lib_put_sf1p.Put(main_obj)
        ret = put.data_transmission_setup()

        self.gen.CloseGen()

        return ret

        # time.sleep(3)
        # ret = gen1.PortsUp()
        # print(f'ret of PortsUp:<{ret}>')
        # return 0

    def DataTransmission(self, main_obj):
        gen_obj = lib_gen_sf1p.Gen(main_obj)
        gen_obj.mux_mng_io(main_obj, '6ToGen')
        time.sleep(2)

        self.gen = lib_etx204.Etx204Gen(main_obj)

        ret = self.gen.OpenGen()
        print(f'ret of OpenGen:<{ret}>')
        if ret == -1:
            return -1

        ret = self.gen.InitEtxGen()
        print(f'ret of InitEtxGen:<{ret}>')
        if ret == 0:
            ret = self.gen.PortsUp()
            print(f'ret of Gen PortsUp:<{ret}>')

        if ret == 0:
            ret = gen_obj.wait(main_obj, 'Waiting for stabilization', 10)
            print(f'ret of wait:<{ret}>')

        if ret == 0:
            ret = self.gen.Start()
            print(f'ret of Gen Start:<{ret}>')

        if ret == 0:
            ret = gen_obj.wait(main_obj, 'Data is running', 10)
            print(f'ret of wait:<{ret}>')

        if ret == 0:
            ret = self.gen.Check()
            print(f'ret of Gen Check:<{ret}>')

        if ret == 0:
            ret = gen_obj.wait(main_obj, 'Data is running', 60)
            print(f'ret of wait:<{ret}>')

        if ret == 0:
            ret = self.gen.Check()
            print(f'ret of Gen Check:<{ret}>')

        if ret == 0:
            ret = self.gen.PortsDown()
            print(f'ret of Gen PortsDown:<{ret}>')

        self.gen.CloseGen()

        return ret

    def SerialPorts(self, main_obj):
        # ::sendSlow 0
        put = lib_put_sf1p.Put(main_obj)
        ret = put.serial_ports_perf()
        return ret

    def GPS(self, main_obj):
        # ::sendSlow 0
        put = lib_put_sf1p.Put(main_obj)
        ret = put.gps_perf()
        return ret

    def LteLeds(self, main_obj):
        put = lib_put_sf1p.Put(main_obj)
        ret = put.lte_leds_perf()
        return ret

    def FrontPanelLeds(self, main_obj):
        put = lib_put_sf1p.Put(main_obj)
        ret = put.front_leds_perf()
        return ret

    def Factory_Settings(self, main_obj):
        put = lib_put_sf1p.Put(main_obj)
        ret = put.read_imei()

        if ret == 0:
            ret = put.check_sim_out()
            if ret == -1 and 'pulled out' in main_obj.gaSet['fail']:
                ret = put.inform_about_sim()
                if ret == 'Stop':
                    ret = -2
                else:
                    ret = put.check_sim_out()

        if ret == 0:
            ret = put.fact_sett_perf()

        return ret

    def SSH(self, main_obj):
        put = lib_put_sf1p.Put(main_obj)
        return put.ssh_perf()

    def Mac_BarCode(self, main_obj):
        put = lib_put_sf1p.Put(main_obj)
        barc_obj = lib_barcode.Barcode(Gui_SF1P.DialogBox)
        gen_obj = lib_gen_sf1p.Gen(main_obj)
        ret = 0
        if 'imei1' not in main_obj.gaSet.keys() or main_obj.gaSet['imei1'] == "NotExists":
            ret = put.read_imei()
            if ret == 0:
                ret = put.read_mac()
        if ret == 0:
            mac1 = ''.join(main_obj.gaSet['mac'].split('-'))
            mac2 = ""
            imei1 = main_obj.gaSet['imei1']
            imei2 = main_obj.gaSet['imei2']
            barcode = main_obj.gaSet['id_number']
            print(mac1, mac2, imei1, imei2)
            txt = f'Barcode:{barcode} MAC:{mac1}'
            if imei1 != 'NotExists':
                txt += f' IMEI1:{imei1}'
            if imei2 != 'NotExists':
                txt += f' IMEI2:{imei2}'
            gen_obj.add_to_log(main_obj, txt)

        if ret == 0:
            ret = barc_obj.reg_id_barcode(main_obj, barcode, mac1, imei1, imei2)

        return ret

    def LoRa(self, main_obj):
        put = lib_put_sf1p.Put(main_obj)
        lra = lib_lora.Lora(main_obj)
        ret = lra.lora_module_conf()
        if ret == 0:
            ret = lra.lora_server_polling()
        if ret == 0:
            ret = lra.lora_gw_mode("shutdown")
        if ret == 0:
            ret = lra.config_lora_device()
        if ret == 0:
            ret = lra.lora_ping('LoraServerIP', main_obj.gaSet['lora_server_ip'])
        if ret == 0:
            ip = main_obj.gaSet[f'chirp_stack_ip.{main_obj.gaSet["lora_fam"]}']
            ret = lra.lora_ping('ChirpStackIP', ip)
        if ret == 0:
            ret = lra.join_lora_device()
        if ret == 0:
            data = datetime.datetime.now().strftime("%d%H%M%S")
            ret = lra.lora_perf(data)
        return ret
