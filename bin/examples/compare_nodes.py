import argparse

from context import api


def _compare_neighbors(node_http_endpoint_A, node_http_endpoint_B):
    response_A = API_CLIENT.get_node_info(node_http_endpoint_A)
    response_B = API_CLIENT.get_node_info(node_http_endpoint_B)
    #print(response_B)
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
    # Compare this host
    PARSER.add_argument('-host0',
        metavar='host', type=str, default='helixnetwork.ddns.net',
        help='Public IP of the host'
    )
    PARSER.add_argument('-port0',
        metavar='port', type=str, default='80',
        help='HTTP port of the host public IP'
    )
    PARSER.add_argument('-ssl0',type=str, default=None)
    # to this host
    PARSER.add_argument('-host1',
        metavar='host', type=str, default='coo.hlxtest.net',
        help='Public IP of the host'
    )
    PARSER.add_argument('-port1',
        metavar='port', type=str, default='8085',
        help='HTTP port of the host public IP'
    )
    PARSER.add_argument('-ssl1',type=str, default=None)

    ARGS = PARSER.parse_args()

    HTTP = "http://{}:{}"
    HTTPS = "https://{}:{}"

    if not (ARGS.ssl0 is None):
        NODE_HTTP_ENDPOINT_A = HTTPS.format(ARGS.host0, ARGS.port0)
    else:
        NODE_HTTP_ENDPOINT_A = HTTP.format(ARGS.host0, ARGS.port0)
    if not (ARGS.ssl1 is None):
        NODE_HTTP_ENDPOINT_B = HTTPS.format(ARGS.host1, ARGS.port1)
    else:
        NODE_HTTP_ENDPOINT_B = HTTP.format(ARGS.host1, ARGS.port1)

    _compare_neighbors(NODE_HTTP_ENDPOINT_A, NODE_HTTP_ENDPOINT_B)
