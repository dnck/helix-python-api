# -*- coding: utf-8 *-*
"""
For testing the basic functionality of the BaseHelixAPI, which
includes adding, removing neighbors, getting node info, and neighbors

Run this with two nodes unconnected to each other and their ports set correctly.

"""
import context
import unittest
import time

HOSTNAME = '192.168.2.98'

HTTP_PORT_A = 8085
HTTP_PORT_B = 9085

UDP_PORT_A = 4100
UDP_PORT_B = 4200

NODE_HTTP_ENDPOINT_A = "http://{}:{}".format(HOSTNAME, HTTP_PORT_A)
NODE_HTTP_ENDPOINT_B = "http://{}:{}".format(HOSTNAME, HTTP_PORT_B)

NEIGHBOR_UDP_ENDPOINT_A = "udp://{}:{}".format(HOSTNAME, UDP_PORT_A)
NEIGHBOR_UDP_ENDPOINT_B = "udp://{}:{}".format(HOSTNAME, UDP_PORT_B)

API_CLIENT = context.api.BaseHelixAPI()

class ApiTests(unittest.TestCase):
    """
    A class for testing the api.
    """
    @unittest.skip("Make sure nodes are running before calling this method")
    def test_get_neighbors(self):
        response_keys = ['neighbors', 'duration']
        response_A = API_CLIENT.get_neighbors(NODE_HTTP_ENDPOINT_A)
        response_B = API_CLIENT.get_neighbors(NODE_HTTP_ENDPOINT_B)
        for key in response_keys:
            self.assertTrue(key, response_A.keys())
            self.assertTrue(key, response_B.keys())

    @unittest.skip("Make sure nodes are running before calling this method")
    def test_get_node_info(self):
        response_A = API_CLIENT.get_node_info(NODE_HTTP_ENDPOINT_A)
        response_B = API_CLIENT.get_node_info(NODE_HTTP_ENDPOINT_B)
        self.assertTrue(response_A['appName']=='HLX')
        self.assertTrue(response_B['appName']=='HLX')

    @unittest.skip("Make sure nodes are running before calling this method")
    def test_add_neighbors_forward_direction(self):
        """" Test adding a neighbor """
        print("")
        response = API_CLIENT.get_neighbors(NODE_HTTP_ENDPOINT_A)
        print(response)
        print("")
        time.sleep(0.5)
        response = API_CLIENT.add_neighbors(
            NODE_HTTP_ENDPOINT_A, [NEIGHBOR_UDP_ENDPOINT_B]
        )
        self.assertTrue(response['addedNeighbors']==1)
        print(response)
        print("")
        time.sleep(0.5)
        response = API_CLIENT.get_neighbors(NODE_HTTP_ENDPOINT_A)
        print(response)

    @unittest.skip("Make sure nodes are running before calling this method")
    def test_add_neighbors_reverse_direction(self):
        """" Test adding a neighbor """
        print("")
        response = API_CLIENT.get_neighbors(NODE_HTTP_ENDPOINT_B)
        print(response)
        print("")
        time.sleep(0.5)
        response = API_CLIENT.add_neighbors(
            NODE_HTTP_ENDPOINT_B, [NEIGHBOR_UDP_ENDPOINT_A]
        )
        self.assertTrue(response['addedNeighbors']==1)
        print(response)
        print("")
        time.sleep(0.5)
        response = API_CLIENT.get_neighbors(NODE_HTTP_ENDPOINT_B)
        print(response)

    @unittest.skip("Make sure nodes are running before calling this method")
    def test_remove_neighbors_forward_direction(self):
        """" Test removing a neighbor """
        response = API_CLIENT.get_neighbors(NODE_HTTP_ENDPOINT_A)
        print(response)
        print("")
        time.sleep(0.5)
        response = API_CLIENT.remove_neighbors(
            NODE_HTTP_ENDPOINT_A, [NEIGHBOR_UDP_ENDPOINT_B]
        )
        print(response)
        print("")
        self.assertTrue(response['removedNeighbors']==1)
        time.sleep(0.5)
        response = API_CLIENT.get_neighbors(NODE_HTTP_ENDPOINT_A)
        print(response)

    @unittest.skip("Make sure nodes are running before calling this method")
    def test_remove_neighbors_reverse_direction(self):
        """" Test removing a neighbor """
        response = API_CLIENT.get_neighbors(NODE_HTTP_ENDPOINT_B)
        print(response)
        print("")
        time.sleep(0.5)
        response = API_CLIENT.remove_neighbors(
            NODE_HTTP_ENDPOINT_B, [NEIGHBOR_UDP_ENDPOINT_A]
        )
        print(response)
        print("")
        self.assertTrue(response['removedNeighbors']==1)
        time.sleep(0.5)
        response = API_CLIENT.get_neighbors(NODE_HTTP_ENDPOINT_B)
        print(response)

if __name__ == "__main__":
    unittest.main()
