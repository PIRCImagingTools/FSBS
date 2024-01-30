import os, sys, shutil, time
import nipype.interfaces.ants as ants
import nipype.interfaces.fsl as fsl
import pandas as pd
import numpy as np
import math
import traceback

home_dir = os.getcwd()
sys.path.append(home_dir)

from utils import helper_functions as helper
from utils import visualization_tools as vt
from utils import extract_volumes as ev

from . import reorientation_functions as rf

def registration(
                subj_name,
                GA, 
                subject_file, 
                mask_file, 
                repeat = False,
                test_parameters = False, 
                tissue_template = None, 
                region_template = None, 
                template_img = None, 
                return_paths = False,
                orient_iterations = 150,
                reorient_method = 'binary',
                **kwargs
                ):

    start_time = time.time()

    # set iterations
    if test_parameters:
        iterations = 1
        orient_iterations = 1
        repeat = True
    else:
        iterations = 250

    # find number of cores to use 
    avail_cores = helper.determine_cpu_cores()

    # setup directories
    template_dir = '/app/CRL_Fetal_Brain_Atlas_2017'
    subj_path = os.path.abspath(subject_file)
    subj_dir = os.path.dirname(subj_path)
    registration_dir = os.path.join(subj_dir, 'Registration_files')
    output_dir = os.path.join(subj_dir, 'Outputs')
    

    for makedir in [registration_dir, output_dir]: 
        os.makedirs(makedir, exist_ok = True)

    # setup file names
    if tissue_template is None or region_template is None or template_img is None:
        template, tissue_template, region_template = helper.get_templates(GA, template_dir)
    else:
        template = template_img
        tissue_template = tissue_template
        region_template = region_template
    
    # files for n4 node, mask node, and orientation node
    bias_file = os.path.join(registration_dir, 'n4.nii.gz')
    brain_extracted_file = os.path.join(registration_dir, 'brain_extracted.nii.gz')
    oriented_bias = os.path.join(registration_dir, 'reorient_bias_corrected.nii.gz')
    oriented_bias_extracted = os.path.join(registration_dir, 'reorient_bet_bias_corrected.nii.gz') 
    
    # forward intermediate images
    intermediate_1_file = os.path.join(registration_dir, 'intermediate_1.nii.gz')
    intermediate_2_file = os.path.join(registration_dir, 'intermediate_2.nii.gz')
    intermediate_3_file = os.path.join(registration_dir, 'intermediate_3.nii.gz')

    # reverse intermediates images for tissue templates
    # rti = reverse tissue intermediates
    tissue_reverse_int_1 = os.path.join(registration_dir,'tissue_inverse_syn.nii.gz')
    tissue_reverse_int_2 = os.path.join(registration_dir, 'tissue_inverse_affine.nii.gz')
    tissue_reverse_int_3 = os.path.join(registration_dir, subj_name + '_tissue_segmentation.nii.gz')

    # reverse intermediates images for region template
    # rri = reverse region intermediates
    region_reverse_int_1 = os.path.join(registration_dir,'region_inverse_syn.nii.gz')
    region_reverse_int_2 = os.path.join(registration_dir, 'region_inverse_affine.nii.gz')
    region_reverse_int_3 = os.path.join(registration_dir, subj_name + '_region_segmentation.nii.gz')


    #transform labels
    orientation_transform = os.path.join(registration_dir, 'orientation_transform_')
    transform_1 = os.path.join(registration_dir,'rigid_transform_')
    transform_2 = os.path.join(registration_dir,'affine_transform_')
    transform_3 = os.path.join(registration_dir,'syn_transform_')
    transform_3_warp = os.path.join(transform_3 + '0Warp.nii.gz')
    transform_3_inv_warp = os.path.join(transform_3 + '0InverseWarp.nii.gz')
    
    # Full transform names
    orientation_transform_name = os.path.join(registration_dir, 'orientation_transform.mat')
    transform_1_name = os.path.join(registration_dir,'rigid_transform.mat')
    transform_2_name = os.path.join(registration_dir,'affine_transform.mat')
    transform_3_name = os.path.join(registration_dir,'syn_inverse_transform.nii.gz')
    transform_3_warp_name = os.path.join(transform_3 + 'Warp.nii.gz')
    transform_3_inv_warp_name = os.path.join(transform_3 + 'InverseWarp.nii.gz')



    #####################
    # Start of pipeline
    #####################kk
    
    print("\nRunning subject {} with GA {}".format(subj_name, GA))
    os.chdir(registration_dir) # files generated by pipeline will go in registarion folder
    
    if test_parameters:
        print("\n\tRunning registration with test parameters\n")
    #n4 Bias Correction
    if not os.path.isfile(bias_file) or repeat:
        print("\tRunning N4 Bias")
        n4Node = ants.N4BiasFieldCorrection()
        n4Node.inputs.input_image = subj_path
        n4Node.inputs.copy_header = True
        n4Node.inputs.dimension = 3
        n4Node.inputs.save_bias = False
        n4Node.inputs.output_image = bias_file
        n4Node.run()
    else:
        print("\tUsing old N4 Node")

    
    # bet node
    if  not os.path.isfile(brain_extracted_file) or repeat:
        print('\tRunning Brain Extraction')
        mask_node = fsl.ImageMaths()
        mask_node.inputs.in_file = bias_file
        mask_node.inputs.mask_file = mask_file
        mask_node.inputs.out_file = brain_extracted_file
        _ = mask_node.run()
    else:
        print("\tUsing old Brain Extraction")


    rf.wrapper_function(reorient_method, 
                        fixed=template, 
                        moving=brain_extracted_file, 
                        moving_out = oriented_bias_extracted,
                        moving_full = bias_file,
                        moving_full_out = oriented_bias,
                        save_dir = registration_dir, 
                        avail_cores = avail_cores, 
                        orient_iterations = orient_iterations, 
                        orientation_transform=orientation_transform, 
                        orientation_transform_name=orientation_transform_name)


    ############################################################################
    ## rigid, Affine, and Syn nodes

    #rigid Node
    if helper.files_missing(intermediate_1_file, transform_1_name) or repeat:
        print("\tRunning Rigid Registration")
        rigidNode = ants.Registration()
        rigidNode.inputs.fixed_image = template
        rigidNode.inputs.moving_image = oriented_bias_extracted
        rigidNode.inputs.metric = ['CC']
        rigidNode.inputs.metric_weight = [1.0]
        rigidNode.inputs.shrink_factors = [[3]]
        rigidNode.inputs.smoothing_sigmas = [[3]]
        rigidNode.inputs.transforms = ['Rigid']
        rigidNode.inputs.num_threads = avail_cores
        rigidNode.inputs.transform_parameters = [(0.25,)]
        rigidNode.inputs.number_of_iterations = [[iterations]]
        rigidNode.inputs.convergence_threshold = [1e-7]
        rigidNode.inputs.output_warped_image = intermediate_1_file
        rigidNode.inputs.verbose = False
        rigidNode.inputs.output_transform_prefix = transform_1
        rigidNode.run()
        
        helper.rename_transform(transform_1, transform_1_name)
    else:
        print("\tUsing old Rigid Registration")

    #affine Node
    if helper.files_missing(intermediate_2_file, transform_2_name) or repeat:
        print("\tRunning Affine Registration")
        affineNode = ants.Registration()
        affineNode.inputs.fixed_image = template
        affineNode.inputs.moving_image = intermediate_1_file
        affineNode.inputs.metric = ['CC']
        affineNode.inputs.metric_weight = [1.0]
        affineNode.inputs.shrink_factors = [[3]]
        affineNode.inputs.smoothing_sigmas = [[3]]
        affineNode.inputs.transforms = ['Affine']
        affineNode.inputs.num_threads = avail_cores
        affineNode.inputs.transform_parameters = [(0.25,)]
        affineNode.inputs.number_of_iterations = [[iterations]]
        affineNode.inputs.convergence_threshold = [1e-7]
        affineNode.inputs.output_warped_image = intermediate_2_file
        affineNode.inputs.verbose = False
        affineNode.inputs.output_transform_prefix = transform_2
        affineNode.run()
        
        helper.rename_transform(transform_2, transform_2_name)
    else:
        print("\tUsing old Affine Registration")

    #syn Node
    if helper.files_missing(intermediate_3_file, transform_3_warp_name, transform_3_inv_warp_name) or repeat:
        print("\tRunning Syn Registration")
        synNode = ants.Registration()
        synNode.inputs.fixed_image = template
        synNode.inputs.moving_image = intermediate_2_file
        synNode.inputs.metric = ['CC']
        synNode.inputs.metric_weight = [1.0]
        synNode.inputs.shrink_factors = [[3]]
        synNode.inputs.smoothing_sigmas = [[3]]
        synNode.inputs.transforms = ['SyN']
        synNode.inputs.num_threads = avail_cores
        synNode.inputs.transform_parameters = [(0.25,)]
        synNode.inputs.number_of_iterations = [[iterations]]
        synNode.inputs.convergence_threshold = [1e-7]
        synNode.inputs.output_warped_image = intermediate_3_file
        synNode.inputs.verbose = False
        synNode.inputs.output_transform_prefix = transform_3
        synNode.run()
        
        helper.rename_transform(transform_3_warp, transform_3_warp_name)
        helper.rename_transform(transform_3_inv_warp, transform_3_inv_warp_name)
    else:
        print("\tUsing old Syn Registration")

    ############################################################################
    ## Apply Transforms - tissue then regions

    ## Tissue    
    # syn
    if not os.path.isfile(tissue_reverse_int_1) or repeat:
        print("\tRunning Apply Tissue Transform: Syn")
        atSyn = ants.ApplyTransforms()
        atSyn.inputs.input_image = tissue_template
        atSyn.inputs.reference_image = oriented_bias_extracted
        atSyn.inputs.output_image = tissue_reverse_int_1
        atSyn.inputs.transforms = [transform_3_inv_warp_name]
        atSyn.inputs.interpolation = 'NearestNeighbor'
        atSyn.inputs.invert_transform_flags = [False] #syn outputs inverse 
        atSyn.run()
    else:
        print("\tUsing old Tissue Syn Transform")

    # affine
    if not os.path.isfile(tissue_reverse_int_2) or repeat:
        print("\tRunning Apply Tissue Transform: Affine")
        atAffine = ants.ApplyTransforms()
        atAffine.inputs.input_image = tissue_reverse_int_1
        atAffine.inputs.reference_image = oriented_bias_extracted
        atAffine.inputs.output_image = tissue_reverse_int_2
        atAffine.inputs.transforms = [transform_2_name]
        atAffine.inputs.interpolation = 'NearestNeighbor'
        atAffine.inputs.invert_transform_flags = [True]
        atAffine.run()
    else:
        print("\tUsing old Tissue Affine Transform")

    # rigid
    if not os.path.isfile(tissue_reverse_int_3) or repeat:
        print("\tRunning Apply Tissue Transform: Rigid")
        atRigid = ants.ApplyTransforms()
        atRigid.inputs.input_image = tissue_reverse_int_2
        atRigid.inputs.reference_image = oriented_bias_extracted
        atRigid.inputs.output_image = tissue_reverse_int_3
        atRigid.inputs.transforms = [transform_1_name]
        atRigid.inputs.interpolation = 'NearestNeighbor'
        atRigid.inputs.invert_transform_flags = [True]
        atRigid.run()
    else:
        print("\tUsing old Tissue Rigid Transform")


    ## Regions
    # syn
    if not os.path.isfile(region_reverse_int_1) or repeat:
        print("\tRunning Apply Regional Transform: Syn")
        atSyn = ants.ApplyTransforms()
        atSyn.inputs.input_image = region_template
        atSyn.inputs.reference_image = oriented_bias_extracted
        atSyn.inputs.output_image = region_reverse_int_1
        atSyn.inputs.transforms = [transform_3_inv_warp_name]
        atSyn.inputs.interpolation = 'NearestNeighbor'
        atSyn.inputs.invert_transform_flags = [False] #syn outputs inverse 
        atSyn.run()
    else:
        print("\tUsing old Regional Syn Transform")


    # affine
    if not os.path.isfile(region_reverse_int_2) or repeat:
        print("\tRunning Apply Regional Transform: Affine")
        atAffine = ants.ApplyTransforms()
        atAffine.inputs.input_image = region_reverse_int_1
        atAffine.inputs.reference_image = oriented_bias_extracted
        atAffine.inputs.output_image = region_reverse_int_2
        atAffine.inputs.transforms = [transform_2_name]
        atAffine.inputs.interpolation = 'NearestNeighbor'
        atAffine.inputs.invert_transform_flags = [True]
        atAffine.run()
    else:
        print("\tUsing old Regional Affine Transform")


    # rigid
    if not os.path.isfile(region_reverse_int_3) or repeat:
        print("\tRunning Apply Regional Transform: Rigid")
        atRigid = ants.ApplyTransforms()
        atRigid.inputs.input_image = region_reverse_int_2
        atRigid.inputs.reference_image = oriented_bias_extracted
        atRigid.inputs.output_image = region_reverse_int_3
        atRigid.inputs.transforms = [transform_1_name]
        atRigid.inputs.interpolation = 'NearestNeighbor'
        atRigid.inputs.invert_transform_flags = [True]
        atRigid.run()
    else:
        print("\tUsing old Regional Rigid Transform")

    
    ############################################################################
    # Move files to output directory    
    output_tissue_seg = os.path.join(output_dir, subj_name + '_tissue_segmentation.nii.gz')
    output_region_seg = os.path.join(output_dir, subj_name + '_region_segmentation.nii.gz')
    output_reoriented_bias_corrected = os.path.join(output_dir, subj_name + '_bias_corrected.nii.gz')
    output_reoriented_bias_corrected_bet = os.path.join(output_dir, subj_name + '_bet_bias_corrected.nii.gz')
    atlas_space_subject = os.path.join(output_dir, subj_name + '_GA_' + str(GA) + '_atlas_space.nii.gz') 

    # copy files to output folder 
    shutil.copy2(tissue_reverse_int_3, output_tissue_seg)
    shutil.copy2(region_reverse_int_3, output_region_seg)
    shutil.copy2(oriented_bias, output_reoriented_bias_corrected)
    shutil.copy2(oriented_bias_extracted, output_reoriented_bias_corrected_bet)
    shutil.copy2(intermediate_3_file, atlas_space_subject)


    ############################################################################
    # Generate QA images

    # Generate segmentation figure
    region_seg_fig = os.path.join(output_dir, subj_name + '_region_seg.png')
    tissue_seg_fig = os.path.join(output_dir, subj_name + '_tissue_seg.png')
    
    vt.view_segmentation(output_reoriented_bias_corrected, output_reoriented_bias_corrected_bet, output_region_seg,
        save_path = region_seg_fig, subj_deid = subj_name)
    
    vt.view_segmentation(output_reoriented_bias_corrected, output_reoriented_bias_corrected_bet, output_tissue_seg,
        save_path = tissue_seg_fig, subj_deid = subj_name)

    ############################################################################
    # Save volume results to output dir
    region_results = os.path.join(output_dir, 'Region_results.xlsx')
    tissue_results = os.path.join(output_dir, 'Tissue_results.xlsx')
    ev.extract_volume(output_region_seg, subj_name, save_path =  region_results)
    ev.extract_volume(output_tissue_seg, subj_name, save_path =  tissue_results)

    ############################################################################
    # Write the version and time for completion
    helper.write_version(output_dir)
    helper.write_time(registration_dir, 'Segmentation', start_time)

    if return_paths:
        return output_reoriented_bias_corrected, output_region_seg, output_tissue_seg


