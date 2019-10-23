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


IO_OPTIONS = {
    'stdout_only': True, 'level': 'info', 'parentdir': '/home/hlx-dev/helix/helix-overlay-manager/api_examples',
    'log_filename': 'ctps.log'
}
log_manager = results_manager.ResultsManager(IO_OPTIONS)
logger = log_manager.logger

def subscribe_to_zmq_topic(node_zmq_endpoint, topic='tx'):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(node_zmq_endpoint)
    socket.setsockopt_string(zmq.SUBSCRIBE, "")
    client = Scientist(logger)
    while True:
        string = socket.recv_string()
        now_time =  time.time()
        topic, msg = string.split(' ')[0], string.split(' ')[1]
        logger.info("topic, msg {} {}".format(topic, msg))
        if topic == 'tx_hash': # TODO: need exceptions here
            tx_hash = msg.split('\n')[0]
            client.record_observation( # input
                tx_hash,
                now_time
            )
            client.num_tx_observed += 1
            if client.minute_passed():
                client.update_state(now_time) # internal change



class Scientist():

    def __init__(self, logger):

        self.logger = logger
        self.publisher = PrometheusExporter()
        self.client = Student(self.logger)
        self.new_tx_dict = {}
        self.num_tx_observed = 0
        self.start_time =  time.time()

    def record_observation(self,key,value):
        self.new_tx_dict[key] = value

    def minute_passed(self):
        if time.time() - self.start_time >= 60:
            print(time.time() - self.start_time )
            self.start_time = time.time()

            return True
        else:
            return False

    def calculate_average_time_until_confirmation(self, now_time):
        """ Compares the time of tx observation to confirm time.
        """
        durations = []
        for key in self.new_tx_dict:
            durations.append(
                self.estimate_duration(
                    now_time, self.new_tx_dict[key]
                )
            )
        num_durations = len(durations)
        if num_durations > 1:
            average_duration = np.mean(durations)
            return average_duration
        else:
            return None

    def estimate_duration(self, now_time, earlier):
        duration = (now_time - earlier)
        return duration

    def update_state(self, now_time):
        now_time = now_time
        # is the tx included by the most recent milestone?
        status = self.client.get_inclusion_state(
            list(self.new_tx_dict.keys())
        )
        # label the transactions as confirmed ...
        confirmed = list(
            np.array(
                list(self.new_tx_dict.keys())
            )[
                np.array(status['states'])
            ]
        )
        # or unconfirmed
        unconfirmed = list(
            np.array(
                list(self.new_tx_dict.keys())
            )[
                np.invert(status['states'])
            ])
        # export metrics
        self.publisher.total_tx.set(self.num_tx_observed)
        self.logger.info(
            'Total observed: {}'.format(self.num_tx_observed)
        )
        self.publisher.total_tx_confirmed.set(len(confirmed))
        self.logger.info(
            'Total confirmed: {}'.format(len(confirmed))
        )
        self.publisher.total_tx_pending_confirmation.set(len(unconfirmed))
        self.logger.info(
            'Total outstanding unconfirmed transactions: {}'.format(
                len(unconfirmed)
            )
        )
        confirmed_tx = {i: self.new_tx_dict[i] for i in confirmed}
        pending_confirmation = {i: self.new_tx_dict[i] for i in unconfirmed}

        average_duration = \
            self.calculate_average_time_until_confirmation(now_time)

        if not (average_duration is None):
            self.publisher.estimated_average_wait_for_confirmation.set(
                average_duration
            )
            self.logger.info(
                'Average estimated time until confirmation: {}'.\
                    format(
                        average_duration
                    )
            )
        self.num_tx_observed = 0
        if False:
            dump_to_json('./results/stats.json', NEW_TRANSACTIONS_DICT)
        self.start_time =  time.time()

    def dump_to_json(self, filename, data):
        with open(filename, 'w') as outfile:
            json.dump(data, outfile)

class Student():
    def __init__(self, logger):
        self.request = api.BaseHelixAPI()
        self.logger = logger
        self.node_http_endpoint = node_http_endpoint

    def get_inclusion_state(self, transactions):
        self.logger.info("Requesting latest milestone")
        latest_milestone = self._get_latest_milestone()
        response = self.request.get_inclusion_states_of_parents(
            self.node_http_endpoint, transactions, latest_milestone
        )
        return response

    def _get_latest_milestone(self):
        self.logger.info("Requesting get_node_info")
        response = self.request.get_node_info(self.node_http_endpoint)
        latest_milestone = response['latestSolidSubtangleMilestone']
        self.logger.info("LSSM = {}".format(latest_milestone))
        return [latest_milestone]

class PrometheusExporter():

    def __init__(self):

        self.total_tx = Gauge('total_tx',
            'Total number of new transactions since previous query reported by the tx zmq topic')

        self.total_tx_confirmed = Gauge('total_tx_confirmed',
            'Total number of tx confirmed since previous query')

        self.total_tx_pending_confirmation = Gauge(
            'total_tx_pending_confirmation', 'Total number of transactions since'+' previous query still '\
                    +' unconfirmed'
        )

        self.estimated_average_wait_for_confirmation = Gauge(
                'estimated_average_wait_for_confirmation',
                'Average estimated time for a transaction to get confirmed'
        )



if __name__ == '__main__':

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
        '-http_port',
        metavar='host',
        type=int,
        default=8085,
        help='Http port of host publisher'
    )
    parser.add_argument(
        '-zmq_port',
        metavar='port',
        type=int,
        default=5556,
        help='Zmq port of the host publisher'
    )
    args = parser.parse_args()

    HOST = args.host

    HTTP_PORT = args.http_port

    ZMQ_PORT = args.zmq_port

    node_http_endpoint = "http://{}:{}".format(HOST, HTTP_PORT)
    node_zmq_endpoint = "tcp://{}:{}".format(HOST, ZMQ_PORT)

    start_http_server(2019)

    subscribe_to_zmq_topic(node_zmq_endpoint)
