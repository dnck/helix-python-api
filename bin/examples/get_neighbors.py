from context import api

HOST = 'coo.hlxtest.net'
HTTP_PORT = 8085

NODE_HTTP_ENDPOINT = "http://{}:{}".format(HOST, HTTP_PORT)
API_CLIENT = api.BaseHelixAPI()

def get_node_info():
    response = API_CLIENT.get_neighbors(NODE_HTTP_ENDPOINT)
    neighbors = response['neighbors']
    for node in neighbors:
        print(node)
        print('')

get_node_info()
