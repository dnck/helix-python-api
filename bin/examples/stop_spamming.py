import argparse

from context import api


def _stop_spamming(node_http_endpoint):
    response = API_CLIENT.stop_spamming(node_http_endpoint)
    print(response)

if __name__ == '__main__':
    API_CLIENT = api.BaseHelixAPI()

    PARSER = argparse.ArgumentParser(description='Get info from a node.')
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


    _stop_spamming(NODE_HTTP_ENDPOINT)
