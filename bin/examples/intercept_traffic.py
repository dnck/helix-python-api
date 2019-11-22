#!/usr/bin/env python3
import argparse, socket
import hashlib


MAX_BYTES = 800
NULL_HASH = "564d4682e53623eac67e8e1a761e99f1f26bbe6ba100f887f011d7fad3ceaf98"
NULL_HASH_0 = "0"*64
TXVM_SIZE = 768


def server(port):
    """
    This server is capable of intercepting pendulum udp packets.
    It sends the packet back to the original sender.
    Upon receiving the packets, the receiver (not this server) will validate
    the bytes. If the receiver gets more duplicates of these bytes,
    and the duplicates are not yet evicted from the cache, then the receiver
    will drop the packets as if it didn't receive them.
    This server just prints the transaction hash of the received packets.
    Regarding the final 32 bytes of the packets, this server does not yet do
    anything. The last 32 bytes could be either the same hash as the hash of
    the first 768 bytes, or different. Depending on this distinction,
    the actual pendulum node would do different things.
    I imagine that we might implement a middle layer in the network that
    receives packets from nodes, and distributes them throughout the network
    depending on need. Kinda like communism. How to determine who needs them?
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', port))
    print('Server listening at {}'.format(sock.getsockname()))
    while True:
        received_bytes, address = sock.recvfrom(MAX_BYTES)
        tx_hash_768 = hashlib.sha3_256(received_bytes[0:TXVM_SIZE]).hexdigest()
        if tx_hash_768 == NULL_HASH:
            print("Received_tx: ", NULL_HASH_0)
        else:
            print("Received_tx: ", tx_hash_768)
        sock.sendto(received_bytes, address)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Intercept pens UDP traffic.')
    parser.add_argument('-p',
                        metavar='PORT',
                        type=int,
                        default=4101,
                        help='UDP port (default 1060)'
                        )
    args = parser.parse_args()
    server(args.p)
