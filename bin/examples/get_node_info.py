import argparse

from context import api

from datetime import datetime
import time


def _get_node_info(node_http_endpoint):
    response = API_CLIENT.get_node_info(node_http_endpoint)
    return response

if __name__ == '__main__':
    API_CLIENT = api.BaseHelixAPI()

    PARSER = argparse.ArgumentParser(description='Get info from a node.')
    PARSER.add_argument('host',
        metavar='host', type=str, default='http://relayer1.hlxtest.net',
        help='Http endpoint'
        )

    ARGS = PARSER.parse_args()

    #while True:
    d = datetime.now().strftime("%H:%M:%S.%s")
    r = _get_node_info(ARGS.host)
    #print(d, r["trunkTransaction"]==r["branchTransaction"])
    print(d, r)
    #time.sleep(0.01)
