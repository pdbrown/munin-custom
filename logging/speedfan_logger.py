#!/usr/local/bin/python

import select
import socket
import json
import time
from collections import defaultdict



port = 3639  # where do you expect to get a msg?
bufferSize = 10240 # whatever you need

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('', port))
s.setblocking(0)


START_XAP = 'xAP-header'

def xap_iter(xap_msg):
    in_payload = False
    payload = {}
    for line in iter(xap_msg.splitlines()):
        if line.startswith('{'):
            in_payload = True
            continue
        if in_payload:
            if line.startswith('}'):
                in_payload = False
                yield payload
                continue
            tokens = line.split('=')
            payload[tokens[0]] = tokens[1]


while True:
    result = select.select([s],[],[])
    msg = result[0][0].recv(bufferSize)
    stats = defaultdict(list)
    for payload in xap_iter(msg):
        if not 'id' in payload:
            continue
        stats[payload['id']].append(payload['curr'])
    if len(stats) == 0:
        continue
    stats['time'] = long(time.time())
    with open('/var/log/speedfan.log', 'a') as log:
        json.dump(stats, log)
        log.write('\n')
