from context import api
import argparse


if __name__ == "__main__":
    API_CLIENT = api.BaseHelixAPI()

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-ip0',type=str, default='172.20.0.2')
    parser.add_argument('-ip1',type=str, default='coo.hlxtest.net')

    parser.add_argument('-http0',type=str, default='8085')
    parser.add_argument('-http1',type=str, default='8085')

    parser.add_argument('-udp0',type=str, default='4100')
    parser.add_argument('-udp1',type=str, default='4100')

    args = parser.parse_args()

    HTTP = "http://{}:{}"

    UDP = "udp://{}:{}"

    peer_a_api = HTTP.format(args.ip0, args.http0)
    peer_b_api = HTTP.format(args.ip1, args.http1)
    peer_a_udp = UDP.format(args.ip0, args.udp0)
    peer_b_udp = UDP.format(args.ip1, args.udp1)

    response = API_CLIENT.add_neighbors(peer_a_api, [peer_b_udp])
    print(peer_a_api, response)

    response = API_CLIENT.add_neighbors(peer_a_api, [peer_b_udp])
    print(peer_b_api, response)
