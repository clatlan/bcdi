# -*- coding: utf-8 -*-

# BCDI: tools for pre(post)-processing Bragg coherent X-ray diffraction imaging data
#   (c) 07/2017-06/2019 : CNRS UMR 7344 IM2NP
#   (c) 07/2019-present : DESY PHOTON SCIENCE
#       authors:
#         Jerome Carnis, carnis_jerome@yahoo.fr

import json
import matplotlib.pyplot as plt
from numbers import Real
import numpy as np
import pathlib
from scipy.interpolate import interp1d
import sys
import tkinter as tk
from tkinter import filedialog
sys.path.append('D:/myscripts/bcdi/')
import bcdi.graph.graph_utils as gu
import bcdi.utils.utilities as util
import bcdi.utils.validation as valid

helptext = """
This script allow to plot and save linecuts through a 2D or 3D object in function of a modulus threshold 
defining the object from the background. Must be given as input: the voxel size (possibly different in all directions), 
the direction of the cuts and a list of points where to apply the cut along this direction.   
"""

datadir = "D:/data/P10_2nd_test_isosurface_Dec2020/data_nanolab/dataset_1_newpsf/result/"  # data folder
savedir = "D:/data/P10_2nd_test_isosurface_Dec2020/data_nanolab/dataset_1_newpsf/result/linecuts/"
# results will be saved here, if None it will default to datadir
threshold = np.linspace(0, 1.0, num=20)
# number or list of numbers between 0 and 1, modulus threshold defining the normalized object from the background
direction = (0, 1, 0)  # tuple of 2 or 3 numbers (2 for 2D object, 3 for 3D) defining the direction of the cut
# in the orthonormal reference frame is given by the array axes. It will be corrected for anisotropic voxel sizes.
points = {(25, 37, 23), (25, 37, 24), (25, 37, 25), (25, 37, 26),
          (26, 37, 23), (26, 37, 24), (26, 37, 25), (26, 37, 26),
          (27, 37, 24), (27, 37, 25)}
# list/tuple/set of 2 or 3 indices (2 for 2D object, 3 for 3D) corresponding to the points where
# the cut alond direction should be performed. The reference frame is given by the array axes.
voxel_size = 5  # positive real number  or tuple of 2 or 3 positive real number (2 for 2D object, 3 for 3D)
width_lines = (98, 100, 102)  # list of vertical lines that will appear in the plot width vs threshold
styles = {0: (0, (2, 6)), 1: 'dashed', 2: (0, (2, 6))}  # line style for the width_lines, 1 for each line
debug = False  # True to print the output dictionary and plot the legend
comment = ''  # string to add to the filename when saving
tick_length = 10  # in plots
tick_width = 2  # in plots

##################################
# end of user-defined parameters #
##################################

###############################
# list of colors for the plot #
###############################
colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
markers = ('.', 'v', '^', '<', '>')

#################
# load the data #
#################
plt.ion()
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(initialdir=datadir,
                                       filetypes=[("NPZ", "*.npz"), ("NPY", "*.npy"),
                                                  ("CXI", "*.cxi"), ("HDF5", "*.h5")])

obj, _ = util.load_file(file_path)
ndim = obj.ndim

#########################
# check some parameters #
#########################
if ndim not in {2, 3}:
    raise ValueError(f'Number of dimensions = {ndim}, expected 2 or 3')

valid.valid_container(direction, container_types=(list, tuple, np.ndarray), length=ndim, item_types=Real,
                      name='line_profile')

valid.valid_container(points, container_types=(list, tuple, set), min_length=1, name='line_profile')
for point in points:
    valid.valid_container(point, container_types=(list, tuple, np.ndarray), length=ndim, item_types=Real,
                          min_included=0, name='line_profile')

if isinstance(voxel_size, Real):
    voxel_size = (voxel_size,) * ndim
