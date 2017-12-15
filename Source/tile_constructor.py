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
    """
    This class compute the optimal coverage of the sunlit part of the moon with video "tiles". A
    minimal overlap between tiles can be specified as well as the minimal width of the empty space
    around the moon panorama.
    
    The tile construction is done in a "normalized" orientation where the connection line between
    the horns of the sunlit phase is vertical and the sunlit limb points towards the right. Please
    note that in this orientation a waning phase is standing south up.
    
    """

    def __init__(self, configuration, de_center, m_diameter, phase_angle, pos_angle):
        """
        Read out parameters from the configuration object and compute the optimal tile coverage.
        
        :param configuration: object containing parameters set by the user
        :param de_center: declination of the moon's center (radians)
        :param m_diameter: diameter of the moon (radians)
        :param phase_angle: phase angle of the sunlit moon phase (0. for New Moon, Pi for Full Moon)
        :param pos_angle: angle (radians) between North and the "North Pole" of the sunlit phase,
        counted counterclockwise
        """

        # Set ephemeris data used in tile construction
        self.de_center = de_center
        self.m_diameter = m_diameter
        self.phase_angle = phase_angle
        self.pos_angle = pos_angle
        self.m_radius = m_diameter / 2.

        # Configuration data
        pixel_size = (configuration.conf.getfloat("Camera", "pixel size"))
        focal_length = (configuration.conf.getfloat("Telescope", "focal length"))
        im_h_pixel = configuration.conf.getint("Camera", "pixel vertical")
        im_w_pixel = (configuration.conf.getint("Camera", "pixel horizontal"))
        ol_outer_pixel = (configuration.conf.getint("Camera", "external margin pixel"))
        ol_inner_min_pixel = (configuration.conf.getint("Camera", "tile overlap pixel"))
        self.limb_first = (configuration.conf.getboolean("Workflow", "limb first"))

        # Height / width of the image, external margin width and tile overlap in radians
        self.im_h = float(im_h_pixel) * atan(pixel_size / focal_length)
        self.im_w = float(im_w_pixel) * atan(pixel_size / focal_length)
        self.ol_outer = float(ol_outer_pixel) * atan(pixel_size / focal_length)
        self.ol_inner_min = (float(ol_inner_min_pixel) * atan(pixel_size / focal_length))

        # Auxiliary parameters used by the "rotate" method in module miscellaneous
        self.flip_x = 1.
        self.flip_y = 1.
        self.scale_factor = 1.

        # Compute the minimum number of tile rows needed to fulfill overlap requirements.
        n_rows = (
        (m_diameter + 2. * self.ol_outer - self.ol_inner_min) / (self.im_h - self.ol_inner_min))
        # Round up to next integer.
        self.n_rows_corrected = int(ceil(n_rows))
        # Increase the vertical tile overlap such that the external margin width is as specified.
        if self.n_rows_corrected > 1:
            self.ol_inner_v = (
            (self.n_rows_corrected * self.im_h - m_diameter - 2. * self.ol_outer) / (
                self.n_rows_corrected - 1.))
        # Only one row of tiles (very unlikely though)
        else:
            self.ol_inner_v = self.ol_inner_min

        # Initialize the tile structure: All tiles in one row form a list. These lists are collected
        # in "lists_of_tiles".
        self.lists_of_tiles = []
        # Initialize the maximum number of tiles in a row.
        max_cols = 0

        # Construct each row of tiles. The origin of the (x,y) coordinate system is at the moon
        # center, x pointing right, y up. x and y are in radians.
        for i in range(self.n_rows_corrected):
            # Compute the y coordinates for the top and bottom of the row.
            y_top = (self.m_radius + self.ol_outer - i * (self.im_h - self.ol_inner_v))
            y_bottom = y_top - self.im_h
            # Compute the x coordinates where the moon limb crosses the top and bottom of the row.
            x_limb_top = (sqrt(self.m_radius ** 2 - min(y_top ** 2, self.m_radius ** 2)))
            x_limb_bottom = (sqrt(self.m_radius ** 2 - min(y_bottom ** 2, self.m_radius ** 2)))
            # The row of tiles does not contain the x axis. The sunlit phase attains its maximum
            # and minimum x values at the top or bottom.
            if y_top * y_bottom > 0.:
                x_max = max(x_limb_top, x_limb_bottom)
                x_min = (min(x_limb_top * cos(phase_angle), x_limb_bottom * cos(phase_angle)))
            # The row of tiles straddles the x axis: the maximal x value of the phase is the
            # moon's radius.
            else:
                x_max = self.m_radius
                # Terminator left of y axix: the easy case.
                if cos(phase_angle) < 0.:
                    x_min = self.m_radius * cos(phase_angle)
                # Terminator to the right of y axis: The minimum x value is attained either at the
                # top or bottom.
                else:
                    x_min = (min(x_limb_top * cos(phase_angle), x_limb_bottom * cos(phase_angle)))

            # Construct the row of tiles. It must span the x interval [x_min, x_max].
            row_of_tiles = []
            # As above for the y coordinate, compute the minimum number of tiles and round up.
            n_cols = ((x_max - x_min + 2. * self.ol_outer - self.ol_inner_min) / (
            self.im_w - self.ol_inner_min))
            n_cols_corrected = int(ceil(n_cols))
            # Update the maximal number of tiles in a row.
            max_cols = max(max_cols, n_cols_corrected)
            # If there is more than one tile in the row: Increase the horizontal tile overlap in
            # this row so that the outer margin is as specified.
            if n_cols_corrected > 1:
                ol_inner_h = (
                (n_cols_corrected * self.im_w - x_max + x_min - 2. * self.ol_outer) / (
                n_cols_corrected - 1.))
            else:
                ol_inner_h = self.ol_inner_min
            # For each tile of this row: Collect all data for this tile in a dictionary.
            for j in range(n_cols_corrected):
                tile = {}
                tile['row_index'] = i
                tile['column_index'] = j
                tile['column_total'] = n_cols_corrected
                tile['x_right'] = (x_max + self.ol_outer - j * (self.im_w - ol_inner_h))
                tile['x_left'] = tile['x_right'] - self.im_w
                tile['y_top'] = y_top
                tile['y_bottom'] = y_bottom
                tile['x_center'] = (tile['x_right'] + tile['x_left']) / 2.
                tile['y_center'] = (tile['y_top'] + tile['y_bottom']) / 2.
                # rotate the (x,y) coordinates to get displacements in (RA,DE) relative to the
                # moon center. Note the approximate correction of the RA displacement because of
                # the moon's declination.
                [tile['delta_ra_center'], tile['delta_de_center']] = (
                    Miscellaneous.rotate(self.pos_angle, self.de_center, self.scale_factor,
                                         self.flip_x, self.flip_y, tile['x_center'],
                                         tile['y_center']))
                # Append the tile to its row.
                row_of_tiles.append(tile)

            # A row of tiles is completed, append it to the global structure.
            self.lists_of_tiles.append(row_of_tiles)

        # Put all tiles in a sequential order. The numbering goes through columns of tiles, always
        # from top to bottom. Depending on parameter "limb first", the process starts at the sunlit
        # limb or at the terminator.
        self.list_of_tiles_sorted = []
        # Start at the sunlit limb.
        if self.limb_first:
            for j in range(max_cols, 0, -1):
                for i in range(self.n_rows_corrected):
                    # Not in all rows there are "max_cols" tiles.
                    if j <= len(self.lists_of_tiles[i]):
                        (self.list_of_tiles_sorted.append(
                            self.lists_of_tiles[i][len(self.lists_of_tiles[i]) - j]))

        # Start at the terminator.
        else:
            for j in range(max_cols):
                for i in range(self.n_rows_corrected):
                    if (j) < len(self.lists_of_tiles[i]):
                        (self.list_of_tiles_sorted.append(
                            self.lists_of_tiles[i][len(self.lists_of_tiles[i]) - j - 1]))

        # Compute the (RA,DE) offsets from moon center for the midpoint on the sunlit limb. The
        # coordinates of this point are (m_radius, 0.) in the (x,y) coordinate system. Rotate into
        # (RA,DE) system.
        [self.delta_ra_limb_center, self.delta_de_limb_center] = (
            Miscellaneous.rotate(self.pos_angle, self.de_center, self.scale_factor, self.flip_x,
                                 self.flip_y, self.m_radius, 0.))


