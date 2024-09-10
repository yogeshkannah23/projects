from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from .forms import FileUploadForm
from django.conf import settings
import os
from django.http import HttpResponse
import shutil
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIRI = Path(__file__).resolve().parent.parent
file_name = ''
# Create your views here.

def index(request):
    return render(request,'info.html')



def file_upload_view(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        FILE_NAME = request.FILES['file'].name
        if form.is_valid():
            file_instance = form.save()
            
            return redirect("analyse")
    else:
        form = FileUploadForm()

    return render(request, 'upload_file.html', {'form': form})

def preprocess():
    
    df = pd.read_csv( str(BASE_DIRI) + f"\\media\\uploads\\{file_name}")
    df['invoice_date'] = pd.to_datetime(df['invoice_date'], format='%d-%m-%Y')
    return df

def analyse(request):
    action = request.GET.get('action')

    if action == 'pie_chart':
        return render(request,'charts/pie_chart_filter.html')
    elif action == 'graph':
        return render(request,'charts/graph.html')
    return render(request,'analyses.html')

def pie_chart_filter(request):
    generated = False
    from_date = ''
    to_date = ''
    options = ['Gender','Payment Method','Shopping Mall','Quantity']
    df= preprocess()
    if request.method == 'POST' and request.POST.get('from_date') and request.POST.get('to_date'):
        from_date = request.POST.get('from_date')
        from_date = datetime.strptime(from_date,'%Y-%m-%d')
        to_date = request.POST.get('to_date')
        to_date = datetime.strptime(to_date,'%Y-%m-%d')
        category = request.POST.get('category')

        #processing
        df = df[(df['invoice_date'] >= from_date) & (df['invoice_date'] < to_date)]
        size = len(df)
        print(df)
        if size == 0:
            return HttpResponse("There is No data from the filter")
        # sample_data = df.head(500)

        if category == 'Gender':
            dict1 = df['gender'].value_counts().to_dict()
            labels = list(dict1.keys())
            sizes = list(dict1.values())
            # plt.figure(figsize=(8, 6))
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
            plt.legend(labels, title="Categories", loc="best")

            # Title
            plt.title('Pie Chart with Legends')

            # Display the pie chart

            # plt.savefig(os.path.join(BASE_DIRI, '\\static'), format='png')
            plt.savefig('.\shop\static\images\out.png', format='png')
            generated = True

        if size >= 100:
            sample_df = df.head(100)
        table = sample_df.to_html(index = False)

        return render(request,'charts/pie_chart_filter.html',{'options':options,'table':table,'size':size,'generated':generated,'from_date':from_date,'to_date':to_date})


    return render(request,'charts/pie_chart_filter.html',{'options':options})

# def pie_filter_view(request):
#     return render()