valid.valid_container(voxel_size, container_types=(list, tuple, np.ndarray), length=ndim, item_types=Real,
                      min_excluded=0, name='line_profile')

savedir = savedir or datadir
pathlib.Path(savedir).mkdir(parents=True, exist_ok=True)

if isinstance(threshold, Real):
    threshold = (threshold,)
valid.valid_container(threshold, container_types=(list, tuple, np.ndarray), item_types=Real,
                      min_included=0, max_included=1, name='line_profile')

if isinstance(width_lines, Real):
    width_lines = (width_lines,)
valid.valid_container(width_lines, container_types=(list, tuple, np.ndarray), item_types=Real,
                      min_excluded=0, name='line_profile')

if not isinstance(styles, dict):
    raise TypeError('styles should be a dictionnary')
if len(styles) != len(width_lines):
    raise ValueError('styles should have as many entries as the number of width_lines')

comment = f'_direction{direction[0]}_{direction[1]}_{direction[2]}_{comment}'

#########################
# normalize the modulus #
#########################
obj = abs(obj) / abs(obj).max()  # normalize the modulus to 1
obj[np.isnan(obj)] = 0  # remove nans
if ndim == 2:
    gu.imshow_plot(array=obj, plot_colorbar=True, reciprocal_space=False, is_orthogonal=True)
else:
    gu.multislices_plot(array=obj, sum_frames=False, plot_colorbar=True, reciprocal_space=False, is_orthogonal=True,
                        slice_position=(25, 37, 25))

#####################################
# create the linecut for each point #
#####################################
result = dict()
for point in points:
    # get the distances and the modulus values along the linecut
    distance, cut = util.linecut(array=obj, point=point, direction=direction, voxel_size=voxel_size)
    # store the result in a dictionary (cuts can have different lengths depending on the direction)
    result[f'voxel {point}'] = {'distance': distance, 'cut': cut}