################################################################################
# Below functions are batched versions of the main registration function

def batch_run(df, path, dry_run=False, test_parameters=False, repeat = False):

    pre_drop_number = len(df)
    clean_df = df.dropna(axis = 0, how = 'any', inplace = False)
    post_drop_number = len(clean_df)

    df_all = df.merge(clean_df['subject_deid'], on = 'subject_deid', how = 'left', indicator = True)
    missing_df = df_all[df_all['_merge'] == 'left_only'].copy()
    missing_df.drop('_merge', axis = 1, inplace = True)
    
    if len(missing_df) > 0:
        print("Subjects missing information, will skip:\n")
        print("\t" + missing_df.to_string(index=False))
    print(f'\n\nRunning registration on {post_drop_number} subjects out of {pre_drop_number} possible subjects')

    subject_paths = []
    for index, s in clean_df.iterrows():
        try:
            if not dry_run:
                #print(f"Subject: {s['subject_deid']}, PMA: {s['pma']},recon_file: {s['recon_file']},mask_file: {s['mask_file']},test_parameters: {test_parameters}") 
                registration(str(s['subject_deid']), float(s['pma']),s['recon_file'],s['mask_file'],test_parameters=test_parameters, repeat=repeat)
                subject_paths.append(os.path.dirname(s['recon_file']))
        except Exception as e:
            print(f"Skipping subject {s['subject_deid']} due to error {e}")
            if not dry_run:
                subj_dir = os.path.dirname(s['recon_file'])
                helper.write_error(subj_dir, e)

    if not dry_run:
        tissue_summary_pdf = os.path.join(path, 'Tissue_segmentation_QA.pdf') 
        region_summary_pdf = os.path.join(path, 'Region_segmentation_QA.pdf') 
        vt.consolidate_result_images('tissue_seg.png', subject_paths, tissue_summary_pdf)
        vt.consolidate_result_images('region_seg.png', subject_paths, region_summary_pdf)

