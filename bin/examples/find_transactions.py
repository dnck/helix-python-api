import argparse

from context import api


def _test_find_transactions(node_http_endpoint,addresses=['0'*64]):
    response = API_CLIENT.find_transaction(node_http_endpoint, addresses)
    #print(len(response['hashes']))
    return response


if __name__ == '__main__':
    API_CLIENT = api.BaseHelixAPI()

    PARSER = argparse.ArgumentParser(description='Get info from a node.')
    PARSER.add_argument('host',
        metavar='host', type=str, default='http://relayer1.hlxtest.net',
        help='Http endpoint'
        )

    ARGS = PARSER.parse_args()
    PARSER.add_argument('-address',
        metavar='address', type=str, default=\
        '9474289ae28f0ea6e3b8bedf8fc52f14d2fa9528a4eb29d7879d8709fd2f6d37',
        help='address to check for'
    )
    ARGS = PARSER.parse_args()

    address = [ARGS.address]

    address =  \
        ['00001c4e9f69181db8c1c4b9b5d951bbab25abac8fc2412641215eba16c14281']

    response = _test_find_transactions(ARGS.host,addresses=address)
    print(response)
