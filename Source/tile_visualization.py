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
    """
    This class visualizes the tesselation of the sunlit phase of the moon computed by the 
    TileConstructor. It provides methods for MPM to show the state of different tiles, or for the
    user to select regions of tiles which then can be marked processed / uprocessed collectively.

    """

    def __init__(self, configuration, tc):
        """
        Initialization, creation of the "Tile Visualization" window and creation of the tile
        display in that window.
        
        :param configuration: object containing parameters set by the user
        :param tc: TileConstructor object with information on the tesselation
        """

        # Initialize instance variables
        self.m_diameter = tc.m_diameter
        self.phase_angle = tc.phase_angle
        self.configuration = configuration
        self.tc = tc
        # The "active tile" is colored blue. It is just being processed. Unprocessed tiles are
        # colored red, processed ones light-blue.
        self.active_tile = None

        # Get the size of the window from the configuration object and create the figure.
        figsize = ((self.configuration.conf.getfloat("Tile Visualization", "figsize horizontal")),
                   (self.configuration.conf.getfloat("Tile Visualization", "figsize vertical")))
        # self.fig = plt.figure(figsize=figsize, frameon=False)
        self.fig = plt.figure(figsize=figsize, facecolor=(0., 0., 0., 1))

        # Switch on interactive mode.
        plt.ion()
        # Replace the window location with coordinates stored from a previous run in configuration.
        self.mngr = plt.get_current_fig_manager()
        (x0, y0, width, height) = self.mngr.window.geometry().getRect()
        # look up stored position of upper left window corner:
        x0 = self.configuration.conf.getint('Hidden Parameters', 'tile window x0')
        y0 = self.configuration.conf.getint('Hidden Parameters', 'tile window y0')
        # move the tile visualization window to the stored position:
        self.mngr.window.setGeometry(x0, y0, width, height)

        self.ax = self.fig.add_subplot(111, facecolor='black')
        # Set the coordinate range in x and y. Coordinates are in radians from now on.
        fig_half_width = self.m_diameter / 2. + 0.0003 + self.tc.ol_outer
        plt.axis(([-fig_half_width, fig_half_width, -fig_half_width, fig_half_width]))
        plt.tick_params(axis='both', which='both', bottom='off', top='off', labelbottom='off',
                        left='off', labelleft='off')
        # Compute and show the current outline of the moon phase.
        polygon_array = np.array(self.__MoonPhase__())
        moon_outline = (Polygon(polygon_array, closed=True, color='#FFD700', alpha=1.))

        self.ax.add_patch(moon_outline)

        # Draw all tiles. Their color is red (unprocessed).
        self.tiles = []
        label_fontsize = self.configuration.conf.getint("Tile Visualization", "label fontsize")
        label_shift = self.configuration.conf.getfloat("Tile Visualization", "label shift")
        for count, t in enumerate(self.tc.list_of_tiles_sorted):
            rectangle = Rectangle((t['x_left'], t['y_bottom']), self.tc.im_w, self.tc.im_h,
                                  color='red', alpha=0.5)
            self.tiles.append(rectangle)
            x_text_pos_col = (t['x_right'] - float(t['column_index'] + 1) / float(
                t['column_total'] + 1) * self.tc.im_w)
            x_text_pos = (label_shift * x_text_pos_col + (1. - label_shift) * t['x_center'])
            plt.text(x_text_pos, t['y_center'], str(count), horizontalalignment='center',
                     verticalalignment='center', fontsize=label_fontsize)

        # Add the tiles in reversed order.
        for t in reversed(self.tiles):
            self.ax.add_patch(t)

        # Initialize the RectangleSelector with which patches of tiles can be selected later.
        toggle_selector.RS = RectangleSelector(self.ax, self.line_select_callback, drawtype='box',
                                               useblit=True, button=[1, 3],
                                               # don't use middle button
                                               minspanx=0, minspany=0, spancoords='pixels')
        plt.connect('key_press_event', toggle_selector)

        # Initialize instance variables.
        self.select_rect_x_min = None
        self.select_rect_x_max = None
        self.select_rect_y_min = None
        self.select_rect_y_max = None

        # Initialize mouse coordinates for rectangle selector.
        self.x1 = -2.
        self.x2 = -2.
        self.y1 = -2.
        self.y2 = -2.
        self.selection_rectangle = None
        self.reset_selection_rectangle()

        self.fig.canvas.set_window_title("MoonPanoramaMaker: Tile Arrangement "
                                         "in normalized orientation (see user "
                                         "guide)")
        plt.tight_layout()
        self.fig.canvas.manager.show()

    def line_select_callback(self, eclick, erelease):
        """
        Callback function, called when a rectangle has been drawn with the mouse. It draws a light
        grey rectangle on the Window to highlight the selected region.
        
        :param eclick: event object created when mouse button was clicked
        :param erelease: event object created when mouse button was released
        :return: -
        """
        # If new coordinates are as the old ones, or if the rectangle has zero width,
        # a point has been selected.
        if self.x1 == eclick.xdata and self.y1 == eclick.ydata and self.x2 == erelease.xdata and \
                self.y2 == erelease.ydata or eclick.xdata == erelease.xdata:
            self.reset_selection_rectangle()
            return

        # eclick and erelease are the press and release events, get corners of rectangle.
        self.x1, self.y1 = eclick.xdata, eclick.ydata
        self.x2, self.y2 = erelease.xdata, erelease.ydata

        # Compute corner coordinates, width and height
        self.select_rect_x_min = min(self.x1, self.x2)
        self.select_rect_x_max = max(self.x1, self.x2)
        self.select_rect_y_min = min(self.y1, self.y2)
        self.select_rect_y_max = max(self.y1, self.y2)
        width = self.select_rect_x_max - self.select_rect_x_min
        height = self.select_rect_y_max - self.select_rect_y_min

        # Not a point selected: remove previous selection_rectangle and draw a new one.
        if self.selection_rectangle is not None:
            self.ax.patches.remove(self.selection_rectangle)
        self.selection_rectangle = Rectangle((self.select_rect_x_min, self.select_rect_y_min),
                                             width, height, color='lightgrey', alpha=0.4)
        self.ax.add_patch(self.selection_rectangle)
        self.fig.canvas.draw()

    def reset_selection_rectangle(self):
        """
        Reset the selection_rectangle.
        
        :return: -
        """

        # Set the corner coordinates to values which cannot occur in reality.
        self.select_rect_x_min = -2.
        self.select_rect_x_max = -2.
        self.select_rect_y_min = -2.
        self.select_rect_y_max = -2.
        # If there is an active selection rectangle: Remove it.
        if self.selection_rectangle is not None:
            self.ax.patches.remove(self.selection_rectangle)
        self.selection_rectangle = None

    def get_selected_tile_numbers(self):
        """
        When a selection_rectangle is drawn, determine which tiles are completely contained in it.
        
        :return: list with the indices of all tiles (completely) contained in selection rectangle
        """

        selected_tile_numbers = []
        # Test for a valid x_max coordinate (rectangle was not reset).
        if self.select_rect_x_max > -1.:
            # Go through the entire tile list, start with tile 0.
            for tile_number, t in enumerate(self.tc.list_of_tiles_sorted):
                # The tile is completely contained in rectangle, add it to the list.
                if t['x_left'] >= self.select_rect_x_min and t[
                    'x_right'] <= self.select_rect_x_max and t[
                    'y_bottom'] >= self.select_rect_y_min and t['y_top'] <= self.select_rect_y_max:
                    selected_tile_numbers.append(tile_number)
        # Reset the selection_rectangle and return the tile number list.
        self.reset_selection_rectangle()
        return selected_tile_numbers

    def __MoonPhase__(self):
        """
        Internal method: Draw the current sunlit phase of the moon to a given resolution.
        
        :return: list of vertices which outline the moon phase.
        """

        moon_radius = self.m_diameter / 2.
        vertices = []

        resolution = 500  # the number of vertices for moon phase
        # Draw the outer (sunlit) moon limb, starting from the top.
        for i in range(resolution):
            phi = np.pi * (float(i) / float(resolution))
            vertices.append([moon_radius * np.sin(phi), moon_radius * np.cos(phi)])
        # Now add the terminator, starting from the bottom.
        for i in range(resolution):
            phi = np.pi * (float(resolution - i) / float(resolution))
            vertices.append(
                [moon_radius * np.sin(phi) * np.cos(self.phase_angle), moon_radius * np.cos(phi)])
        return vertices

    def mark_active(self, index):
        """
        Mark tile with index "index" as active. Set its color to "blue" and redraw the window.
        
        :param index: 
        :return: 
        """

        # Memorize this tile as "active_tile".
        self.active_tile = self.tiles[index]
        self.active_tile.set_color('blue')

    def mark_processed(self, index_list):
        """
        Mark all tiles of a list as processed. Change the "processed" field in their descriptor,
        and set their color to "skyblue" in the visualization window.
        
        :param index_list: list of tile indices.
        :return: -
        """

        for index in index_list:
            self.tc.list_of_tiles_sorted[index]['processed'] = True
            self.tiles[index].set_color('skyblue')

    def mark_all_processed(self):
        """
        Mark all tiles as processed, both in the TileConstructor list and in the visualization
        window.
        
        :return: -
        """

        for t in self.tc.list_of_tiles_sorted:
            t['processed'] = True
        for t in self.tiles:
            t.set_color('skyblue')

    def mark_unprocessed(self, index_list):
        """
        Mark all tiles of a list as unprocessed. Change the "processed" field in their descriptor,
        and set their color to "red" in the visualization window.

        :param index_list: list of tile indices.
        :return: -
        """

        for index in index_list:
            self.tc.list_of_tiles_sorted[index]['processed'] = False
            self.tiles[index].set_color('red')

    def mark_all_unprocessed(self):
        """
        Mark all tiles as unprocessed, both in the TileConstructor list and in the visualization
        window.

        :return: -
        """

        for t in self.tc.list_of_tiles_sorted:
            t['processed'] = False
        for t in self.tiles:
            t.set_color('red')

    def close_tile_visualization(self):
        """
        Save the current position of the tile visualization window in configuration and close the
        window.
        
        :return: 
        """

        (x0, y0, width, height) = self.mngr.window.geometry().getRect()
        self.configuration.conf.set('Hidden Parameters', 'tile window x0', str(x0))
        self.configuration.conf.set('Hidden Parameters', 'tile window y0', str(y0))
        plt.close()


if __name__ == "__main__":

    configuration = configuration.Configuration()

    de_center = radians(15.)
    m_diameter = radians(31. / 60.)
    phase_angle = radians(120.)
    pos_angle = radians(22.)

    tc = tile_constructor.TileConstructor(configuration, de_center, m_diameter, phase_angle,
                                          pos_angle)
    tv = TileVisualization(configuration, tc)

    for i in range(len(tv.tiles)):
        plt.pause(0.1)
        tv.mark_active(i)
        plt.pause(0.1)
        tv.mark_processed([i])

    plt.pause(2.)

    tv.mark_all_unprocessed()

    plt.pause(2.)

    tv.mark_all_processed()

    plt.pause(2.)

    tv.close_tile_visualization()

    # for i in range(10):
    #     tv = TileVisualization(configuration, tc)
    #     if i%2==0:
    #         tv.mark_all_processed()
    #     else:
    #         tv.mark_all_unprocessed()
    #     plt.pause(1)
    #     tv.close_tile_visualization()