def batch_registration_csv(file_path, subject_label="subject_deid", ga_label="ga",
    recon_label = "recon", mask_label = "mask", dry_run = False, test_parameters=False, repeat=False):

    if not os.path.isfile(file_path):
        print('\n\tCSV/Excel file not found. Try again.\n')
        sys.exit()
    
    df = helper.load_excel_or_csv(os.path.abspath(file_path))  

    required_args = {
        'subject_deid':[subject_label, False], 
        'pma':[ga_label, False], 
        'recon_file':[recon_label, False], 
        'mask_file':[mask_label, False]
    }

    # Searches the columns in the loaded DF for the correct named columns either using default names or 
    # user supplied column names. 
    for key, (col_name, included) in required_args.items():
        required_args[key][0] = col_name.lower().replace(' ', '_')
        if required_args[key][0] in df.columns:
            required_args[key][1] = True

    # Checks if any required colunms are missing. If so, next step is to alert user and end the program. 
    incorrect_col_labels = []
    missing_column = False
    for key, (col_name, included) in required_args.items():
        if not included:
            incorrect_col_labels.append(col_name)
            missing_column = True

    if missing_column: #Missing required column, alert user.
        err_string ="\nColumn names in Excel/CSV don't match expected values. "
        err_string+="Please change column labels or specify column lables. " 
        err_string+=f"Incorrectly labeled columns are {', '.join(incorrect_col_labels)}.\n"
        print(err_string)
        sys.exit()

    rename_dict = {}
    for key, (col_name, included) in required_args.items():
        rename_dict[col_name] = key

    df.rename(rename_dict, axis=1, inplace = True)

    df['recon_file'] = [os.path.abspath(os.path.join('/data', x)) for x in df['recon_file']]
    df['mask_file'] = [os.path.abspath(os.path.join('/data', x)) for x in df['mask_file']]

    out_path = os.path.dirname(file_path)
    batch_run(df, out_path, dry_run = dry_run, test_parameters = test_parameters, repeat = repeat)

