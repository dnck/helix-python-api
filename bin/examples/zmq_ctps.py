# -*- coding:utf-8 -*-
'''
A ZMQ and Prometheus client for scrapping the helix-1.0 ZMQ topics
'''
import argparse
import json
import os
import regex
import zmq
from queue import Queue
from context import api
import time
from datetime import datetime
from context import results_manager
import threading
import random


TESTNET_HOSTS =  [
    "coo.hlxtest.net:8085",
    "zmq.hlxtest.net:8085",
    "hlxtest.net:8085",
    "node1.hlxtest.net:8085",
    "node2.hlxtest.net:8085",
    "node3.hlxtest.net:8085",
    "helix-esports.net:8085",
    "helixnetwork.ddns.net:80"
]

ALL_ZMQ_TOPICS = [
    'dns', 'nghbr', 'dnscv', 'dnscc', 'dnscu', 'hmr', 'antn', 'lmsi',
    'lmhs', 'rstat', 'rntn', 'rtl', 'lmi', 'lmhs', 'sn0', 'sn', 'ct5s2m',
    't5s2m', 'mctn', 'tx'
    ]

IO_OPTIONS = {
    'stdout_only': True,
    'level': 'info',
    'parentdir': '/Users/cook/helix/helix-python-api/bin/examples/results',
    'log_filename': 'ctps.log'
}

LOG_MANAGER = results_manager.ResultsManager(IO_OPTIONS)

LOGGER = LOG_MANAGER.logger

TXHASH_TEMPLATE = {
    'hash': None,
    'address': None,
    'msg': None,
    'signature': None,
    'value': None,
    'bundleNonceHash': None,
    'timestamp': None,
    'currentIndex': None,
    'lastIndex': None,
    'bundleHash': None,
    'trunk': None,
    'branch': None,
    'arrivalTime': None,
    'tagValue': None
}

TXHASH_PATTERN = regex.compile(r"\b[a-f0-9]{64}")

def convert_to_transaction(response, TXHASH_TEMPLATE):
    response = [i.split() for i in response['tx_hash']]
    TXHASH_TEMPLATE['hash'] = response[0][0]
    TXHASH_TEMPLATE['address'] = response[1][0]
    TXHASH_TEMPLATE['msg'] = response[2]
    TXHASH_TEMPLATE['signature'] = response[3][0]
    TXHASH_TEMPLATE['value'] = response[4][0]
    TXHASH_TEMPLATE['bundleNonceHash'] = response[5][0]
    TXHASH_TEMPLATE['timestamp'] = response[6][0]
    TXHASH_TEMPLATE['currentIndex'] = response[7][0]
    TXHASH_TEMPLATE['lastIndex'] = response[8][0]
    TXHASH_TEMPLATE['bundleHash'] = response[9][0]
    TXHASH_TEMPLATE['trunk'] = response[10][0]
    TXHASH_TEMPLATE['branch'] = response[11][0]
    TXHASH_TEMPLATE['arrivalTime'] = response[12][0]
    TXHASH_TEMPLATE['tagValue'] = response[13][0]
    return TXHASH_TEMPLATE

def convert_oracle_topic(d):
    temp = {'address': None}
    for k,v in d.items():
        temp['address'] = k.split('ORACLE_')[1]
        for item in json.loads(v[0]):
            temp.update({str(item['bundle_index']): item})
    return temp

def subscribe_to_zmq_topics(host, port, pending):
    value_tx = (None, None)

    # subscribe to all topics
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://{}:{}".format(host, port))
    socket.setsockopt_string(zmq.SUBSCRIBE, '')

    while True:
        string = socket.recv_string()
        now = datetime.now()
        data = {string.split(' ')[0]: string.split(' ')[1:]}
        match = regex.match(TXHASH_PATTERN, list(data.keys())[0])
        if 'tx_hash' in data.keys(): # tx_hash topic from MsgQPrvImpl.publishTx
            data = convert_to_transaction(data, TXHASH_TEMPLATE)
            if data['value'] != '0':
                value_tx = (data['hash'], now)
                pending.put(value_tx)
                LOGGER.info("Incoming value tx_hash: {}".format(value_tx[0]))
                LOGGER.info("Incoming value address: {}".format(
                    data["address"]
                ))
                LOGGER.info("Incoming value bundleHash: {}".format(
                    data["bundleHash"]
                ))

# You can actually randomly sample here - node_http_endpoints
def get_inclusion_state(api_client, node_http_endpoint, pending):
    UPPERLIMIT = 600 # ten minutes
    node_http_endpoints = [node_http_endpoint.format(i) for i in TESTNET_HOSTS]
    while True:
        tx_hash_local_time = pending.get(timeout=43200.0)
        if tx_hash_local_time:
            node_http_endpoint = random.choice(node_http_endpoints)
            latest_milestone = _get_latest_milestone(
                api_client, node_http_endpoint
            )
            LOGGER.debug(
                'Checking whether {} is approved by {}'.format(
                    tx_hash_local_time[0], latest_milestone[0]
                )
            )
            response = api_client.get_inclusion_states_of_parents(
                node_http_endpoint, [tx_hash_local_time[0]], latest_milestone
            )
            now = datetime.now()
            confirmed = response['states'].pop()
            duration = (now - tx_hash_local_time[1])
            if not confirmed and duration.total_seconds() < UPPERLIMIT:
                pending.put(tx_hash_local_time)
                LOGGER.debug(
                    "Tx pending confirmation: {}. "+\
                    "Tx will be purged from memory in {} seconds.".\
                        format(
                            tx_hash_local_time[0], 600-duration.total_seconds()
                        )
                )
            else:
                duration = (now - tx_hash_local_time[1])
                LOGGER.info(
                    'Tx confirmed {} after {} seconds.'.format(
                        tx_hash_local_time[0], duration.total_seconds()
                    )
                )
        time.sleep(5.0)

def _get_latest_milestone(api_client, node_http_endpoint):
    response = api_client.get_node_info(node_http_endpoint)
    latest_milestone = response['latestSolidSubtangleMilestone']
    return [latest_milestone]

if __name__ == '__main__':

    api_client = api.BaseHelixAPI()

    parser = argparse.ArgumentParser(
        description='Subscribe to a stream of data'
    )

    parser.add_argument(
        '-host',
         metavar='host',
         type=str,
         default='zmq.hlxtest.net',
         help='IP of host publisher'
    )

    parser.add_argument(
        '-port',
        metavar='port',
        type=str,
        default='5556',
        help='Port of the host publisher'
    )

    args = parser.parse_args()

    node_http_endpoint = "http://{}"

    pending =  Queue()

    t0 = threading.Thread(
        target=subscribe_to_zmq_topics,
        args=(args.host, args.port, pending,)
    )

    t1 = threading.Thread(
        target=get_inclusion_state,
        args=(api_client, node_http_endpoint, pending,)
    )

    t0.start()

    t1.start()
