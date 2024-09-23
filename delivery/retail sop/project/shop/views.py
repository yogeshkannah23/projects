from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from .forms import FileUploadForm
from django.conf import settings
from shop.utility import preprocess
from django.http import HttpResponse
from pathlib import Path
import os
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import numpy as np


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



def analyse(request):
    action = request.GET.get('action')

    if action == 'pie_chart':
        return render(request,'charts/pie_chart_filter.html')
    elif action == 'graph':
        # graph_filter('charts/graph_filter.html')
        # return 
        # categories = ['Payment Method','Shopping Mall','Gender','Category']
        return render(request,'charts/graph.html',{
            # 'categories':categories
        })
    elif action == 'bar':
        return render(request,'charts/bar_chart.html')
    return render(request,'analyses.html')

def graph(request):
    generated = False
    from_date = ''
    to_date = ''
    df = preprocess(BASE_DIRI)  # Assuming preprocess function loads your data
    min_date = df['invoice_date'].min()
    max_date = df['invoice_date'].max()
    df['invoice_date'] = pd.to_datetime(df['invoice_date'], dayfirst=True)
    

    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.strptime(to_date, '%Y-%m-%d')

        if from_date and to_date:
            month_diff = (to_date.year - from_date.year) * 12 + (to_date.month - from_date.month)
            category = request.POST.get('category')
            if category == 'Gender':
                category = 'gender'
            elif category == 'Payment Method':
                category = 'payment_method'
            elif category == 'Shopping Mall':
                category = 'shopping_mall'
            elif category == 'Quantity':
                category = 'quantity'
            elif category == 'Category':
                category = 'category'

            # Process data by months
            data_lst = list()
            for i in range(month_diff):
                tf = df[(df['invoice_date'].dt.year == from_date.year) & 
                        (df['invoice_date'].dt.month == from_date.month + i)]
                temp = tf[category].value_counts().to_dict()
                data_lst.append(temp)

            unique_mall = df[category].unique()
            data_dict = dict()
            for i in unique_mall:
                temp = []
                for j in range(len(data_lst)):
                    temp.append(data_lst[j].get(i, 0))  # Use get(i, 0) to handle missing keys
                data_dict[i] = temp

            df = pd.DataFrame(data_dict)
            lst = ['r', 'g', 'b', 'c', 'm', 'y', 'k', '#FF5733', '#33FF57', '#3357FF']

            # Plot data
            for i in range(len(df.columns)):
                df[df.columns[i]].plot(label=df.columns[i], grid=False, color=lst[i])
            
            # plt.figure(figsize=(6,6))
            plt.xlabel('Months')
            plt.ylabel('Values')
            plt.title(f'{from_date} To {to_date}')
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            # plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

            # plt.tight_layout() 


            plt.savefig(os.path.join(BASE_DIRI, 'shop/static/images/out.png'), format='png')
            # plt.savefig('.\project\shop\static\images\out.png', format='png')
            plt.close()

            # Buffer handling
            # buffer = io.BytesIO()

            # # Save the current plot into the buffer
            # plt.savefig(buffer, format='png')
            # plt.close()  # Close the plot to free memory and prevent overlay

            # buffer.seek(0)  # Move the buffer cursor to the start
            # image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            generated = True
            size = len(df)
            sample_df = df.head(10) if size > 10 else df
            table = sample_df.to_html(index=False)

            # Render the template with the graph and data table
            return render(request, 'charts/graph.html', {
                'table': table,
                'size': size,
                'generated': generated,
                # 'imager': image_base64
            })

    return render(request, 'charts/graph.html',{
        'min_date':min_date,
        'max_date':max_date
    })


