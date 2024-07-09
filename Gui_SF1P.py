import sys
import re
import os
import tkinter as tk
from tkinter import ttk
from tkinter import *
from PIL import Image, ImageTk
import functools
from functools import partial
import glob
import time
from datetime import datetime
from pathlib import Path
import winsound

import Tests
# import Tests
import rad_apps
from rad_apps import EmplName
from lib_gen_sf1p import Gen
from Tests import *
from lib_barcode import *


class Gui:
    def __init__(self, main_obj):
        print(f'Gui, self:{self}, main_obj:{main_obj}')
        print(f'Gui, main_obj.gaSet:{main_obj.gaSet}')

        gui_num = main_obj.gaSet['gui_num']
        self.root = Tk()
        main_obj.gaSet['root'] = self.root
        # self.parent = self.root
        self.root.title(str(gui_num))
        # self.root.wm_protocol("WM_DELETE_WINDOW", partial(self.my_quit))
        self.mainframe = ttk.Frame(self.root)
        # self.menuframe = ttk.Frame(self.mainframe)
        self.topframe = ttk.Frame(self.mainframe)
        self.centerframe = ttk.Frame(self.mainframe)
        self.bottomframe = ttk.Frame(self.mainframe)

        menu_bar_obj = MenuBar(main_obj)
        self.root.wm_protocol("WM_DELETE_WINDOW" , partial(self.my_quit,  self.root, main_obj))

        self.my_toolbar = Toolbar(self.topframe, main_obj)

        self.my_statusbar = StatusBar(self.mainframe, main_obj)
        main_obj.my_statusbar = self.my_statusbar
        self.my_statusbar.sstatus("This is the statusbar1")

        self.fr0 = ttk.Frame(self.centerframe, relief="flat")

        self.fr_uut_id = ttk.Frame(self.fr0, relief="groove")
        self.lab_uut_id = ttk.Label(self.fr_uut_id, text="UUT's ID Number: ")
        self.uut_id = tk.StringVar()
        # App.uut_id = self.uut_id
        self.ent_uut_id = ttk.Entry(self.fr_uut_id, textvariable=self.uut_id, width=20)
        self.ent_uut_id.bind('<Return>', partial(self.bind_uutId_entry, main_obj))
        script_dir = os.path.dirname(__file__)
        self.img = Image.open(os.path.join(script_dir, "images", "clear1.ico"))
        use_img = ImageTk.PhotoImage(self.img)
        self.bt_clr_uut_id = ttk.Button(self.fr_uut_id, image=use_img,
                                        command=lambda: self.uut_id.set(""))
        self.bt_clr_uut_id.image = use_img
        self.lab_uut_id.pack(side="left", padx=2)
        self.ent_uut_id.pack(side="left")
        self.bt_clr_uut_id.pack(side="left")
        self.fr_uut_id.pack(anchor="w", padx=2, pady=2, fill=BOTH, expand=True, ipady=3)

        self.fr_curr_tst = ttk.Frame(self.fr0, relief="groove")
        self.lab_curr_tst = ttk.Label(self.fr_curr_tst, text="Current Test: ")
        self.curr_tst = tk.StringVar()
        Gui.curr_tst = self.curr_tst
        self.ent_curr_tst = ttk.Entry(self.fr_curr_tst, textvariable=self.curr_tst, width=35, justify='center')
        self.lab_curr_tst.pack(side="left", padx=2)
        self.ent_curr_tst.pack(side="left")
        self.fr_curr_tst.pack(anchor="w", padx=2, pady=2, fill=BOTH, expand=True, ipady=3)

        self.fr0.pack(side=LEFT, padx=2, fill=BOTH, expand=True)

        self.topframe.pack(side=TOP, fill=X)
        self.centerframe.pack(side=TOP, fill=BOTH)
        self.bottomframe.pack(side=BOTTOM, fill=X)
        self.mainframe.pack(side=TOP, expand=True, fill=BOTH)
        # print(f'main2 {app.gaSet}')

        self.root.geometry(main_obj.gaSet['geom'])

        if main_obj.gaSet['demo']:
            db_dict = {
                "title": "DEMO version",
                "message": "You are working with ATE's DEMO version\n\
        Please confirm you know products should not be released to the customer with this version",
                "type": ["OK", "Abort"],
                "icon": "::tk::icons::question",
                'default': 0
            }

            string, res_but, ent_dict = DialogBox(self.root, db_dict).show()
            print(string, res_but)
            if res_but == "Abort":
                for f in glob.glob("SW*.txt"):
                    os.remove(f)
                self.root.destroy()
                sys.exit()
            self.root.title(f"DEMO!!! {gui_num}")

        else:
            self.root.title(f"{gui_num} : ")

        self.uut_id.set('DC1002310503')  # 'DC1002287436' 'DC1002310503' 'DC1002274432' 'DC1002306591'
        self.ent_uut_id.focus_set()
        self.root.bind('<Alt-r>', partial(self.my_toolbar.button_run, main_obj))
        self.root.bind('<Alt-b>', partial(self.bind_root_altR, main_obj))
        self.root.mainloop()

    def bind_root_altR(self, main_obj, *event):
        print(f'bind_root_altR')
        main_obj.gaSet['use_exist_barcode'] = 1
    def bind_uutId_entry(self, main_obj, *event):
        print(f'bind_uutId_entry main_obj:{main_obj}')
        gen_obj = Gen(main_obj)
        id_number = self.uut_id.get()
        self.uut_id.set('')
        Toolbar.cb1.config(values=[])
        Toolbar.var_start_from.set('')
        self.my_statusbar.sstatus(f"Getting data from DBR for {id_number}")

        dbr_name = Gen.get_dbr_name(Gen, id_number)
        gui_num = main_obj.gaSet['gui_num']
        self.root.title(str(gui_num) + ': ' + dbr_name)
        #print(f'dbr_name:_{dbr_name}_')
        if dbr_name is None:
            db_dict = {
                "title": "Get DBR name fail",
                "message": f"Get DBR name for {id_number} fail",
                "type": ["Ok"],
                "icon": "::tk::icons::error"
            }
            string, str12, ent_dict = DialogBox(self.root, db_dict).show()
            return False

        mrkt_name = Gen.get_mrkt_name(Gen, id_number)
        #print(f'mrkt_name:_{mrkt_name}_')
        if mrkt_name is None:
            db_dict = {
                "title": "Get Marketing name fail",
                "message": f"Get Marketing name for {id_number} fail",
                "type": ["Ok"],
                "icon": "::tk::icons::error"
            }
            string, str12, ent_dict = DialogBox(self.root, db_dict).show()
            return False

        csl = Gen.get_csl(Gen, id_number)
        #print(f'csl:_{csl}_')
        if csl is None:
            db_dict = {
                "title": "Get CSL fail",
                "message": f"Get CSL for {id_number} fail",
                "type": ["Ok"],
                "icon": "::tk::icons::error"
            }
            string, str12, ent_dict = DialogBox(self.root, db_dict).show()
            return False

        main_obj.gaSet['id_number'] = id_number
        main_obj.gaSet['dbr_name'] = dbr_name
        main_obj.gaSet['mrkt_name'] = dbr_name
        main_obj.gaSet['csl'] = csl

        print(f'bind_uutId_entry1 {main_obj.gaSet}')

        ret = Gen.retrive_dut_fam(Gen, main_obj)
        if ret is not True:
            self.my_statusbar.sstatus(ret, 'red')
            return False
        gen_obj.toggle_comDut()
        # MenuBar.termmenu.entryconfigure(0, label=f'UUT: {main_obj.gaSet["comDut"]}')
        Gen.get_dbr_sw(Gen, main_obj)

        gen_obj.power(main_obj, 1, 1)
        tests = AllTests()
        tests.build_tests(main_obj)
        main_obj.test_names_lst = tests.test_names_lst
        print(f'Main sf1p test_names_lst:{tests.test_names_lst}')
        Toolbar.cb1.config(values=tests.test_names_lst, height=1 + len(tests.test_names_lst))
        Toolbar.var_start_from.set(tests.test_names_lst[0])

        self.my_statusbar.sstatus(f"Done")

    def my_quit(self, parent, main_obj, *event):
        print(f"my_quit, self:{self}, parent:{parent}, main_obj:{main_obj}")
        Gen.save_init(Gen, main_obj, main_obj.gaSet['gui_num'])
        print("TBD: Gen.delete_markNum(Gen)")
        db_dict = {
            "title": "Confirm exit",
            "message": "Are you sure you want to close the application?",
            "type": ["Yes", "No"],
            "icon": "::tk::icons::question",
            'default': 0
        }
        string, res_but, ent_dict = DialogBox(parent, db_dict).show()
        print(string, res_but)
        if res_but == "Yes":
            for f in glob.glob("SW*.txt"):
                os.remove(f)
            parent.destroy()
            sys.exit()

    def gui_get_operator(self, main_obj):
        if main_obj.gaSet['rad_net'] is False:
            main_obj.gaSet['emp_numb'] = "NA"
            main_obj.gaSet['emp_name'] = "NA"
            return 0
        parent = main_obj.gaSet['root']
        ent_lbl = "Scan here the Operator's Employee Number "
        db_dict = {
            "title": "Get Operator Name",
            "type": ["Ok", "Cancel"],
            "message": "Operator's Employee Number ",
            "icon": "images/oper32.ico",
            'default': 0,
            'entry_qty': 1,
            'entry_per_row': 1,
            'entry_lbl': [ent_lbl],
            'entry_frame_bd': 0
        }

        cont_while = True
        ret = -1
        msg = ""
        emp_numb, emp_name = None, None
        # kwargs = {"Scan here the Operator's Employee Number ": '111884', 'invokeBut': 'Ok'}
        kwargs = {"ilya": '111884', 'invokeBut': 'Ok'}
        if 'emp_numb' in main_obj.gaSet.keys():
            kwargs["last"] = main_obj.gaSet['emp_numb']
        else:
            kwargs["last"] = "114965"
        while cont_while:
            string, res_but, ent_dict = DialogBox(parent, db_dict, kwargs).show()
            emp_numb = ent_dict[ent_lbl].get()
            print(f'gui_get_operator string:{string}, res_but:{res_but}, emp_numb:{emp_numb}')
            res = 0
            if res_but == 'Cancel':
                return -2
            else:
                if len(emp_numb) != 6 or emp_numb.isdigit() is False:
                    msg = f"The number {emp_numb} is not valid\nTry again"
                    res = -1
                    continue

                if res == 0:
                    db_file = "operDB.db"
                    emp_name = rad_apps.EmplName.sqlite_get_empl_name(EmplName, db_file, emp_numb)
                    if emp_name is None:
                        emp_name = EmplName.get_operator(emp_numb)
                        print(f'emp_numb:{emp_numb}, emp_name:{emp_name}')
                        if re.search('Employee Not Found!', emp_name):
                            msg = f"No operator name for number {emp_numb}\nTry again"
                            res = -1
                            continue
                        EmplName.sqlite_add_empl_name(EmplName, db_file, emp_numb, emp_name)

                    main_obj.gaSet['emp_numb'] = emp_numb
                    main_obj.gaSet['emp_name'] = emp_name
                    cont_while = False
                    ret = 0

                if ret != 0:
                    return ret

        return ret

