#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by Zoltan Bozoky on 2015.04.12.
Under GPL licence.
"""

import xlwt


class Excel(object):
    """
    """
    def __init__(self):
        """
        """
        self.workbook = xlwt.Workbook()
        #
        self.sheet_names = []
        #
        self.column_limit = 150
        #
        return None
    ### =================================================================== ###
    def add_sheet(self, sheetname, data):
        """
        """
        column_start = 0
        #
        for sheet_index in xrange((len(data) / self.column_limit) + 1):
            #    
            self.sheet_names.append(''.join((sheetname, '_', str(sheet_index + 1))))
            #
            sheet = self.workbook.add_sheet(self.sheet_names[-1])
            #
            column_end = len(data) - column_start
            if column_end > self.column_limit:
                column_end = self.column_limit
            #
            for column in xrange(column_end):
                for row in xrange(len(data[column_start + column])):
                    #
                    try:
                        value = float(data[column_start + column][row])
                    except ValueError:
                        value = data[column_start + column][row]
                    #
                    sheet.write(row, column, value)
            #
            column_start += column_end
        # 
        return None
    ### =================================================================== ###
    def save_excel_file(self, filename):
        """
        """
        self.workbook.save(filename)
        #
        return None
    ### =================================================================== ###
    ### =================================================================== ###
    ### =================================================================== ###

