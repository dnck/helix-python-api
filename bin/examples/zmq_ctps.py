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

IO_OPTIONS = {
    'stdout_only': True, 'level': 'info', 'parentdir': '/home/hlx-dev/helix/helix-python-api/examples',
    'log_filename': 'ctps.log'
}
log_manager = results_manager.ResultsManager(IO_OPTIONS)
logger = log_manager.logger


template = {
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

def convert_response(template, response):
    response = [i.split() for i in response['tx_hash']]
    template['hash'] = response[0][0]
    template['address1'] = response[1][0]
    template['msg'] = response[2]
    template['address2'] = response[3][0]
    template['value'] = response[4][0]
    template['timestamp'] = response[5][0]
    template['timestamp'] = response[6][0]
    template['currentIndex'] = response[7][0]
    template['lastIndex'] = response[8][0]
    template['bundleHash'] = response[9][0]
    template['trunk'] = response[10][0]
    template['branch'] = response[11][0]
    template['arrivalTime'] = response[12][0]
    template['tagValue'] = response[13][0]
    return template

def convert_oracle_topic(d):
    temp = {'address': None}
    for k,v in d.items():
        temp['address'] = k.split('ORACLE_')[1]
        for item in json.loads(v[0]):
            #temp.update((item))
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
        match = regex.match(txhash_pattern, list(data.keys())[0])
        # this comes first
        if 'tx_hash' in data.keys(): # tx_hash topic from MsgQPrvImpl.publishTx
            data = convert_response(template, data)
            if data['value'] != '0':
                value_tx = (data['hash'], now)
                pending.put(value_tx)
                logger.info(
                    "Observed new value tx in zmq at time: {} {}".format(
                        value_tx[0], now
                    )
                )
                #print('\n')
        # then comes this
        if list(data.keys())[0].startswith(
            'ORACLE' # oracle topic from Node.processReceivedData
        ):
            data = convert_oracle_topic(data)
        # then comes this?
        if match: # tx topic from where?
            data = json.loads(data[match.string][0])
            data.update({'address': match.string})


def get_inclusion_state(api_client, node_http_endpoint, pending):
    while True:
        tx_hash_local_time = pending.get(timeout=43200.0)
        if tx_hash_local_time:
            latest_milestone = _get_latest_milestone(node_http_endpoint)
            # print(
            #     'Checking whether {} is approved by {}'.format(
            #         [tx_hash_local_time[0]], latest_milestone[0]
            #     )
            # )
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
        time.sleep(1.0)

def _get_latest_milestone(node_http_endpoint):
    response = API_CLIENT.get_node_info(node_http_endpoint)
    latest_milestone = response['latestSolidSubtangleMilestone']
    return [latest_milestone]

if __name__ == '__main__':
    API_CLIENT = api.BaseHelixAPI()

    parser = argparse.ArgumentParser(description='Subscribe to a stream of data')
    parser.add_argument('--host', metavar='host', type=str, default='zmq.hlxtest.net', help='IP of host publisher')
    parser.add_argument('--port', metavar='port', type=str, default='5556', help='Port of the host publisher')
    args = parser.parse_args()

    node_http_endpoint = "http://{}:{}".format(args.host, 8085)

    pending =  Queue()
    t0 = threading.Thread(target=subscribe_to_zmq_topics, args=(args.host, args.port, pending,))
    #mkdir_if_not_exists('./results')
    t1 = threading.Thread(target=get_inclusion_state, args=(API_CLIENT, node_http_endpoint, pending,))

    t0.start()
    t1.start()