class MenuBar:
    def __init__(self, main_obj, *args, **kwargs):
        print(f'MenuBar main_obj:{main_obj}')
        parent = main_obj.gaSet['root']

        self.menubar = Menu(parent)

        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="History", command=partial(Gen.open_history, self))
        self.filemenu.add_separator()
        # filemenu.add_command(label="Update INIT and UserDefault files on all the Testers")

        self.filemenu.add_command(label=f"Edit Modems' file", command=partial(Gen.edit_mdm_file, Gen))
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=partial(Gui.my_quit, self, parent, main_obj))
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.toolsmenu = Menu(self.menubar, tearoff=0)
        self.pwr_menu = Menu(self.toolsmenu, tearoff=0)
        self.pwr_menu.add_command(label="PS-1 & PS-2 ON", command=lambda: Gen.gui_Power(Gen, main_obj, 1, 1))
        self.pwr_menu.add_command(label="PS-1 & PS-2 OFF", command=lambda: Gen.gui_Power(Gen, main_obj, 1, 0))
        self.pwr_menu.add_command(label="PS-1 & PS-2 OFF and ON", command=lambda: Gen.gui_PowerOffOn(Gen, main_obj, 1))
        self.toolsmenu.add_cascade(label="Power", menu=self.pwr_menu)

        self.mux_menu = Menu(self.toolsmenu, tearoff=0)
        self.mux_menu.add_command(label="ETH6 - Generator", command=lambda: Gen.mux_mng_io(Gen, main_obj, 'gui e6-g'))
        self.mux_menu.add_command(label="PS-1 & PS-2 OFF", command=lambda: Gen.gui_Power(Gen, main_obj, 1, 0))
        self.mux_menu.add_command(label="PS-1 & PS-2 OFF and ON", command=lambda: Gen.gui_PowerOffOn(Gen, main_obj, 1))
        self.toolsmenu.add_cascade(label="MUX", menu=self.mux_menu)

        self.toolsmenu.add_separator()

        self.use_ex_barc = IntVar()
        try:
            set = main_obj.gaSet['use_exist_barcode']
        except KeyError:
            set = 0
        self.use_ex_barc.set(set)
        MenuBar.use_ex_barc = self.use_ex_barc
        self.toolsmenu.add_radiobutton(label="Don't use exist Barcodes", variable=self.use_ex_barc,
                                  value=0,
                                  command=partial(self.rb_ueb_cmd, main_obj,
                                                  'use_exist_barcode',
                                                  self.use_ex_barc))
        self.toolsmenu.add_radiobutton(label="Use exist Barcodes", variable=self.use_ex_barc,
                                  value=1,
                                  command=partial(self.rb_ueb_cmd, main_obj,
                                                  'use_exist_barcode',
                                                  self.use_ex_barc))
        self.toolsmenu.add_separator()

        self.one_tst = IntVar()
        MenuBar.one_tst = self.one_tst
        try:
            set = main_obj.gaSet['one_test']
        except KeyError:
            set = 0
        self.one_tst.set(set)
        self.toolsmenu.add_radiobutton(label="One test ON", variable=self.one_tst, value=1,
                                  command=partial(self.rb_ueb_cmd, main_obj,
                                                  'one_test',
                                                  self.one_tst))
        self.toolsmenu.add_radiobutton(label="One test OFF", variable=self.one_tst, value=0,
                                  command=partial(self.rb_ueb_cmd, main_obj,
                                                  'one_test',
                                                  self.one_tst))
        self.toolsmenu.add_separator()
        self.menubar.add_cascade(label="Tools", menu=self.toolsmenu)

        self.termmenu = Menu(self.menubar, tearoff=0)
        MenuBar.termmenu = self.termmenu
        print(f'termmenu:<{self.termmenu}>')
        self.termmenu.add_command(label=f"UUT: {main_obj.gaSet['comDut']}",
                             command=lambda: Gen.open_teraterm(main_obj, "comDut"))
        self.termmenu.add_command(label=f"Gen-1: {main_obj.gaSet['comGen1']}",
                             command=lambda: Gen.open_teraterm(main_obj, "comGen1"))
        self.termmenu.add_command(label=f"Gen-2: {main_obj.gaSet['comGen2']}",
                             command=lambda: Gen.open_teraterm(main_obj, "comGen2"))
        self.termmenu.add_command(label=f"Serial-1: {main_obj.gaSet['comSer1']}",
                             command=lambda: Gen.open_teraterm(main_obj, "comSer1"))
        self.termmenu.add_command(label=f"Serial-2: {main_obj.gaSet['comSer2']}",
                             command=lambda: Gen.open_teraterm(main_obj, "comSer2"))
        self.termmenu.add_command(label=f"485-2: {main_obj.gaSet['comSer485']}",
                             command=lambda: Gen.open_teraterm(main_obj, "comSer485"))
        self.menubar.add_cascade(label="Terminal", menu=self.termmenu)

        parent.config(menu=self.menubar)

    def rb_ueb_cmd(self, main_obj, key, value):
        val = value.get()
        print(f'rb_ueb_cmd', {self}, {key}, {val})
        main_obj.gaSet[key] = val
        Gen.save_init(Gen, main_obj, main_obj.gaSet['gui_num'])


