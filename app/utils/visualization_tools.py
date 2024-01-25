import SimpleITK as sitk
import numpy as np
import os, sys, re
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib as mpl
import matplotlib.image as mpimg
import PIL.Image
import argparse as ap

def return_center(arr):
    centers = []
    arr = (arr > 0).astype(int)
    x = arr.sum(axis = 1).sum(axis = 1).tolist() #x
    y = arr.sum(axis = 0).sum(axis = 1).tolist() #y
    z = arr.sum(axis = 0).sum(axis = 0).tolist() #z
    for i in [x, y, z]:
        max_val = max(i)
        ind = i.index(max_val)
        centers.append(ind)
        
    return centers


def pad_arr(arr, kernel, val = 1):
    ax, ay, az = arr.shape
    kx = kernel.shape[0]
    pad_size = int(kx-1)
    side_pad = int(pad_size/2)
    
    new_arr = np.full((ax + pad_size, ay + pad_size, az + pad_size), val)
    new_arr[side_pad:-side_pad, side_pad:-side_pad, side_pad:-side_pad] = arr[:,:,:]
    return new_arr


def inflate_arr(arr, shape = None, fill_array = None, fill=0.0, other_arr = None):
    ashape = arr.shape
    if shape is None:
        shape = fill_array.shape
    else:
        shape = tuple(shape)
    if len(ashape) != len(shape):
        raise Exception("Input array  and output array size have different number of dimensions")
    for a, s in zip(ashape, shape):
        if a > s:
            raise Exception("Input array size is larger than desired output shape")

    if fill_array is None:
        new_arr = np.full(shape, fill).astype(float)
    else:
        new_arr = fill_array.astype(float)
    
    start = [round((x-y)/2) for x, y in zip(shape, ashape)]
    end = [x+y for x, y in zip(start, ashape)]
    new_arr[start[0]:end[0], start[1]:end[1], start[2]:end[2]] = arr[:,:,:]
    if other_arr is None:
        return new_arr
    else:
        res_list = []
        res_list.append(new_arr)
        for oarr in other_arr:
            if fill_array is None:
                temp_arr = np.full(shape, fill).astype(float)
            else:
                temp_arr = fill_array.astype(float)

            temp_arr[start[0]:end[0], start[1]:end[1], start[2]:end[2]] = oarr[:,:,:]
            res_list.append(temp_arr)
        return res_list

def pad_to_box(arr, *masks):
    shape = arr.shape
    ms = max(shape)
    new_shape = (ms, ms, ms)

    new_arr = inflate_arr(arr, shape = (new_shape))
    other_masks = []
    for m in masks:
        new_mask = inflate_arr(m, shape = (new_shape))
        other_masks.append(new_mask)
    return (new_arr, *other_masks)


def crop_to_segmentation(mask_arr, *img_arrs, dilate_percent = 1.2):
    x_arr = np.nonzero(mask_arr.sum(axis=2).sum(axis=1))[0]
    y_arr = np.nonzero(mask_arr.sum(axis=2).sum(axis=0))[0]
    z_arr = np.nonzero(mask_arr.sum(axis=0).sum(axis=0))[0]
    mask_shape = mask_arr.shape
    bounds = [(x_arr[0], x_arr[-1]), (y_arr[0], y_arr[-1]), (z_arr[0], z_arr[-1])]

    crop_box = []

    for b, ms in zip(bounds, mask_shape):
        # b are the bounds from above
        # ms are the mask shape from above
        dim_span = b[1] - b[0] 
        new_dim_span = dim_span * dilate_percent
        diff = round((new_dim_span - dim_span)/2)
        low = b[0] - diff
        high = b[1] + diff
        low = max(low, 0)
        high = min(high, ms)

        crop_box.append(low)
        crop_box.append(high)

    new_mask_arr = mask_arr[crop_box[0]:crop_box[1], crop_box[2]:crop_box[3], crop_box[4]:crop_box[5]]
    res = []
    for img_arr in img_arrs: 
        new_img_arr = img_arr[crop_box[0]:crop_box[1], crop_box[2]:crop_box[3], crop_box[4]:crop_box[5]]
        res.append(new_img_arr)
    
    return (new_mask_arr, *res)



def get_ijk_slices(arr, centers):
    i = arr[centers[0],:,:]
    j = arr[:,centers[1],:]
    k = arr[:,:,centers[2]]
    return i,j,k


def check_path_and_load_array(file_path):
    abs_path = os.path.abspath(file_path)
    img = sitk.ReadImage(abs_path, imageIO='NiftiImageIO')
    return sitk.GetArrayFromImage(img)
    

def get_color_dict():
    atlas_dir = '/app/CRL_Fetal_Brain_Atlas_2017'
    lf = os.path.join(atlas_dir, 'labelkey.txt')
    with open(lf, 'r') as f:
        data = f.read().splitlines()

    p = re.compile('^#.*')
    opacity = 0
    color_dict = {}
    for d in data:
        m = p.search(d)
        if not m:
            index = int(d[0:5])
            red = int(d[8:11])
            green = int(d[13:16])
            blue = int(d[18:21])
            color_dict[index] = (red, green, blue, opacity)
            opacity = 1
            
    return color_dict


