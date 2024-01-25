import os, sys
import shutil
import psutil
import datetime
import pandas as pd
import numpy as np
import time
import json
import pathlib

def find_reconstruction_files(path, search_term = 'recon', exclude_term = None, search_dir = None, exclude_dir = None):
    recon_file, mask_file = None, None

    #for root, dirs, files in os.walk(path):
    #    for f in files:
    for f in os.listdir(path):
            if (exclude_term is not None and exclude_term in f) or os.path.basename(path) == exclude_dir:
                continue
            if search_dir is None or os.path.basename(path) == search_dir:
                if search_term in f.lower() and 'mask' not in f.lower() and '.nii' in f.lower():
                    recon_file = os.path.join(path, f)
                if 'mask' in f.lower() and '.nii' in f.lower():
                    mask_file = os.path.join(path, f)
    return recon_file, mask_file


def determine_cpu_cores():
    cpu_per = psutil.cpu_percent(interval=1, percpu=True)
    min_cores = 5
    avail_cores = 0
    for per in cpu_per:
        if per < 10.0:
            avail_cores+=0.75
    avail_cores = max(int(avail_cores), min_cores)
    return avail_cores

def get_templates(GA, template_dir):
    GA = round(int(GA))
    if GA > 38: 
        GA = 38

    if GA < 36:
        GA_str = str(GA)
    else:   # atlas name changes after GA == 36
        GA_str = str(GA) + 'exp'

    template = os.path.join(template_dir,'STA' + GA_str + '.nii.gz')
    tissue_template = os.path.join(template_dir,'STA' + GA_str + '_tissue.nii.gz')
    region_template = os.path.join(template_dir,'STA' + GA_str + '_regional.nii.gz') 
    
    return template, tissue_template, region_template

def get_ga(subj_id, ga_df):
    subj_id = str(subj_id).lower()
    try:
        subj_pma = ga_df.loc[:,'ga'][ga_df.deid == subj_id].values[0]
        return subj_pma
    except:
        return None

def find(name, path):
    newname = None
    for root, dirs, files in os.walk(path):
        for f in files:
            if name in f:
                newname = os.path.join(root, f)
                return newname
    return newname


def load_excel_or_csv(excel_path, type_dict = None, colnames=None):
    excel_abs_path = os.path.abspath(excel_path)
    suffix = os.path.basename(excel_abs_path).split('.')[1]
    if suffix.lower() == 'csv':
        df = pd.read_csv(excel_abs_path, dtype = type_dict)
    elif suffix.lower() == 'xlsx' or suffix.lower() == 'xls':
        df = pd.read_excel(excel_path, dtype = type_dict)
    else:
        print(f"Unable to read file {excel_abs_path}.")
        sys.exit()

    df.columns = [x.lower().replace(' ','_') for x in df.columns]
    df.replace('.', np.nan, inplace = True)

    if colnames is not None and len(colnames) == len(df.columns):
        df.columns = colnames
    
    return df

def rename_transform(full_prefix, new_file_name):
    file_dir = os.path.dirname(full_prefix)
    file_prefix = os.path.basename(full_prefix)
    old_file_name = find(file_prefix, file_dir)
    new_file_name = os.path.join(file_dir, os.path.basename(new_file_name))
    if old_file_name is not None:
        shutil.move(old_file_name, new_file_name)

def files_missing(*files):
    for f in files:
        if not os.path.isfile(f):
            return True
    return False

def write_version(path):
    root_path = pathlib.Path(__file__).parents[1]
    app_info_file = os.path.join(root_path, "fsbs_info.json")
    t = datetime.date.today()
    date_string = t.strftime('%Y-%m-%d')

    with open(app_info_file, 'r') as read_file:
        data = json.load(read_file)
    
    version_msg = f"FSBS version {data['version']} as of {data['release_date']}\n"

    version_file = os.path.join(path, 'version_information.txt')
    with open(version_file, 'a+') as f:
        f.write(version_msg)


def write_error(path, e):
    t = datetime.date.today()
    date_string = t.strftime('%Y-%m-%d')
    error_msg = f'Error on {date_string}:\n{e}\n'

    error_file = os.path.join(path, 'error_information.txt')
    with open(error_file, 'a+') as f:
        f.write(error_msg)


def write_time(path, process, start_time, msg = None):
    end_time = time.time()
    t = datetime.date.today()
    date_string = t.strftime('%Y-%m-%d at %H:%M')
    if msg is None:
        msg = f'\n{process.title()} completed at {date_string} took {(end_time - start_time)/60:.2f} minutes to complete.\n'
    time_file = os.path.join(path, 'running_time.txt')
    with open(time_file, 'a+') as f:
        f.write(msg)

