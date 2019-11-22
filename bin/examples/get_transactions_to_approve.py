import argparse

from context import api

from datetime import datetime
import time


def _get_transactions_to_approve(node_http_endpoint):
    response = API_CLIENT.get_transactions_to_approve(
        node_http_endpoint, 3 # depth = 3
    )
    return response

if __name__ == '__main__':
    API_CLIENT = api.BaseHelixAPI()

    PARSER = argparse.ArgumentParser(description='Get tips from a node.')
    PARSER.add_argument('host',
        metavar='host', type=str, default='http://relayer1.helixmain.net',
        help='Http endpoint'
        )

    ARGS = PARSER.parse_args()

    while True:
        d = datetime.now().strftime("%H:%M:%S.%s")
        r = _get_transactions_to_approve(ARGS.host)
        print(d, r["trunkTransaction"]==r["branchTransaction"])
        if not r["trunkTransaction"]==r["branchTransaction"]:
            print(r["trunkTransaction"], r["branchTransaction"])
        time.sleep(0.1)
