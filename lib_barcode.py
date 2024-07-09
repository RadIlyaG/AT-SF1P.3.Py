import re
import winsound
#from Gui_SF1P import DialogBox
from rad_apps import Mac
# from lib_gen_sf1p import Gen


class Barcode:
    def __init__(self, dlgbox_obj, **kwargs):
        self.barc_name = ''
        self.barcode_dict = {}
        self.dlgbox_obj = dlgbox_obj
        self.db_dict = {}
        self.ent_dict = {}
        self.kwargs = kwargs

    def gui_read_barcode(self, main_obj):
        print(f'gui_read_barcode self:{self}, main_obj:{main_obj}, self.dlgbox_obj:{self.dlgbox_obj}')
        if main_obj.gaSet['use_exist_barcode'] == 1:
            barcode = main_obj.gaSet['id_number']
            self.barc_name += barcode
            ret = 0
        else:
            main_obj.gaSet['id_mac_link'] = 'NA'
            main_obj.gaSet['main_trace'] = 'NA'
            main_obj.gaSet['ps_trace'] = 'NA'
            parent = main_obj.gaSet['root']
            self.db_dict = {
                "title": "ID Barcode",
                "message": "Scan here DUT's ID Barcode",
                "type": ["Ok", "Cancel"],
                "icon": "::tk::icons::information",
                'default': 0,
                'entry_per_row': 1
            }
            if main_obj.gaSet['ps'] == 'WDC' or main_obj.gaSet['ps'] == '12V':
                self.db_dict['entry_qty'] = 3
                self.db_dict['entry_lbl'] = ["ID", "Main Card's Traceability", "PS Card's Traceability"]
                self.db_dict['rad_qty'] = 3
            else:
                self.db_dict['entry_qty'] = 2
                self.db_dict['entry_lbl'] = ["ID", "Main Card's Traceability"]
                self.db_dict['rad_qty'] = 2

            self.kwargs['ID'] = 'DC1002310503'  # 'DC1002287436' 'DC1002310503' 'DC1002308359' 'DC1002306591'
            self.kwargs["Main Card's Traceability"] = '21101011'  #  '21012153' '21101011' '21220620' '21293962'
            self.kwargs['invokeBut'] = 'Ok'
            cont_while = True
            ret = -1
            while cont_while:
                string, res_but, ent_dict = self.dlgbox_obj(parent, self.db_dict, self.kwargs).show()
                print(f'gui_read_barcode string:{string}, res_but:{res_but}')
                if res_but == "Cancel":
                    ret = -2
                    break

                res = 0
                for ent in self.db_dict['entry_lbl']:
                    res = 0
                    val = ent_dict[ent].get()
                    print(f'\nentry:{ent}, val:{val}')
                    if re.search(r'Traceability', ent):
                        print(f'Traceability entry:{ent}, val:{val}')
                    else:
                        print(f'Not Traceability entry:{ent}, val:{val}')
                        if len(val) != 11 and len(val) != 12:
                            self.db_dict["message"] = "ID Barcode should be 11 or 12 chars"
                            res = -1
                            break
                        if str(val)[0:2].isalpha() is False:
                            self.db_dict["message"] = "Two first chars of ID Barcode should be letters"
                            res = -1
                            break
                        if str(val)[2:].isdigit() is False:
                            self.db_dict["message"] = "Except two first chars of ID Barcode, the rest should be digits"
                            res = -1
                            break

                    self.barcode_dict[ent] = val

                if res == 0:
                    # if all checks passed -> break the loop
                    ret = 0

                    cont_while = False

            # print(barcode_dict)
            # if ret == 0:
            #     for ent in db_dict['entry_lbl']:
            #         gaSet['IdBarcode'][ent] = self.barcode_dict[ent]
            #         self.barc_name += self.barcode_dict[ent]+'-'
            # else:
            #     for ent in db_dict['entry_lbl']:
            #         gaSet['IdBarcode'][ent] = 'no_IdBarcode'
            #         self.barc_name += 'noIdBarcode'+'-'
            # self.barc_name = self.barc_name.rstrip('-')

        # gui_num = gaSet['gui_num']
        # gaSet['log'] = {}
        # gaSet['log'][gui_num] = f"c:/logs/{gaSet['log_time']}-{self.barc_name}.txt"

        if main_obj.gaSet['use_exist_barcode'] == 0 and ret == 0:
            for ent in self.db_dict['entry_lbl']:
                barcode = ent_dict[ent].get()
                # print(f'add to ret_list barcode:{barcode}')

                if not re.search(r'Traceability', ent):
                    main_obj.gaSet['id_number'] = barcode
                    res = Mac.check_mac(barcode, 'AABBCCFFEEDD')
                    print(f'CheckMac res. Barcode:{barcode}, res:{res}')
                    main_obj.gaSet['id_mac_link'] = res
                elif re.search(r'Main', ent):
                    main_obj.gaSet['main_trace'] = barcode
                elif re.search(r'PS', ent):
                    main_obj.gaSet['ps_trace'] = barcode

        if main_obj.gaSet['use_exist_barcode'] == 1:
            main_obj.gaSet['use_exist_barcode'] = 0

        return ret

    def reg_id_barcode(self, main_obj, barcode, mac, imei1, imei2):
        print(f'\nreg_id_barcode')
        kwargs = {}
        kwargs['barcode'] = barcode
        kwargs["mac1"] = mac
        kwargs["mac2"] = ""
        kwargs['imei1'] = imei1
        kwargs['imei2'] = imei2

        print(f'reg_id_barcode {kwargs}')
        res = Mac.mac_reg(kwargs)
        print(f"res of reg_id_barcode {kwargs}: {res}")
        if res:
            ret = 0
        else:
            ret = -1
            main_obj.gaSet['fail'] = 'Fail to update Data-Base'
        return ret


if __name__ == '__main__':
    gaSet = {}
    gaSet['use_exist_barcode'] = 0
    Barcode.gui_read_barcode(Barcode, gaSet)