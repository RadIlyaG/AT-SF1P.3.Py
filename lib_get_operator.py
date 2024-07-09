import re
from dialogBox import CustomDialog as DialogBox
from RL import Lib_RadApps


def gui_get_operator(msg, gaSet):
    parent = gaSet['root']
    ent_lbl = "Scan here the Operator's Employee Number "
    db_dict = {
        "title": "Get Operator Name",
        "type": ["Ok", "Cancel"],
        "message": msg,
        "icon": "images/oper32.ico",
        'default': 0,
        'entry_qty': 1,
        'entry_per_row': 1,
        'entry_lbl': [ent_lbl],
        'entry_frame_bd': 0
    }
    string, res_but, ent_dict = DialogBox(parent, db_dict).show()
    # print(f'gui_get_operator string:{string}, res_but:{res_but}, ent_dict:{ent_dict[ent_lbl].get()}')
    return res_but, ent_dict[ent_lbl].get()


if __name__ == '__main__':
    def get_e_n(gaSet):
        if gaSet['rad_net'] is False:
            return 0

        cont_while = True
        ret = -1
        msg = ""
        while cont_while:
            but, emp_numb = gui_get_operator(msg, gaSet)
            print(f'but:{but}, emp_numb:{emp_numb}')
            res = 0
            if but == 'Cancel':
                ret = -2
                break
            else:
                if len(emp_numb) != 6 or emp_numb.isdigit() is False:
                    msg = f"The number {emp_numb} is not valid\nTry again"
                    res = -1
                    continue

                if res == 0:
                    db_file = "operDB.db"
                    emp_name = Lib_RadApps.sqlite_get_empl_name(db_file, emp_numb)
                    if emp_name is None:
                        emp_name = Lib_RadApps.get_operator(emp_numb)
                        print(f'emp_numb:{emp_numb}, emp_name:{emp_name}')
                        if re.search('Employee Not Found!', emp_name):
                            msg = f"No operator name for number {emp_numb}\nTry again"
                            res = -1
                            continue
                        Lib_RadApps.sqlite_add_empl_name(db_file, emp_numb, emp_name)
                    return emp_name
                    # if all checks passed -> break the loop
                    ret = 0
                    cont_while = False
        if ret != 0:
            return ret

        # db_file = "operDB.db"
        # emp_name = Lib_RadApps.sqlite_get_empl_name(db_file, emp_numb)
        # if emp_name is None:
        #     emp_name = Lib_RadApps.get_operator(emp_numb)
        #     print(f'emp_numb:{emp_numb}, emp_name:{emp_name}')
        #     Lib_RadApps.sqlite_add_empl_name(db_file, emp_numb, emp_name)
        return emp_name

    from tkinter import Tk
    gaSet = {}
    root = Tk()
    gaSet['root'] = root
    gaSet['rad_net'] = True
    ret =0
    while ret != -2:
        ret = get_e_n(gaSet)

    root.mainloop()