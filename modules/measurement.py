#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by Zoltan Bozoky on 2015.04.09.
Under GPL licence.

Purpose:
========
Handle a plate reader measument file

"""

import numpy as np
import os
from modules.block import Block
from modules.label import Label
from modules.excel import Excel
from modules.plot import plot_response
from modules.plot import plot_start_slopes
from modules.plot import plot_mean_curve
from modules.plot import plot_baseline


class Measurement(object):
    """
    """
    def __init__(self):
        """
        """
        self.label = None
        self.sigma = 1.5
        #
        return None
    ### ==================================================================== ###
    def read_measurement_datafile(self, datafilename):
        """
        """
        self._datafilename = datafilename
        # ------------------------
        # Read the whole file once
        # ------------------------
        with open(datafilename, 'r') as datafile:
            # Replace \x00 to nothing, split the lines, remove extra, split by tab
            lines = [line.strip().split('\t') for line in
                               datafile.read().replace('\x00', '').splitlines()]
        # ------------------------
        # Plate formated Kinetic measurements
        # ------------------------
        if ((lines[1][3] == 'PlateFormat') and (lines[1][4] == 'Kinetic')):
            self.separate_block_information(lines)
        #
        return None
    ### ==================================================================== ###
    def read_label_datafile(self, label_filename, time_of_addition_takes=30):
        """
        """
        # Store the filename of the label file
        self.label_filename = label_filename
        # Create a label object
        self.label = Label()
        # Read the label file content
        self.label.read_label_file(label_filename)
        # Adjust the time
        for block in xrange(1, self.number_of_blocks):
            self.data[block].time_shift = self.data[block-1].time[-1] + time_of_addition_takes
        # Calculate the important parameters
        self.calculate_baseline()
        self.calculate_response()
        self.calculate_mean_curve()
        self.calculate_slope(time_of_addition_takes)
        #
        return None
    ### ==================================================================== ###
    def separate_block_information(self, lines):
        """
        """
        self.number_of_blocks = int(lines[0][0].split()[-1])
        #
        self.data = {}
        self.last_baseline = 0
        #
        start = 1
        for block in xrange(self.number_of_blocks):
            #
            end = start
            while ((end < len(lines)) and (not lines[end][0].startswith('~End'))):
                end += 1
            # ---------------------
            # Extract the data
            # ---------------------
            self.data[block] = Block(lines[start:end])
            # ---------------------
            # Remember the last baseline index
            # ---------------------
            if 'baseline' in self.data[block].block_name:
                self.last_baseline = block
            #
            start = end + 1
        # ---------------------
        self.total_number_of_points = 0
        # ---------------------
        # Normalize data to the last baseline point
        # ---------------------
        for block in self.data:
            #
            self.data[block].normalize(self.data[self.last_baseline].raw_value[:, -1])
            #
            self.total_number_of_points += self.data[block].number_of_points
        #
        return None
    ### ==================================================================== ###
    def calculate_baseline(self, number_of_data = 3):
        """
        """
        self.baseline = {}
        block = self.last_baseline
        # Get the corresponding labels
        groups = self.label.get_group(block)
        # Collect data for each group
        for name in groups:
            # Baseline
            original_data = self.data[block].last(number_of_data, True)[groups[name]].mean(axis=1)
            # Filter out outlier and store the result
            self.baseline[name] = self.outlier_filter(original_data)
        #
        return None
    ### ==================================================================== ###
    def calculate_response(self):
        """
        Response of each block is the difference between the max value in block
        and the last value of the previous block
        """
        self.response = {}
        # Go through each block except the first
        for block in xrange(1, self.number_of_blocks):
            #
            self.response[block] = {}
            # Get the corresponding labels
            groups = self.label.get_group(block)
            # Collect data for each group
            for name in groups:
                #
                original_data = self.data[block].difference(
                                previous_block_last_elements=self.data[block - 1].last()[0],
                                use_max=block < self.number_of_blocks - 1)[groups[name]]
                # Filter out outlier and store the result
                self.response[block][name] = self.outlier_filter(original_data)
        #
        return None
    ### ==================================================================== ###
    def calculate_mean_curve(self):
        """
        """
        self.mean_curve = {}
        self.mean_time = {}
        # Go through each block
        for block in xrange(self.number_of_blocks):
            #
            self.mean_curve[block] = {}
            self.mean_time[block] = {}
            # Get the corresponding labels
            groups = self.label.get_group(block)
            # Collect data for each group
            for name in groups:
                # Traces
                original_data = np.hstack([self.data[previous_block].value[groups[name], :]
                                          for previous_block in xrange(block + 1)])
                # Filter out outlier and store the result
                self.mean_curve[block][name] = self.outlier_filter(original_data)
                #
                self.mean_time[block][name] = np.hstack([self.data[previous_block].time
                                          for previous_block in xrange(block + 1)])
        #
        return None
    ### ==================================================================== ###
    def calculate_slope(self, time_of_addition_takes):
        """
        """
        self.start_slope = {}
        # Go through each block except the first
        for block in xrange(1, self.number_of_blocks):
            #
            self.start_slope[block] = {}
            # Get the corresponding labels
            groups = self.label.get_group(block)
            # Collect data for each group
            for name in groups:
                #
                original_data = self.data[block].slope(self.data[block-1].last()[0],
                                           time_of_addition_takes)[groups[name]]
                # Filter out outlier and store the result
                self.start_slope[block][name] = self.outlier_filter(original_data)
        #
        return None
    ### ==================================================================== ###
    def outlier_filter_1d(self, data):
        """
        """
        mask = np.absolute(data - data.mean()) < data.std() * self.sigma
        if mask.sum() == 0:
            mask = np.ones(data.shape, dtype = np.bool8)
        #
        return data[mask]
    ### ==================================================================== ###
    def outlier_filter(self, data):
        """
        """
        filtered_data = {'mean' : [],
                         'std' : [],
                         'len' : [],
                         'original_data' : data}
        # 1D data
        if len(data.shape) == 1:
            row = self.outlier_filter_1d(data)
            #
            filtered_data['mean'].append(row.mean())
            filtered_data['std'].append(row.std())
            filtered_data['len'].append(len(row))
        else:
            # 2D data
            for i in xrange(data.shape[1]):
                row = self.outlier_filter_1d(data[:, i])
                filtered_data['mean'].append(row.mean())
                filtered_data['std'].append(row.std())
                filtered_data['len'].append(len(row))
        #
        return filtered_data
    ### ==================================================================== ###
    def info(self):
        """
        """
        info_text = ''.join(('Filename: ', self._datafilename, '\n'))
        info_text = ''.join((info_text, self.data[0].info(True)))
        info_text = ''.join((info_text, 'Number of blocks: ', str(self.number_of_blocks), '\n'))
        for block in xrange(self.number_of_blocks):
            info_text = ''.join((info_text, str(block+1), '. ', self.data[block].info(False)))
        #
        if self.label:
            info_text = ''.join((info_text, self.label.info()))
        #
        return info_text
    ### ==================================================================== ###
    def save_datafile(self, save_excel_filename):
        """
        """
        workbook = Excel()
        # ---------------------------
        # Grouped normalized data
        # ---------------------------
        for block in self.mean_curve:
            data = []
            # Header
            a = ['Time']
            for time in self.mean_time[block][self.mean_time[block].keys()[0]]:
                a.append(time)
            data.append(a)
            # Values
            for group in self.mean_curve[block]:
                for column in xrange(len(self.mean_curve[block][group]['original_data'])):
                    if column == 0:
                        a = [group]
                    else:
                        a = ['']
                    for value in self.mean_curve[block][group]['original_data'][column]:
                        a.append(value)
                    #
                    data.append(a)
            workbook.add_sheet('grouped_' + self.data[block].block_name, data)
        # ---------------------------
        # Raw and normalized data
        # ---------------------------
        data = []
        # Header 1
        a = ['']
        a.append('Raw data')
        a.append('Block')
        for block in self.data:
            for time in self.data[block].time:
                a.append(self.data[block].block_name)
        a.append('')
        a.append('')
        a.append('Normalized')
        a.append('Block')
        for block in self.data:
            for time in self.data[block].time:
                a.append(self.data[block].block_name)
        data.append(a)
        # Header 2
        a = ['Label']
        a.append('Raw data')
        a.append('Time')
        for block in self.data:
            for time in self.data[block].time:
                a.append(time)
        a.append('')
        a.append('')
        a.append('Normalized')
        a.append('Time')
        for block in self.data:
            for time in self.data[block].time:
                a.append(time)
        data.append(a)
        # Values
        for well_index in xrange(len(self.label.well_order)):
            a = []
            a.append(';'.join(self.label.all_labels[self.label.well_order[well_index]]))
            a.append('Raw data')
            a.append(self.label.well_order[well_index])
            for block in self.data:
                for value in self.data[block].raw_value[well_index]:
                    a.append(value)
            a.append('')
            a.append('')
            a.append('Normalized')
            a.append(self.label.well_order[well_index])
            for block in self.data:
                for value in self.data[block].value[well_index]:
                    a.append(value)
            data.append(a)
        workbook.add_sheet('raw_data', data)
        # ---------------------------
        # Mean
        # ---------------------------
        for block in self.mean_curve:
            data = []
            # Header
            a = ['Time']
            for time in self.mean_time[block][self.mean_time[block].keys()[0]]:
                a.append(time)
            a.append('')
            a.append('Std')
            for time in self.mean_time[block][self.mean_time[block].keys()[0]]:
                a.append(time)
            data.append(a)
            # Values
            for group in self.mean_curve[block]:
                a = [group]
                for value in self.mean_curve[block][group]['mean']:
                    a.append(value)
                a.append('')
                a.append(group)
                for value in self.mean_curve[block][group]['std']:
                    a.append(value)

                data.append(a)
            workbook.add_sheet('mean_' + self.data[block].block_name, data)
        # ---------------------------
        # Baseline average
        # ---------------------------
        data = []
        # Header
        a = ['Label']
        for i in xrange(len(self.baseline[self.baseline.keys()[0]]['original_data'])):
            a.append(i + 1)
        a.append('')
        a.append('Mean')
        a.append('Std')
        a.append('Number of data')
        data.append(a)
        # Values
        for group in self.baseline:
            a = [group]
            for value in self.baseline[group]['original_data']:
                a.append(value)
            a.append('')
            a.append(self.baseline[group]['mean'][0])
            a.append(self.baseline[group]['std'][0])
            a.append(self.baseline[group]['len'][0])
            data.append(a)
        workbook.add_sheet('baseline average', data)
        # ---------------------------
        # Peak response
        # ---------------------------
        for block in self.response:
            data = []
            # Header
            a = ['Label']
            for i in xrange(len(self.response[block][self.response[block].keys()[0]]['original_data'])):
                a.append(i + 1)
            a.append('')
            a.append('Mean')
            a.append('Std')
            a.append('Number of data')
            data.append(a)
            # Values
            for group in self.response[block]:
                a = [group]
                for value in self.response[block][group]['original_data']:
                    a.append(value)
                a.append('')
                a.append(self.response[block][group]['mean'][0])
                a.append(self.response[block][group]['std'][0])
                a.append(self.response[block][group]['len'][0])
                data.append(a)
            workbook.add_sheet('peak_' + self.data[block].block_name, data)
        # ---------------------------
        # Slope
        # ---------------------------
        for block in self.response:
            data = []
            # Header
            a = ['Label']
            for i in xrange(len(self.start_slope[block][self.start_slope[block].keys()[0]]['original_data'])):
                a.append(i + 1)
            a.append('')
            a.append('Mean')
            a.append('Std')
            a.append('Number of data')
            data.append(a)
            # Values
            for group in self.start_slope[block]:
                a = [group]
                for value in self.start_slope[block][group]['original_data']:
                    a.append(value)
                a.append('')
                a.append(self.start_slope[block][group]['mean'][0])
                a.append(self.start_slope[block][group]['std'][0])
                a.append(self.start_slope[block][group]['len'][0])
                data.append(a)
            workbook.add_sheet('slope_' + self.data[block].block_name, data)
        #
        print save_excel_filename
        workbook.save_excel_file(save_excel_filename)
        #
        return None
    ### ==================================================================== ###
    def plot_data(self, plate_name, folder_name):
        """
        """
        folder_name = ''.join((folder_name,
                               os.path.sep,
                               plate_name.replace(' ', '_'),
                               '_figures',
                               os.path.sep))
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)
        # ---------------------------
        # Baseline
        # ---------------------------
        print 'baseline figure...',
        plot_baseline(self.baseline, plate_name, folder_name)
        # ---------------------------
        # Response
        # ---------------------------
        print 'peak response figures...',
        plot_response(self.response, plate_name, folder_name)
        # ---------------------------
        # Response
        # ---------------------------
        print 'start slopes figures...',
        plot_start_slopes(self.start_slope, plate_name, folder_name)
        # ---------------------------
        # Mean curve
        # ---------------------------
        print 'mean curve figures...',
        addition = [[0.0, 'baseline']]
        for block in xrange(1, len(self.data)):
            addition.append([self.data[block-1].time[-1], self.data[block].block_name])
        plot_mean_curve(self.mean_time, self.mean_curve, addition, plate_name, folder_name)
        #
        print 'DONE.'
        # 
        return None
    ### ==================================================================== ###
    @property
    def sigma(self):
        return self._sigma
    @sigma.setter
    def sigma(self, value):
        self._sigma = float(value)
        return None
    ### ==================================================================== ###
    ### ==================================================================== ###
    ### ==================================================================== ###


