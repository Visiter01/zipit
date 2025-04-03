# zipit/huffman.py
import heapq
import os
from collections import Counter
import pickle
from io import BytesIO

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
        
    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanCompression:
    def __init__(self):
        self.heap = []
        self.codes = {}
        self.reverse_mapping = {}
        
    def make_frequency_dict(self, text):
        """Calculate frequency of each character in the text"""
        return Counter(text)
        
    def make_heap(self, frequency):
        """Create a priority queue from frequencies"""
        for char, freq in frequency.items():
            node = HuffmanNode(char, freq)
            heapq.heappush(self.heap, node)
            
    def merge_nodes(self):
        """Build the Huffman tree by merging nodes"""
        while len(self.heap) > 1:
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)
            
            merged = HuffmanNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            
            heapq.heappush(self.heap, merged)
            
    def make_codes_helper(self, node, current_code):
        """Generate codes for each character recursively"""
        if node is None:
            return
            
        if node.char is not None:
            self.codes[node.char] = current_code
            self.reverse_mapping[current_code] = node.char
            return
            
        self.make_codes_helper(node.left, current_code + "0")
        self.make_codes_helper(node.right, current_code + "1")
        
    def make_codes(self):
        """Create Huffman codes"""
        root = heapq.heappop(self.heap)
        current_code = ""
        self.make_codes_helper(root, current_code)
        
    def get_encoded_text(self, text):
        """Encode the text using the Huffman codes"""
        encoded_text = ""
        for char in text:
            encoded_text += self.codes[char]
        return encoded_text
    
    def pad_encoded_text(self, encoded_text):
        """Add padding to make encoded text length a multiple of 8"""
        extra_padding = 8 - len(encoded_text) % 8
        for i in range(extra_padding):
            encoded_text += "0"
            
        padded_info = "{0:08b}".format(extra_padding)
        encoded_text = padded_info + encoded_text
        return encoded_text
    
    def get_byte_array(self, padded_encoded_text):
        """Convert binary string to bytes"""
        if len(padded_encoded_text) % 8 != 0:
            raise ValueError("Encoded text not padded properly")
            
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return bytes(b)
    
    def compress(self, data):
        """Compress the input data"""
        if not data:
            return None
            
        frequency = self.make_frequency_dict(data)
        self.make_heap(frequency)
        self.merge_nodes()
        self.make_codes()
        
        encoded_text = self.get_encoded_text(data)
        padded_encoded_text = self.pad_encoded_text(encoded_text)
        
        compressed_data = self.get_byte_array(padded_encoded_text)
        
        # Store frequency dictionary for later decompression
        freq_dict_bytes = pickle.dumps(frequency)
        
        # Combine frequency dict and compressed data
        result = len(freq_dict_bytes).to_bytes(4, byteorder='big')
        result += freq_dict_bytes
        result += compressed_data
        
        return result
    
    @staticmethod
    def remove_padding(padded_encoded_text):
        """Remove padding from the encoded text"""
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)
        
        padded_encoded_text = padded_encoded_text[8:]
        encoded_text = padded_encoded_text[:-extra_padding] if extra_padding > 0 else padded_encoded_text
        
        return encoded_text
    
    @staticmethod
    def decode_text(encoded_text, reverse_mapping):
        """Decode the encoded text using the reverse mapping"""
        current_code = ""
        decoded_text = bytearray()
        
        for bit in encoded_text:
            current_code += bit
            if current_code in reverse_mapping:
                decoded_text.append(reverse_mapping[current_code])
                current_code = ""
                
        return bytes(decoded_text)
    
    @classmethod
    def decompress(cls, compressed_data):
        """Decompress the data"""
        if not compressed_data:
            return None
            
        # Extract frequency dictionary
        freq_dict_size = int.from_bytes(compressed_data[:4], byteorder='big')
        freq_dict_bytes = compressed_data[4:4+freq_dict_size]
        frequency = pickle.loads(freq_dict_bytes)
        
        # Extract compressed data
        compressed_data = compressed_data[4+freq_dict_size:]
        
        # Convert bytes to binary string
        bit_string = ""
        for byte in compressed_data:
            bit_string += bin(byte)[2:].rjust(8, '0')
            
        # Remove padding
        encoded_text = cls.remove_padding(bit_string)
        
        # Rebuild Huffman tree and decode
        huffman = cls()
        huffman.make_heap(frequency)
        huffman.merge_nodes()
        huffman.make_codes()
        
        decompressed = cls.decode_text(encoded_text, huffman.reverse_mapping)
        
        return decompressed
