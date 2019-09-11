import argparse

from context import api


def get_inclusion_state(node_http_endpoint, transactions=['0'*64]):
    latest_milestone = _get_latest_milestone(node_http_endpoint)
    print('Checking whether {} is approved by {}'.format(transactions[0], latest_milestone[0]))
    response = API_CLIENT.get_inclusion_states_of_parents(node_http_endpoint, transactions, latest_milestone)
    print(response['states'].pop())

def _get_latest_milestone(node_http_endpoint):
    response = API_CLIENT.get_node_info(node_http_endpoint)
    latest_milestone = response['latestSolidSubtangleMilestone']
    return [latest_milestone]

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
    TXHASH = '0000ba8d669f2b4b31d43cd76c9255456e86a8a97705fe8cd2203eb80b9a618c'
    get_inclusion_state(NODE_HTTP_ENDPOINT, [TXHASH])
