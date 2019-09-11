import argparse

from context import api


def _test_find_transactions(node_http_endpoint,addresses=['0'*64]):
    response = API_CLIENT.find_transaction(node_http_endpoint, addresses)
    print(len(response['hashes']))


if __name__ == '__main__':
    API_CLIENT = api.BaseHelixAPI()

    PARSER = argparse.ArgumentParser(description='Get info from a node.')
    PARSER.add_argument('-host',
        metavar='host', type=str, default='coo.hlxtest.net',
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
    PARSER.add_argument('-address',
        metavar='address', type=str, default=\
        '9474289ae28f0ea6e3b8bedf8fc52f14d2fa9528a4eb29d7879d8709fd2f6d37',
        help='address to check for'
    )
    ARGS = PARSER.parse_args()

    if not (ARGS.ssl is None):
        NODE_HTTP_ENDPOINT = "https://{}:{}".format(ARGS.host, ARGS.port)
    else:
        NODE_HTTP_ENDPOINT = "http://{}:{}".format(ARGS.host, ARGS.port)

    address = [PARSER.address]

    _test_find_transactions(NODE_HTTP_ENDPOINT,addresses=address)
