#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created by Zoltan Bozoky 2015.04.14.
Under GPL licence.
"""

import wx
from front_end import FrontEnd


# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = FrontEnd()
    frame.Show()
    app.MainLoop()