class Toolbar:
    def button_run(self, main_obj, *event):
        # print(f'button_run1 main_obj:{main_obj}, {main_obj.gaSet}')
        gen_obj = Gen(main_obj)
        # print(f"{Gen.my_time(Gen)} Button RUN pressed")
        print(f"{gen_obj.my_time()} Button RUN pressed")
        clear = lambda: os.system('cls')
        clear()

        main_obj.gaSet['but_run_time'] = str(time.time()).split('.')[0]
        main_obj.my_statusbar.sstatus("")
        main_obj.gaSet['act'] = 1
        self.button1.state(["pressed", "disabled"])
        self.button2.state(["!pressed", "!disabled"])

        now = datetime.datetime.now()
        main_obj.gaSet['log_time'] = now.strftime("%Y.%m.%d-%H.%M.%S")

        Path('c:\\logs').mkdir(parents=True, exist_ok=True)
        gui_num = main_obj.gaSet['gui_num']

        main_obj.gaSet['fw_dict'] = gen_obj.loadModemsFWfile()
        # print(f"{Gen.my_time(Gen)} Button RUN pressed, event={event}")
        # print(f'button_run1 {main_obj.gaSet}')

        # Gen.add_to_log(Gen, main_obj, "")

        wav = "C:\\RLFiles\\Sound\\Wav\\info.wav"
        winsound.PlaySound(wav, winsound.SND_FILENAME)
        barc_obj = Barcode(DialogBox)
        ret = barc_obj.gui_read_barcode(main_obj)
        if ret == 0:
            retrIdTra = rad_apps.RetriveIdTraceData()
            mainPcb = retrIdTra.get_value(main_obj.gaSet['main_trace'], "PCBTraceabilityIDData")['pcb']
            print(f'ButRun MainPcb:<{mainPcb}>')
            mainHW = re.search('V([\d\.]+)I', mainPcb)
            if mainHW is None:
                main_obj.gaSet['fail'] = "Get PCB version fail"
                ret = -1
            else:
                main_obj.gaSet['mainHW'] = float(mainHW.group(1))

        # print(f'button_run2 ret:{ret}  {main_obj.gaSet}')

        if ret == 0:
            wav = "C:\\RLFiles\\Sound\\Wav\\info.wav"
            winsound.PlaySound(wav, winsound.SND_FILENAME)
            ret = Gui.gui_get_operator(Gui, main_obj)
            # print(f'button_run3 ret:{ret} {main_obj.gaSet}')

            if ret == 0:
                ret = gen_obj.open_rl(main_obj)  # Gen.open_rl(Gen, main_obj)
                #print(f'button_run4 ret after open_rl :{ret}')
                if ret == 0:
                    main_obj.gaSet['log'] = f"c:/logs/{main_obj.gaSet['log_time']}_{gui_num}_{main_obj.gaSet['id_number']}.txt"
                    # Gen.add_to_log(Gen, main_obj, f"ID Number: {main_obj.gaSet['id_number']}")
                    # Gen.add_to_log(Gen, main_obj, f"Main TraceID Number: {main_obj.gaSet['main_trace']}")
                    # Gen.add_to_log(Gen, main_obj, f"DBR Name: {main_obj.gaSet['dbr_name']}")
                    # Gen.add_to_log(Gen, main_obj, f"Employee Number: {main_obj.gaSet['emp_numb']}, Name: {main_obj.gaSet['emp_name']}")
                    gen_obj.add_to_log(main_obj, f"ID Number: {main_obj.gaSet['id_number']}")
                    gen_obj.add_to_log(main_obj, f"Main TraceID Number: {main_obj.gaSet['main_trace']}")
                    gen_obj.add_to_log(main_obj, f"DBR Name: {main_obj.gaSet['dbr_name']}")
                    gen_obj.add_to_log(main_obj,
                                   f"Employee Number: {main_obj.gaSet['emp_numb']}, Name: {main_obj.gaSet['emp_name']}")
                    gen_obj.add_to_log(main_obj, '\n')

                    #tests_obj = AllTests
                    #test_names_lst = tests_obj.build_tests(main_obj)

                    test_names_lst = main_obj.test_names_lst
                    fst_tst = test_names_lst.index(Toolbar.var_start_from.get())
                    tests = test_names_lst[fst_tst:]
                    print(f'button_run4 fst_tst:{fst_tst} tests:{tests}')
                    #from all_tests import AllTests

                    main_obj.my_statusbar.startTime(gen_obj.my_time())

                    for tst in tests:
                        tst = tst.split('..')[1]
                        gen_obj.add_to_log(main_obj, f"Start of {tst}")
                        Gui.curr_tst.set(tst)
                        print(f'\n{gen_obj.my_time()} Start of {tst}')
                        main_obj.gaSet['root'].update()
                        ret = getattr(Tests.AllTests, tst)(Gen, main_obj)
                        if ret != 0:
                            if ret == -2:
                                main_obj.gaSet['fail'] = "User Stop"
                            ret_txt = f"Fail. Reason: {main_obj.gaSet['fail']}"
                        else:
                            ret_txt = 'Pass'
                        print(f'Ret of Test {tst}:{ret}')
                        gen_obj.add_to_log(main_obj, f"End of {tst}, result: {ret_txt}\n")
                        if ret != 0:
                            break
                else:
                    main_obj.gaSet['fail'] = "Open RL Fail"

                gen_obj.close_rl(main_obj)

                if ret == 0:
                    #ret = open_rl(self.gaSet)
                    if ret == 0:
                        run_status = ''
                        #all_tests_obj = AllTests(self.gaSet)
                        #ret = AllTests.testing_loop(self.gaSet)
                        #ret = all_tests_obj.testing_loop()
                        # self.gaSet['puts_log'].info(f'Ret of Testing:{ret}')
                        print(f"{gen_obj.my_time()} Ret of Testing:{ret}")
                       # close_rl(self.gaSet)

        # After Tests
        main_obj.my_statusbar.runTime("")
        main_obj.gaSet['use_exist_barcode'] = 0
        src = None
        if 'log' in main_obj.gaSet:
            src = Path(main_obj.gaSet['log'])
        print(f'\n After Tests ret:{ret}')

        if ret == 0:
            wav = "C:\\RLFiles\\Sound\\Wav\\pass.wav"
            main_obj.my_statusbar.sstatus("")
            main_obj.my_statusbar.sstatus("Done", 'green')

            dst = f'{os.path.splitext(src)[0]}-PASS{os.path.splitext(src)[1]}'
            os.rename(src, dst)
            run_status = 'Pass'
        elif ret == 1:
            wav = "C:\\RLFiles\\Sound\\Wav\\info.wav"
            main_obj.my_statusbar.sstatus("The test has been perform", 'yellow')
        else:
            run_status = 'Fail'
            if ret == -2:
                main_obj.gaSet['fail'] = 'User stop'
                run_status = ''
            elif ret == -3:
                run_status = ''

            main_obj.my_statusbar.sstatus(f"Test FAIL: {main_obj.gaSet['fail']}", 'red')
            wav = "C:\\RLFiles\\Sound\\Wav\\fail.wav"
            if src and os.path.isfile(src):
                dst = f'{os.path.splitext(src)[0]}-FAIL{os.path.splitext(src)[1]}'
                os.rename(src, dst)

        self.button1.state(["!pressed", "!disabled"])
        self.button2.state(["pressed", "disabled"])
        # self.button1.config(relief="raised", state="normal")
        # self.button2.config(relief="sunken", state="disabled")

        try:
            # playsound(wav, block=False)
            winsound.PlaySound(wav, winsound.SND_FILENAME)
        except Exception as e:
            pass
        finally:
            MenuBar.use_ex_barc.set(0)
            print(f'ButRun finally: ret:{ret}  {main_obj.gaSet}')

    def button_stop(self, main_obj):
        main_obj.gaSet['root'].update()
        gen_obj = Gen(main_obj)
        print(f"\n{gen_obj.my_time()} !!! button_stop 1 pressed")
        main_obj.gaSet['act'] = 0
        self.button1.state(["!pressed", "!disabled"])
        self.button2.state(["pressed", "disabled"])


    def button_two(self):
        print("button 2 pressed")

    def __init__(self, parent, main_obj):

        # self.sep1 = Separator(parent)
        # self.sep1.pack(fill="x", expand=True)
        # self.sep2 = Separator(parent)
        # self.sep2.pack(side="bottom", fill="x", expand=True)

        self.l1 = Label(parent, text="Start from:")
        self.l1.pack(side="left", padx=2)

        self.var_start_from = StringVar()
        Toolbar.var_start_from = self.var_start_from
        self.cb1 = ttk.Combobox(parent, justify='center', width=35, textvariable=self.var_start_from)
        # self.cb1.option_add('*TCombobox*Listbox.Justify', 'center')
        Toolbar.cb1 = self.cb1
        self.cb1.pack(side="left", padx=2)

        script_dir = os.path.dirname(__file__)
        self.img = Image.open(os.path.join(script_dir, "images", "run1.gif"))
        use_img = ImageTk.PhotoImage(self.img)
        self.button1 = ttk.Button(parent, command=partial(self.button_run, main_obj), image=use_img)
        Toolbar.button1 = self.button1
        self.button1.image = use_img
        self.button1.state(["!pressed", "!disabled"])

        self.img = Image.open(os.path.join(script_dir, "images", "stop1.gif"))
        use_img = ImageTk.PhotoImage(self.img)
        self.button2 = ttk.Button(parent, command=partial(self.button_stop, main_obj), image=use_img)
        Toolbar.button2 = self.button2
        self.button2.image = use_img
        self.button2.state(["!pressed", "!disabled"])

        self.img = Image.open(os.path.join(script_dir, "images", "find1.1.ico"))
        use_img = ImageTk.PhotoImage(self.img)
        self.button3 = ttk.Button(parent, command=self.button_two, image=use_img)
        self.button3.image = use_img

        self.button1.pack(side="left", padx=(12, 0))
        self.button2.pack(side="left", padx=(2, 2))
        self.button3.pack(side="left", padx=(10, 2))



