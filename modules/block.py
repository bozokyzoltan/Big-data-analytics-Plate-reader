#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by Zoltan Bozoky on 2015.04.09.
Under GPL licence.

Purpose:
========
Handling the plate reader output file
"""

import numpy as np


def calculate_slope(x, y):
    """
    """
    x = np.array(x)
    y = np.array(y)
    #
    xy = x * y
    #
    slope = (((len(x) * xy.sum()) - (x.sum()*y.sum())) /
             ((len(x) * sum(x**2)) - x.sum()**2))
    return slope
### ======================================================================== ###




class Block(object):
    """
    """
    def __init__(self, lines):
        """
        """
        self.column_names = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self._wells = []
        self.non_exists = 9.9E+99
        # -----------------------------
        # Block name is the second value of the first row in the header
        # -----------------------------
        self.block_name = lines[0][1]
        # -----------------------------
        # TimeFormat or Well scan
        # -----------------------------
        self.file_format = lines[0][3]
        # -----------------------------
        # Measurement type: Kinetic
        # -----------------------------
        self.measurement_type = lines[0][4]
        # -----------------------------
        # Number of timepoints or pixels
        # -----------------------------
        self.number_of_points = lines[0][9]
        # -----------------------------
        # The third row only contains well measurements
        # -----------------------------
        self.used_wells = []
        for index in xrange(2, len(lines[2])):
            if lines[2][index] != '':
                self.used_wells.append(index)
        self.number_of_wells = len(self.used_wells)
        # -----------------------------
        # Number of columns
        # -----------------------------
        self.number_of_columns = lines[0][18]
        # -----------------------------
        # Total number of cells on the plate
        # -----------------------------
        self.plate_size = lines[0][19]
        # -----------------------------
        # How many lines one timepoint recording has
        # -----------------------------
        self.number_of_rows_per_timepoint = self.plate_size / int(len(lines[1]) - 1)
        # -----------------------------
        # Storage of time in different timepoints
        # -----------------------------
        self._relative_time = []
        self._absolute_time = []
        self._temperature = []
        # -----------------------------
        # Actual data storeage
        # -----------------------------
        self._raw_value = np.zeros((self.number_of_wells * self.number_of_rows_per_timepoint,
                              self.number_of_points
                             ),
                             dtype = np.float32)
        self._value = np.zeros((self.number_of_wells * self.number_of_rows_per_timepoint,
                              self.number_of_points
                             ),
                             dtype = np.float32)
        # -----------------------------
        #
        # -----------------------------
        for point in xrange(self.number_of_points):
            #
            time_point_start = 2 + point * (self.number_of_rows_per_timepoint + 1)
            time_point_end = time_point_start + self.number_of_rows_per_timepoint

            time, temp, value = self.separate_time_point_data(lines[time_point_start:time_point_end],
                                                              point == 0
                                                             )

            self.relative_time = time
            self.temparature = temp
            self._raw_value[:, point] = value
            self._value[:, point] = value
        # -----------------------------
        self.find_max()
        self.find_min()
        self.time_shift = 0
        self.slopes = None
        self.slopes_time = 0
        #
        return None
    ### ==================================================================== ###
    def separate_time_point_data(self, lines, first_timepoint):
        """
        """
        time_point = 0
        temperature = 0
        values = []
        for i in xrange(len(lines)):
            if i == 0:
                time_point = self.time2sec(lines[i][0])
                temperature = float(lines[i][1])
            for well in xrange(self.number_of_wells):
                if i == 0:
                    position = self.used_wells[well]
                else:
                    position = well#self.used_wells[well] - 2

                if first_timepoint:
#                    self.wells = self.column_names[i] + str(well+1)
                    self.wells = self.column_names[i] + str(self.used_wells[well] - 1)
                #
                try:
                    values.append(float(lines[i][position]))
                except IndexError:
                    values.append(self.non_exists)
                except ValueError:
                    values.append(self.non_exists)
        #
        return time_point, temperature, np.array(values, dtype = np.float32)
    ### ==================================================================== ###
    def time2sec(self, time_string):
        """
        """
        #
        return sum([multiplier * float(timepoint) for (multiplier, timepoint) in zip([3600, 60, 1], time_string.split(':'))])
    ### ========================================================================
    def normalize(self, values):
        """
        """
        for i in xrange(len(values)):
            if values[i] < self.non_exists:
                self._value[i, :] /= values[i]
        #
        self._max /= values
        self._min /= values
        #
        return None
    ### ========================================================================
    def find_max(self):
        """
        """
        self._max = np.empty(self._raw_value.shape[0], dtype = np.float32)
        for i in xrange(self._raw_value.shape[0]):
            value = self.value[i]
            mask = value < self.non_exists * 0.1
            self._max[i] = value[mask].max()
        #
        return None
    ### ========================================================================
    def find_min(self):
        """
        """
        self._min = np.empty(self._raw_value.shape[0], dtype = np.float32)
        for i in xrange(self._raw_value.shape[0]):
            value = self.value[i]
            mask = value < self.non_exists * 0.1
            self._min[i] = value[mask].min()
        #
        return None
    ### ========================================================================
    @property
    def time_shift(self):
        return self._timeshift
    #
    @time_shift.setter
    def time_shift(self, shift):
        """
        """
        self._timeshift = float(shift)
        #
        self._absolute_time = []
        for timepoint in self.relative_time:
            self._absolute_time.append(timepoint + shift)
        #
        return None
    ### ========================================================================
    def info(self, full):
        text = ''
        if full:
            text = ''.join((
                            '-'*20, '\nINFO\n', '-'*20, '\n',
                            'Plate size: ', str(self.plate_size), ' wells\n',
                            'Used well number: ', str(len(self.wells)), '\n',
                          ))
        else:
            text = ''.join((
                            'Block name: ', self.block_name, '\n',
                            '   - duration: ', str(self.relative_time[-1]), ' sec\n',
                            '   - number of points measured: ', str(self.number_of_points), '\n'
                          ))
        #
        return text
    ### ========================================================================
    @property
    def block_name(self):
        return self._block_name
    @block_name.setter
    def block_name(self, name):
        self._block_name = str(name).lower()
        return None
    ### ==================================================================== ###
    @property
    def file_format(self):
        return self._file_format
    @file_format.setter
    def file_format(self, name):
        self._file_format = str(name)
        return None
    ### ==================================================================== ###
    @property
    def measurement_type(self):
        return self._measurement_type
    @measurement_type.setter
    def measurement_type(self, value):
        self._measurement_type = str(value)
        return None
    ### ==================================================================== ###
    @property
    def number_of_points(self):
        return self._number_of_points
    @number_of_points.setter
    def number_of_points(self, value):
        self._number_of_points = int(value)
        return None
    ### ==================================================================== ###
    @property
    def number_of_wells(self):
        return self._number_of_wells
    @number_of_wells.setter
    def number_of_wells(self, value):
        self._number_of_wells = int(value)
        return None
    ### ==================================================================== ###
    @property
    def number_of_columns(self):
        return self._number_of_columns
    @number_of_columns.setter
    def number_of_columns(self, value):
        self._number_of_columns = int(value)
        return None
    ### ==================================================================== ###
    @property
    def plate_size(self):
        return self._plate_size
    @plate_size.setter
    def plate_size(self, value):
        self._plate_size = int(value)
        return None
    ### ==================================================================== ###
    @property
    def number_of_rows_per_timepoint(self):
        return self._number_of_rows_per_timepoint
    @number_of_rows_per_timepoint.setter
    def number_of_rows_per_timepoint(self, value):
        self._number_of_rows_per_timepoint = int(value)
        return None
    ### ==================================================================== ###
    @property
    def relative_time(self):
        return self._relative_time
    @relative_time.setter
    def relative_time(self, value):
        self._relative_time.append(value)
        return None
    ### ==================================================================== ###
    @property
    def temperature(self):
        return self._temperature
    @temperature.setter
    def temparature(self, value):
        self._temperature.append(value)
        return None
    ### ==================================================================== ###
    @property
    def non_exists(self):
        return self._non_exists
    @non_exists.setter
    def non_exists(self, value):
        self._non_exists = value
        return None
    ### ==================================================================== ###
    @property
    def wells(self):
        return self._wells
    @wells.setter
    def wells(self, value):
        self._wells.append(value)
        return None
    ### ==================================================================== ###
    @property
    def time(self):
        return self._absolute_time
    ### ==================================================================== ###
    @property
    def value(self):
        return self._value
    ### ==================================================================== ###
    @property
    def raw_value(self):
        return self._raw_value
    ### ==================================================================== ###
    @property
    def max(self):
        return self._max
    ### ==================================================================== ###
    @property
    def min(self):
        return self._min
    ### ==================================================================== ###
    def last(self, number_of_data = 1, use_raw_data = False):
        """
        """
        if self.value.shape[1] >= number_of_data:
            if use_raw_data:
                last_values = self.raw_value[:,-1*number_of_data:]
            else:
                last_values = self.value[:,-1*number_of_data:]
        else:
            if use_raw_data:
                last_values = self.raw_value
            else:
                last_values = self.value

        #
        return last_values
    ### ==================================================================== ###
    def difference(self, previous_block_last_elements, use_max=True):
        """
        """
        if use_max:
            diff = self.max - previous_block_last_elements
        else:
            diff = self.min - previous_block_last_elements
        #
        return diff
    ### ==================================================================== ###
    def slope(self, previous_block_last_elements, number_of_points_to_use = 5, time_addition_takes = 30):
        """
        """
        if self.slopes_time != time_addition_takes:
            #
            number_of_points_to_use -= 1
            if self.value.shape[1] <= number_of_points_to_use:
                number_of_points_to_use = self.value.shape[1]
            #
            time = np.array([0] + [time_addition_takes + timepoint for timepoint in self._relative_time[:number_of_points_to_use]], dtype = np.float32)
            #
            data = np.empty((self.value.shape[0], 1 + number_of_points_to_use), dtype = np.float32)
            data[:, 0] = previous_block_last_elements
            data[:, 1:] = self.value[:, :number_of_points_to_use]

            self.slopes = np.empty(data.shape[0], dtype = np.float32)
            for i in xrange(data.shape[0]):
                self.slopes[i] = calculate_slope(time, data[i,:])
            #
            self.slopes_time = time_addition_takes
        #
        return self.slopes
    ### ==================================================================== ###
    ### ==================================================================== ###
    ### ==================================================================== ###

