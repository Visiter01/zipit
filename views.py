# zipit/views.py
from django.shortcuts import render
from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .huffman import HuffmanCompression

@csrf_exempt
def compress_file(request):
    """Django view to compress an uploaded file"""
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        # Read file content
        file_content = uploaded_file.read()
        
        # Compress the file
        huffman = HuffmanCompression()
        compressed_data = huffman.compress(file_content)
        
        # Save compressed file
        compressed_filename = f"{uploaded_file.name}.huff"
        compressed_file_path = default_storage.save(f"compressed/{compressed_filename}", ContentFile(compressed_data))
        
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
        
        # Decompress the file
        decompressed_data = HuffmanCompression.decompress(compressed_data)
        
        if not decompressed_data:
            return HttpResponse("Decompression failed.", status=400)
        
        # Original filename (removing .huff extension)
        if uploaded_file.name.endswith('.huff'):
            original_filename = uploaded_file.name[:-5]  # Remove .huff
        else:
            original_filename = f"decompressed_{uploaded_file.name}"
        
        # Save decompressed file
        decompressed_file_path = default_storage.save(f"decompressed/{original_filename}", ContentFile(decompressed_data))
        
        # Create response with download
        response = HttpResponse(decompressed_data, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{original_filename}"'
        
        return response
    
    return render(request, 'zipit/upload.html')

def home(request):
    """Home page view with upload forms"""
    return render(request, 'zipit/upload.html')
