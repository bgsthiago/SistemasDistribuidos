import threading
import time
import struct
import socket
import sys
import random

PORT = 9001
GROUP = '225.0.0.250'
NPROCESS = 3

MSGS = ['Alice', 'Helena', 'Isabela', 'Laura', 'Luiza', 'Manuela', 'Sofia', 'Valentina',
        'Arthur', 'Bernardo', 'Davi', 'Gabriel', 'Heitor', 'Lucca', 'Lorenzo', 'Miguel', 'Matheus', 'Pedro']


def add_socket_to_group():
    # Cria um socket UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Permite que mais de um socket utilize o mesmo endereço na mesma máquina
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Conecta por localhost e porta fornecida
    s.bind(('', PORT))

    group = socket.inet_aton(GROUP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    return s


def receiver(id, clock, lista):

    s = add_socket_to_group()

    # Loop, printing any data we receive
    while True:
        data, source = s.recvfrom(1500)
        while data[-1:] == '\0':
            data = data[:-1]  # Strip trailing \0's
        msg = data.decode('utf-8')

        print(id, clock, msg)


def sender(message):
    # Cria socket UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Enviar a mensagem
    data = message.encode('utf-8') + b'\0'
    s.sendto(data, (GROUP, PORT))
    time.sleep(0.5)


if __name__ == "__main__":
    lista = []
    id = sys.argv[1]
    clock = sys.argv[2]

    # Cria thead responśvel por receber as mensagens
    t = threading.Thread(target=receiver, args=(id, clock, lista))
    t.start()

    # Thread principal é responsável por enviar os pacotes e "entregá-los" à aplicação
    while(True):
        time.sleep(1)
        input()
        msg = random.choice(MSGS)
        print("")
        message = {
            'id': sys.argv[1],
            'timestamp': sys.argv[2],
            'content': msg
        }
        sender(message)
        print("")
