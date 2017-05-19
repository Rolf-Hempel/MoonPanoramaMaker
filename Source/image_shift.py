import datetime
import os
import shutil
from math import atan

import cv2
import matplotlib.pyplot as plt
from Image import fromarray
from numpy import ndarray, zeros_like, count_nonzero
from sklearn.cluster import DBSCAN

from configuration import Configuration
from socket_client import SocketClientDebug


class ImageShift:
    def __init__(self, configuration, camera_socket, debug=False):
        self.configuration = configuration
        self.camera_socket = camera_socket
        self.pixel_size = (self.configuration.conf.getfloat(
            "Camera", "pixel size"))
        self.focal_length = (self.configuration.conf.getfloat(
            "Telescope", "focal length"))
        self.ol_inner_min_pixel = (self.configuration.conf.getint(
            "Camera", "tile overlap pixel"))
        self.compression_factor = self.ol_inner_min_pixel / 40
        self.pixel_angle = atan(self.pixel_size / self.focal_length)
        self.ol_angle = self.ol_inner_min_pixel * self.pixel_angle
        self.scale = self.compression_factor * self.pixel_angle
        self.debug = debug

        home = os.path.expanduser("~")
        self.image_dir = home + "\\MoonPanoramaMaker_alignment_images"
        try:
            shutil.rmtree(self.image_dir)
        except:
            pass
        for retry in range(100):
            try:
                os.mkdir(self.image_dir)
                break
            except:
                print "mkdir failed, retrying..."

        self.alignment_image_counter = 0

        # create CLAHE and ORB objects.
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        self.orb = cv2.ORB_create(WTA_K=3, nfeatures=50,
                                  scoreType=cv2.ORB_HARRIS_SCORE,
                                  edgeThreshold=30, patchSize=31,
                                  scaleFactor=1.2, nlevels=8)
        # create BFMatcher object
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING2, crossCheck=True)

        (reference_image_array, width, height, dynamic) = \
            self.camera_socket.acquire_still_image(self.compression_factor)

        (self.reference_image_array, self.reference_image,
         self.reference_image_kp, self.reference_image_des) = \
            self.normalize_and_analyze_image(reference_image_array,
                                             "alignment_reference_image.pgm")

        # draw only keypoints location,not size and orientation
        if self.debug:
            img = cv2.drawKeypoints(self.reference_image_array,
                                    self.reference_image_kp,
                                    self.reference_image_array)
            plt.imshow(img)
            plt.show()

    def normalize_and_analyze_image(self, image_array, filename_appendix):
        height, width = image_array.shape[:2]

        normalized_image_array = self.clahe.apply(image_array)
        normalized_image = fromarray(normalized_image_array, 'L')

        normalized_image_filename = self.build_filename() + filename_appendix
        normalized_image.save(normalized_image_filename)
        normalized_image_kp = self.orb.detect(normalized_image_array, None)
        # compute the descriptors with ORB
        normalized_image_kp, normalized_image_des = self.orb.compute(
            normalized_image_array, normalized_image_kp)
        return (normalized_image_array, normalized_image, normalized_image_kp,
                normalized_image_des)

    def build_filename(self):
        dt = str(datetime.datetime.now())
        return (self.image_dir + "\\" + dt[11:13] + "-" + dt[14:16] + "-" + \
                dt[17:19] + "_")

    def shift_vs_reference(self):
        filename_appendix = "alignment_image-" + "{0:0>3}".format(
            self.alignment_image_counter) + ".pgm"

        (shifted_image_array, width, height, dynamic) = \
            self.camera_socket.acquire_still_image(self.compression_factor)
        (self.shifted_image_array, self.shifted_image, self.shifted_image_kp,
         self.shifted_image_des) = \
            self.normalize_and_analyze_image(shifted_image_array,
                                             filename_appendix)

        # Match descriptors.
        matches = self.bf.match(self.reference_image_des,
                                self.shifted_image_des)

        # Sort them in the order of their distance.
        matches = sorted(matches, key=lambda x: x.distance)

        # Draw first 10 matches.
        if self.debug:
            img3 = cv2.drawMatches(self.reference_image_array,
                                   self.reference_image_kp,
                                   self.shifted_image_array,
                                   self.shifted_image_kp,
                                   matches[:10], None, flags=2)
            plt.imshow(img3), plt.show()

        X_matrix = ndarray(shape=(len(matches), 2), dtype=float)
        for m in range(len(matches)):
            reference_index = matches[m].queryIdx
            shifted_index = matches[m].trainIdx
            X_matrix[m][0] = self.shifted_image_kp[shifted_index].pt[0] - \
                             self.reference_image_kp[reference_index].pt[0]
            X_matrix[m][1] = self.shifted_image_kp[shifted_index].pt[1] - \
                             self.reference_image_kp[reference_index].pt[1]

        db = DBSCAN(eps=3., min_samples=10).fit(X_matrix)
        core_samples_mask = zeros_like(db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True
        labels = db.labels_

        x_shift = 0.
        y_shift = 0.
        for m in range(len(matches)):
            if labels[m] == 0:
                x_shift += X_matrix[m][0]
                y_shift += X_matrix[m][1]
        self.alignment_image_counter += 1
        outliers = count_nonzero(labels)
        in_cluster = (len(labels) - outliers)
        if in_cluster < 10:
            raise RuntimeError(
                "Image shift computation # " +
                str(self.alignment_image_counter - 1) +
                " failed, consistent shifts: " + str(in_cluster) +
                ", outliers: " + str(outliers))
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
    port = 9820
    mysocket = SocketClientDebug(host, port)
    print "Client: socket connected"
    iso = ImageShift(configuration, mysocket, debug=False)
    try:
        shift_x, shift_y, in_cluster, outliers = iso.shift_vs_reference()
        print "shift in x: ", shift_x, ", shift in y: ", shift_y
        print "Number of consistent measurements: ", in_cluster
        print "Number of outliers: ", outliers
    except RuntimeError as e:
        print e
