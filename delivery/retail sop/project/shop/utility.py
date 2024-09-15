import os
import glob
import shutil

import os
import pandas as pd


def preprocess(BASE_DIRI):
    path = str(BASE_DIRI)+'\\media\\uploads'
    file_path = get_latest_file_in_dir(path)
    df = pd.read_csv(file_path)
    # df['invoice_date'] = pd.to_datetime(df['invoice_date'], format='%d-%m-%Y')
    return df

def get_latest_file_in_dir(directory):
    # Get a list of all files in the directory
    files = glob.glob(os.path.join(directory, '*'))
    
    if not files:
        return None  # Return None if there are no files
    
    # Get the file with the latest modification time
    latest_file = max(files, key=os.path.getmtime)
    
    return latest_file