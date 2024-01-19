import os
import sys 
import json
import re
from tqdm import tqdm
import numpy as np
import pandas as pd
import SimpleITK as sitk
import time
import argparse as ap


try:
    import helper_functions as helper
except:
    from . import helper_functions as helper
    

atlas_dir = '/app/CRL_Fetal_Brain_Atlas_2017'

################################################################################
# Main functions designed to extract volumes from segmentation files. 

def get_labels(label_path = None):
    if label_path is None:
        full_path = os.path.join(atlas_dir, 'labelkey.txt')
    else:
        full_path = label_path
    stop_pattern = re.compile('^#*#$')
    
    with open (full_path, 'r') as f:
        line = f.readline()
        while not stop_pattern.search(line):
            line = f.readline()
        data = f.read().splitlines()

    p = re.compile('".*"')
    label_l = []
    for c, d in enumerate(data):
        m = p.search(d)
        if m:
            label_l.append(m.group().replace('"',''))

    return label_l


def extract_volume(path, subj_id, return_type = None, save_path = None, show = False, label_path = None):
    try:
        image = sitk.ReadImage(path, imageIO="NiftiImageIO")
        x, y, z = image.GetSpacing()
        voxel_volume = x*y*z
        
        img_arr = sitk.GetArrayFromImage(image)
        img_max = int(img_arr.max()) + 1

        volumes = []
        for i in range(img_max):
            res = np.sum(img_arr == i)
            volumes.append(res * voxel_volume)
        res_dict = {subj_id:volumes}
        res = pd.DataFrame.from_dict(res_dict)

        if save_path is not None:
            labels = get_labels(label_path)
            max_length = max(len(labels), len(volumes))
            for k, v in res_dict.items():
                diff = max_length - len(v)
                if diff > 0:
                    zeros = [0] * diff
                    v.extend(zeros)

            res = pd.DataFrame.from_dict(res_dict)
            res.index = labels

            save_path = os.path.abspath(save_path)
            res.to_excel(save_path, header = True, index = True)

        if show:
            for enum, v in enumerate(volumes):
                print("{:>3d}: {:>12.3f}".format(enum, v))

        
        if return_type == 'df':
            return res
        elif return_type == 'list':
            return volumes
        elif return_type == 'dict':
            return res_dict
        

    except IOError as e: 
        print("File not found")
    except Exception as e:
        print("Error")
        print(e)


################################################################################
# Functions designed to be used in batches.

def find_pattern_file(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for f in files:
            if 'Registration_files' in root:
                continue
            if pattern.lower() in f.lower():
                full_path = os.path.join(root, f)
                return full_path

def batch_extraction(directories = None, pattern = None, save_directory = None, file_name = None, ret_df = False, label_path = None):
    """
    directory: Put direcotry you want to search
    pattern: pattern to search directory for
    save_directory = Where to save excel results to
    """
    subj_paths = []

    for dir_path in directories:
        dir_path = os.path.abspath(dir_path)
        dir_subj_paths = [os.path.join(dir_path, x) for x in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, x))]
        subj_paths.extend(dir_subj_paths)

    save_path = os.path.join(save_directory, file_name)
    
    print(f'\n\tExtracting Volumes on {len(subj_paths)} subjects and saving to {save_path}\n')

    res_dict = {}
    for subj_path in tqdm(subj_paths):
        subj_id = os.path.basename(subj_path)
        segmentation_file = find_pattern_file(subj_path, pattern)
        if segmentation_file is None:
            continue
        
        subj_dict = extract_volume(segmentation_file, subj_id, return_type = 'dict')
        res_dict.update(subj_dict)
    
    max_length = 0
    for k, v in res_dict.items():
        if len(v) > max_length:
            max_length = len(v)

    for k, v in res_dict.items():
        diff = max_length - len(v)
        if diff > 0:
            zeros = [0] * diff
            v.extend(zeros)

    res = pd.DataFrame.from_dict(res_dict)
    
    labels = get_labels(label_path)
    max_length = max(max_length, len(labels))
    for k, v in res_dict.items():
        diff = max_length - len(v)
        if diff > 0:
            zeros = [0] * diff
            v.extend(zeros)

    res = pd.DataFrame.from_dict(res_dict)
    res.index = labels
    
    res.to_excel(save_path, header = True, index = True)

    if ret_df:
        return res