class DialogBox(tk.Toplevel):
    def __init__(self, parent, db_dict, *args):
        self.args = args
        print(f"DialogBox parent:{parent} txt:{db_dict['message']} args:{args}")
        tk.Toplevel.__init__(self, parent)
        x_pos = parent.winfo_x() + 20
        y_pos = parent.winfo_y() + 20

        if 'message' in db_dict:
            msg = db_dict['message']
        else:
            db_dict['message'] = ''
            msg = ""
        message = msg

        if 'entry_qty' in db_dict:
            self.entry_qty = db_dict['entry_qty']
        else:
            self.entry_qty = 0

        if 'entry_per_row' in db_dict:
            entry_per_row = db_dict['entry_per_row']
        else:
            entry_per_row = 1

        entry_lines_qty = int(self.entry_qty/entry_per_row)
        # print(f'entry_lines_qty {entry_lines_qty}')

        new_lines_qty = message.count('\n')
        hei = 16*new_lines_qty + 44*entry_lines_qty + 60

        minH = 80
        # set minimum height to minH pixels
        if hei < minH:
            hei = minH
        # print(f'new_lines_qty {new_lines_qty} hei {hei}')

        maxW = 0
        for line in message.split('\n'):
            if len(line) > maxW:
                maxW = len(line)

        width = maxW * 8

        minW = 270
        # set minimum with to $minW pixels
        if width < minW:
            width = minW

        # print(f'self.max {maxW}, width {width}')
        # self.geometry(f'{width}x{hei}+{x_pos}+{y_pos}')
        self.geometry(f'+{x_pos}+{y_pos}')
        self.title(db_dict['title'])
        # self.bind('<Configure>', lambda event: print(self.geometry()))

        self.fr1 = tk.Frame(self)
        fr_img = tk.Frame(self.fr1)
        if re.search("tk::icons", db_dict['icon']):
            use_img_run = db_dict['icon']
        else:
            self.imgRun = Image.open(db_dict['icon'])
            use_img_run = ImageTk.PhotoImage(self.imgRun)
        l_img = tk.Label(fr_img, image=use_img_run)
        l_img.image = use_img_run
        l_img.pack(padx=10, anchor='n')

        fr_right = tk.Frame(self.fr1)
        fr_msg = tk.Frame(fr_right)
        l_msg = tk.Label(fr_msg, text=db_dict['message'])
        l_msg.pack(padx=10)

        if 'entry_lbl' in db_dict:
            entry_lbl = db_dict['entry_lbl']
        else:
            entry_lbl = ""
        if 'entry_frame_bd' in db_dict:
            bd = db_dict['entry_frame_bd']
        else:
            bd = 2
        self.ent_dict = {}
        if self.entry_qty > 0:
            self.list_ents = []
            fr_ent = tk.Frame(fr_right, bd=bd, relief='groove')
            for fi in range(0, self.entry_qty):
                f = tk.Frame(fr_ent, bd=0, relief='groove')
                txt = entry_lbl[fi]
                lab = tk.Label(f, text=txt)
                self.ent_dict[txt] = tk.StringVar()
                # CustomDialog.ent_dict[fi] = self.ent_dict[fi]
                self.list_ents.append(ttk.Entry(f, textvariable=self.ent_dict[txt]))
                # print(f'txt:{len(txt)}, entW:{ent.cget("width")}')
                self.list_ents[fi].pack(padx=2, side='right', fill='x')
                self.list_ents[fi].bind("<Return>", functools.partial(self.cmd_ent, fi))
                if entry_lbl != "":
                    lab.pack(padx=2, side='right')
                row = int((fi)/entry_per_row)
                column = int((fi)%entry_per_row)
                # print(f'fi:{fi}, txt:{txt}, row:{row} column:{column} entW:{ent.cget("width")}')
                f.grid(padx=(2, 10), pady=2, row=row, column=column, sticky='e')

        fr_msg.pack()
        if self.entry_qty > 0:
            fr_ent.pack(anchor='e', padx=2, pady=2, expand=1)

        fr_img.grid(row=0, column=0)
        fr_right.grid(row=0, column=1)

        self.frBut = tk.Frame(self)
        print(f"buts:{db_dict['type']}")

        self.buts_lst = []
        for butn in db_dict['type']:
            self.but = tk.ttk.Button(self.frBut, text=butn, width=10, command=functools.partial(self.on_but, butn))
            if args and butn == args[0]['invokeBut']:
                self.buts_lst.append((butn, self.but))
            self.but.bind("<Return>", functools.partial(self.on_but, butn))
            self.but.pack(side="left", padx=2)
            if 'default' in db_dict:
                default = db_dict['default']
            else:
                default = 0
            if db_dict['type'].index(butn) == default:
                self.but.configure(state="active")
                # self.bind('<space>', (lambda e, b=self.but: self.but.invoke()))
                self.but.focus_set()
                self.default_but = self.but

        if self.entry_qty > 0:
            self.list_ents[0].focus_set()

        self.fr1.pack(fill="both", padx=2, pady=2)

        self.frBut.pack(side="bottom", fill="y", padx=2, pady=2)

        self.var = tk.StringVar()
        self.but = ""

        if self.entry_qty > 0:
            # print(self.list_ents)
            # print(self.ent_dict)
            # print(self.args)
            # print(self.buts_lst)
            self.bind('<Control-y>', functools.partial(self.bind_diaBox, 'y'))
            self.bind('<Alt-l>', functools.partial(self.bind_diaBox, 'l'))

    def bind_diaBox(self, let, *event):
        for arg in self.args:
            for key, val in arg.items():
                print(let, key, val)
                if key != 'invokeBut':
                    if let == 'l':
                        val = arg['last']
                        key = "Scan here the Operator's Employee Number "
                    elif let == 'y' and 'ilya' in arg.keys():
                        val = arg['ilya']
                        key = "Scan here the Operator's Employee Number "

                    self.ent_dict[key].set(val)

        for butn, butn_obj in self.buts_lst:
            butn_obj.invoke()

    def cmd_ent(self, fi, event=None):
        # print(f'cmd_ent self:{self}, fi:{fi}, entry_qty:{self.entry_qty}, event:{event}')
        if fi+1 == self.entry_qty:
            # last entry -> set focus to default button
            self.default_but.invoke()
            # pass
        else:
            # not last entry -> set focus to next entry
            self.list_ents[fi+1].focus_set()

    def on_but(self, butn, event=None):
        # print(f'on_but self:{self}, butn:{butn}, event:{event}')
        self.but = butn
        self.destroy()
    # def on_ok(self, event=None):
    #     self.but = "ok"
    #     self.destroy()
    # def ca_ok(self, event=None):
    #     self.but = "ca"
    #     self.destroy()

    def show(self):
        self.wm_deiconify()
        # self.entry.focus_force()
        self.wait_window()
        # try:
        #     print(f'DialogBox show ent_dict:{self.ent_dict}')
        # except Exception as err:
        #     print(err)
        return [self.var.get(), self.but, self.ent_dict]