if __name__ == "__main__":
    from math import radians, degrees

    configuration = configuration.Configuration()
    de_center = radians(6.736112)
    m_diameter = radians(0.562625)
    phase_angle = radians(170.678)
    pos_angle = radians(-39.066)

    tc = TileConstructor(configuration, de_center, m_diameter, phase_angle, pos_angle)

    print("Construction of tiles:")
    for i in range(len(tc.lists_of_tiles)):
        row_of_tiles = tc.lists_of_tiles[i]
        print(" ")
        print("row number i:", i)
        for j in range(len(row_of_tiles)):
            tile = row_of_tiles[j]
            print(("tile no.: ", j, ", x_left: ", tile['x_left'], ", x_right: ", tile['x_right'],
                   ", y_top: ", tile['y_top'], ", y_bottom: ", tile['y_bottom']))

    print(" ")
    print("Sorted list of ", len(tc.list_of_tiles_sorted), " tiles:")
    tile_no = 0
    for tile in tc.list_of_tiles_sorted:
        print(("Tile no: ", tile_no, ", Row index: ", tile['row_index'], ", Column index: ",
               tile['column_index'], ", (x,y): ", tile['x_center'], tile['y_center'],
               ", (dRA,dDe): ", degrees(tile['delta_ra_center']), degrees(tile['delta_de_center'])))
        tile_no += 1

    tile_no = 0
    for tile in tc.list_of_tiles_sorted:
        ra_center = 23.4861097 + degrees(tile['delta_ra_center'])
        de_center = 6.736112 + degrees(tile['delta_de_center'])
        print("Tile no: ", tile_no, ", (RA,DE Center): ", ra_center, de_center)
        tile_no += 1

    print(" ")
    print((
    "Limb center coordinates: d_RA: ", tc.delta_ra_limb_center, ", d_DE: ", tc.delta_de_limb_center))
