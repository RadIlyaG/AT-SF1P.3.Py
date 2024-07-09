import rl_etx204

def OpenGen(main_obj, gen):
    com = main_obj.gaSet[f'comGen{gen}'][3:]
    e204 = rl_etx204.Etx204()
    print(f'com:{com}')
    ret = e204.open(com)
    print(f'ret of etx204 open:<{ret}>')


    e204.close()