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


def subscribe_to_zmq_topics(host, port):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://{}:{}".format(host, port))
    # subscribe to all topics with an empty string
    socket.setsockopt_string(zmq.SUBSCRIBE, '')
    value_tx = (None, None)
    while True:
        string = socket.recv_string()
        data = {string.split(' ')[0]: string.split(' ')[1:]}
        # tx_hash topic from Java MsgQPrvImpl.publishTx
        if 'tx_hash' in data.keys():
            data = convert_txhash_topic(txhash_template, data)
        # oracle topic from Java Node.processReceivedData
        if list(data.keys())[0].startswith('ORACLE'):
            data = convert_oracle_topic(data)
        # tx topic from where in Java idk??
        match = regex.match(txhash_pattern, list(data.keys())[0])
        if match:
            data = json.loads(data[match.string][0])
            data.update({'address': match.string})
        # all other topics are already formatted pretty
        write_dict_to_json('./results/test.json', data)
        # TODO: label the topics during input.

txhash_pattern = regex.compile(r"\b[a-f0-9]{64}")

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

def convert_txhash_topic(txhash_template, response):
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

def write_dict_to_json(filename, data):
    """Write an in-memory Python dictionary to a formatted .json file."""
    filename = os.path.normpath(filename)
    with open(filename, "a") as file_obj:
        json.dump(data, file_obj, indent=4, sort_keys=True)
        file_obj.write(',\n')

def mkdir_if_not_exists(dirname):
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Subscribe to a stream of data'
    )
    parser.add_argument(
        '--host', metavar='host',
        type=str,
        default='zmq.hlxtest.net',
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

    mkdir_if_not_exists(args.logs_dir)

    subscribe_to_zmq_topics(args.host, args.port)