def batch_registration_dir(path, ga_excel, search_term = None, exclude_term = None, 
                            search_dir = None, exclude_dir = None, dry_run = False, test_parameters=False, repeat=False):
    path = os.path.abspath(path)
    skip_dirs = ['.ipynb_checkpoints'] # Common directories that need skipped
    subj_dirs = [os.path.join(path, x) for x in os.listdir(path) if os.path.isdir(os.path.join(path, x)) and x not in skip_dirs]
    type_dict =  {0: str, 1: float}
    ga_df = helper.load_excel_or_csv(ga_excel, type_dict = type_dict, colnames=['deid', 'ga'])

    df = pd.DataFrame(columns = ['subject_deid', 'pma', 'recon_file', 'mask_file'])
    
    for subj_dir in subj_dirs:
        recon_file, mask_file = helper.find_reconstruction_files(subj_dir, search_term = search_term, exclude_term = exclude_term, 
                                                    search_dir = search_dir, exclude_dir = exclude_dir)
        subj_id = os.path.basename(subj_dir)
        subj_pma = helper.get_ga(subj_id, ga_df)

        ser = pd.Series({'subject_deid':subj_id, 'pma':subj_pma, 'recon_file':recon_file, 'mask_file':mask_file}) 
        df = pd.concat([df, ser.to_frame().T], axis = 0)

    batch_run(df, path, dry_run = dry_run, test_parameters = test_parameters, repeat = repeat)








