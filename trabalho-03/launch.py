from subprocess import call
from random import randint
import time

for i in range(30000, 30005):
    call(['gnome-terminal', '-e', 'bash', '--command',
          'python3 proc.py {} {}'.format(str(i), str(i-30000))])
    time.sleep(1)
