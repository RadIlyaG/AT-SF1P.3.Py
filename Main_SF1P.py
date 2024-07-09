from tkinter import Tk

class MainTester():
    def __init__(self, gui_num):
        self.gui_num = gui_num
        root = Tk()
        root.mainloop()

    
if __name__ == '__main__':
    print(f'Main sf1p')
    tester = MainTester(33)
    print(tester.gui_num)
    