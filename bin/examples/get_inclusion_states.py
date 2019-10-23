import argparse

from context import api


def get_inclusion_state(node_http_endpoint, transactions=['0'*64]):
    latest_milestone = _get_latest_milestone(node_http_endpoint)
    print('Checking whether {} is approved by {}'.format(transactions[0], latest_milestone[0]))
    response = API_CLIENT.get_inclusion_states_of_parents(node_http_endpoint, transactions, latest_milestone)
    print(response['states'].pop())

def _get_latest_milestone(node_http_endpoint):
    response = API_CLIENT.get_node_info(node_http_endpoint)
    latest_milestone = response['latestSolidRoundHash']
    return [latest_milestone]

if __name__ == '__main__':
    API_CLIENT = api.BaseHelixAPI()

    PARSER = argparse.ArgumentParser(description='Get info from a node.')
    PARSER.add_argument('-host',
        metavar='host', type=str, default='localhost',
        help='Public IP of the host'
    )
    PARSER.add_argument('-port',
        metavar='port', type=str, default='8085',
        help='HTTP port of the host public IP'
    )
    PARSER.add_argument('-ssl',
        metavar='http or https', type=str, default=None,
        help='http or https'
    )
    PARSER.add_argument('-txhash',
        metavar='txhash', type=str, default=\
        '0000b00d0aa0103c6f437fb94c0ce69cafd0ded6f2061b63141e98f7dd5637ed',
        help='txhash to check on'
    )
    ARGS = PARSER.parse_args()

    if not (ARGS.ssl is None):
        NODE_HTTP_ENDPOINT = "https://{}:{}".format(ARGS.host, ARGS.port)
    else:
        NODE_HTTP_ENDPOINT = "http://{}:{}".format(ARGS.host, ARGS.port)

    TXHASH = [ARGS.txhash]

    get_inclusion_state(NODE_HTTP_ENDPOINT, TXHASH)