def merge_individual_excel_results(directory, save_dir = None):
    tis_result_excels = []
    reg_result_excels = []

    for root, dirs, files in os.walk(directory):
        for f in files:
            if f == 'Region_results.xlsx':
                reg_result_excels.append(os.directory.join(root, f))
            elif f == 'Tissue_results.xlsx':
                tis_result_excels.append(os.directory.join(root, f))

    if save_dir is None:
        save_dir = directory
    
    tis_df_save_name = os.path.join(save_dir, 'All_tissue_results.xlsx')
    reg_df_save_name = os.path.join(save_dir, 'All_region_results.xlsx')

    tis_df = pd.DataFrame()
    for res_file in tis_result_excels:
        pass
        





    

################################################################################
"""

    This section is for running the above functions after the fact through the 
    FSBS terminal interface. 

"""
def main():
    parser = ap.ArgumentParser(
        prog = "extract_volumes.py",
        description = "Python script to extract volumes from segmentation files.",
    )
    parser.add_argument('-fh', '--full_help', action = 'store_true', 
        help = 'Show help messages for all commandline options.', default = False)


    subparse = parser.add_subparsers(help = 'Choose which option to run', dest = 'method')
    ev_parse = subparse.add_parser('extract_volumes')
    be_parse = subparse.add_parser('batch_extraction')
    me_parse = subparse.add_parser('merge_excel_results')

    # Extract volume parser
    ev_parse.add_argument('path', type = str, help = 'Path to file which needs the volumes extracted.')
    ev_parse.add_argument('subject_id', help = 'Subject ID')
    ev_parse.add_argument('-rt', '--return_type', help = 'How results should be return.', 
            choices = ['df', 'list', 'dict'], default = None)
    ev_parse.add_argument('-sp', '--save_path', help='Where ouput should be saved with valid filename.',
            default = None)
    ev_parse.add_argument('--show', help='Whether to print output to the terminal.', action = 'store_true',
            default = False)
    ev_parse.add_argument('-lp', '--label_path', help = 'Path to desired ITK-Snap label file.', default=None)

    # Batch extraction parser
    be_parse.add_argument('-d', '--directories', nargs = '+', help = "Directories to run batch extraction in.", required = True)
    be_parse.add_argument('-p', '--pattern', help = 'Pattern to find within filenames that need extracted.', required = True)
    be_parse.add_argument('-sd', '--save_directory', help='Direcotry to save results into. Default is extraction directory', default = None, required = True)
    be_parse.add_argument('-fn', '--filename', help = 'Basename for results output file.', default = None, required=True)
    be_parse.add_argument('-lp', '--label_path', help = 'Path to desired ITK-Snap label file.', default=None)

    
    # Merge excel parser
    me_parse.add_argument('directory', help = "Directory to search for volumetric results in to merge into one excel.")
    me_parse.add_argument('-sd', '--save_dir', help='Which directory result files should be saved to',
            default = None)

    parsers = [parser, ev_parse, be_parse, me_parse]

    args = parser.parse_args()
    if args.full_help:
        cols, _ = os.get_terminal_size()
        for p in parsers:
            p.print_help()
            print('-'*cols)
    
    
    elif args.method == 'extract_volumes':
        extract_volume(args.path, args.subject_id, 
            return_type = args.return_type, save_path = args.save_path, show = args.show, label_path=args.label_path)
    
    elif args.method == 'batch_extraction':
        batch_extraction(args.directories, args.pattern, save_directory=args.save_directory, file_name=args.filename, ret_df=False, label_path=args.label_path)

    elif args.method == 'merge_excel_results':
        merge_individual_excel_results(args.directory, save_dir = args.save_dir)

if __name__ == "__main__":
    main()