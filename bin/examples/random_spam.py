import argparse
import random
import time

from context import api


def _start_spamming(node_http_endpoint, spam_interval):
    response = API_CLIENT.start_spamming(node_http_endpoint, spam_interval)
    print(response)

def _stop_spamming(node_http_endpoint):
    response = API_CLIENT.stop_spamming(node_http_endpoint)
    print(response)

def pause(high):
    sleep_time = random.randint(0, high) * 60
    time.sleep(sleep_time)

if __name__ == '__main__':
    API_CLIENT = api.BaseHelixAPI()

    PARSER = argparse.ArgumentParser(description='Spam from the nodes.')

    PARSER.add_argument('-host',
        metavar='host', type=str, default='helixnetwork.ddns.net',
        help='Public IP of the host'
    )
    PARSER.add_argument('-port',
        metavar='port', type=str, default='80',
        help='HTTP port of the host public IP'
    )
    PARSER.add_argument('-ssl',
        metavar='http or https', type=str, default=None,
        help='http or https'
    )
    ARGS = PARSER.parse_args()

    if not (ARGS.ssl is None):
        NODE_HTTP_ENDPOINT = "https://{}:{}".format(ARGS.host, ARGS.port)
    else:
        NODE_HTTP_ENDPOINT = "http://{}:{}".format(ARGS.host, ARGS.port)

    while True:
        _start_spamming(NODE_HTTP_ENDPOINT, random.randint(100, 1000))
        pause(2)
        _start_spamming(NODE_HTTP_ENDPOINT, random.randint(100, 1000))
        pause(2)
        _start_spamming(NODE_HTTP_ENDPOINT, random.randint(100, 1000))
        pause(2)
        _start_spamming(NODE_HTTP_ENDPOINT, random.randint(100, 1000))
        pause(20)
        _stop_spamming(NODE_HTTP_ENDPOINT)
        pause(1)
        _stop_spamming(NODE_HTTP_ENDPOINT)
        pause(1)
        _stop_spamming(NODE_HTTP_ENDPOINT)
        pause(1)
        _stop_spamming(NODE_HTTP_ENDPOINT)
        pause(1)
        pause(5)
