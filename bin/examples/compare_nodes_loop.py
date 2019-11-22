import argparse
import time

from context import api

TESTNET_NODES = [
    #"http://nominee1.helixmain.net:8085",
    "http://relayer1.helixmain.net:8085",
    "http://relayer2.helixmain.net:8085",
    "http://relayer3.helixmain.net:8085"
]

def get_sync_metric(node_http_endpoint):
    return API_CLIENT.get_node_info(node_http_endpoint)


if __name__ == '__main__':

    API_CLIENT = api.BaseHelixAPI()

    while True:
        responses = {}
        for node in TESTNET_NODES:
            responses[node] = get_sync_metric(node)
        for node in responses:
            print(
                node,
                responses[node]["currentRoundIndex"],
                responses[node]["latestSolidRoundIndex"],
                responses[node]["currentRoundIndex"] - responses[node]["latestSolidRoundIndex"]
            )
        time.sleep(5.0)
