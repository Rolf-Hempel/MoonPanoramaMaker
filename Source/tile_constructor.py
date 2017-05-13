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

from math import ceil, sqrt, cos, atan

import configuration
from miscellaneous import Miscellaneous


class TileConstructor:
    def __init__(self, configuration, de_center, m_diameter, phase_angle,
                 pos_angle):

        self.de_center = de_center
        self.m_diameter = m_diameter
        self.phase_angle = phase_angle
        self.pos_angle = pos_angle
        self.m_radius = m_diameter / 2.
        pixel_size = (configuration.conf.getfloat(
            "Camera", "pixel size"))
        focal_length = (configuration.conf.getfloat(
            "Telescope", "focal length"))

        im_h_pixel = configuration.conf.getint("Camera", "pixel vertical")
        im_w_pixel = (configuration.conf.getint(
            "Camera", "pixel horizontal"))
        ol_outer_pixel = (configuration.conf.getint(
            "Camera", "external margin pixel"))
        ol_inner_min_pixel = (configuration.conf.getint(
            "Camera", "tile overlap pixel"))
        self.im_h = float(im_h_pixel) * atan(pixel_size / focal_length)
        self.im_w = float(im_w_pixel) * atan(pixel_size / focal_length)
        self.ol_outer = float(ol_outer_pixel) * atan(pixel_size / focal_length)
        self.ol_inner_min = (float(ol_inner_min_pixel)
                             * atan(pixel_size / focal_length))
        self.flip_x = 1.
        self.flip_y = 1.
        self.scale_factor = 1.

        self.limb_first = (configuration.conf.getboolean(
            "Workflow", "limb first"))

        n_rows = ((m_diameter + 2. * self.ol_outer - self.ol_inner_min) /
                  (self.im_h - self.ol_inner_min))
        # print "n_rows: ", n_rows
        self.n_rows_corrected = int(ceil(n_rows))
        # print "n_rows rounded: ", self.n_rows_corrected
        if self.n_rows_corrected > 1:
            self.ol_inner_v = ((self.n_rows_corrected * self.im_h - m_diameter
                                - 2. * self.ol_outer) / (
                                   self.n_rows_corrected - 1.))
        else:
            self.ol_inner_v = self.ol_inner_min
        # print "ol_inner_v: ", self.ol_inner_v

        self.lists_of_tiles = []
        max_cols = 0

        for i in range(self.n_rows_corrected):
            y_top = (self.m_radius + self.ol_outer
                     - i * (self.im_h - self.ol_inner_v))
            y_bottom = y_top - self.im_h
            # print "i: ", i, ", y_top: ", y_top, ", y_bottom:", y_bottom
            x_limb_top = (sqrt(self.m_radius ** 2
                               - min(y_top ** 2, self.m_radius ** 2)))
            x_limb_bottom = (sqrt(self.m_radius ** 2
                                  - min(y_bottom ** 2, self.m_radius ** 2)))
            # print ("x_limb_top: ", x_limb_top,
            #        ", x_limb_bottom: ", x_limb_bottom)
            if y_top * y_bottom > 0.:
                x_max = max(x_limb_top, x_limb_bottom)
                x_min = (min(x_limb_top * cos(phase_angle),
                             x_limb_bottom * cos(phase_angle)))
            else:
                x_max = self.m_radius
                if cos(phase_angle) < 0.:
                    x_min = self.m_radius * cos(phase_angle)
                else:
                    x_min = (min(x_limb_top * cos(phase_angle),
                                 x_limb_bottom * cos(phase_angle)))

                    # print "x_min: ", x_min, ", x_max:", x_max

            row_of_tiles = []
            n_cols = (
                (x_max - x_min + 2. * self.ol_outer - self.ol_inner_min) /
                (self.im_w - self.ol_inner_min))
            # print "n_cols: ", n_cols
            n_cols_corrected = int(ceil(n_cols))
            # print "n_cols rounded: ", n_cols_corrected
            max_cols = max(max_cols, n_cols_corrected)
            if n_cols_corrected > 1:
                ol_inner_h = ((n_cols_corrected * self.im_w - x_max + x_min
                               - 2. * self.ol_outer) / (n_cols_corrected - 1.))
            else:
                ol_inner_h = self.ol_inner_min
            # print "ol_inner_h: ", ol_inner_h
            for j in range(n_cols_corrected):
                tile = {}
                tile['row_index'] = i
                tile['column_index'] = j
                tile['column_total'] = n_cols_corrected
                tile['x_right'] = (x_max + self.ol_outer
                                   - j * (self.im_w - ol_inner_h))
                tile['x_left'] = tile['x_right'] - self.im_w
                tile['y_top'] = y_top
                tile['y_bottom'] = y_bottom
                tile['x_center'] = (tile['x_right'] + tile['x_left']) / 2.
                tile['y_center'] = (tile['y_top'] + tile['y_bottom']) / 2.
                [tile['delta_ra_center'], tile['delta_de_center']] = (
                    Miscellaneous.rotate(self.pos_angle, self.de_center,
                                         self.scale_factor, self.flip_x,
                                         self.flip_y, tile['x_center'],
                                         tile['y_center']))
                row_of_tiles.append(tile)

            self.lists_of_tiles.append(row_of_tiles)

        # print " "
        # print "max_cols: ", max_cols

        self.list_of_tiles_sorted = []
        if self.limb_first:
            for j in range(max_cols, 0, -1):
                for i in range(self.n_rows_corrected):
                    if j <= len(self.lists_of_tiles[i]):
                        (self.list_of_tiles_sorted.append(
                            self.lists_of_tiles[i][
                                len(self.lists_of_tiles[i]) - j]))
                        # print ("tile i: ", i, ", j: ",
                        #        len(self.lists_of_tiles[i])-j, " appended")
        else:
            for j in range(max_cols):
                for i in range(self.n_rows_corrected):
                    if (j) < len(self.lists_of_tiles[i]):
                        (self.list_of_tiles_sorted.append(
                            self.lists_of_tiles[i]
                            [len(self.lists_of_tiles[i]) - j - 1]))
                        # print ("tile i: ", i, ", j: ",
                        #        len(self.lists_of_tiles[i])-j-1, " appended")

                        # print ("length of sorted list: ",
                        #        len(self.list_of_tiles_sorted))
        [self.delta_ra_limb_center, self.delta_de_limb_center] = (
            Miscellaneous.rotate(self.pos_angle, self.de_center,
                                 self.scale_factor, self.flip_x,
                                 self.flip_y, self.m_radius, 0.))


