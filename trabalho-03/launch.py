from subprocess import call
from random import randint
import time

for i in range(30000, 30004):
    call(['gnome-terminal', '-e', 'bash', '--command',
          'python proc.py {} {}'.format(str(i), str(i-30000))])
    time.sleep(1)
