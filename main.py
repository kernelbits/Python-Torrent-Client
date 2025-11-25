import hashlib
from benCoding import TorrentDecoder, bencode
from tracker import get_peers, parse_peers_blob
from client import PeerClient


def main():
    # 1. Open torrent file
    with open('debian.torrent', 'rb') as f:
        file_content = f.read()

    # 2. Decode metainfo (Use bencoding.py)
    decoder = TorrentDecoder(file_content)
    meta_info = decoder.decode()
    info_dict = meta_info[b'info']

    # 3. Calculate Info Hash
    bencoded_info = bencode(info_dict)
    info_hash = hashlib.sha1(bencoded_info).digest()

    # 4. Get Tracker URL
    tracker_url = meta_info[b'announce'].decode('utf-8')
    file_length = info_dict[b'length']

    print(f"Tracker: {tracker_url}")
    
    # 5. Connect to Tracker (Use tracker.py)
    # This is where your new code gets tested!
    peers_blob = get_peers(tracker_url, info_hash, file_length)
    
    # 6. Parse Peers (Use tracker.py)
    peers = parse_peers_blob(peers_blob)
    
    print(f"Found {len(peers)} peers:")
    for ip, port in peers[:5]:
        print(f"  {ip}:{port}")

    my_peer_id = b'-PC0001-' + b'123456789012' # 20 bytes
    for ip, port in peers:
        # Create a client for this peer
        client = PeerClient(ip, port, info_hash, my_peer_id)
        
        # Try to connect
        if client.connect():
            # IF SUCCESS: Stop looping! We found a friend.
            print(f"Connected to {ip}")
            break
            


if __name__ == "__main__":
    main()