import argparse
import time

from context import api


def _compare_neighbors(node_http_endpoint_A, node_http_endpoint_B):
    response_A = API_CLIENT.get_node_info(node_http_endpoint_A)
    response_B = API_CLIENT.get_node_info(node_http_endpoint_B)
    print(
        '-'*16, '\n',
        node_http_endpoint_A, '\n',
        'ms: '+response_A['latestMilestone'], '\n',
        'lssm '+response_A['latestSolidSubtangleMilestone'], '\n\n',
        node_http_endpoint_B, '\n',
        'ms: '+response_B['latestMilestone'], '\n',
        'lssm '+response_B['latestSolidSubtangleMilestone'], '\n',
        '-'*16
    )

if __name__ == '__main__':
    API_CLIENT = api.BaseHelixAPI()

    PARSER = argparse.ArgumentParser(description='Get info from a node.')
    PARSER.add_argument('-host0',
        metavar='host', type=str, default='79.193.43.206',
        help='Public IP of the host'
    )
    PARSER.add_argument('-port0',
        metavar='port', type=str, default='80',
        help='HTTP port of the host public IP'
    )
    PARSER.add_argument('-host1',
        metavar='host', type=str, default='coo.hlxtest.net',
        help='Public IP of the host'
    )
    PARSER.add_argument('-port1',
        metavar='port', type=str, default='8085',
        help='HTTP port of the host public IP'
    )
    ARGS = PARSER.parse_args()

    NODE_HTTP_ENDPOINT_A = "http://{}:{}".format(ARGS.host0, ARGS.port0)
    NODE_HTTP_ENDPOINT_B = "http://{}:{}".format(ARGS.host1, ARGS.port1)

    while True:
        _compare_neighbors(NODE_HTTP_ENDPOINT_A, NODE_HTTP_ENDPOINT_B)
        time.sleep(4.0)
