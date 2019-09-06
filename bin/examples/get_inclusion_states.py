from context import api

HOST = 'coo.hlxtest.net'
HTTP_PORT = 8085

NODE_HTTP_ENDPOINT = "http://{}:{}".format(HOST, HTTP_PORT)
API_CLIENT = api.BaseHelixAPI()

def get_latest_milestone():
    response = API_CLIENT.get_node_info(NODE_HTTP_ENDPOINT)
    latest_milestone = response['latestSolidSubtangleMilestone']
    return [latest_milestone]

def get_inclusion_state():
    transaction = ['9c9f31235c36700dc5819b2c71ab3595eb2da41017b1cfabc82c40b75df94c69']
    latest_milestone = get_latest_milestone()
    print('Checking whether {} is approved by {}'.format(transaction[0], latest_milestone[0]))
    response = API_CLIENT.get_inclusion_states_of_parents(NODE_HTTP_ENDPOINT, transaction, latest_milestone)
    print(response['states'].pop())

get_inclusion_state()
