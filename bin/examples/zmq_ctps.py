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
    "79.193.43.206:80"
]


IO_OPTIONS = {
    'stdout_only': False,
    'level': 'info',
    'parentdir': '/Users/cook/helix/helix-python-api/bin/examples/results',
    'log_filename': 'ctps.log'
}

log_manager = results_manager.ResultsManager(IO_OPTIONS)

logger = log_manager.logger


txhash_template = {
    'hash': None,
    'address1': None,
    'msg': None,
    'address2': None,
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

txhash_pattern = regex.compile(r"\b[a-f0-9]{64}")

def convert_response(txhash_template, response):
    response = [i.split() for i in response['tx_hash']]
    txhash_template['hash'] = response[0][0]
    txhash_template['address1'] = response[1][0]
    txhash_template['msg'] = response[2]
    txhash_template['address2'] = response[3][0]
    txhash_template['value'] = response[4][0]
    txhash_template['timestamp'] = response[5][0]
    txhash_template['timestamp'] = response[6][0]
    txhash_template['currentIndex'] = response[7][0]
    txhash_template['lastIndex'] = response[8][0]
    txhash_template['bundleHash'] = response[9][0]
    txhash_template['trunk'] = response[10][0]
    txhash_template['branch'] = response[11][0]
    txhash_template['arrivalTime'] = response[12][0]
    txhash_template['tagValue'] = response[13][0]
    return txhash_template

def convert_oracle_topic(d):
    temp = {'address': None}
    for k,v in d.items():
        temp['address'] = k.split('ORACLE_')[1]
        for item in json.loads(v[0]):
            temp.update({str(item['bundle_index']): item})
    return temp

ALL_ZMQ_TOPICS = [
    'dns', 'nghbr', 'dnscv', 'dnscc', 'dnscu', 'hmr', 'antn', 'lmsi',
    'lmhs', 'rstat', 'rntn', 'rtl', 'lmi', 'lmhs', 'sn0', 'sn', 'ct5s2m',
    't5s2m', 'mctn', 'tx'
    ]

def write_dict_to_json(filename, data):
    """Write an in-memory Python dictionary to a formatted .json file."""
    filename = os.path.normpath(filename)
    with open(filename, "a") as file_obj:
        json.dump(data, file_obj, indent=4, sort_keys=True)
        file_obj.write(',\n')

def mkdir_if_not_exists(dirname):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

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
        logger.info('Topic: {}'.format(string.split(' ')[0]))
        match = regex.match(txhash_pattern, list(data.keys())[0])

        # this comes first
        if 'tx_hash' in data.keys(): # tx_hash topic from MsgQPrvImpl.publishTx
            data = convert_response(txhash_template, data)
            if data['value'] != '0':
                value_tx = (data['hash'], now)
                pending.put(value_tx)
                logger.info("Incoming value tx_hash: {}".format(value_tx[0]))
                logger.info("Incoming value address: {}".format(
                    data["address1"]
                ))
                logger.info("Incoming value bundleHash: {}".format(
                    data["bundleHash"]
                ))
        # then comes this
        if list(data.keys())[0].startswith(
            'ORACLE' # oracle topic from Node.processReceivedData
        ):
            data = convert_oracle_topic(data)
            logger.info('Bundle address published: {}'.format(data['address']))
            for x in data:
                if not (x == 'address'):
                    logger.info(
                        'bundle_hash: {}'.format(
                            data[x]['bundle_hash']
                        )
                    )
                    logger.info(
                        'tx_hash: {}'.format(
                            data[x]['tx_hash']
                        )
                    )
        # then comes this?
        if match: # tx topic from where? and what does it mean?
            data = json.loads(data[match.string][0])
            data.update({'address': match.string})
            logger.info('tx address: {}'.format(data['address']))
            logger.info('tx hash: {}'.format(data['hash']))


# You can actually randomly sample here - node_http_endpoints
def get_inclusion_state(api_client, node_http_endpoint, pending):
    node_http_endpoints = [node_http_endpoint.format(i) for i in TESTNET_HOSTS]
    while True:
        tx_hash_local_time = pending.get(timeout=43200.0)

        if tx_hash_local_time:
            node_http_endpoint = random.choice(node_http_endpoints)
            latest_milestone = _get_latest_milestone(
                api_client, node_http_endpoint
            )
            logger.info(
                'Checking whether {} is approved by {}'.format(
                    [tx_hash_local_time[0]], latest_milestone[0]
                )
            )
            response = api_client.get_inclusion_states_of_parents(
                node_http_endpoint, [tx_hash_local_time[0]], latest_milestone
            )
            now = datetime.now()
            confirmed = response['states'].pop()
            if not confirmed:
                pending.put(tx_hash_local_time)
            else:
                duration = (now - tx_hash_local_time[1])
                logger.info(
                    'Time (s) until confirmation for tx {} = {}'.format(
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

    #mkdir_if_not_exists('./results')
    t1 = threading.Thread(
        target=get_inclusion_state,
        args=(api_client, node_http_endpoint, pending,)
    )

    t0.start()

    t1.start()
