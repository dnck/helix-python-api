# -*- coding: utf-8 *-*
"""
A python script for adding and removing neighbors in the helix network.

The user can supply a list of IP addresses from a txt file,
and provide a topology.
"""

import requests
import time
import json

API_VERSION = "0.01"

DEFAULT_HEADERS = {
    "Content-type": "application/json",
    "X-HELIX-API-Version": API_VERSION,
}


class BaseHelixAPI:
    """
        The basic Helix client API for getting info from the node about itself
        and its neighbors, and adding and removing neighbors.

        Attributes:
            commands (dict):
    """

    def __init__(self):
        self.commands = {
            "addNeighbors": {"command": "addNeighbors", "uris": []},
            "removeNeighbors": {"command": "removeNeighbors", "uris": []},
            "getNeighbors": {"command": "getNeighbors"},
            "getNodeInfo": {"command": "getNodeInfo"},
            "findTransactions": {"command": "findTransactions", "addresses": []},
            "getTips": {"command": "getTips"},
            "getTransactionsToApprove": {"command": "getTransactionsToApprove"},
            "getInclusionStates": {"command": "getInclusionStates",    "transactions": [], "tips": []},
            "startSpamming": {"command": "startSpamming", "spamDelay": int},
            "stopSpamming": {"command": "stopSpamming"}
        }

    def get_node_info(self, http_endpoint):
        """
        Implements the getNodeInfo api request and prints the results

        Args:
            http_endpoint (str)
        """
        command = self.commands["getNodeInfo"]
        return send_request(http_endpoint, command)

    def get_neighbors(self, http_endpoint):
        """
        Implements the getNeighbors api request and prints the results

        Args:
            http_endpoint (str)
        """
        command = self.commands["getNeighbors"]
        return send_request(http_endpoint, command)

    def add_neighbors(self, http_endpoint, uris):
        """
        Implements the addNeighbors api request and prints the results

        Args:
            http_endpoint (str)
            uris (list)
        """
        command = self.commands["addNeighbors"]
        command["uris"] = uris
        return send_request(http_endpoint, command)

    def remove_neighbors(self, http_endpoint, uris):
        """
        Implements the removeNeighbors api request and prints the results

        Args:
            http_endpoint (str)
            uris (list)
        """
        command = self.commands["removeNeighbors"]
        command["uris"] = uris
        return send_request(http_endpoint, command)

    def get_tips(self, http_endpoint):
        """
        Implements the removeNeighbors api request and prints the results

        Args:
            http_endpoint (str)
            uris (list)
        """
        command = self.commands["getTips"]
        return send_request(http_endpoint, command)

    def find_transaction(self, http_endpoint, addresses=[]):
        """
        Implements the removeNeighbors api request and prints the results

        Args:
            http_endpoint (str)
            uris (list)
        """
        command = self.commands["findTransactions"]
        command["addresses"] = addresses
        return send_request(http_endpoint, command)

    def get_transactions_to_approve(self, http_endpoint, depth=3):
        """
        Implements the removeNeighbors api request and prints the results

        Args:
            http_endpoint (str)
            uris (list)
        """
        command = self.commands["getTransactionsToApprove"]
        command["depth"] = depth
        return send_request(http_endpoint, command)

    def get_inclusion_states_of_parents(self, http_endpoint, parent_transactions, child_transactions):
        """
        Implements the removeNeighbors api request and prints the results

        Args:
            http_endpoint (str)
            uris (list)
        """
        command = self.commands["getInclusionStates"]
        command["transactions"] = parent_transactions
        command["tips"] = child_transactions
        return send_request(http_endpoint, command)

    def start_spamming(self, http_endpoint, spam_interval):
        """
        Implements the startSpamming api request and prints the results

        Args:
            http_endpoint (str)
            spam_interval (int) - time in ms between spam tx
        """
        command = self.commands["startSpamming"]
        command["spamDelay"] = spam_interval
        return send_request(http_endpoint, command)

    def stop_spamming(self, http_endpoint):
        """
        Implements the startSpamming api request and prints the results

        Args:
            http_endpoint (str)
            spam_interval (int) - time in ms between spam tx
        """
        command = self.commands["stopSpamming"]
        return send_request(http_endpoint, command)


def send_request(node_http_endpoint, command):
    """Posts the command to the http endpoint of the node"""
    result = requests.post(
        url=node_http_endpoint, data=json.dumps(command), headers=DEFAULT_HEADERS
    )
    try:
        pretty_json = json.loads(result.text)
    except Exception as err:
        print(err)
        return False
    return pretty_json
