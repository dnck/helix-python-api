from context import api
import argparse


if __name__ == "__main__":
    API_CLIENT = api.BaseHelixAPI()

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-host0',type=str, default='172.20.0.2')
    parser.add_argument('-host1',type=str, default='coo.hlxtest.net')

    parser.add_argument('-http0',type=str, default='8085')
    parser.add_argument('-http1',type=str, default='8085')

    parser.add_argument('-udp0',type=str, default='4100')
    parser.add_argument('-udp1',type=str, default='4100')

    parser.add_argument('-ssl0',type=str, default=None)
    parser.add_argument('-ssl1',type=str, default=None)

    args = parser.parse_args()

    HTTP = "http://{}:{}"
    HTTPS = "https://{}:{}"

    UDP = "udp://{}:{}"

    if not (args.ssl0 is None):
        peer_a_api = HTTPS.format(args.host0, args.http0)
    else:
        peer_a_api = HTTPS.format(args.host0, args.http0)
        
    if not (args.ssl1 is None):
        peer_b_api = HTTPS.format(args.host1, args.http1)
    else:
        peer_b_api = HTTP.format(args.host1, args.http1)

    peer_a_udp = UDP.format(args.host0, args.udp0)
    peer_b_udp = UDP.format(args.host1, args.udp1)

    response = API_CLIENT.add_neighbors(peer_a_api, [peer_b_udp])
    print(peer_a_api, response)

    response = API_CLIENT.add_neighbors(peer_b_api, [peer_a_udp])
    print(peer_b_api, response)