def pie_chart_filter(request):
    generated = False
    from_date = ''
    to_date = ''
    df = preprocess(BASE_DIRI)  # Assuming preprocess function loads your data
    min_date = df['invoice_date'].min()
    max_date = df['invoice_date'].max()
    df['invoice_date'] = pd.to_datetime(df['invoice_date'],dayfirst=True)

    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')

        if from_date and to_date:
            try:
                from_date = datetime.strptime(from_date, '%Y-%m-%d')
                to_date = datetime.strptime(to_date, '%Y-%m-%d')
            except ValueError:
                return HttpResponse("Invalid date format. Please use YYYY-MM-DD.")

            category = request.POST.get('category')

            # Filter data based on date range
            df = df[(df['invoice_date'] >= from_date) & (df['invoice_date'] <= to_date)]
            size = len(df)

            if size == 0:
                return HttpResponse(f"No data available for the selected date range.Please Select the date Range between {min_date} to {max_date}")

            # Create a dictionary based on the selected category
            dict1 = {}
            if category == 'Gender':
                dict1 = df['gender'].value_counts().to_dict()
            elif category == 'Payment Method':
                dict1 = df['payment_method'].value_counts().to_dict()
            elif category == 'Shopping Mall':
                dict1 = df['shopping_mall'].value_counts().to_dict()
            elif category == 'Quantity':
                dict1 = df['quantity'].value_counts().to_dict()
            elif category == 'Category':
                dict1 = df['category'].value_counts().to_dict()
            elif category == 'Age':
                dict1 = df['age'].value_counts().to_dict()
                # Create ranges for age groups
                dict2 = {'1-20': 0, '20-40': 0, '40-60': 0, '60-80': 0, '80-100': 0}
                for age, count in dict1.items():
                    if 1 <= age <= 20:
                        dict2['1-20'] += count
                    elif 21 <= age <= 40:
                        dict2['20-40'] += count
                    elif 41 <= age <= 60:
                        dict2['40-60'] += count
                    elif 61 <= age <= 80:
                        dict2['60-80'] += count
                    elif 81 <= age <= 100:
                        dict2['80-100'] += count
                dict1 = dict2

            labels = list(dict1.keys())
            sizes = list(dict1.values())

            # # Plot the pie chart
            # plt.figure(figsize=(6,6))  # Optional: specify figure size
            # plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
            # plt.title(f'{category} Distribution')



            # plt.savefig(os.path.join(BASE_DIRI, 'shop/static/images/out.png'), format='png')
            # # plt.savefig('.\project\shop\static\images\out.png', format='png')
            # plt.close()



            # Save the plot to a byte buffer
            # buffer = io.BytesIO()
            # plt.savefig(buffer, format='png')
            # # plt.close()  # Always close the plot to free memory
            # buffer.seek(0)

            # # Encode the plot image in base64 format
            # image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            generated = True

            # Display a sample of the filtered data (if large)
            sample_df = df.head(10) if size > 10 else df
            table = sample_df.to_html(index=False)

            # Render template with the pie chart and filtered table
            return render(request, 'charts/pie_chart_filter.html', {
                'table': table,
                'size': size,
                'generated': generated,
                'from_date': from_date.strftime('%Y-%m-%d'),
                'to_date': to_date.strftime('%Y-%m-%d'),
                'labels':labels,
                'sizes':sizes
                # 'imager': image_base64
            })

    # Initial GET request
    return render(request, 'charts/pie_chart_filter.html',{
        'min_date':min_date,
        'max_date':max_date
    })

def bar_chart(request):
    generated = False
    from_date = ''
    to_date = ''
    df = preprocess(BASE_DIRI)  # Assuming preprocess function loads your data
    min_date = df['invoice_date'].min()
    max_date = df['invoice_date'].max()
    df['invoice_date'] = pd.to_datetime(df['invoice_date'], dayfirst=True)
    

    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        from_date = datetime.strptime(from_date, '%Y-%m-%d')
        to_date = datetime.strptime(to_date, '%Y-%m-%d')

        if from_date and to_date:
            month_diff = (to_date.year - from_date.year) * 12 + (to_date.month - from_date.month)
            category = request.POST.get('category')
            if category == 'Gender':
                category = 'gender'
            elif category == 'Payment Method':
                category = 'payment_method'
            elif category == 'Shopping Mall':
                category = 'shopping_mall'
            elif category == 'Quantity':
                category = 'quantity'
            elif category == 'Category':
                category = 'category'

            # Process data by months
            date = list()
            data_lst = list()
            for i in range(month_diff):
                tf = df[(df['invoice_date'].dt.year == from_date.year) & 
                        (df['invoice_date'].dt.month == from_date.month + i)]
                temp = tf[category].value_counts().to_dict()
                data_lst.append(temp)
                date.append(tf['invoice_date'].head(1).dt.month.tolist()[0])

            unique_category = df[category].unique()
            data_dict = dict()
            for i in unique_category:
                temp = []
                for j in range(len(data_lst)):
                    temp.append(data_lst[j].get(i, 0))  # Use get(i, 0) to handle missing keys
                data_dict[i] = temp


            df = pd.DataFrame(data_dict)

            generated = True
            size = len(df)
            sample_df = df.head(10) if size > 10 else df
            table = sample_df.to_html(index=False)

            # Render the template with the graph and data table
            return render(request, 'charts/bar_chart.html', {
                'table': table,
                'size': size,
                'generated': generated,
                'date':date,
                'unique_category':unique_category,
                'keys':list(data_dict.keys()),
                'values':list(data_dict.values()),
                'iter':len(unique_category)
                # 'imager': image_base64
            })

    return render(request, 'charts/bar_chart.html',{
        'min_date':min_date,
        'max_date':max_date
    })