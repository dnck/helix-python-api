from context import api

HOST = 'coo.hlxtest.net'
HTTP_PORT = 8085

NODE_HTTP_ENDPOINT = "http://{}:{}".format(HOST, HTTP_PORT)
API_CLIENT = api.BaseHelixAPI()

def get_transactions_to_approve():
    depth = 3
    response = API_CLIENT.get_transactions_to_approve(NODE_HTTP_ENDPOINT, depth)
    print(response)

get_transactions_to_approve()
