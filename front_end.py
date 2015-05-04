#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by Zoltan Bozoky 2015.04.13.
Under GPL licence.

"""

import wx
from wx.lib.intctrl import IntCtrl
import os
from modules.measurement import Measurement


class FrontEnd(wx.Frame):
    """
    """
    def __init__(self):
        """
        """
        self.PlateReader = Measurement()

        wx.Frame.__init__(self, None, wx.ID_ANY, "Kinetic measurement converter",
                          size = (465, 400), style = wx.CAPTION | wx.MINIMIZE_BOX |wx.CLOSE_BOX)
        self.Centre()
        #
        splitter = wx.SplitterWindow(self, -1, style=wx.SP_3D)
        #
        panel1 = wx.Panel(splitter, wx.ID_ANY, size =(460,180))
        panel2 = wx.Panel(splitter, wx.ID_ANY, size =(460,280))
        splitter.SplitHorizontally(panel1, panel2, 65)
        # ---------------------
        # 1. Load datafile
        # ---------------------
        self.button_data = wx.Button(panel1, id=wx.ID_ANY, label="1. Load datafile", pos=(5,5), size=(150,30))
        self.button_data.Bind(wx.EVT_BUTTON, self.onButton_data)
        # ---------------------
        # 2. Time of addition
        # ---------------------
        self.addition_time_text = wx.StaticText(panel1, id=wx.ID_ANY, pos=(165,12), label='2. Time of an addition (sec):')
        self.addition_time = IntCtrl(panel1, id=wx.ID_ANY, pos=(350,8), size=(40,25))
        self.addition_time.SetMin(0)
        self.addition_time.SetMax(10000)
        self.addition_time.SetValue(30)
        # ---------------------
        # 3. Load labels
        # ---------------------
        self.button_label = wx.Button(panel1, id=wx.ID_ANY, label="3. Load label file", pos=(5,35), size=(150,30))
        self.button_label.Bind(wx.EVT_BUTTON, self.onButton_label)
        self.button_label.Hide()
        # ---------------------
        # 4. Save data
        # ---------------------
        self.button_save = wx.Button(panel1, id=wx.ID_ANY, label="4. Save converted data", pos=(155,35), size=(150,30))
        self.button_save.Bind(wx.EVT_BUTTON, self.onButton_save)
        self.button_save.Hide()
        # ---------------------
        # 5. Plot figures
        # ---------------------
        self.button_plot = wx.Button(panel1, id=wx.ID_ANY, label="5. Plot figures", pos=(305,35), size=(150,30))
        self.button_plot.Bind(wx.EVT_BUTTON, self.onButton_plot)
        self.button_plot.Hide()


        self.edit = wx.TextCtrl(panel2, id = wx.ID_ANY, pos=(5,0), size=(450, 300), style = wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_AUTO_URL)
        text = ''
        self.edit.SetValue(text)
        self.edit.Hide()
        #
        wx.StaticText(panel1, id=wx.ID_ANY, pos=(418,0), label='bozoky')
        #
        return None
    ### ========================================================================
    def onButton_data(self, event):
        """
        This method is fired when its corresponding button is pressed
        """
        openFileDialog = wx.FileDialog(self,
                               'Open plate reader measurement file in plate format',
                               '',
                               '',
                               'Plate reader files (*.xls)|*.xls',
                               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
                                      )
        #
        if openFileDialog.ShowModal() != wx.ID_CANCEL:
            #
            self.PlateReader.read_measurement_datafile(openFileDialog.GetPath())
            #
            self.data_filename = os.path.basename(openFileDialog.GetPath()).split('.')[0]
            self.save_filename = openFileDialog.GetPath().split('.')[0] + '_analyzed.xls'
            #
            self.button_label.Show()
            self.edit.Show()
            self.edit.SetValue(self.PlateReader.info())
            self.button_save.Label = '4. Save converted data'
        #
        openFileDialog.Destroy()
        #
        return None
    ### ========================================================================
    def onButton_label(self, event):
        """
        This method is fired when its corresponding button is pressed
        """
        openFileDialog = wx.FileDialog(self,
                               'Open plate reader measurement file in plate format',
                               '',
                               '',
                               'Plate reader files (*.xls)|*.xls',
                               wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
                                      )
        #
        if openFileDialog.ShowModal() != wx.ID_CANCEL:
            #
            self.PlateReader.read_label_datafile(openFileDialog.GetPath(), self.addition_time.GetValue())
            #
            self.button_save.Show()
            self.button_plot.Show()
            #
            self.edit.SetValue(self.PlateReader.info())
        #
        openFileDialog.Destroy()
        #
        return None
    ### ========================================================================
    def onButton_plot(self, event):
        """
        This method is fired when its corresponding button is pressed
        """
        self.PlateReader.plot_data(self.data_filename, os.path.dirname(self.save_filename))
        #
        return None
    ### ========================================================================
    def onButton_save(self, event):
        """
        This method is fired when its corresponding button is pressed
        """
        if self.save_filename != '':
            self.button_save.Label = '4. Saving...'
            add_time = self.addition_time.GetValue()
            #
            self.PlateReader.save_datafile(self.save_filename)
            #
            self.button_save.Label = '4. Saved'
        #
        return None
    ### ========================================================================
    ### ========================================================================
    ### ========================================================================



