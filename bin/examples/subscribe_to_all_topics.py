# -*- coding:utf-8 -*-
'''
A ZMQ and Prometheus client for scrapping the helix-1.0 ZMQ topics

Note, instead of iterating through the list,

ALL_ZMQ_TOPICS = [
    'dns', 'nghbr', 'dnscv', 'dnscc', 'dnscu', 'hmr', 'antn', 'lmsi',
    'lmhs', 'rstat', 'rntn', 'rtl', 'lmi', 'lmhs', 'sn0', 'sn', 'ct5s2m',
    't5s2m', 'mctn', 'tx'
    ]

we subscribe to all topics by opening a zmq context socket configured to
listen for all messages on a specific port.

Some of the messages we receive through zmq are not formatted for dumping to
json, so we decode these messages and parse them to json like objects. These objects are dumped to a directory on the filesystem.
'''
import argparse
import json
import os
import regex
import zmq

from context import results_manager

IO_OPTIONS = {
    'stdout_only': True,
    'level': 'info',
    'parentdir': '/Users/cook/helix/helix-python-api/bin/examples/results',
    'log_filename': 'ctps.log'
}

LOG_MANAGER = results_manager.ResultsManager(IO_OPTIONS)

LOGGER = LOG_MANAGER.logger

class ResponseConverter():

    def __init__(self):

        self.txhash_pattern = regex.compile(r"\b[a-f0-9]{64}")

        self.txhash_template = {
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

    def match_txhash(self, str):
        return regex.match(self.txhash_pattern, str)

    def convert_to_transaction(self, response):
        response = [i.split() for i in response['tx_hash']]
        self.txhash_template['hash'] = response[0][0]
        self.txhash_template['address'] = response[1][0]
        self.txhash_template['msg'] = response[2]
        self.txhash_template['signature'] = response[3][0]
        self.txhash_template['value'] = response[4][0]
        self.txhash_template['bundleNonceHash'] = response[5][0]
        self.txhash_template['timestamp'] = response[6][0]
        self.txhash_template['currentIndex'] = response[7][0]
        self.txhash_template['lastIndex'] = response[8][0]
        self.txhash_template['bundleHash'] = response[9][0]
        self.txhash_template['trunk'] = response[10][0]
        self.txhash_template['branch'] = response[11][0]
        self.txhash_template['arrivalTime'] = response[12][0]
        self.txhash_template['tagValue'] = response[13][0]
        return self.txhash_template

    def convert_oracle_topic(self, data):
        temp = {'address': None}
        for k,v in data.items():
            temp['address'] = k.split('ORACLE_')[1]
            for item in json.loads(v[0]):
                temp.update({str(item['bundle_index']): item})
        return temp


def subscribe_to_zmq_topics(host, port):
    converter = ResponseConverter()
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://{}:{}".format(host, port))
    # subscribe to all topics with an empty string
    socket.setsockopt_string(zmq.SUBSCRIBE, '')
    while True:
        string = socket.recv_string()
        print(string)
        data = {string.split(' ')[0]: string.split(' ')[1:]}
        # tx_hash topic from Java MsgQPrvImpl.publishTx
        if 'tx_hash' in data.keys():
            data = converter.convert_to_transaction(data)
            #LOGGER.info("{}".format({"tx_hash": data}))
            continue
        # oracle topic from Java Node.processReceivedData
        if list(data.keys())[0].startswith('ORACLE'):
            data = converter.convert_oracle_topic(data)
            #LOGGER.info("{}".format({"oracle": data}))
            continue
        # tx topic from where in Java idk??
        match = converter.match_txhash(list(data.keys())[0])
        if match:
            data = json.loads(data[match.string][0])
            data.update({'address': match.string})
            #LOGGER.info("{}".format({"tx": data}))
            continue
        #LOGGER.info("{}".format(data))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Subscribe to a stream of data'
    )
    parser.add_argument(
        '--host', metavar='host',
        type=str,
        default='nominee1.hlxtest.net',
        help='IP of host publisher'
    )
    parser.add_argument(
        '--port',
        metavar='port',
        type=str,
        default='5556',
        help='Port of the host publisher'
    )
    parser.add_argument(
        '--logs_dir',
        metavar='logs_dir',
        type=str,
        default='./results',
        help='Directory to write the json file to'
    )
    args = parser.parse_args()

    subscribe_to_zmq_topics(args.host, args.port)
