import struct 
import socket 
import hashlib 

class Handshake:
    def __init__(self, info_hash, peer_id):
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.protocol = b"BitTorrent protocol"
        self.protocol_len = bytes([len(self.protocol)])
        self.reserved = b"\x00" * 8 

    def serialize(self):
        return self.protocol_len + self.protocol + self.reserved + self.info_hash + self.peer_id

class PeerClient:
    def __init__(self, peer_ip, peer_port, info_hash, peer_id, piece_manager):
        self.ip = peer_ip
        self.port = peer_port
        self.info_hash = info_hash
        self.peer_id = peer_id
        self.piece_manager = piece_manager # <--- NEW: We use the manager now
        
        self.socket = None
        self.peer_choking = True 
        self.am_interested = False 

        self.piece_buffer = b''
        self.current_piece_index = None 
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5) # Increased timeout slightly
            print(f"Connecting to {self.ip}:{self.port}...")
            self.socket.connect((self.ip, self.port))

            h = Handshake(self.info_hash, self.peer_id)
            self.socket.sendall(h.serialize())

            response = self.socket.recv(68)
            if len(response) < 68: return False
                
            received_hash = response[28:48]
            if received_hash == self.info_hash:
                print(f"✅ Handshake Successful with {self.ip}!")
                self.send_interested()
                self.listen_for_messages() 
                return True
            else:
                self.socket.close()
                return False
        except Exception as e:
            print(f"❌ Error connecting to {self.ip}: {e}")
            if self.socket: self.socket.close()
            return False
        
    def send_message(self, msg_id, payload=b''):
        msg_len = 1 + len(payload)
        header = struct.pack('!IB', msg_len, msg_id)
        self.socket.sendall(header + payload)

    def send_interested(self):
        self.send_message(2)
        self.am_interested = True 

    def request_new_piece(self):
        """Asks the manager for the next job"""
        self.piece_buffer = b'' # Reset buffer
        next_index = self.piece_manager.get_next_piece_index()
        
        if next_index is None:
            print("🎉 No more pieces needed! Disconnecting.")
            self.socket.close()
            return

        self.current_piece_index = next_index
        print(f"Requesting Piece {next_index}...")
        self.send_request(next_index, 0, 16384)

    def handle_message(self, msg_id, payload):
        if msg_id == 0:
            print("Peer CHOKED us.")
            self.peer_choking = True
            
        elif msg_id == 1:
            print("🚀 Peer UNCHOKED us!")
            self.peer_choking = False
            self.request_new_piece() # <--- Start the loop!
            
        elif msg_id == 5:
            print("Peer sent BITFIELD.")
        elif msg_id == 4:
            pass # Peer 'Have' message, ignore for now

        elif msg_id == 7:
            # Parse header
            piece_index = struct.unpack("!I", payload[0:4])[0]
            block_offset = struct.unpack("!I", payload[4:8])[0]
            block_data = payload[8:]
            
            self.piece_buffer += block_data
            
            # Use Manager's piece length (handles last piece logic logic too)
            expected_len = self.piece_manager.piece_length
            
            # Check if incomplete
            if len(self.piece_buffer) < expected_len:
                next_offset = len(self.piece_buffer)
                remaining = expected_len - next_offset
                block_size = min(16384, remaining)
                self.send_request(self.current_piece_index, next_offset, block_size)
            else:
                # Piece Done!
                print(f"✨ PIECE {piece_index} DOWNLOADED.")
                
                # Verify
                actual_hash = hashlib.sha1(self.piece_buffer).digest()
                expected_hash = self.piece_manager.get_expected_hash(piece_index)

                if actual_hash == expected_hash:
                    print(f"✅ Valid Piece {piece_index}.")
                    with open(f"piece_{piece_index}.dat", "wb") as f:
                        f.write(self.piece_buffer)
                    self.piece_manager.mark_complete(piece_index)
                    
                    # GET NEXT PIECE
                    self.request_new_piece()
                else:
                    print("❌ Hash Mismatch. Retrying...")
                    self.piece_manager.mark_failed(piece_index)
                    self.request_new_piece()

    def read_n_bytes(self, n):
        data = b''
        while len(data) < n:
            try:
                chunk = self.socket.recv(n - len(data))
                if not chunk: raise ConnectionError("Closed")
                data += chunk
            except socket.timeout: raise ConnectionError("Timeout")
        return data

    def listen_for_messages(self):
        while True:
            try:
                length_bytes = self.read_n_bytes(4)
                message_length = struct.unpack("!I", length_bytes)[0]
                if message_length == 0: continue
                
                message_id = int(self.read_n_bytes(1)[0])
                payload_length = message_length - 1
                
                if payload_length > 0: payload = self.read_n_bytes(payload_length)
                else: payload = b''
                
                self.handle_message(message_id, payload)
            except Exception as e:
                print(f"Message loop ended: {e}")
                break

    def send_request(self, piece_index, block_offset, block_length):
        req = struct.pack("!IBIII", 13, 6, piece_index, block_offset, block_length)
        self.socket.sendall(req)