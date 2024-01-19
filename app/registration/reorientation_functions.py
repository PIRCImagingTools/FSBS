import os, sys
import nipype.interfaces.ants as ants
import nipype.interfaces.fsl as fsl
from utils import helper_functions as helper


def tissue_extraction(input_file, template_file, save_dir):
    # fsl fast node
    # extracts bet'd image and template image for alignment
    bet_pve0 = os.path.join(save_dir, 'bet_pve_0.nii.gz')
    temp_pve0 = os.path.join(save_dir, 'template_pve_0.nii.gz')
    if not os.path.isfile(bet_pve0):
        print('\tRunning FSL Fast')
        fast = fsl.FAST()
        fast.inputs.in_files = input_file
        fast.inputs.out_basename = 'bet'
        fast.inputs.number_classes = 4
        fast.inputs.img_type = 2
        fast.run()

        # re-run fast using the template file
        fast.inputs.in_files = template_file
        fast.inputs.out_basename = 'template'
        fast.run()

    return bet_pve0, temp_pve0


def binarize_nii_file(nii_file, save_dir, file_save_prefix):

    bin_mask = os.path.join(save_dir, f'{file_save_prefix}_bin_mask.nii.gz')

    bn = fsl.UnaryMaths()
    bn.inputs.in_file = nii_file
    bn.inputs.operation = 'bin'
    bn.inputs.out_file = bin_mask
    bn.run()

    return bin_mask


def run_rigid_registration(fixed, moving, avail_cores, orient_iterations, orientation_transform, orientation_transform_name):
    rigidNode = ants.Registration()
    rigidNode.inputs.fixed_image = fixed
    rigidNode.inputs.moving_image = moving
    rigidNode.inputs.metric = ['CC']
    rigidNode.inputs.metric_weight = [1.0]
    rigidNode.inputs.shrink_factors = [[3]]
    rigidNode.inputs.smoothing_sigmas = [[5]]
    rigidNode.inputs.transforms = ['Rigid']
    rigidNode.inputs.num_threads = avail_cores
    rigidNode.inputs.transform_parameters = [(0.25,)]
    rigidNode.inputs.number_of_iterations = [[orient_iterations]]
    rigidNode.inputs.convergence_threshold = [1e-5]
    rigidNode.inputs.output_warped_image = False
    rigidNode.inputs.verbose = False
    rigidNode.inputs.output_transform_prefix = orientation_transform
    rigidNode.run()

    helper.rename_transform(orientation_transform, orientation_transform_name)
    return orientation_transform_name


def apply_orientation(moving_file, fixed_file, transform_file, out_file):

    atRigid = ants.ApplyTransforms()
    atRigid.inputs.input_image = moving_file
    atRigid.inputs.reference_image = fixed_file
    atRigid.inputs.output_image = out_file
    atRigid.inputs.transforms = [transform_file]
    atRigid.inputs.interpolation = 'NearestNeighbor'
    atRigid.inputs.invert_transform_flags = [True]
    atRigid.run()



def wrapper_function(method, fixed, moving, moving_out, moving_full, moving_full_out, 
                    save_dir, avail_cores, orient_iterations, 
                    orientation_transform, orientation_transform_name):

    if not os.path.isfile(moving_full) or not os.path.isfile(moving_full_out):
        print("\tRunning Orientation Registration")
        if method == 'binary':
            fixed_orientation_file = binarize_nii_file(nii_file=fixed, save_dir = save_dir, file_save_prefix='template')
            moving_orientation_file = binarize_nii_file(nii_file=moving, save_dir = save_dir, file_save_prefix="subject")
        elif method == 'tissue_class':
            moving_orientation_file, fixed_orientation_file = tissue_extraction(moving, fixed, save_dir)

        # Takes whichever moving and fixed files have been determined above and runs the orientation step
        # Orient transform is then used to transform the bias corrected and the bet_bias corrected input files
        # these files then go through the remainder of the pipeline
        orient_transform_file = run_rigid_registration(fixed_orientation_file, moving_orientation_file, 
                                                        avail_cores, orient_iterations, 
                                                        orientation_transform, orientation_transform_name)

        apply_orientation(moving, fixed, orient_transform_file, moving_out)
        apply_orientation(moving_full, fixed, orient_transform_file, moving_full_out)
    else:
        print("\tUsing old Rigid Registration")
