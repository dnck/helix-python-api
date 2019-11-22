import argparse
import time

from prometheus_client import start_http_server, Gauge

from context import api


TESTNET_NODES = [
    "http://ec2-18-223-97-229.us-east-2.compute.amazonaws.com:8085",
    "http://ec2-13-58-211-16.us-east-2.compute.amazonaws.com:8085",
    "http://ec2-3-133-124-21.us-east-2.compute.amazonaws.com:8085",
    "http://ec2-13-59-10-68.us-east-2.compute.amazonaws.com:8085"
]


udp_names = {
    "ec2-18-223-97-229.us-east-2.compute.amazonaws.com:4100": "validator",
    "ec2-13-58-211-16.us-east-2.compute.amazonaws.com:4100": "node_1",
    "ec2-3-133-124-21.us-east-2.compute.amazonaws.com": "node_2",
    "ec2-13-59-10-68.us-east-2.compute.amazonaws.com:4100": "node_3"
}


http_public_ipv4_to_names = {
    TESTNET_NODES[0]: "validator",
    TESTNET_NODES[1]: "node_1",
    TESTNET_NODES[2]: "node_2",
    TESTNET_NODES[3]: "node_3"
}

TO_EXPORT = {}


def get_sync_metric(node_http_endpoint):
    response = API_CLIENT.get_node_info(node_http_endpoint)
    view = http_public_ipv4_to_names[node_http_endpoint]
    sync = response["currentRoundIndex"] - response["latestSolidRoundIndex"]
    view = view+"_sync"
    if view not in TO_EXPORT:
        TO_EXPORT.update({view: Gauge(view, "read the label!")})
    else:
        TO_EXPORT[view].set(sync)


def get_neighbor_stats(node_http_endpoint):
    view = http_public_ipv4_to_names[node_http_endpoint]
    response = API_CLIENT.get_neighbors(node_http_endpoint)
    neighbors = response['neighbors']
    neighbor_stats = {}
    for node in neighbors:
        metric_start = "{}_view_of_{}".format(view, udp_names[node["address"]])
        neighbor_stats.update(
            {metric_start+"_all_tx": node["numberOfAllTransactions"]}
            )
        neighbor_stats.update(
            {metric_start+"_tx_rqst": node["numberOfRandomTransactionRequests"]}
            )
        neighbor_stats.update(
            {metric_start+"_new_tx": node["numberOfNewTransactions"]}
            )
        neighbor_stats.update(
            {metric_start+"_invalid_tx": node["numberOfInvalidTransactions"]}
            )
        neighbor_stats.update(
            {metric_start+"_stale_tx": node["numberOfStaleTransactions"]}
            )
        neighbor_stats.update(
            {metric_start+"_sent_tx": node["numberOfSentTransactions"]}
            )
    for k,v in neighbor_stats.items():
        if k not in TO_EXPORT:
            TO_EXPORT.update({k: Gauge(k, "read the label!")})
        else:
            TO_EXPORT[k].set(v)


if __name__ == '__main__':

    API_CLIENT = api.BaseHelixAPI()

    start_http_server(6969)

    while True:
        responses = {}
        for node in TESTNET_NODES:
            get_sync_metric(node)
            get_neighbor_stats(node)
        time.sleep(10.0)