if __name__ == "__main__":
    from math import radians, degrees

    configuration = configuration.Configuration()
    de_center = radians(6.736112)
    m_diameter = radians(0.562625)
    phase_angle = radians(170.678)
    pos_angle = radians(-39.066)

    tc = TileConstructor(configuration, de_center, m_diameter, phase_angle,
                         pos_angle)

    print "Construction of tiles:"
    for i in range(len(tc.lists_of_tiles)):
        row_of_tiles = tc.lists_of_tiles[i]
        print " "
        print "row number i:", i
        for j in range(len(row_of_tiles)):
            tile = row_of_tiles[j]
            print ("tile no.: ", j, ", x_left: ", tile['x_left'],
                   ", x_right: ", tile['x_right'],
                   ", y_top: ", tile['y_top'], ", y_bottom: ",
                   tile['y_bottom'])

    print " "
    print "Sorted list of ", len(tc.list_of_tiles_sorted), " tiles:"
    tile_no = 0
    for tile in tc.list_of_tiles_sorted:
        print ("Tile no: ", tile_no, ", Row index: ", tile['row_index'],
               ", Column index: ", tile['column_index'],
               ", (x,y): ", tile['x_center'], tile['y_center'],
               ", (dRA,dDe): ", degrees(tile['delta_ra_center']),
               degrees(tile['delta_de_center']))
        tile_no += 1

    tile_no = 0
    for tile in tc.list_of_tiles_sorted:
        ra_center = 23.4861097 + degrees(tile['delta_ra_center'])
        de_center = 6.736112 + degrees(tile['delta_de_center'])
        print "Tile no: ", tile_no, \
            ", (RA,DE Center): ", ra_center, de_center
        tile_no += 1

    print " "
    print ("Limb center coordinates: d_RA: ", tc.delta_ra_limb_center,
           ", d_DE: ", tc.delta_de_limb_center)
