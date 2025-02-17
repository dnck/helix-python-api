import argparse

from context import api


def _start_spamming(node_http_endpoint, spam_interval):
    response = API_CLIENT.start_spamming(node_http_endpoint, spam_interval)
    print(response)

if __name__ == '__main__':
    API_CLIENT = api.BaseHelixAPI()

    PARSER = argparse.ArgumentParser(description='Get info from a node.')
    PARSER.add_argument('-host',
        metavar='host', type=str, default='79.193.43.206',
        help='Public IP of the host'
    )
    PARSER.add_argument('-port',
        metavar='port', type=str, default='8085',
        help='HTTP port of the host public IP'
    )
    PARSER.add_argument('-ms',
        metavar='port', type=int, default=1000,
        help='Interval between spam in ms'
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


    _start_spamming(NODE_HTTP_ENDPOINT, ARGS.ms)
