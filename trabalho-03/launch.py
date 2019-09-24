from subprocess import call
from random import randint

r = randint(0, 4)

for i in range(0, 4):
    if i == r:
        call(['gnome-terminal', '-e', 'bash', '--command',
              'python proc.py 30000 {} 1'.format(str(i))])
    else:
        call(['gnome-terminal', '-e', 'bash', '--command',
              'python proc.py 30000 {} 0'.format(str(i))])
