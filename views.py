# zipit/views.py
from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .huffman import HuffmanCompression
from .deflate_compression import CompressFactory, CompressionMethod

@csrf_exempt
def compress_file(request):
    """Django view to compress an uploaded file"""
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Read file content and store it
        file_content = uploaded_file.read()
        
        # Get compression method from form (default to DEFLATE if not specified)(as deflate is more efficient)
        compression_method = int(request.POST.get('compression_method', CompressionMethod.DEFLATE))
        compression_level = int(request.POST.get('compression_level', 6))  # Default to medium compression(6 is for balanced 4 for lower and 9 for highest compression)
        
        # Compress the file using the factory
        if compression_method == CompressionMethod.HUFFMAN:
            # Use original Huffman method for backward compatibility
            huffman = HuffmanCompression()
            compressed_data = huffman.compress(file_content)
            compressed_filename = f"{uploaded_file.name}.huff"
        else:  # DEFLATE
            compressed_data = CompressFactory.compress(
                file_content, 
                method=compression_method,
                level=compression_level
            )
            compressed_filename = f"{uploaded_file.name}.dflt"
        
        # Save compressed file
        compressed_file_path = default_storage.save(
            f"compressed/{compressed_filename}", 
            ContentFile(compressed_data)
        )
        
        # Create response with download
        response = HttpResponse(compressed_data, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{compressed_filename}"'
        
        return response
    
    return render(request, 'zipit/upload.html')

@csrf_exempt
def decompress_file(request):
    """Django view to decompress an uploaded compressed file"""
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Read compressed content
        compressed_data = uploaded_file.read()
        
        # Check file extension to determine decompression method
        if uploaded_file.name.endswith('.huff'):
            # Use original Huffman decompression for backward compatibility
            decompressed_data = HuffmanCompression.decompress(compressed_data)
            original_filename = uploaded_file.name[:-5]  # Remove .huff
        elif uploaded_file.name.endswith('.dflt'):
            # Use the factory for DEFLATE decompression
            decompressed_data = CompressFactory.decompress(compressed_data)
            original_filename = uploaded_file.name[:-5]  # Remove .dflt
        else:
            # Try to detect method from data
            try:
                decompressed_data = CompressFactory.decompress(compressed_data)
                original_filename = f"decompressed_{uploaded_file.name}"
            except Exception as e:
                # If that fails, try original Huffman decompression
                try:
                    decompressed_data = HuffmanCompression.decompress(compressed_data)
                    original_filename = f"decompressed_{uploaded_file.name}"
                except Exception as inner_e:
                    return HttpResponse(f"Decompression failed: File format not recognized", status=400)
        
        if not decompressed_data:
            return HttpResponse("Decompression failed.", status=400)
        
        # Save decompressed file
        decompressed_file_path = default_storage.save(
            f"decompressed/{original_filename}", 
            ContentFile(decompressed_data)
        )
        
        # Create response with download
        response = HttpResponse(decompressed_data, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{original_filename}"'
        
        return response
    
    return render(request, 'zipit/upload.html')

def home(request):
    """Home page view with upload forms"""
    return render(request, 'zipit/upload.html')
