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

neighbor = {
    0: [1, 9],
    1: [0, 2, 6],
    2: [1, 3],
    3: [2, 4, 5],
    4: [3, 5, 6],
    5: [3, 4, 8],
    6: [1, 4, 7, 9],
    7: [6, 8],
    8: [7, 5],
    9: [0, 6]
}

NPROCESS = 10
PORT_LIST = [i for i in range(30000, 30010)]

my_id = int(sys.argv[1])
my_cap = int(sys.argv[2])
current_leader = 0
started_election = False
parent = -1
response_list = []
child_list = []
election_id = -1


def reset_structures():
    global response_list
    global child_list
    global parent
    global start_election

    response_list = []
    child_list = []
    parent = -1
    start_election = False


def make_reply(msg_type, capacity, cap_owner):
    msg = {
        'id': my_id,
        'capacity': capacity,
        'cap_owner': cap_owner,
        'type': msg_type
    }

    return msg


def handle_message(msg, my_id):
    global current_leader
    global started_election
    global parent
    global election_id

    print(f'\nReceived message: {msg}')

    msg_type = msg['type']
    print(f'------- TIPO DA MENSAGEM :{msg_type}')

    if msg_type == 'ELECTION STARTED':
        
        # se nao tem eleicao acontecendo
        if election_id == -1:
            election_id = msg['election_id']
        # se tem eleicao acontecendo, pega a com maior id
        elif msg['election_id'] != election_id:
                if msg['election_id'] > election_id:
                    election_id = msg['election_id']
                    reset_structures()
                else:
                    return

        # envia mensagem ao pai, para que o pai possa adicioná-lo
        # a sua lista de filhos
        if parent == -1:
            parent = msg['id']

            child_msg = {
                'id': my_id,
                'type': 'CHILD ANNOUNCEMENT'
            }

            sender(child_msg, PORT_LIST[parent])

            start_election(my_id, election_id)
        else:
            reply = make_reply('RESPONSE', my_cap, my_id)
            send_reply(reply, PORT_LIST[msg['id']])
    elif msg_type == 'RESPONSE':
        response_list.append(msg)

        print(len(response_list), len(neighbor[my_id]))
        
        max_cap = my_cap
        cap_owner = my_id
        # pega a maior capacidade
        for i in response_list:
            if i['capacity'] > max_cap:
                max_cap = i['capacity']
                cap_owner = i['cap_owner']

        if started_election == False:
            if len(response_list) == len(neighbor[my_id]) - 1:
                # responde o pai
                reply = make_reply('RESPONSE', max_cap, cap_owner)
                send_reply(reply, PORT_LIST[parent])

        # mensagem de resposta chegou na fonte
        else:
            if len(response_list) == len(neighbor[my_id]):
                current_leader = cap_owner
                announce_leader(cap_owner)

    elif msg_type == 'LEADER ANNOUNCEMENT':
        current_leader = msg['leader_id']

        # repassa mensagem de novo lider para os filhos
        announce_leader(current_leader)

        reset_structures()
        election_id = -1
    
    elif msg_type == 'CHILD ANNOUNCEMENT':
        child_list.append(msg['id'])


# envia mensagem de novo lider para todos os filhos
def announce_leader(leader_id):
    for i in child_list:
            msg = {
                'id': my_id,
                'leader_id': leader_id,
                'type': 'LEADER ANNOUNCEMENT'
            }

            sender(msg, PORT_LIST[i])


def receiver(my_id, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))

    while True:
        data, source = s.recvfrom(1500)
        data = data.decode('utf-8')
        message = json.loads(data)

        t = threading.Thread(target=handle_message,
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



def sender(message, port):
    time.sleep(1)
    # Create UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Send message
    message['reply_port'] = PORT_LIST[my_id]
    data = json.dumps(message)
    print(f'Sending {message} to {port}...\n\n')
    s.sendto(data.encode('utf-8'), ('127.0.0.1', port))


def start_election(my_id, election_id):
    message = {
        'id': my_id,
        'type': 'ELECTION STARTED',
        'election_id': election_id
    }

    for each in neighbor[my_id]:
        if each != parent:
            sender(message, PORT_LIST[each])


if __name__ == "__main__":
    print(f"Starting proccess: {my_id}")

    # Cria thead responśvel por receber as mensagens
    t = threading.Thread(target=receiver, args=(my_id, PORT_LIST[my_id]))
    t.start()

    # Main thread
    while(True):
        cmd = input()
        # Starting election
        if cmd == 'start':
            started_election = True
            election_id = time.time()
            start_election(my_id, election_id)
        if cmd == 'leader':
            print('')
            print(f' O lider atual é {current_leader}') 
            print('')

        print("")
