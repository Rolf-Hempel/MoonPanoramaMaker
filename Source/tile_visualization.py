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

from math import radians

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, Polygon
from matplotlib.widgets import RectangleSelector

import configuration
import tile_constructor


def toggle_selector(event):
    pass


class TileVisualization:
    def __init__(self, configuration, tc):

        self.m_diameter = tc.m_diameter
        self.phase_angle = tc.phase_angle
        self.configuration = configuration
        self.tc = tc
        self.active_tile = None

        plt.ion()
        figsize = ((self.configuration.conf.getfloat(
            "Tile Visualization", "figsize horizontal")),
                   (self.configuration.conf.getfloat(
                       "Tile Visualization", "figsize vertical")))
        self.fig = plt.figure(figsize=figsize)

        self.mngr = plt.get_current_fig_manager()
        (x0, y0, width, height) = self.mngr.window.geometry().getRect()
        # look up stored position of upper left window corner:
        x0 = int(
            self.configuration.conf.get('Hidden Parameters', 'tile window x0'))
        y0 = int(
            self.configuration.conf.get('Hidden Parameters', 'tile window y0'))
        # move the tile visualization window to the stored position:
        self.mngr.window.setGeometry(x0, y0, width, height)

        self.ax = self.fig.add_subplot(111, axisbg='black')
        fig_half_width = self.m_diameter / 2. + 0.0003 + self.tc.ol_outer
        plt.axis(([-fig_half_width, fig_half_width,
                   -fig_half_width, fig_half_width]))
        plt.tick_params(axis='both', which='both', bottom='off',
                        top='off', labelbottom='off', left='off',
                        labelleft='off')
        polygon_array = np.array(self.__MoonPhase__())
        moon_outline = (Polygon(polygon_array, closed=True,
                                color='#FFD700', alpha=1.))

        self.ax.add_patch(moon_outline)

        self.tiles = []
        count = 0
        label_fontsize = self.configuration.conf.getint("Tile Visualization",
                                                        "label fontsize")
        label_shift = self.configuration.conf.getfloat("Tile Visualization",
                                                       "label shift")
        for t in self.tc.list_of_tiles_sorted:
            rectangle = Rectangle((t['x_left'], t['y_bottom']), self.tc.im_w,
                                  self.tc.im_h, color='red', alpha=0.5)
            self.tiles.append(rectangle)
            x_text_pos_col = (t['x_right'] - float(t['column_index'] + 1) /
                              float(t['column_total'] + 1) * self.tc.im_w)
            x_text_pos = (label_shift * x_text_pos_col +
                          (1. - label_shift) * t['x_center'])
            plt.text(x_text_pos, t['y_center'], str(count),
                     horizontalalignment='center', verticalalignment='center',
                     fontsize=label_fontsize)
            count += 1

        for t in reversed(self.tiles):
            self.ax.add_patch(t)

        toggle_selector.RS = RectangleSelector(self.ax,
                                               self.line_select_callback,
                                               drawtype='box', useblit=True,
                                               button=[1, 3],
                                               # don't use middle button
                                               minspanx=0, minspany=0,
                                               spancoords='pixels')
        plt.connect('key_press_event', toggle_selector)
        self.selection_rectangle = None
        self.reset_selection_rectangle()
        self.fig.canvas.set_window_title("MoonPanoramaMaker: Tile Arrangement "
                                         "in normalized orientation (see user "
                                         "guide)")
        plt.tight_layout()
        self.fig.canvas.draw()

    def line_select_callback(self, eclick, erelease):
        # eclick and erelease are the press and release events
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        # print("(%8.7f, %8.7f) --> (%8.7f, %8.7f)" % (x1, y1, x2, y2))
        # print(
        #     " The button you used were: %s %s" % (
        #     eclick.button, erelease.button))
        self.select_rect_x_min = min(x1, x2)
        self.select_rect_x_max = max(x1, x2)
        self.select_rect_y_min = min(y1, y2)
        self.select_rect_y_max = max(y1, y2)
        width = self.select_rect_x_max - self.select_rect_x_min
        height = self.select_rect_y_max - self.select_rect_y_min
        if width >= 0.00005 and height >= 0.00005:
            if self.selection_rectangle != None:
                self.ax.patches.remove(self.selection_rectangle)
            self.selection_rectangle = Rectangle(
                (self.select_rect_x_min, self.select_rect_y_min), width,
                height,
                color='lightgrey', alpha=0.4)
            self.ax.add_patch(self.selection_rectangle)
            self.fig.canvas.draw()
        else:
            self.reset_selection_rectangle()

    def reset_selection_rectangle(self):
        self.select_rect_x_min = -2.
        self.select_rect_x_max = -2.
        self.select_rect_y_min = -2.
        self.select_rect_y_max = -2.
        if self.selection_rectangle != None:
            self.ax.patches.remove(self.selection_rectangle)
            self.fig.canvas.draw()
        self.selection_rectangle = None

    def get_selected_tile_numbers(self):
        selected_tile_numbers = []
        if self.select_rect_x_max > -1.:
            tile_number = 0
            for t in self.tc.list_of_tiles_sorted:
                if t['x_left'] >= self.select_rect_x_min and t[
                    'x_right'] <= self.select_rect_x_max and \
                                t['y_bottom'] >= self.select_rect_y_min and t[
                    'y_top'] <= self.select_rect_y_max:
                    selected_tile_numbers.append(tile_number)
                tile_number += 1
        self.reset_selection_rectangle()
        return selected_tile_numbers

    def __MoonPhase__(self):
        moon_radius = self.m_diameter / 2.
        vertices = []
        resolution = 500  # the number of vertices for moon phase
        for i in range(resolution):
            phi = np.pi * (float(i) / float(resolution))
            vertices.append(
                [moon_radius * np.sin(phi), moon_radius * np.cos(phi)])
        for i in range(resolution):
            phi = np.pi * (float(resolution - i) / float(resolution))
            vertices.append(
                [moon_radius * np.sin(phi) * np.cos(self.phase_angle),
                 moon_radius * np.cos(phi)])
        return vertices

    def mark_active(self, index):
        self.active_tile = self.tiles[index]
        self.active_tile.set_color('blue')
        self.fig.canvas.draw()

    def mark_processed(self, index_list):
        for index in index_list:
            self.tc.list_of_tiles_sorted[index]['processed'] = True
            self.tiles[index].set_color('skyblue')
        self.fig.canvas.draw()

    def mark_all_processed(self):
        for t in self.tc.list_of_tiles_sorted:
            t['processed'] = True
        for t in self.tiles:
            t.set_color('skyblue')
        self.fig.canvas.draw()

    def mark_unprocessed(self, index_list):
        for index in index_list:
            self.tc.list_of_tiles_sorted[index]['processed'] = False
            self.tiles[index].set_color('red')
        self.fig.canvas.draw()

    def mark_all_unprocessed(self):
        for t in self.tc.list_of_tiles_sorted:
            t['processed'] = False
        for t in self.tiles:
            t.set_color('red')
        self.fig.canvas.draw()

    def close_tile_visualization(self):
        (x0, y0, width, height) = self.mngr.window.geometry().getRect()
        self.configuration.conf.set('Hidden Parameters', 'tile window x0',
                                    str(x0))
        self.configuration.conf.set('Hidden Parameters', 'tile window y0',
                                    str(y0))
        plt.close()


if __name__ == "__main__":
    import time

    configuration = configuration.Configuration()

    de_center = radians(15.)
    m_diameter = radians(31. / 60.)
    phase_angle = radians(120.)
    pos_angle = radians(22.)

    tc = tile_constructor.TileConstructor(configuration, de_center, m_diameter,
                                          phase_angle, pos_angle)
    tv = TileVisualization(configuration, tc)

    for i in range(len(tv.tiles)):
        time.sleep(0.1)
        tv.mark_active(i)
        time.sleep(0.1)
        tv.mark_processed([i])

    time.sleep(2)

    tv.mark_all_unprocessed()

    time.sleep(2)

    tv.mark_all_processed()

    time.sleep(2)

    tv.close_tile_visualization()