class StatusBar(ttk.Frame):
    def __init__(self, parent, main_obj):
        ttk.Frame.__init__(self, parent)
        self.label1 = tk.Label(self, anchor='center', width=66, relief="groove")
        self.label1.pack(side='left', padx=1, pady=1)
        self.label2 = tk.Label(self, anchor=W, width=15, relief="sunken")
        self.label2.pack(side='left', padx=1, pady=1)
        self.label3 = tk.Label(self, width=5, relief="sunken", anchor='center')
        self.label3.pack(side='left', padx=1, ipadx=2, pady=1)
        self.pack(side=BOTTOM, fill=X, padx=2, pady=2)
        self.main_obj = main_obj

    def sstatus(self, texto, bg="SystemButtonFace"):
        if bg == 'red':
            bg = 'salmon'
        elif bg == 'green':
            bg = 'springgreen'
        self.label1.config(text=texto, bg=bg)  # 'salmon' for red , springgreen 'olivedrab1' for green
        self.label1.update_idletasks()
        self.main_obj.gaSet['root'].update()
        # self.gaSet['file_log'].info(f"{texto}")
        # self.gaSet['puts_log'].info(f"{texto}")

    def rstatus(self):
        return self.label1.cget('text')

    def startTime(self, texto):
        self.label2.config(text=texto)
        self.label2.update_idletasks()

    def runTime(self, texto):
        self.label3.config(text=texto)
        self.label3.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()