######################
#  plot the linecuts #
######################
fig = plt.figure(figsize=(12, 9))
ax = plt.subplot(111)
plot_nb = 0
for key, value in result.items():
    # value is a dictionary {'distance': 1D array, 'cut': 1D array}
    line, = ax.plot(value['distance'], value['cut'], color=colors[plot_nb % len(colors)],
                    marker=markers[(plot_nb // len(colors)) % len(markers)], fillstyle='none', markersize=10,
                    linestyle='-', linewidth=1)
    line.set_label(f'cut through {key}')
    plot_nb += 1

ax.tick_params(labelbottom=False, labelleft=False, direction='out', length=tick_length, width=tick_width)
ax.spines['right'].set_linewidth(tick_width)
ax.spines['left'].set_linewidth(tick_width)
ax.spines['top'].set_linewidth(tick_width)
ax.spines['bottom'].set_linewidth(tick_width)
fig.savefig(savedir + 'cut' + comment + '.png')

ax.set_xlabel('width (nm)', fontsize=20)
ax.set_ylabel('modulus', fontsize=20)
if debug:
    ax.legend(fontsize=14)
ax.tick_params(labelbottom=True, labelleft=True, axis='both', which='major', labelsize=16)
fig.savefig(savedir + 'cut' + comment + '_labels.png')

#################################################################################
# calculate the evolution of the width of the object depending on the threshold #
#################################################################################
for key, value in result.items():
    fit = interp1d(value['distance'], value['cut'])
    dist_interp = np.linspace(value['distance'].min(), value['distance'].max(), num=10000)
    cut_interp = fit(dist_interp)
    width = np.empty(len(threshold))

    # calculate the function width vs threshold
    for idx, thres in enumerate(threshold):
        # calculate the distances where the modulus is equal to threshold
        crossings = np.argwhere(cut_interp > thres)
        if len(crossings) > 1:
            width[idx] = dist_interp[crossings.max()] - dist_interp[crossings.min()]
        else:
            width[idx] = 0

    # fit the function width vs threshold and estimate where it crosses the expected widths
    fit = interp1d(width, threshold)  # width vs threshold is monotonic (decreasing with increasing threshold)
    fit_thresh = np.empty(len(width_lines))
    for idx, val in enumerate(width_lines):
        fit_thresh[idx] = fit(val)
    # update the dictionary value
    value['threshold'] = threshold
    value['width'] = width
    value['fitted_threshold'] = fit_thresh

#################################################
# calculate statistics on the fitted thresholds #
#################################################
count = 0
tmp_thres = np.zeros((len(width_lines), len(points)))
for key, value in result.items():
    # iterating over points, value is a dictionary
    for idx in range(len(width_lines)):
        tmp_thres[idx, count] = value['fitted_threshold'][idx]
    count += 1
mean_thres = np.mean(tmp_thres, axis=1)
std_thres = np.std(tmp_thres, axis=1)

# update the dictionary
result['direction'] = direction
result['expected_width'] = width_lines
result['mean_thres'] = np.round(mean_thres, decimals=3)
result['std_thres'] = np.round(std_thres, decimals=3)

#################################
#  plot the widths vs threshold #
#################################
fig = plt.figure(figsize=(12, 9))
ax = plt.subplot(111)
plot_nb = 0
for key, value in result.items():
    if isinstance(value, dict):  # iterating over points, value is a dictionary
        line, = ax.plot(value['threshold'], value['width'], color=colors[plot_nb % len(colors)],
                        marker=markers[(plot_nb // len(colors)) % len(markers)], fillstyle='none', markersize=10,
                        linestyle='-', linewidth=1)
        line.set_label(f'cut through {key}')
        plot_nb += 1

ax.tick_params(labelbottom=False, labelleft=False, direction='out', length=tick_length, width=tick_width)
ax.spines['right'].set_linewidth(tick_width)
ax.spines['left'].set_linewidth(tick_width)
ax.spines['top'].set_linewidth(tick_width)
ax.spines['bottom'].set_linewidth(tick_width)
for index, hline in enumerate(width_lines):
    ax.axhline(y=hline, linestyle=styles[index], color='k', linewidth=1.5)
fig.savefig(savedir + 'width_vs_threshold' + comment + '.png')
ymin, ymax = ax.get_ylim()

ax.set_xlim(left=0.335, right=0.565)
ax.set_ylim(bottom=96, top=104)
fig.savefig(savedir + 'width_vs_threshold' + comment + '_zoom.png')
ax.tick_params(labelbottom=True, labelleft=True, axis='both', which='major', labelsize=16)
plt.pause(0.5)
fig.savefig(savedir + 'width_vs_threshold' + comment + '_zoom_labels.png')

ax.set_xlim(left=0, right=1)
ax.set_ylim(bottom=ymin, top=ymax)
ax.set_xlabel('threshold', fontsize=20)
ax.set_ylabel('width (nm)', fontsize=20)
ax.set_title(f"Width vs threshold in the direction {result['direction']}\n", fontsize=20)
if debug:
    ax.legend(fontsize=14)
fig.text(0.15, 0.30, f"expected widths: {result['expected_width']}", size=16)
fig.text(0.15, 0.25, f"fitted thresholds: {result['mean_thres']}", size=16)
fig.text(0.15, 0.20, f"stds: {result['std_thres']}", size=16)
ax.tick_params(labelbottom=True, labelleft=True, axis='both', which='major', labelsize=16)
plt.pause(0.5)
fig.savefig(savedir + 'width_vs_threshold' + comment + '_labels.png')

###################
# save the result #
###################
if debug:
    print('output dictionary:\n', json.dumps(result, cls=util.CustomEncoder, indent=4))

with open(savedir+'cut' + comment + '.json', 'w', encoding='utf-8') as file:
    json.dump(result, file, cls=util.CustomEncoder, ensure_ascii=False, indent=4)

plt.ioff()
plt.show()
