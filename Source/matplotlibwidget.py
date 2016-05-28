# -*- coding: utf-8; -*-
"""
Copyright (c) 2016 Rolf Hempel, rolf6419@gmx.de

This file is part of the MoonPanoramaMaker tool (MPM).
https://github.com/Rolf-Hempel/MoonPanoramaMaker

MPM is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with MPM.  If not, see <http://www.gnu.org/licenses/>.

"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure


class MatplotlibWidget(Canvas):
    def __init__(self, parent=None, hold=False):
        super(MatplotlibWidget, self).__init__(Figure())

        self.setParent(parent)
        self.figure = plt.figure()
        self.plotrect = self.figure.add_subplot(2, 1, 1)
        self.plotrect.set_title('Drift in RA and DE', fontsize=12)
        self.plotrect.set_ylabel("RA (')", fontsize=10)
        labels_x = self.plotrect.get_xticklabels()
        labels_y = self.plotrect.get_yticklabels()
        for xlabel in labels_x:
            xlabel.set_fontsize(8)
        for ylabel in labels_y:
            ylabel.set_fontsize(8)
        self.plotdecl = self.figure.add_subplot(2, 1, 2)
        self.plotdecl.set_xlabel('Minutes since first alignment', fontsize=10)
        self.plotdecl.set_ylabel("DE (')", fontsize=10)
        self.figure.subplots_adjust(left=0.13, right=0.96, bottom=0.12)
        labels_x = self.plotdecl.get_xticklabels()
        labels_y = self.plotdecl.get_yticklabels()
        for xlabel in labels_x:
            xlabel.set_fontsize(8)
        for ylabel in labels_y:
            ylabel.set_fontsize(8)
        plt.close()

    def plotDataPoints(self, al_point_numbers, ra_corrections, de_corrections,
                       first_index, last_index):
        self.plotrect.plot(al_point_numbers, ra_corrections, 'bo')
        xd = [al_point_numbers[first_index], al_point_numbers[last_index]]
        yd = [ra_corrections[first_index], ra_corrections[last_index]]
        self.plotrect.plot(xd, yd, 'ro-', label='drift')
        self.plotdecl.plot(al_point_numbers, de_corrections, 'bo')
        xd = [al_point_numbers[first_index], al_point_numbers[last_index]]
        yd = [de_corrections[first_index], de_corrections[last_index]]
        self.plotdecl.plot(xd, yd, 'ro-', label='drift')
        self.draw()
