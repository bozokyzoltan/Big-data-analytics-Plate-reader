#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by Zoltan Bozoky on 2015.04.09.
Under GPL licence.

Purpose:
========
Handle the label file

"""

import numpy as np
import xlrd


class Label(object):
    """
    """
    def __init__(self):
        """
        """
        self.row_names = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self.block_info = []
        #
        return None
    ### ==================================================================== ###
    def read_label_file(self, filename):
        """
        A1 cell must contain information about any addition
        First row must contain numbers from 1..4 or 1..12 or ...
        First column must contain letters from A..D or A..H or ...
        """
        # ----------------------
        # Open the xls file
        # ----------------------
        book = xlrd.open_workbook(filename)
        # actual label information storage
        self.all_labels = {}
        self.label_types = {}
        self.well_order = []
        # Go through all sheets
        for sheet_index, sheet_name in enumerate(book.sheet_names()):
            #
            sheet = book.sheet_by_name(sheet_name)
            # ----------------------
            # 'A1' cell contains information about the reading number
            # ----------------------
            if sheet.cell_value(0,0) != '':
                self.block_info.append(sheet_index)
            # ----------------------
            #
            # ----------------------
            self.label_types[sheet_index] = set()
            # ----------------------
            # Read the labels from the sheet
            # ----------------------
            for row in xrange(1, sheet.nrows):
                for col in xrange(1, sheet.ncols):
                    # Well name goes from A1, A2, ..., H11, H12
                    well_name = self.row_names[row - 1] + str(col)
                    # Read the label for the well
                    well_value = str(sheet.cell_value(row, col))
                    # Forgot about the empty wells
                    if well_value != '':
                        # Record the order of the wells
                        if sheet_index == 0:
                            self.well_order.append(well_name)
                        # Count how many different labels appears on the sheet
                        self.label_types[sheet_index].add(well_value)
                        # Record the actual data
                        if well_name not in self.all_labels:
                            self.all_labels[well_name] = []
                        self.all_labels[well_name].append(well_value)
        # ----------------------
        # Group corresponding labels together
        # ----------------------
        self._group_wells()
        #
        print self.well_order
        return None
    ### ==================================================================== ###
    def create_tag(self, well_name, block):
        """
        """
        tag = ''
        well_name = self.all_labels[well_name][:block + 1]
        #
        for i in xrange(len(well_name)):
            #
            if len(self.label_types[i]) > 1:
                tag = ''.join((tag, well_name[i], ';'))
        #
        return tag[:-1]
    ### ==================================================================== ###
    def _group_wells(self):
        """
        """
        self.group_labels = {}
        # ----------------------
        # create a group label for each block of addition
        # ----------------------
        for block_index, block in enumerate(self.block_info):
            # ----------------------
            # group_labels contains information for each block
            # ----------------------
            self.group_labels[block_index] = {}
            # ----------------------
            # Each well index appends to the corresponding label
            # ----------------------
            for well_index, well in enumerate(self.well_order):
                #
                tag = self.create_tag(well, block)
#                tag = ';'.join((self.all_labels[well][:block + 1]))
                #
                if tag not in self.group_labels[block_index]:
                    self.group_labels[block_index][tag] = []
                #
                self.group_labels[block_index][tag].append(well_index)
        #
        return None
    ### ==================================================================== ###
    def get_group(self, block_number):
        """
        Numbering of the block_number starts with 0 (=block index)
        """
        return self.group_labels[block_number]
    ### ==================================================================== ###
    def get_well_label_name(self, well_index, block, full_name = False, separation_character = ';'):
        """
        """
        tag = ''
        for i in xrange(self.block_info[block]):
            # ----------------------
            # Skip non unique labels
            # ----------------------
            if (full_name or (len(self.label_types[i]) > 1)):
                # Add tags together
                tag = ''.join((tag,
                               self.all_labels[self.well_order[well_index]][i],
                               separation_character,
                             ))
        #
        return tag[:-1]
    ### ==================================================================== ###
    def longest_label_length(self, block):
        """
        """
        longest = 0
        for group in self.group_labels[block]:
            if len(self.group_labels[block][group]) > longest:
                longest = len(self.group_labels[block][group])
        #
        return longest
    ### ==================================================================== ###
    def info(self):
        """
        """
        info_text = ''.join(('-'*20, '\nGROUPS\n', '-'*20, '\n'))
        #
        for block in self.group_labels:
            for key in self.group_labels[block]:
                #
                info_text = ''.join((info_text,
                                     'label: ', key.replace(';', ' '), '\n',
                                     'number of wells in the group: ', str(len(self.group_labels[block][key])), '\n',
                                     'wells: ', ','.join((self.well_order[i] for i in self.group_labels[block][key])), '\n',
                                     '-'*5, '\n'
                                   ))
        #
        return info_text
    ### ==================================================================== ###
    ### ==================================================================== ###
    ### ==================================================================== ###

