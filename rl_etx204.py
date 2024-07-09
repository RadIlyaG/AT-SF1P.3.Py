import tkinter
from tkinter import messagebox

class Etx204:
    def __init__(self):
        self.tkl = tkinter.Tk()
        self.tkl.eval('source lib_etx204_scr.tcl')
        
    def open(self, gen):
        return self.tkl.eval(f'RLEtxGen::Open {gen} -package RLCom')
        
    def close(self):
        return self.tkl.eval(f'RLEtxGen::CloseAll')
        