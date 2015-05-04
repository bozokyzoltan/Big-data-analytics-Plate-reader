#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by Zoltan Bozoky on 2015.04.10.
Under GPL licence.

Purpose:
========
Generate plots

"""

import numpy as np
import os
import math
from pylab import plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt


def group_similar(names):
    """
    """
    names.sort()
    number_of_tags_in_name = len(names[0].split(';'))
    name_group = [[] for _ in xrange(number_of_tags_in_name)]
    for name in names:
        tag = name.split(';')
        for i in xrange(len(tag)):
            if tag[i] not in name_group[i]:
                name_group[i].append(tag[i])
    return name_group
### ======================================================================== ###

def get_index(group, name):
    """
    """
    color_index = 0
    shade_index = 0
    pattern_index = 0
    if len(group) > 0:
        color_index = group[0].index(name.split(';')[0])
    if len(group) > 1:
        shade_index = group[1].index(name.split(';')[1])
    if len(group) > 2:
        pattern_index = group[2].index(name.split(';')[2])
    #
    return color_index, shade_index, pattern_index
### ======================================================================== ###

def color_shade_pattern(color_index, shade_index, pattern_index, group):
    """
    """
    colors = ((0.8477, 0.8477, 0.8477),
              (0.7969, 0.9180, 0.7695),
              (0.5000, 0.6914, 0.8242),
              (0.9883, 0.7031, 0.3828),
              (0.9805, 0.5000, 0.4453))

    color = colors[color_index % 5]

    if len(group) > 1:
        color = [0.5*c + 0.5 * (float(shade_index)/len(group[1]))  for c in color]

    pattern = [' ', '/' , 'o', 'x', '\\' , '|' , '-' , '+' ,  'O', '.', '*'][pattern_index]
    #
    return color, pattern
### ======================================================================== ###
def set_plot_color(index):
    """
    """
    colors = ((0.8906, 0.1016, 0.1094),
              (0.2148, 0.4922, 0.7188),
              (0.3308, 0.6836, 0.2891),
              (0.5938, 0.3047, 0.6367),
              (1.0000, 0.4980, 0.0000),
              (1.0000, 1.0000, 0.2000),
              (0.6510, 0.3373, 0.1569),
              (0.9686, 0.5059, 0.7490),
              (0.6000, 0.6000, 0.6000))
    #
    return colors[index % len(colors)]

### ======================================================================== ###

def plot_response(data, plate_name, save_folder = 'Figures/'):
    """
    """
    if not os.path.isdir(save_folder):
        os.makedirs(save_folder)

    for block in data:
        #
        group = group_similar(data[block].keys())
        names = data[block].keys()
        names.sort()
        #
        plt.figure(figsize=(16, 4 + len(names)/8), dpi=300)
        #
        for i, name in enumerate(names):
            a, b, c = get_index(group, name)
            color, pattern = color_shade_pattern(a, b, c, group)
            mean = data[block][name]['mean'][0]
            std = data[block][name]['std'][0]

            plt.barh([i], [mean], height=1.0, color=color, hatch=pattern)
            plt.errorbar([mean], [i+0.5], xerr=[std], ecolor = [0,0,0], linestyle = '')

        plt.yticks([i+0.5 for i in xrange(len(names))], names, size = 8)
        plt.title(plate_name)
        plt.ylim(0, len(names))
        plt.xlabel('change')
        plt.tight_layout()

        plt.savefig(save_folder + 'response_' + str(block + 1))
    #
    return None
### ======================================================================== ###

def plot_start_slopes(data, plate_name, save_folder = 'Figures/'):
    """
    """
    if not os.path.isdir(save_folder):
        os.makedirs(save_folder)

    for block in data:
        #
        group = group_similar(data[block].keys())
        names = data[block].keys()
        names.sort()
        #
        plt.figure(figsize=(16, 4 + len(names)/8), dpi=300)
        #
        for i, name in enumerate(names):
            a, b, c = get_index(group, name)
            color, pattern = color_shade_pattern(a, b, c, group)
            mean = data[block][name]['mean'][0]
            std = data[block][name]['std'][0]

            plt.barh([i], [mean], height=1.0, color=color, hatch=pattern)
            plt.errorbar([mean], [i+0.5], xerr=[std], ecolor = [0,0,0], linestyle = '')

        plt.yticks([i+0.5 for i in xrange(len(names))], names, size = 8)
        plt.title(plate_name)
        plt.ylim(0, len(names))
        plt.xlabel('change')
        plt.tight_layout()

        plt.savefig(save_folder + 'slopes_' + str(block + 1))
    #
    return None
### ======================================================================== ###

def plot_mean_curve(time_data, data, additions, plate_name, save_folder = r'Figures/'):
    """
    """
    if not os.path.isdir(save_folder):
        os.makedirs(save_folder)

    for block in data:
        #
        group = group_similar(data[block].keys())
        names = data[block].keys()
        names.sort()
        # -----------------
        # Plot each group individualy
        # -----------------
        data_per_inch = 5.0

        y_len = int(math.sqrt(len(names)))
        x_len = int(np.ceil(len(names) / float(y_len)))

        fig, axs = plt.subplots(y_len, x_len, sharex=True, sharey=True,
                                figsize=(x_len*data_per_inch,y_len*data_per_inch), dpi=300)

        y_min = data[block][names[0]]['original_data'].min()
        y_max = data[block][names[0]]['original_data'].max()

        for i, name in enumerate(names):
            if data[block][name]['original_data'].min() < y_min:
                y_min = data[block][name]['original_data'].min()
            if data[block][name]['original_data'].max() > y_max:
                y_max = data[block][name]['original_data'].max()
        y_range = y_max - y_min
                
        for i, name in enumerate(names):
            px = i / x_len
            py = i % x_len
            if y_len > 1:
                position = (px, py)
            else:
                position = py

            time = time_data[block][name]
            mean = np.array(data[block][name]['mean'])
            std = np.array(data[block][name]['std'])
            all_curve = data[block][name]['original_data']

            axs[position].plot(time, [1.0 for _ in time], 'k-')
            for curve in all_curve:
                axs[position].plot(time, curve, color = [0.7 for _ in xrange(3)])
            axs[position].plot(time, mean, color = [0.2 for _ in xrange(3)], linewidth = 2.5, label = name)
            axs[position].plot(time, mean+std, 'k--', color = [0.2 for _ in xrange(3)], linewidth = 2.5)
            axs[position].plot(time, mean-std, 'k--', color = [0.2 for _ in xrange(3)], linewidth = 2.5)

            for addition in additions[:block+1]:
                axs[position].plot([addition[0] for _ in xrange(2)], [0.0,3.0], 'k-')
                axs[position].text(addition[0], 0.98, addition[1], rotation=270)
            
            if i % x_len == 0:
                axs[position].set_ylabel('Normalized fluorescence', size = 14)
            if i / x_len == y_len - 1:
                axs[position].set_xlabel('Time / sec', size = 14)
                
            axs[position].set_xlim(0, time[-1])

            for j, text in enumerate(name.split(';')):
                axs[position].text(10, y_max - y_range*j*0.1, text, size = 14)

        axs[position].set_ylim(y_min-y_range*0.1, y_max+y_range*0.1)
        
#        plt.suptitle(plate_name)
        plt.subplots_adjust(wspace = 0.01, hspace = 0.01)
        plt.tight_layout()
        plt.savefig(save_folder + 'block_' + str(block + 1))
    #
    return None
### ======================================================================== ###

def plot_baseline(data, plate_name, save_folder = r'Figures/'):
    """
    """
    colors = ((0.2, 0.2, 0.2),
              (0.5, 0.5, 0.5),
              (0.7, 0.7, 0.7),
              (0.3, 0.3, 0.3))

    names = data.keys()
    names.sort()
    fig, axs = plt.subplots(figsize=(8,3))
    for index, name in enumerate(names):
        for value in data[name]['original_data']:
            plot_color = colors[index % len(colors)]
            
            if abs(value - data[name]['mean'][0]) > data[name]['std'][0] * 2.0:
                axs.plot([value], [index], 'ko', markerfacecolor = [1,1,1])
            else:
                axs.plot([value], [index], 'ko', color = plot_color)

        axs.plot([data[name]['mean'][0] for _ in xrange(2)],
                 [index-0.25, index+0.25],
                  'k-')
        axs.plot([data[name]['mean'][0] - data[name]['std'][0] for _ in xrange(2)],
                 [index-0.25, index+0.25],
                 'k--')
        axs.plot([data[name]['mean'][0] + data[name]['std'][0] for _ in xrange(2)],
                 [index-0.25, index+0.25],
                 'k--')

    plt.yticks([i for i in xrange(len(names))], names, size = 10)
    plt.title(plate_name)
    plt.ylim(-0.5,len(names)-0.5)
    plt.xlabel('Fluorescent intensity')
    plt.tight_layout()

    save_filename = save_folder + 'baseline_average'

    pdf = PdfPages(save_filename.split('.')[0] + '.pdf')
    pdf.savefig(fig)
    pdf.close()

    plt.savefig(save_filename)
    #
    return None
### ======================================================================== ###

