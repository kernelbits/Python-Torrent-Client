import hashlib
from benCoding import TorrentDecoder, bencode
from tracker import get_peers, parse_peers_blob
from client import PeerClient
from piece_manager import PieceManager
import random

def main():
    # 1. Open
    with open('debian.torrent', 'rb') as f:
        file_content = f.read()

    # 2. Decode
    decoder = TorrentDecoder(file_content)
    meta_info = decoder.decode()
    info_dict = meta_info[b'info']

    # 3. Hash
    bencoded_info = bencode(info_dict)
    info_hash = hashlib.sha1(bencoded_info).digest()

    # 4. Tracker
    tracker_url = meta_info[b'announce'].decode('utf-8')
    file_length = info_dict[b'length']
    
    print(f"Tracker: {tracker_url}")
    peers_blob = get_peers(tracker_url, info_hash, file_length)
    peers = parse_peers_blob(peers_blob)
    print(f"Found {len(peers)} peers.")

    my_peer_id = f"-PC0001-{str(random.randint(100000000000, 999999999999))}".encode('utf-8')

    # 5. INITIALIZE PIECE MANAGER
    pieces_blob = info_dict[b'pieces']
    piece_length = info_dict[b'piece length']
    manager = PieceManager(pieces_blob, piece_length, file_length)

    # 6. START
    for ip, port in peers:
        # Pass the manager!
        client = PeerClient(ip, port, info_hash, my_peer_id, manager)
        
        if client.connect():
            print(f"Connected to {ip}")
            # The client will now loop downloading pieces until done or disconnected
            break

if __name__ == "__main__":
    main()