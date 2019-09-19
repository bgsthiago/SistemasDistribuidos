import threading
import time
import struct
import socket
import sys
import random
import json
import os
from operator import itemgetter

PORT = 5007
GROUP = '224.1.1.1'
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
    # Update Lamport's clock only if incoming message isn't my own
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

        print(f'Received ACK {msg_id} {msg_timestamp}')

        for i in message_queue:
            # print('id e timestamp da msg: ', msg_id, i['id'], msg_timestamp, i['timestamp'])
            if i['id'] == msg_id and i['timestamp'] == msg_timestamp:
                i['n_ack'] += 1
                # print(i['n_ack'])

                # If all ACK's were received, message is ready to be delievered
                if i['n_ack'] == NPROCESS:
                    print('-------- Message queue ------')
                    [print(item) for item in message_queue]
                break

    else:
        print(f'Received message: {message}')

        # Add message to the queue with 0 ACK received
        message['n_ack'] = 0
        message_queue.append(message)
        
        # Send ACK
        # ACK format: 'ACK msg_id msg_timestamp'
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


def sender(message):
    # Create UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Time-to-live.
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
    message_queue = []
    id = os.getpid()

    print(f"Starting proccess: {id}")

    # Create thread that will receive messages
    t = threading.Thread(target=receiver, args=(message_queue, id))
    t.start()

    # Main thread
    while(True):
        input()
        msg = random.choice(MSGS)
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
