from dialogBox import CustomDialog as DialogBox
from RL import Lib_RadApps
from lib_gen_sf1p import my_time


def gui_read_barcode(gaSet):
    barc_name = ''
    barcode_dict = {}
    if gaSet['use_exist_barcode'] == 1:
        barcode = gaSet['IdBarcode']['DUT']
        barc_name += barcode
        ret = 0
    else:
        parent = gaSet['root']
        db_dict = {
            "title": "ID Barcode",
            "message": "Scan here DUT's ID Barcode",
            "type": ["Ok", "Cancel"],
            "icon": "::tk::icons::information",
            'default': 0,
            'entry_qty': 1,
            'entry_per_row': 1,
            'entry_lbl': ["DUT"]
        }

        cont_while = True
        ret = -1
        while cont_while:

            string, res_but, ent_dict = DialogBox(parent, db_dict).show()
            print(f'gui_read_barcode string:{string}, res_but:{res_but}')
            if res_but == "Cancel":
                ret = -2
                break

            res = 0
            for ent in db_dict['entry_lbl']:
                res = 0
                val = ent_dict[ent].get()
                # print(f'entry:{ent}, val:{val}')
                if len(val) != 11 and len(val) != 12:
                    db_dict["message"] = "ID Barcode should be 11 or 12 chars"
                    res = -1
                    continue
                if str(val)[0:2].isalpha() is False:
                    db_dict["message"] = "Two first chars of ID Barcode should be letters"
                    res = -1
                    continue
                if str(val)[2:].isdigit() is False:
                    db_dict["message"] = "Except two first chars of ID Barcode, the rest should be digits"
                    res = -1
                    continue

                barcode_dict[ent] = val

            if res == 0:
                # if all checks passed -> break the loop
                ret = 0

                cont_while = False

        # print(barcode_dict)
        if ret == 0:
            for ent in db_dict['entry_lbl']:
                gaSet['IdBarcode'][ent] = barcode_dict[ent]
                barc_name += barcode_dict[ent]+'-'
        else:
            for ent in db_dict['entry_lbl']:
                gaSet['IdBarcode'][ent] = 'no_IdBarcode'
                barc_name += 'noIdBarcode'+'-'
        barc_name = barc_name.rstrip('-')

    gui_num = gaSet['gui_num']
    gaSet['log'] = {}
    gaSet['log'][gui_num] = f"c:/logs/{gaSet['log_time']}-{barc_name}.txt"

    if gaSet['use_exist_barcode'] == 0 and ret == 0:
        for ent in db_dict['entry_lbl']:
            barcode = gaSet['IdBarcode'][ent]
            res = Lib_RadApps.check_mac(barcode, 'AABBCCFFEEDD')
            print(f'CheckMac res. Barcode:{barcode}, res:{res}')

    if gaSet['use_exist_barcode'] == 1:
        gaSet['use_exist_barcode'] = 0

    return ret


def reg_id_barcode(gaSet):
    print(f'reg_id_barcode {gaSet}')
    mac = '012345543210'
    barcode = gaSet['IdBarcode']['DUT']

    args = mac, barcode
    if gaSet['dut_fam']['cell']['cell'] != 0:
        if gaSet['dut_fam']['cell']['qty'] == 1:
            imei1 = gaSet['dut_fam']['cell']['imei1']
            args.append(imei1=imei1)
        elif gaSet['dut_fam']['cell']['qty'] == 2:
            imei1 = gaSet['dut_fam']['cell']['imei1']
            imei2 = gaSet['dut_fam']['cell']['imei2']
            args.append(imei1=imei1, imei2=imei2)
    txt = f'Registration MAC:{mac} to ID Barcode:{barcode}'
    # App.my_statusbar.sstatus(txt)
    gaSet['file_log'].info(txt)
    # gaSet['puts_log'].info(txt)
    print(f"{my_time()} {txt}")
    res = Lib_RadApps.mac_reg(*args)
    # gaSet['puts_log'].info(f'res of mac_reg_{args}: {res}')
    print(f"{my_time()} res of mac_reg_{args}: {res}")
    if res:
        ret = 0
    else:
        ret = -1
        gaSet['fail'] = 'Fail to update Data-Base'
    return ret
