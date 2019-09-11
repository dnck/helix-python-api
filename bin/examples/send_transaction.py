# TODO: Implement the prepareTransfers and sendTransactionStrings in Python
#
# from context import api
#
# api_client = api.BaseHelixAPI()
#
# class Converter():
#     def __init__(self):
#         pass
#     def ascii_2_txhex(str):
#         pass
#
# sender_seed =
#   "d2ebccb3cff4ea6a6c7ba4d2528cf60c14e0f4d1af762bdda9442efb94cdc857";
#
# receiver_address =
#   "b61d8ef4b9557cc87f91143cd169a897ec584e21b81036af8692a36487dae5f63b121d50";
#
# transfer = {
#   "address": receiver_address,
#   "value": 1,
#   "message": Converter.ascii_2_txhex("abcd"),
#   "tag": "abcd123"
# }
#
# response = api_client.prepare_transfers(sender_seed, [transfer])
#
# stored_tx_bytes = response.tx_bytes
#
# response = helix.send_transaction_strings(stored_tx_bytes, 5, 2)
