import hashlib

class TorrentDecoder:
    def __init__(self, data):
        self.data = data
        self.index = 0

    def decode(self):
        # Stop if we reached the end of the file
        if self.index >= len(self.data):
            return None
        
        # Check the current character to decide what to do
        current_char = chr(self.data[self.index])
        
        if current_char == 'i':
            return self.decode_int()
        elif current_char.isdigit():
            return self.decode_string()
        elif current_char == 'l':
            return self.decode_list()
        elif current_char == 'd':
            return self.decode_dict()
        else:
            # If we hit weird data, just skip it (safety mechanism)
            self.index += 1
            return None

    def decode_int(self):
        # Format: i[number]e
        self.index += 1  # Skip 'i'
        temp_digits = ""
        while True:
            char = chr(self.data[self.index])
            if char == 'e':
                self.index += 1  # Skip 'e'
                break
            temp_digits += char
            self.index += 1
        return int(temp_digits)

    def decode_string(self):
        # Format: [length]:[string]
        length_str = ""
        # 1. Read the length
        while chr(self.data[self.index]) != ':':
            length_str += chr(self.data[self.index])
            self.index += 1
        
        # 2. Skip the colon
        self.index += 1
        
        # 3. Read the data
        length = int(length_str)
        # We slice raw bytes, we do NOT convert to string (keep it binary!)
        result = self.data[self.index : self.index + length]
        self.index += length
        return result

    def decode_list(self):
        # Format: l[item][item]e
        self.index += 1  # Skip 'l'
        my_list = []
        while True:
            # Check for end of list
            if chr(self.data[self.index]) == 'e':
                self.index += 1  # Skip 'e'
                return my_list
            # Recursively decode the next item
            item = self.decode()
            my_list.append(item)

    def decode_dict(self):
        # Format: d[key][value]e
        self.index += 1  # Skip 'd'
        my_dict = {}
        while True:
            # Check for end of dict
            if chr(self.data[self.index]) == 'e':
                self.index += 1  # Skip 'e'
                return my_dict
            
            # 1. Decode Key (Always a string)
            key = self.decode()
            # 2. Decode Value (Can be anything)
            value = self.decode()
            
            my_dict[key] = value

def bencode(data):
    # Used to turn the 'info' dict back into bytes for hashing
    if isinstance(data, int):
        return f"i{data}e".encode()
    
    elif isinstance(data, bytes):
        return f"{len(data)}:".encode() + data
    
    elif isinstance(data, str):
        # Helper: If we accidentally pass a string, convert to bytes
        return f"{len(data)}:".encode() + data.encode()
        
    elif isinstance(data, list):
        encoded = b"l"
        for item in data:
            encoded += bencode(item)
        encoded += b"e"
        return encoded
    
    elif isinstance(data, dict):
        encoded = b"d"
        # IMPORTANT: Keys must be sorted for the Hash to be correct
        keys = sorted(data.keys())
        for key in keys:
            encoded += bencode(key)
            encoded += bencode(data[key])
        encoded += b"e"
        return encoded
