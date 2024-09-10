from django.shortcuts import render
from django.http import request,HttpResponse
from django.core.files.storage import FileSystemStorage
# Create your views here.

def index(request):
    uploaded_file_url = None
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        uploaded_file_url = fs.url(filename)
        print(uploaded_file_url)
        return render(request, 'index.html', {'uploaded_file_url': uploaded_file_url})
