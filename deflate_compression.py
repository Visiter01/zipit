# zipit/deflate_compression.py
import zlib
import struct
import os
from io import BytesIO
from .huffman import HuffmanCompression

class CompressionMethod:
    HUFFMAN = 0
    DEFLATE = 1
    
class DeflateCompression:
    @staticmethod
    def compress(data, level=9):
        """
        Compress data using DEFLATE algorithm with specified compression level.
        Level ranges from 0 (no compression) to 9 (maximum compression).
        """
        if not data:
            return None
        
        # i have compressed  the data using zlib this is inbuilt feature ffor compression
        compressed_data = zlib.compress(data, level)
        
        # Prepare the result: 1 byte for method + compressed data
        result = struct.pack('B', CompressionMethod.DEFLATE)
        result += compressed_data
        
        return result
    
    @staticmethod
    def decompress(compressed_data):
        """Decompress data that was compressed with DEFLATE algorithm"""
        if not compressed_data:
            return None
        
        # Extract the compressed data (skip the method byte)
        data_to_decompress = compressed_data[1:]
        
        #  i have decompresses  using zlib again in built feature for decompressor
        decompressed_data = zlib.decompress(data_to_decompress)
        
        return decompressed_data

class CompressFactory:
    """Factory class to choose between compression methods"""
    
    @staticmethod
    def compress(data, method=CompressionMethod.DEFLATE, level=9):
        """
        Compress data using the specified method.
        
        Args:
            data: The data to compress
            method: CompressionMethod.HUFFMAN or CompressionMethod.DEFLATE
            level: Compression level for DEFLATE (0-9)
            
        Returns:
            Compressed data with method indicator at the start
        """
        if method == CompressionMethod.HUFFMAN:
            huffman = HuffmanCompression()
            result = huffman.compress(data)
            # Prepend method indicator
            return struct.pack('B', CompressionMethod.HUFFMAN) + result
        elif method == CompressionMethod.DEFLATE:
            return DeflateCompression.compress(data, level)
        else:
            raise ValueError(f"Unsupported compression method: {method}")
    
    @staticmethod
    def decompress(compressed_data):
        """
        Decompress data using the method indicator at the start.
        
        Args:
            compressed_data: The data to decompress with method indicator
            
        Returns:
            Decompressed data
        """
        if not compressed_data:
            return None
            
        # Extract the compression method (this used to from byte information )
        method = struct.unpack('B', compressed_data[:1])[0]
        
        if method == CompressionMethod.HUFFMAN:
            huffman = HuffmanCompression()
            # just some error indicator
            return huffman.decompress(compressed_data[1:])
        elif method == CompressionMethod.DEFLATE:
            return DeflateCompression.decompress(compressed_data)
        else:
            raise ValueError(f"Unsupported compression method: {method}")