def convert_to_4d_color(arr, color_dict):
    x,y = arr.shape
    new_arr = np.zeros((x,y,4))
    a = 1
    for (x,y), val in np.ndenumerate(arr):
        val = int(val)
        r,g,b,a = color_dict[val]
        new_arr[x,y,:] = r,g,b,a
    new_arr[:,:,:3] = new_arr[:,:,:3]/256
    return new_arr

        
def view_segmentation(img_file, mask_file, seg_file, subj_deid = None, show = False, save_path = None):   
    img_arr = check_path_and_load_array(img_file)
    mask_arr = check_path_and_load_array(mask_file)
    mask_arr = (mask_arr > 0).astype(int)
    seg_arr = check_path_and_load_array(seg_file)
    
    seg_arr = np.flip(seg_arr, axis = 0)
    mask_arr = np.flip(mask_arr, axis = 0)
    img_arr = np.flip(img_arr, axis = 0)

    seg_arr, img_arr, mask_arr = crop_to_segmentation(seg_arr, img_arr, mask_arr)
    img_arr, seg_arr, mask_arr = pad_to_box(img_arr, seg_arr, mask_arr)
    
    gridspec_kws = dict(width_ratios = [0.33, 0.33, 0.33], height_ratios = [0.33, 0.33, 0.33], 
                        wspace = 0.05, hspace = 0.05)
    fig, axes = plt.subplots(3,3, figsize = (4,4), facecolor = 'white', dpi = 200, gridspec_kw = gridspec_kws)

    centers = return_center(seg_arr)
    img_all = get_ijk_slices(img_arr, centers)
    mask_all = get_ijk_slices(mask_arr, centers)
    seg_all = get_ijk_slices(seg_arr, centers)
    col_names = ['Axial', 'Coronal', 'Sagittal']
    
    color_dict = get_color_dict()
    
    for ax_row in axes:
        for ax in ax_row:
            ax.axis('off')
    
    for ax, img, col_name in zip(axes[0,:], img_all, col_names):
        ax.set_title(col_name, fontweight = 'bold', fontsize = 8)
        ax.imshow(img, cmap = 'gray')
    
    for ax, img, mask in zip(axes[1,:], img_all, mask_all):
        ax.imshow(img, cmap = 'gray')
        mask_rgb = convert_to_4d_color(mask, color_dict)
        ax.imshow(mask_rgb, alpha = 0.3)
    
    for ax, img, seg in zip(axes[2,:], img_all, seg_all):
        ax.imshow(img, cmap = 'gray')
        seg_rgb = convert_to_4d_color(seg, color_dict)
        ax.imshow(seg_rgb, alpha = 0.3)
        
    if subj_deid is not None:
        fig.suptitle(f'DEID: {subj_deid}', fontweight = 'bold', fontsize = 8)
    
    plt.axis('off')
    if save_path is not None:
        plt.savefig(save_path, dpi = 300, bbox_inches = 'tight')
    
    if show:
        plt.show()
    else:
        plt.close()

def convert_result_images_to_pdf(img_paths, save_path, output_directory = None):
    imgs = []
    for img in img_paths:
        im = PIL.Image.open(img).convert("RGB")
        imgs.append(im)
    
    if output_directory:
        save_path = os.path.join(output_directory, os.path.basename(save_path))

    imgs[0].save(save_path, save_all = True, append_images = imgs[1:])

def consolidate_result_images(search_string, search_paths, save_path, output_directory = None):
    img_paths = []
    for path in search_paths: 
        for root, dirs, files in os.walk(path):
            for f in files:
                if search_string in f:
                    img_paths.append(os.path.join(root, f))
    
    img_paths.sort(key = lambda x: os.path.basename(x))

    convert_result_images_to_pdf(img_paths, save_path, output_directory)


if __name__ == "__main__":


    parser = ap.ArgumentParser(
        prog = 'visualization_tools.py',
        formatter_class = ap.ArgumentDefaultsHelpFormatter,
        description = 'Tools helpful for visualization of segmentation results.'
    )

    parser.add_argument('-sd', '--search_directories', help='Absolute path to direcotry or directories to search within.', required=True, nargs='+')
    parser.add_argument('-ss', '--search_string', help = 'String which must be in the file in order to add to pdf output.', required=True)
    parser.add_argument('-sp', '--save_path', help = 'Absolute path with filename of how the resulting pdf should be saved. If output_directory is specified, that option will override and only file name is required.', required=True)
    parser.add_argument('-od', '--output_directory', help = 'Optional directory to save file to instead of save_path.', default = None)

    if len(sys.argv) == 1: #case when no arguments are provided, goes to help
        parser.print_help()
    else:
        args = parser.parse_args()
        consolidate_result_images(
                args.search_directories,
                args.search_string, 
                args.save_path, 
                output_directory = args.output_directory)