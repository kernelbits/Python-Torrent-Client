import math

class PieceManager:
    def __init__(self, pieces_blob, piece_length, total_length):
        self.pieces_blob = pieces_blob
        self.piece_length = piece_length
        self.total_length = total_length
        
        # Calculate total pieces (e.g. 500 bytes / 100 per piece = 5 pieces)
        self.total_pieces = math.ceil(self.total_length / self.piece_length)
        
        # 0 = Missing, 1 = Pending, 2 = Complete
        self.pieces_status = [0] * self.total_pieces
        
        print(f"PieceManager Initialized: {self.total_pieces} pieces to download.")

    def get_next_piece_index(self):
        # Find the first 'Missing' (0) piece
        for i in range(self.total_pieces):
            if self.pieces_status[i] == 0:
                self.pieces_status[i] = 1 # Mark pending
                return i
        return None

    def get_expected_hash(self, index):
        start = index * 20
        end = start + 20
        return self.pieces_blob[start:end]

    def mark_complete(self, index):
        self.pieces_status[index] = 2
        print(f"--- Progress: {self.pieces_status.count(2)} / {self.total_pieces} pieces ---")

    def mark_failed(self, index):
        self.pieces_status[index] = 0 # Reset to missing