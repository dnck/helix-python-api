import argparse

from context import api

def _get_neighbors(node_http_endpoint):
    response = API_CLIENT.get_neighbors(node_http_endpoint)
    neighbors = response['neighbors']
    for node in neighbors:
        print(node)
        print('')

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
    ARGS = PARSER.parse_args()

    NODE_HTTP_ENDPOINT = "http://{}:{}".format(ARGS.host, ARGS.port)

    _get_neighbors(NODE_HTTP_ENDPOINT)
