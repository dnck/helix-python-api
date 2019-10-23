# -*- coding:utf-8 -*-
'''
A ZMQ subscription client wrapper.

ALL_ZMQ_TOPICS = [
    'dns', 'nghbr', 'dnscv', 'dnscc', 'dnscu', 'hmr', 'antn', 'lmsi',
    'lmhs', 'rstat', 'rntn', 'rtl', 'lmi', 'lmhs', 'sn0', 'sn', 'ct5s2m',
    't5s2m', 'mctn', 'tx'
    ]
'''
import argparse
import json
import os
import regex
import zmq

from context import results_manager



class SubClient():

    def __init__(self, host, port, topic):
        self.endpoint = "tcp://{}:{}".format(host, port)
        self.topic = topic
        self.logger = results_manager.LogManager(
            level="debug", output="stdout"
        )


    def subscribe_to_zmq_topic(self):
        self.logger.info("Subscribing to {} from {}".format(
                                self.topic, self.endpoint))
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(self.endpoint)
        socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)

        while True:
            string = socket.recv_string()
            self.logger.info(string)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Subscribe to a stream of data'
    )
    parser.add_argument(
        '-host', metavar='host',
        type=str,
        default='nominee1.hlxtest.net',
        help='IP of host publisher'
    )
    parser.add_argument(
        '-port',
        metavar='port',
        type=str,
        default='5556',
        help='Port of the host publisher'
    )
    parser.add_argument(
        '-topic',
        metavar='topic',
        type=str,
        default='ctx',
        help='topic to subscribe to'
    )

    args = parser.parse_args()

    client = SubClient(args.host, args.port, args.topic)

    client.subscribe_to_zmq_topic()
