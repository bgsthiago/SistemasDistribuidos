from subprocess import call
from random import randint
import time

PORT_LIST = [i for i in range(30000, 30010)]

capacidade = {
    0: 4,
    1: 6,
    2: 3,
    3: 2,
    4: 1,
    5: 4,
    6: 2,
    7: 8,
    8: 5,
    9: 4

}

for k, v in capacidade.items():
    call(['gnome-terminal', '-e', 'bash', '--command',
          'python3 proc.py {} {}'.format(str(k), str(v))])
    time.sleep(1)
