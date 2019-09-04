import threading
import time
import struct
import socket
import sys
import random
import json
import os
from operator import itemgetter

PORT = 9001
GROUP = '225.0.0.250'
NPROCESS = 3

MSGS = ['Alice', 'Helena', 'Isabela', 'Laura', 'Luiza', 'Manuela', 'Sofia', 'Valentina',
        'Arthur', 'Bernardo', 'Davi', 'Gabriel', 'Heitor', 'Lucca', 'Lorenzo', 'Miguel', 'Matheus', 'Pedro']

# Lamport's clock
clock = int(sys.argv[1])


def add_socket_to_group():
    # Create UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Allow the address to be used by more than one socket
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(('', PORT))

    group = socket.inet_aton(GROUP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    return s



def proccess_message(message, message_queue, my_id):
    global clock

    message_queue.append(message)

    # Sort the queue by timestamp then by proccess ID
    message_queue.sort(key=itemgetter('timestamp', 'id'))

    print('-------- Message queue ------')
    [print(x) for x in message_queue]

    # Update Lamport's clock only if the incoming message isn't mine
    if message['id'] != my_id:
        msg_timestamp = message['timestamp']
        if msg_timestamp > clock:
            clock = msg_timestamp + 1
        else:
            clock += 1


def receiver(message_queue, my_id):
    s = add_socket_to_group()

    # Print all data received in multicast group
    while True:
        data, source = s.recvfrom(1500)
        data = data.decode('utf-8')
        message = json.loads(data)

        # print(id, timestamp, content)
        print("")
        t = threading.Thread(target=proccess_message, args=(message, message_queue, my_id))
        t.start()


def sender(message, message_queue):
    # Create UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send message
    data = json.dumps(message)
    s.sendto(data.encode('utf-8'), (GROUP, PORT))
    time.sleep(0.5)

    # Update clock
    global clock
    clock += 1


if __name__ == "__main__":
    message_queue = []
    id = os.getpid()

    print(f"Starting proccess: {id}")

    # Cria thead responśvel por receber as mensagens
    t = threading.Thread(target=receiver, args=(message_queue, id))
    t.start()

    # Thread principal é responsável por enviar os pacotes e "entregá-los" à aplicação
    while(True):
        input()
        msg = random.choice(MSGS)
        print("")
        message = {
            'id': id,
            'timestamp': clock,
            'content': msg
        }
        sender(message, message_queue)
        print("")
        time.sleep(1)
