""" Sistemas Distribuídos 2019/2 - Atividade 3
    Algoritmo do Valentão

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

NPROCESS = 5
PORT_LIST = [30000, 30001, 30002, 30003, 30004]
TIME_LIMIT = 3 # in seconds
MSGS = ['Alice', 'Helena', 'Isabela', 'Laura', 'Luiza', 'Manuela', 'Sofia', 'Valentina',
        'Arthur', 'Bernardo', 'Davi', 'Gabriel', 'Heitor', 'Lucca', 'Lorenzo', 'Miguel', 'Matheus', 'Pedro']

# Lamport's clock
clock = 1

my_port = int(sys.argv[1])
my_id = int(sys.argv[2])
election_responses = []
current_leader = 0
last_message_ACK = False
started_election = False


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


def election():
    global current_leader
    global started_election

    if started_election == True:
        return
    else:
        started_election = True

    message = {
        'id': my_id,
        'timestamp': clock,
        'content': f'ELECTION {my_id}',
        'type': 'ELECTION'
    }

    # Send election message to all process with higher ID 
    if my_id < NPROCESS-1:
        for i in range(my_id + 1, NPROCESS):
            sender(message, PORT_LIST[i])

        time.sleep(TIME_LIMIT)

    # If no one replies OK for election message or
    # this process has the highest ID
    # make this process leader
    if len(election_responses) == 0:
        announcement_msg = {
            'id': my_id,
            'timestamp': clock,
            'content': f'LEADER ANNOUNCEMENT {my_id}',
            'type': 'LEADER_ANNOUNCEMENT'
        }

        current_leader = my_id
        print(f'---- The new leader is {current_leader} -----\n')

        for i in range(NPROCESS):
            if i != my_id:
                sender(announcement_msg, PORT_LIST[i])

    election_responses.clear()


if __name__ == "__main__":
    print(f"Starting proccess: {my_id}")

    # Cria thead responśvel por receber as mensagens
    t = threading.Thread(target=receiver, args=(my_id, my_port))
    t.start()

    # Main thread
    while(True):
        dest = int(input())
        msg = random.choice(MSGS)
        print("")

        message = {
            'id': my_id,
            'timestamp': clock,
            'content': msg,
            'type': 'NORMAL'
        }

        # Send message and wait for ACK
        last_message_ACK = False
        sender(message, PORT_LIST[dest])
        time.sleep(TIME_LIMIT)

        # If leader doesn't respond ACK,
        # start new election
        if last_message_ACK == False and dest == current_leader:
            election_thread = threading.Thread(target=election)
            election_thread.start() 

        print("")
