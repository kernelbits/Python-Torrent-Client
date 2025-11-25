import urllib.parse
import urllib.request
import random
import socket
import struct
from benCoding import TorrentDecoder

def build_tracker_url(base_url, info_hash, file_length, peer_id, port=6881):
    # 1. Create the dictionary with RAW data
    params = {
        'info_hash': info_hash, #
        'peer_id': peer_id,     
        'port': port,
        'uploaded': 0,
        'downloaded': 0,
        'left': file_length,
        'compact': 1,
        'event': 'started'
    }
    
    # 2. Let urllib handle the magic (Byte encoding, joining with &, etc)
    query_string = urllib.parse.urlencode(params)
    
    # 3. Combine them
    return base_url + "?" + query_string

def get_peers(tracker_url, info_hash, file_length):
    # 1. Generate Peer ID
    # Format: -PC0001- + 12 random digits
    peer_id = f"-PC0001-{str(random.randint(100000000000, 999999999999))}"
    
    # 2. Build the URL (Call your helper function!)
    url = build_tracker_url(tracker_url, info_hash, file_length, peer_id)
    
    print(f"Requesting: {url}") # Debug print to see what you built!

    # 3. Send Request
    # use urllib.request.urlopen(url)
    # Check if response.status == 200
    # response_data = response.read()
    with  urllib.request.urlopen(url) as response:
        if response.status != 200:
            raise ConnectionError(f"Tracker failed with status code : {response.status}")
        response_data = response.read()

    
    # 4. Decode Response
    # Use TorrentDecoder(response_data).decode()
    response_decode = TorrentDecoder(response_data).decode()
    print("Tracker Response Keys : ",response_decode.keys())
    if b'failur ereason' in response_decode:
        failure_msg = response_decode[b'failure reason'].decode("utf-8")
        raise ConnectionError(f"Tracker Error : {failure_msg}")
    print("DEBUG RESPONSE:", response_decode)


    # 5. Return the binary blob from the dictionary (key is b'peers')
    return response_decode[b'peers']

def parse_peers_blob(peers_blob):
    peers = []
    if len(peers_blob) % 6 != 0:
        raise ValueError("Data is not Correct")
    for i in range(0,len(peers_blob),6):
        chunk = peers_blob[i: i+6]
        ip = socket.inet_ntoa(chunk[0:4])
        port = struct.unpack("!H", chunk[4:6])[0]
        peers.append((ip, port))
    return peers 