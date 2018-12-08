# -*- coding: utf-8; -*-
"""
Copyright (c) 2017 Rolf Hempel, rolf6419@gmx.de

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

import datetime
import os
import shutil
import time
from math import atan

import cv2
import matplotlib.pyplot as plt
from PIL.Image import fromarray
from configuration import Configuration
from miscellaneous import Miscellaneous
from numpy import ndarray, zeros_like, count_nonzero
from sklearn.cluster import DBSCAN
from socket_client import SocketClient, SocketClientDebug


class ImageShift:
    """
    The ImageShift class uses still pictures of the landmark area on the moon to measure the drift
    of the telescope. At initialization time, a reference picture is taken (at this time the user
    has brought the landmark under the camera cross hairs). During auto-alignment operations, new
    images are taken and their offset versus the reference frame is determined.

    ImageShift uses the ORB keypoint detection mechanism from OpenCV. For outlier detection in
    shift computation it uses the DBSCAN clustering algorithm from scikit-learn.

    """

    def __init__(self, configuration, camera_socket, debug=False):
        """
        Initialize the ImageShift object, capture the reference frame and find keypoints in the
        reference frame.

        :param configuration: object containing parameters set by the user
        :param camera_socket: the socket_client object used by the camera
        :param debug: if set to True, display keypoints and matches in Matplotlib windows.
        """

        self.configuration = configuration
        self.camera_socket = camera_socket

        # Initialize instance variables.
        self.shifted_image_array = None
        self.shifted_image = None
        self.shifted_image_kp = None
        self.shifted_image_des = None

        # Get camera and telescope parameters.
        pixel_size = (self.configuration.conf.getfloat("Camera", "pixel size"))
        self.focal_length = (self.configuration.conf.getfloat("Telescope", "focal length"))
        ol_inner_min_pixel = (self.configuration.conf.getint("Camera", "tile overlap pixel"))
        # The still pictures produced by the camera are reduced both in x and y pixel directions
        # by "compression_factor". Set the compression factor such that the overlap between tiles
        # is resolved in a given number of pixels (pixels_in_overlap_width). This resolution should
        # be selected such that the telescope pointing can be determined precisely enough for
        # auto-alignment.
        self.compression_factor = ol_inner_min_pixel / self.configuration.pixels_in_overlap_width
        # Compute the angle corresponding to a single pixel in the focal plane.
        self.pixel_angle = atan(pixel_size / self.focal_length)
        # Compute the angle corresponding to the overlap between tiles.
        self.ol_angle = ol_inner_min_pixel * self.pixel_angle
        # The scale value is the angle corresponding to a single pixel in the compressed camera
        # images.
        self.scale = self.compression_factor * self.pixel_angle
        self.debug = debug

        # During auto-alignment all still images captured are stored in a directory in the user's
        # home directory. If such a directory is found from an old MPM run, delete it first.
        self.image_dir = os.path.join(self.configuration.home,
                                      ".MoonPanoramaMaker_alignment_images")

        # If the directory is old, delete it first.
        if os.path.exists(self.image_dir) and time.time() - os.path.getmtime(
                self.image_dir) > self.configuration.alignment_pictures_retention_time:
            try:
                shutil.rmtree(self.image_dir)
            except:
                raise RuntimeError

        # If the directory does not exist or has just been deleted, create a new one.
        if not os.path.exists(self.image_dir):
                # Create directory for still images. In Windows this operation sometimes fails.
                # Therefore, retry until the operation is successful.
                success = False
                for retry in range(self.configuration.polling_time_out_count):
                    try:
                        os.mkdir(self.image_dir)
                        success = True
                        break
                    except:
                        if self.configuration.protocol_level > 1:
                            Miscellaneous.protocol(
                                "Warning: In imageShift, mkdir failed, retrying...")
                        plt.pause(0.1)
                # Raise a runtime error if all loop iterations were unsuccessful.
                if not success:
                    raise RuntimeError

        # The counter is used to number the alignment images captured during auto-alignment.
        self.alignment_image_counter = 0

        # Create CLAHE and ORB objects.
        self.clahe = cv2.createCLAHE(clipLimit=self.configuration.clahe_clip_limit, tileGridSize=(
            self.configuration.clahe_tile_grid_size, self.configuration.clahe_tile_grid_size))
        self.orb = cv2.ORB_create(WTA_K=self.configuration.orb_wta_k,
                                  nfeatures=self.configuration.orb_nfeatures,
                                  scoreType=cv2.ORB_HARRIS_SCORE,
                                  edgeThreshold=self.configuration.orb_edge_threshold,
                                  patchSize=self.configuration.orb_patch_size,
                                  scaleFactor=self.configuration.orb_scale_factor,
                                  nlevels=self.configuration.orb_n_levels)
        # Create BFMatcher object
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING2, crossCheck=True)

        try:
            if self.configuration.camera_debug:
                # For debugging purposes: use stored image (already compressed) from observation run
                # Begin with first stored image for every autoalignment initialization.
                self.camera_socket.image_counter = 0
                (reference_image_array, width, height,
                 dynamic) = self.camera_socket.acquire_still_image(1)
            else:
                # Capture the reference image which shows perfect alignment, apply compression.
                (reference_image_array, width, height,
                 dynamic) = self.camera_socket.acquire_still_image(self.compression_factor)

            # Normalize brightness and contrast, and determine keypoints and their descriptors.
            (self.reference_image_array, self.reference_image, self.reference_image_kp,
             self.reference_image_des) = self.normalize_and_analyze_image(reference_image_array,
                                                                    "alignment_reference_image.pgm")
        except:
            raise RuntimeError

        # Draw only keypoints location, not size and orientation
        if self.debug:
            img = cv2.drawKeypoints(self.reference_image_array, self.reference_image_kp,
                                    self.reference_image_array)
            plt.imshow(img)
            plt.show()

    def normalize_and_analyze_image(self, image_array, filename_appendix):
        """
        For an image array (as produced by the camera), optimize brightness and contrast. Store the
        image in the reference image directory. Then use ORB for keypoint detection and descriptor
        computation.

        :param image_array: Numpy array with image as produced by the camera object.
        :param filename_appendix: String to be appended to filename. The filename begins with
        the current time (hours, minutes, seconds) for later reference.
        :return: tuple with four objects: the normalized image array, the image object, the
        keypoints, and the keypoint descriptors.
        """

        # height, width = image_array.shape[:2]

        # Optimize the contrast in the image.
        normalized_image_array = self.clahe.apply(image_array)

        # Version for tests: use image (already normalized) stored at last session.
        # normalized_image_array = image_array

        # Build the normalized image from the luminance channel.
        normalized_image = fromarray(normalized_image_array, 'L')
        # Write the normalized image to disk.
        normalized_image_filename = self.build_filename() + filename_appendix
        normalized_image.save(normalized_image_filename)
        if self.configuration.protocol_level > 2:
            Miscellaneous.protocol("Still image '" + filename_appendix +
                                   " captured for auto-alignment.")
        # Use the ORB for keypoint detection
        normalized_image_kp = self.orb.detect(normalized_image_array, None)
        # Compute the descriptors with ORB
        normalized_image_kp, normalized_image_des = self.orb.compute(normalized_image_array,
                                                                     normalized_image_kp)
        return normalized_image_array, normalized_image, normalized_image_kp, normalized_image_des

    def build_filename(self):
        """
        Create the filename for an alignment image. The name begins with time info
        (hour-minutes-seconds), followed by an underscore.

        :return: filename
        """

        return os.path.join(self.image_dir, "{0}_".format(datetime.datetime.now().strftime("%H-%M-%S")))

    def shift_vs_reference(self):
        """
        Take an image through the camera_socket, normalize and analyze it, and compute the shift
        (linear translation) of this image as compared to the reference frame.

        :return: A tuple of four objects: shift in x (radians), shift in y (radians), number of
        keypoints with consistent shift values, number of outliers
        """

        filename_appendix = "alignment_image-{0:0>3}.pgm".format(self.alignment_image_counter)

        try:
            if self.configuration.camera_debug:
                # For debugging purposes: use stored image (already compressed) from observation run
                (shifted_image_array, width, height,
                 dynamic) = self.camera_socket.acquire_still_image(1)
            else:
                # Acquire a still image, apply compression.
                (shifted_image_array, width, height,
                 dynamic) = self.camera_socket.acquire_still_image(self.compression_factor)

        except:
            raise RuntimeError("Acquisition of still image failed.")

        try:
            # Normalize and analyze the image.
            (self.shifted_image_array, self.shifted_image, self.shifted_image_kp,
             self.shifted_image_des) = self.normalize_and_analyze_image(shifted_image_array,
                                                                        filename_appendix)
        except:
            raise RuntimeError("Still image normalization failed.")

        try:
            # Match descriptors.
            matches = self.bf.match(self.reference_image_des, self.shifted_image_des)
        except:
            raise RuntimeError("Descriptor matching failed.")

        # Sort them in the order of their distance.
        matches = sorted(matches, key=lambda x: x.distance)

        # Draw first 10 matches.
        if self.debug:
            img3 = cv2.drawMatches(self.reference_image_array, self.reference_image_kp,
                                   self.shifted_image_array, self.shifted_image_kp, matches[:10],
                                   None, flags=2)
            plt.imshow(img3), plt.show()

        # Set up a matrix containing for all matches the pixel shifts in x and y.
        x_matrix = ndarray(shape=(len(matches), 2), dtype=float)
        for m in range(len(matches)):
            reference_index = matches[m].queryIdx
            shifted_index = matches[m].trainIdx
            x_matrix[m][0] = self.shifted_image_kp[shifted_index].pt[0] - \
                             self.reference_image_kp[reference_index].pt[0]
            x_matrix[m][1] = self.shifted_image_kp[shifted_index].pt[1] - \
                             self.reference_image_kp[reference_index].pt[1]

        try:
            # Use DBSCAN to find the cluster with consistent shifts. Set the cluster radius and
            # minimum
            # sample size.
            db = DBSCAN(eps=self.configuration.dbscan_cluster_radius,
                        min_samples=self.configuration.dbscan_minimum_sample).fit(x_matrix)
            core_samples_mask = zeros_like(db.labels_, dtype=bool)
            core_samples_mask[db.core_sample_indices_] = True
            # The list "labels" defines the cluster number for each match. Only the first cluster
            # (with number 0) will be used.
            labels = db.labels_
        except:
            raise RuntimeError("Shift clustering failed.")

        # Compute the average shift for all matches within the cluster.
        x_shift = 0.
        y_shift = 0.
        for m in range(len(matches)):
            if labels[m] == 0:
                x_shift += x_matrix[m][0]
                y_shift += x_matrix[m][1]
            #     # For debugging: print detailed shift values for cluster members and outliers.
            #     print("in Cluster: x=" + str(x_matrix[m][0]) + ", y=" + str(x_matrix[m][1]))
            # else:
            #     print("out of Cluster: x=" + str(x_matrix[m][0]) + ", y=" + str(x_matrix[m][1]))
        self.alignment_image_counter += 1
        # Count the matches outside the cluster (i.e. with label!=0).
        outliers = count_nonzero(labels)
        # Compute number of matches in the cluster. If it is too low (<10), raise a RuntimeError.
        in_cluster = (len(labels) - outliers)
        if in_cluster < self.configuration.dbscan_minimum_in_cluster:
            raise RuntimeError("Image shift computation # " + str(
                self.alignment_image_counter - 1) + " failed, consistent shifts: " + str(
                in_cluster) + ", outliers: " + str(outliers) + ".")
        # Translate the average shift values into radians.
        else:
            x_shift = (x_shift / in_cluster) * self.scale
            y_shift = (y_shift / in_cluster) * self.scale
            return x_shift, y_shift, in_cluster, outliers


if __name__ == "__main__":
    # Time (UT):  2015/10/26 20:55:00
    # pos_angle = radians(-39.074)
    # de_center = radians(6.736)

    configuration = Configuration()
    host = 'localhost'
    port = configuration.fire_capture_port_number
    if configuration.camera_debug:
        mysocket = SocketClientDebug(host, port, configuration.camera_debug_delay)
    else:
        mysocket = SocketClient(host, port)
    print("Client: socket connected")
    iso = ImageShift(configuration, mysocket, debug=configuration.alignment_debug)
    try:
        shift_x, shift_y, in_cluster, outliers = iso.shift_vs_reference()
        print("shift in x: ", shift_x, ", shift in y: ", shift_y)
        print("Number of consistent measurements: ", in_cluster)
        print("Number of outliers: ", outliers)
    except RuntimeError as e:
        print(e)
