from context import api
import argparse


if __name__ == "__main__":
    API_CLIENT = api.BaseHelixAPI()

    parser = argparse.ArgumentParser(description='')

    parser.add_argument('-host0',type=str, default='helixnetwork.ddns.net')

    parser.add_argument('-host1',type=str, default='stmpe.ml')

    parser.add_argument('-http0',type=str, default='8085')

    parser.add_argument('-http1',type=str, default='443')

    parser.add_argument('-udp0',type=str, default='4100')

    parser.add_argument('-udp1',type=str, default='4100')

    parser.add_argument('-ssl0',type=str, default=None)
    parser.add_argument('-ssl1',type=str, default=None)

    args = parser.parse_args()

    HTTP = "http://{}:{}"
    HTTPS = "https://{}:{}"

    UDP = "udp://{}:{}"

    response = API_CLIENT.remove_neighbors(peer_a_api, [peer_b_udp])
    print(peer_a_api, response)

    response = API_CLIENT.remove_neighbors(peer_b_api, [peer_a_udp])
    print(peer_b_api, response)
