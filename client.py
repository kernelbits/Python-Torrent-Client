import struct 
import socket 

class Handshake:
    def __init__(self,info_hash,peer_id):
        self.info_hash = info_hash
        self.peer_id = peer_id

        self.protocol = b"BitTorrent protocol"
        self.protocol_len = bytes([len(self.protocol)])
        self.reserved = b"\x00" * 8 
        

    def serialize(self):
        return self.protocol_len + self.protocol + self.reserved + self.info_hash + self.peer_id



class PeerClient:
    def __init__(self,peer_ip,peer_port,info_hash,peer_id):
        self.ip = peer_ip
        self.port = peer_port
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.socket = None
        
    def connect(self):
        try:
            # 1. Create Socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # 2. Set Timeout (Crucial! Otherwise it hangs for minutes)
            self.socket.settimeout(3)
            
            print(f"Connecting to {self.ip}:{self.port}...")
            
            # 3. Connect using the IP, not the ID!
            self.socket.connect((self.ip, self.port))

            # 4. Send Handshake (Pass the required arguments!)
            h = Handshake(self.info_hash, self.peer_id)
            self.socket.sendall(h.serialize())

            # 5. Receive Response (Expect 68 bytes)
            response = self.socket.recv(68)
            
            # 6. Validate
            if len(response) < 68:
                print("❌ Peer disconnected early.")
                return False
                
            # Do NOT decode() binary data. Just read the bytes.
            # Byte 28 to 48 is the Info Hash
            received_hash = response[28:48]
            
            if received_hash == self.info_hash:
                print(f"✅ Handshake Successful with {self.ip}!")
                self.socket.close() # Closing for now since we are just testing
                return True
            else:
                print(f"❌ Peer has wrong file hash.")
                self.socket.close()
                return False

        except Exception as e:
            # This catches timeout, connection refused, etc.
            print(f"❌ Error connecting to {self.ip}: {e}")
            if self.socket:
                self.socket.close()
            return False



