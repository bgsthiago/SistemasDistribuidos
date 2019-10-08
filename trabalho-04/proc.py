""" Sistemas Distribuídos 2019/2 - Atividade 4
    Algoritmo de eleição de líder em rede wireless

    Integrantes:
    Luiz Felipe Guimarães - RA: 743570
    Thiago Borges         - RA: 613770
"""


import threading
import time
import struct
import socket
import sys
import random
import json
import os


neibor = {1: [2, 3, 4],
          2: [1, 3],
          3: [5, 1, 2],
          4: [1, 5],
          5: [4, 3],
          6: [],
          7: [],
          8: [],
          9: [],
          10: []
          }


NPROCESS = 10
PORT_LIST = [30001, 30002, 30003, 30004, 30006, 30007, 30008, 30009, 30010]
TIME_LIMIT = 3  # in seconds
MSGS = ['Alice', 'Helena', 'Isabela', 'Laura', 'Luiza', 'Manuela', 'Sofia', 'Valentina',
        'Arthur', 'Bernardo', 'Davi', 'Gabriel', 'Heitor', 'Lucca', 'Lorenzo', 'Miguel', 'Matheus', 'Pedro']

# Lamport's clock
clock = 1

my_port = int(sys.argv[1])
my_id = int(sys.argv[2])
my_cap = int(sys.arv[3])
election_responses = []
current_leader = 0
last_message_ACK = False
started_election = False
received_election = False
father = 0


def make_reply(msg_type, content):
    msg = {
        'id': my_id,
        'timestamp': clock,
        'content': content,
        'type': msg_type
    }

    return msg


def handle_message(msg, my_id):
    global clock
    global last_message_ACK
    global current_leader
    global started_election
    global father

    msg_type = msg['type']
    print(f'------- TIPO DA MENSAGEM :{msg_type}')

    if msg_type == 'ACK':
        last_message_ACK = True
    elif msg_type == 'OK':
        election_responses.append(msg['id'])
    elif msg_type == 'ELECTION':
        reply = make_reply('OK', f'OK {my_id}')
        send_reply(reply, msg['reply_port'])

        election_thread = threading.Thread(target=election)
        election_thread.start()
    elif msg_type == 'LEADER_ANNOUNCEMENT':
        started_election = False
        current_leader = msg['id']
        print(f'---- The new leader is {current_leader} -----\n')
    elif msg_type == 'STARTED ELECTION':
        if father != 0:
            father = msg['id']
            start_election(my_id, clock)
    else:
        msg_id = msg['id']
        msg_timestamp = msg['timestamp']

        reply = make_reply('ACK', f'ACK {msg_id} {msg_timestamp}')
        send_reply(reply, msg['reply_port'])


def proccess_message(message, my_id):
    global clock

    # Update Lamport's clock only if the incoming message isn't mine
    if message['id'] != my_id:
        msg_timestamp = message['timestamp']
        if msg_timestamp > clock:
            clock = msg_timestamp + 1
        else:
            clock += 1

    handle_message(message, my_id)

    # Add message to the queue with 0 ACK received
    print(f'\nReceived message: {message}')


def receiver(my_id, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))

    while True:
        data, source = s.recvfrom(1500)
        data = data.decode('utf-8')
        message = json.loads(data)

        t = threading.Thread(target=proccess_message,
                             args=(message, my_id))
        t.start()


def send_reply(message, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send reply message
    data = json.dumps(message)
    print(f'Sending reply {message} to {port}...\n\n')
    try:
        s.sendto(data.encode('utf-8'), ('', port))
    except OSError:
        pass

    # Update clock
    global clock
    clock += 1


def sender(message, port):
    time.sleep(1)
    # Create UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send message
    message['reply_port'] = my_port
    data = json.dumps(message)
    print(f'Sending {message} to {port}...\n\n')
    s.sendto(data.encode('utf-8'), ('127.0.0.1', port))

    # Update clock
    global clock
    clock += 1


def start_election(my_id, clock):
    message = {
        'id': my_id,
        'timestamp': clock,
        'type': 'ELECTION STARTED',
        'timestamp': time.time()
    }

    for each in neibor[my_id]:
        if each != father:
            sender(message, PORT_LIST[each])


if __name__ == "__main__":
    print(f"Starting proccess: {my_id}")

    # Cria thead responśvel por receber as mensagens
    t = threading.Thread(target=receiver, args=(my_id, my_port))
    t.start()

    # Main thread
    while(True):
        cmd = input()
        # Starting election
        if cmd == 'start':
            started_election = True
            start_election(my_id, clock)

        print("")
