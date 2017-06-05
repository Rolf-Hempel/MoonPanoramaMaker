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

import sys
sys.setrecursionlimit(5000)

import os
import shutil
from distutils.core import setup

import py2exe

import matplotlib
import pytz

setup(windows=[{"script": "moon_panorama_maker.py"}],
      options={"py2exe": {
          "includes": ["alignment", "camera", "camera_configuration_delete",
                       "camera_configuration_editor",
                       "camera_configuration_input", "camera_delete_dialog",
                       "camera_dialog", "compute_drift_rate", "configuration",
                       "configuration_dialog", "configuration_editor",
                       "DisplayLandmark",
                       "drift_rate_dialog", "edit_landmarks", "image_shift",
                       "input_error_dialog", "landmark_selection",
                       "matplotlibwidget",
                       "miscellaneous", "moon_ephem", "qtgui",
                       "show_input_error", "show_landmark", "socket_client",
                       "telescope",
                       "tile_constructor", "tile_number_input_dialog",
                       "tile_visualization", "ViewLandmarks", "workflow",
                       "scipy.sparse.csgraph._validation", "scipy.special._ufuncs_cxx",
                       "sklearn.utils.lgamma", "sklearn.neighbors.typedefs",
                       "sklearn.utils.sparsetools._graph_validation",
                       "sklearn.utils.weight_vector"],
          "excludes": ['pytz'],
          'packages': ['matplotlib', 'bisect'],
      }},
      data_files=matplotlib.get_py2exe_datafiles(), )

# Deal with the pytz problem. It was excluded in the above operation.
srcDir = os.path.dirname(pytz.__file__)
dstDir = os.path.join('dist', 'pytz')
shutil.copytree(srcDir, dstDir, ignore=shutil.ignore_patterns('*.py'))
