""" Sistemas Distribuídos 2019/2 - Atividade 1
    Multicast ordenado utilizando relógios de Lampert

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
from operator import itemgetter
from resource import Resource

PORT = 5007
GROUP = '224.1.1.1'
NPROCESS = 3

# MSGS = ['Alice', 'Helena', 'Isabela', 'Laura', 'Luiza', 'Manuela', 'Sofia', 'Valentina',
#         'Arthur', 'Bernardo', 'Davi', 'Gabriel', 'Heitor', 'Lucca', 'Lorenzo', 'Miguel', 'Matheus', 'Pedro']

RESOURCES = ['A', 'B', 'C']

# Lamport's clock
clock = int(sys.argv[1])


def add_socket_to_group():
    # Create UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Allow the address to be used by more than one socket
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(('', PORT2))

    group = socket.inet_aton(GROUP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    return s


def make_reply(type, my_id, resource_name, timestamp):
    return {
        'id': my_id,
        'timestamp': clock,
        'is_ack': False,
        'content': {
            'resource_name': resource_name,
            'type': type
        }
    }


def access_resource(resource):
    global clock

    print(f'Acessando recurso {resource}...')
    time.sleep(1)
    print(f'Liberando recurso {resource}...')

    # Send OK messages every processes in next_queue
    for addr in resource.next_queue:
        reply = make_reply('OK', my_id, resource_name, clock)
        send_reply(reply, addr)

    # Reset state, next_queue and number of "OK" received
    resource.state = 'unrequested'
    resource.next_queue.clear()
    resource.n_ok = 0


# message content: {resource_name, type}
def hand_message(msg, resource_list, my_id):
    global clock
    reply = None
    
    # Get resource in resource list
    resource_name = msg['content']['resource_name']
    idx = resource_list.index(Resource(resource_name))
    resource = resource_list[idx]

    if msg['content']['type'] == 'REQUEST':
        # If i'm accessing the resource, send a "permission denied" reply
        if resource.state == 'using':
            reply = make_reply('PERMISSION DENIED', my_id, resource_name, clock)

        # If i want to access the resource, check who requested it first:
        #  - If it was me, send a "permission denied" reply
        #  - If it wasn't me, send an "OK" reply
        elif resource.state == 'requested':
            if resource.req_timestamp < msg['timestamp']:
                reply = make_reply('PERMISSION DENIED', my_id, resource_name, clock)
            elif resource.req_timestamp == msg['timestamp']:
                if my_id > msg['id']:
                    reply = make_reply('PERMISSION DENIED', my_id, resource_name, clock)
                else:
                    reply = make_reply('OK', my_id, resource_name, clock)
            else:
                reply = make_reply('OK', my_id, resource_name, clock)
        # If I don't want to access the resource, send an "OK" reply
        else:
            reply = make_reply('OK', my_id, resource_name, clock)

        # If I've send a "permission denied" reply, put the sender process in next_queue
        if reply['content']['type'] == 'PERMISSION DENIED':
            resource.next_queue.append(msg['addr'])
            
    elif msg['content']['type'] == 'OK':
        resource.n_ok += 1

        # If I've got everyone's "OK", access resource
        if resource.n_ok == NPROCESS-1:
            access_resource(resource)
    
    send_reply(reply, msg['addr'])


def proccess_message(message, message_queue, resource_list, my_id):
    global clock
    # Update Lamport's clock only if the incoming message isn't mine
    if message['id'] != my_id:
        msg_timestamp = message['timestamp']
        if msg_timestamp > clock:
            clock = msg_timestamp + 1
        else:
            clock += 1

    # ACK format: 'ACK msg_id msg_timestamp'
    if message['is_ack'] == True:
        msg = message['content'].split(' ')
        msg_id = int(msg[1])
        msg_timestamp = int(msg[2])

        # Find message that this ACK belongs to
        for i in message_queue:
            # print('id e timestamp da msg: ', msg_id, i['id'], msg_timestamp, i['timestamp'])
            if i['id'] == msg_id and i['timestamp'] == msg_timestamp:
                i['n_ack'] += 1
                # print(i['n_ack'])

                # If all ACK's were received, message is ready to be delievered
                if i['n_ack'] == NPROCESS:
                    print('-------- Message queue ------')
                    [print(item) for item in message_queue]

                    # Send message to application
                    if i['id'] != my_id:
                        hand_message(i, resource_list, my_id)

                break

    else:
        # Add message to the queue with 0 ACK received
        print(f'Received message: {message}')

        message['n_ack'] = 0
        message_queue.append(message)
        
        # Send ACK
        msg_id = message['id']
        msg_timestamp = message['timestamp']

        ack_message = {
            'id': my_id,
            'timestamp': clock,
            'content': f'ACK {msg_id} {msg_timestamp}',
            'is_ack': True
        }

        print(f'Sending ACK {msg_id} {msg_timestamp}')
        sender(ack_message)

        # Sort the queue by timestamp then by proccess ID
        message_queue.sort(key=itemgetter('timestamp', 'id'))


def receiver(message_queue, resource_list, my_id):
    global s

    # Print all data received in multicast group
    while True:
        data, source = s.recvfrom(1500)
        data = data.decode('utf-8')
        message = json.loads(data)
        message['addr'] = source

        # print(id, timestamp, content)
        print("")
        t = threading.Thread(target=proccess_message, args=(message, message_queue, resource_list, my_id))
        t.start()


def send_reply(message, addr):
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    global s
    
    # Send reply message
    data = json.dumps(message)
    s.sendto(data.encode('utf-8'), addr)

    # Update clock
    global clock
    clock += 1


def sender(message):
    # Create UDP socket
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    global s

    # Time-to-live (optional). Não permitir que o pacote alcance se espalhe para a rede externa
    ttl_bin = struct.pack('@i', 1)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)

    # Send message
    data = json.dumps(message)
    print(f'Sending {message}...\n\n')
    s.sendto(data.encode('utf-8'), (GROUP, PORT))
    # time.sleep(0.5)

    # Update clock
    global clock
    clock += 1

if __name__ == "__main__":
    s = add_socket_to_group()
    message_queue = []
    resource_list = [Resource(i) for i in RESOURCES]

    id = os.getpid()

    print(f"Starting proccess: {id}")

    # Cria thead responśvel por receber as mensagens
    t = threading.Thread(target=receiver, args=(message_queue, resource_list, id))
    t.start()

    # Main thread
    while(True):
        resource_name = input('Insira o nome do recurso que deseja utilizar (A, B, C): ')

        # Change the desired resource's state to requested and set request timestamp
        idx = resource_list.index(Resource(resource_name))
        resource = resource_list[idx]
        resource.state = 'requested'
        resource.req_timestamp = clock

        # Create request message
        msg = {
            'resource_name': resource_name,
            'type': 'REQUEST'
        }

        print("")
        print(f'Pedindo permissão para utilizar o recurso {resource_name}')
        print("")

        message = {
            'id': id,
            'timestamp': clock,
            'content': msg,
            'is_ack': False
        }
        sender(message)
        print("")
        
        # time.sleep(1)
