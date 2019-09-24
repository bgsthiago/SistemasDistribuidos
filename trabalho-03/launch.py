from subprocess import call
from random import randint

r = randint(30000, 30004)

for i in range(30000, 30004):
    if i == r:
        call(['gnome-terminal', '-e', 'bash', '--command',
              'python proc.py {} 1'.format(str(i))])
    else:
        call(['gnome-terminal', '-e', 'bash', '--command',
              'python proc.py {} 0'.format(str(i))])
