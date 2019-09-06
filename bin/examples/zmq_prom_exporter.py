# -*- coding:utf-8 -*-
'''
A ZMQ and Prometheus client for scrapping the helix-1.0 ZMQ topics
'''
import argparse
import random
import sys
import zmq
import json
import time
import datetime

import numpy as np

from prometheus_client import start_http_server, Gauge

from context import api

from context import results_manager

HOSTNAME = 'zmq.hlxtest.net'
HTTP_PORT = 8085
NODE_HTTP_ENDPOINT = "http://{}:{}".format(HOSTNAME, HTTP_PORT)

API_CLIENT = api.BaseHelixAPI()
CONFIRMED = 0

TX_COUNTER = Gauge('num_new_transactions',
    'Total number of new transactions since previous query reported by the tx zmq topic')

NUM_CONFIRMED = Gauge('num_confirmed',
    'Total number of tx confirmed since previous query')

OUTSTANDING_UNCONFIRMED = Gauge('num_outstanding_unconfirmed',
    'Total number of transactions since previous query still unconfirmed')

AVERAGE_EST_TIMETOCONFIRM =  Gauge('avg_est_confirm_time',
    'Average estimated time for a transaction to get confirmed')

IO_OPTIONS = {
    'stdout_only': False, 'level': 'info', 'parentdir': '/home/hlx-dev/helix/helix-overlay-manager/api_examples',
    'log_filename': 'ctps.log'
}

io_man = results_manager.ResultsManager(IO_OPTIONS)

def get_latest_milestone():
    response = API_CLIENT.get_node_info(NODE_HTTP_ENDPOINT)
    latest_milestone = response['latestSolidSubtangleMilestone']
    return [latest_milestone]

def get_inclusion_state(transactions):
    latest_milestone = get_latest_milestone()
    response = API_CLIENT.get_inclusion_states_of_parents(NODE_HTTP_ENDPOINT, transactions, latest_milestone)
    return response

def minute_passed(oldepoch):
    return time.time() - oldepoch >= 2

def put_key_value_in_dict(dict,key,value):
    dict[key] = value
    return dict

def dump_to_json(filename, data):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

def estimate_duration(earlier):
    now = time.time()
    duration = (now - earlier)
    return duration

def calculate_average_time_until_confirmation(dict):
    durations = []
    for key in dict:
        duration = estimate_duration(dict[key])
        durations.append(duration)
    num_durations = len(durations)
    if num_durations > 1:
        average_duration = np.mean(durations)
        return average_duration
    else:
        return 'NaN'

def subscribe_to_zmq_topic(host, port):
    NEW_TRANSACTIONS_LIST = []
    NEW_TRANSACTIONS_DICT = {}
    num_obs = 0
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://{}:{}".format(host, port))
    socket.setsockopt_string(zmq.SUBSCRIBE, "tx")
    now_time =  time.time()
    print('Connected to zmq socket...')
    while True:
        string = socket.recv_string()
        topic, msg = string.split(' ')[0], string.split(' ')[1]

        if topic == 'tx_hash':
            NEW_TRANSACTIONS_LIST.append(msg.split('\n')[0])
            put_key_value_in_dict(NEW_TRANSACTIONS_DICT, msg.split('\n')[0], time.time())
            num_obs += 1

        if minute_passed(now_time):
            status = get_inclusion_state(NEW_TRANSACTIONS_LIST)
            confirmed = list(np.array(NEW_TRANSACTIONS_LIST)[np.array(status['states'])])
            unconfirmed = list(np.array(NEW_TRANSACTIONS_LIST)[np.invert(status['states'])])
            io_man.logger.info('Total observed: {}'.format(num_obs))
            TX_COUNTER.set(num_obs)
            io_man.logger.info('Total confirmed: {}'.format(len(confirmed)))
            NUM_CONFIRMED.set(len(confirmed))
            io_man.logger.info('Total outstanding unconfirmed transactions: {}'.format(len(unconfirmed)))
            OUTSTANDING_UNCONFIRMED.set(len(unconfirmed))
            NEW_TRANSACTIONS_LIST = unconfirmed
            CONFIRMED_DICT = {i: NEW_TRANSACTIONS_DICT[i] for i in confirmed}
            NEW_TRANSACTIONS_DICT = {i: NEW_TRANSACTIONS_DICT[i] for i in unconfirmed}
            average_duration = calculate_average_time_until_confirmation(CONFIRMED_DICT)
            if len(confirmed):
                io_man.logger.info('Average estimated time until confirmation: {}'.format(average_duration))
                AVERAGE_EST_TIMETOCONFIRM.set(average_duration)
            #dump_to_json('./results/stats.json', NEW_TRANSACTIONS_DICT)
            num_obs = 0
            now_time = time.time()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Subscribe to a stream of data')
    parser.add_argument('--host', metavar='host', type=str, default='zmq.hlxtest.net', help='IP of host publisher')
    parser.add_argument('--port', metavar='port', type=str, default='5556', help='Port of the host publisher')
    args = parser.parse_args()
    start_http_server(2019)
    subscribe_to_zmq_topic(args.host, args.port)
