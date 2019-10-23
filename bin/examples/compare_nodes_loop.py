import argparse
import time

from context import api

TESTNET_NODES = [
    # "https://nominee1.hlxtest.net:8087",
    "https://relayer1.hlxtest.net:8087",
    "https://relayer2.hlxtest.net:8087",
    "https://relayer3.hlxtest.net:8087"
]

def _compare_neighbors(node_http_endpoint):
    return API_CLIENT.get_node_info(node_http_endpoint)


if __name__ == '__main__':

    API_CLIENT = api.BaseHelixAPI()

    while True:
        responses = {}
        for node in TESTNET_NODES:
            responses[node] = _compare_neighbors(node)
        for node in responses:
            print(
                node,
                responses[node]["currentRoundIndex"],
                responses[node]["latestSolidRoundIndex"],
                responses[node]["currentRoundIndex"] - responses[node]["latestSolidRoundIndex"]
            )
        time.sleep(5.0)
