from context import api

HOST = 'coo.hlxtest.net'
HTTP_PORT = 8085

NODE_HTTP_ENDPOINT = "http://{}:{}".format(HOST, HTTP_PORT)
API_CLIENT = api.BaseHelixAPI()

def test_find_transactions():
    addresses = ['9474289ae28f0ea6e3b8bedf8fc52f14d2fa9528a4eb29d7879d8709fd2f6d37']
    response = API_CLIENT.find_transaction(NODE_HTTP_ENDPOINT, addresses)
    print(len(response['hashes']))

test_find_transactions()
