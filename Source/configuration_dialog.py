# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'configuration_dialog.ui'
#
# Created: Sun Jul 23 18:01:26 2017
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ConfigurationDialog(object):
    def setupUi(self, ConfigurationDialog):
        ConfigurationDialog.setObjectName(_fromUtf8("ConfigurationDialog"))
        ConfigurationDialog.resize(879, 933)
        self.gridLayout_2 = QtGui.QGridLayout(ConfigurationDialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.scrollArea = QtGui.QScrollArea(ConfigurationDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setSizeIncrement(QtCore.QSize(0, 0))
        self.scrollArea.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 857, 880))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.input_polling_interval = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_polling_interval.setFont(font)
        self.input_polling_interval.setToolTip(_fromUtf8(""))
        self.input_polling_interval.setObjectName(_fromUtf8("input_polling_interval"))
        self.gridLayout.addWidget(self.input_polling_interval, 27, 2, 1, 4)
        self.fig_size_horizontal = QtGui.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fig_size_horizontal.sizePolicy().hasHeightForWidth())
        self.fig_size_horizontal.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.fig_size_horizontal.setFont(font)
        self.fig_size_horizontal.setObjectName(_fromUtf8("fig_size_horizontal"))
        self.gridLayout.addWidget(self.fig_size_horizontal, 18, 0, 1, 1)
        self.tile_visualization = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.tile_visualization.setFont(font)
        self.tile_visualization.setObjectName(_fromUtf8("tile_visualization"))
        self.gridLayout.addWidget(self.tile_visualization, 17, 0, 1, 1)
        self.input_limb_first = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_limb_first.setFont(font)
        self.input_limb_first.setObjectName(_fromUtf8("input_limb_first"))
        self.gridLayout.addWidget(self.input_limb_first, 14, 2, 1, 4)
        self.input_camera_automation = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_camera_automation.setFont(font)
        self.input_camera_automation.setObjectName(_fromUtf8("input_camera_automation"))
        self.gridLayout.addWidget(self.input_camera_automation, 15, 2, 1, 4)
        self.camera_automation = QtGui.QLabel(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_automation.sizePolicy().hasHeightForWidth())
        self.camera_automation.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.camera_automation.setFont(font)
        self.camera_automation.setObjectName(_fromUtf8("camera_automation"))
        self.gridLayout.addWidget(self.camera_automation, 15, 0, 1, 1)
        self.polling_interval = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.polling_interval.setFont(font)
        self.polling_interval.setObjectName(_fromUtf8("polling_interval"))
        self.gridLayout.addWidget(self.polling_interval, 27, 0, 1, 1)
        self.timezone = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.timezone.setFont(font)
        self.timezone.setObjectName(_fromUtf8("timezone"))
        self.gridLayout.addWidget(self.timezone, 4, 0, 1, 1)
        self.longitude = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.longitude.setFont(font)
        self.longitude.setObjectName(_fromUtf8("longitude"))
        self.gridLayout.addWidget(self.longitude, 1, 0, 1, 1)
        self.name = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.name.setFont(font)
        self.name.setObjectName(_fromUtf8("name"))
        self.gridLayout.addWidget(self.name, 6, 0, 1, 1)
        self.hub = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.hub.setFont(font)
        self.hub.setObjectName(_fromUtf8("hub"))
        self.gridLayout.addWidget(self.hub, 24, 0, 1, 1)
        self.elevation = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.elevation.setFont(font)
        self.elevation.setObjectName(_fromUtf8("elevation"))
        self.gridLayout.addWidget(self.elevation, 3, 0, 1, 1)
        self.latitude = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.latitude.setFont(font)
        self.latitude.setObjectName(_fromUtf8("latitude"))
        self.gridLayout.addWidget(self.latitude, 2, 0, 1, 1)
        self.chooser = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.chooser.setFont(font)
        self.chooser.setObjectName(_fromUtf8("chooser"))
        self.gridLayout.addWidget(self.chooser, 23, 0, 1, 1)
        self.label_shift = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_shift.setFont(font)
        self.label_shift.setObjectName(_fromUtf8("label_shift"))
        self.gridLayout.addWidget(self.label_shift, 21, 0, 1, 1)
        self.geographical_position = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("MS Shell Dlg 2"))
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.geographical_position.setFont(font)
        self.geographical_position.setObjectName(_fromUtf8("geographical_position"))
        self.gridLayout.addWidget(self.geographical_position, 0, 0, 1, 1)
        self.fig_size_vertical = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.fig_size_vertical.setFont(font)
        self.fig_size_vertical.setObjectName(_fromUtf8("fig_size_vertical"))
        self.gridLayout.addWidget(self.fig_size_vertical, 19, 0, 1, 1)
        self.label_font_size = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_font_size.setFont(font)
        self.label_font_size.setObjectName(_fromUtf8("label_font_size"))
        self.gridLayout.addWidget(self.label_font_size, 20, 0, 1, 1)
        self.ASCOM = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.ASCOM.setFont(font)
        self.ASCOM.setObjectName(_fromUtf8("ASCOM"))
        self.gridLayout.addWidget(self.ASCOM, 22, 0, 1, 1)
        self.camera = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.camera.setFont(font)
        self.camera.setObjectName(_fromUtf8("camera"))
        self.gridLayout.addWidget(self.camera, 5, 0, 1, 1)
        self.workflow = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.workflow.setFont(font)
        self.workflow.setObjectName(_fromUtf8("workflow"))
        self.gridLayout.addWidget(self.workflow, 10, 0, 1, 1)
        self.camera_trigger_delay = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.camera_trigger_delay.setFont(font)
        self.camera_trigger_delay.setObjectName(_fromUtf8("camera_trigger_delay"))
        self.gridLayout.addWidget(self.camera_trigger_delay, 16, 0, 1, 1)
        self.focal_length = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.focal_length.setFont(font)
        self.focal_length.setObjectName(_fromUtf8("focal_length"))
        self.gridLayout.addWidget(self.focal_length, 9, 0, 1, 1)
        self.wait_interval = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.wait_interval.setFont(font)
        self.wait_interval.setObjectName(_fromUtf8("wait_interval"))
        self.gridLayout.addWidget(self.wait_interval, 26, 0, 1, 1)
        self.edit_camera = QtGui.QPushButton(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edit_camera.sizePolicy().hasHeightForWidth())
        self.edit_camera.setSizePolicy(sizePolicy)
        self.edit_camera.setMinimumSize(QtCore.QSize(0, 0))
        self.edit_camera.setMaximumSize(QtCore.QSize(45, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.edit_camera.setFont(font)
        self.edit_camera.setObjectName(_fromUtf8("edit_camera"))
        self.gridLayout.addWidget(self.edit_camera, 6, 3, 1, 1)
        self.camera_chooser = QtGui.QComboBox(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.camera_chooser.setFont(font)
        self.camera_chooser.setObjectName(_fromUtf8("camera_chooser"))
        self.gridLayout.addWidget(self.camera_chooser, 6, 2, 1, 1)
        self.new_camera = QtGui.QPushButton(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.new_camera.sizePolicy().hasHeightForWidth())
        self.new_camera.setSizePolicy(sizePolicy)
        self.new_camera.setMinimumSize(QtCore.QSize(0, 0))
        self.new_camera.setMaximumSize(QtCore.QSize(45, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.new_camera.setFont(font)
        self.new_camera.setObjectName(_fromUtf8("new_camera"))
        self.gridLayout.addWidget(self.new_camera, 6, 4, 1, 1)
        self.delete_camera = QtGui.QPushButton(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.delete_camera.sizePolicy().hasHeightForWidth())
        self.delete_camera.setSizePolicy(sizePolicy)
        self.delete_camera.setMinimumSize(QtCore.QSize(0, 0))
        self.delete_camera.setMaximumSize(QtCore.QSize(45, 16777215))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.delete_camera.setFont(font)
        self.delete_camera.setObjectName(_fromUtf8("delete_camera"))
        self.gridLayout.addWidget(self.delete_camera, 6, 5, 1, 1)
        self.input_longitude = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_longitude.setFont(font)
        self.input_longitude.setObjectName(_fromUtf8("input_longitude"))
        self.gridLayout.addWidget(self.input_longitude, 1, 2, 1, 4)
        self.input_latitude = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_latitude.setFont(font)
        self.input_latitude.setObjectName(_fromUtf8("input_latitude"))
        self.gridLayout.addWidget(self.input_latitude, 2, 2, 1, 4)
        self.input_elevation = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_elevation.setFont(font)
        self.input_elevation.setObjectName(_fromUtf8("input_elevation"))
        self.gridLayout.addWidget(self.input_elevation, 3, 2, 1, 4)
        self.input_timezone = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_timezone.setFont(font)
        self.input_timezone.setObjectName(_fromUtf8("input_timezone"))
        self.gridLayout.addWidget(self.input_timezone, 4, 2, 1, 4)
        self.input_focal_length = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_focal_length.setFont(font)
        self.input_focal_length.setObjectName(_fromUtf8("input_focal_length"))
        self.gridLayout.addWidget(self.input_focal_length, 9, 2, 1, 4)
        self.input_fig_size_horizontal = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_fig_size_horizontal.setFont(font)
        self.input_fig_size_horizontal.setObjectName(_fromUtf8("input_fig_size_horizontal"))
        self.gridLayout.addWidget(self.input_fig_size_horizontal, 18, 2, 1, 4)
        self.input_fig_size_vertical = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_fig_size_vertical.setFont(font)
        self.input_fig_size_vertical.setObjectName(_fromUtf8("input_fig_size_vertical"))
        self.gridLayout.addWidget(self.input_fig_size_vertical, 19, 2, 1, 4)
        self.input_label_font_size = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_label_font_size.setFont(font)
        self.input_label_font_size.setObjectName(_fromUtf8("input_label_font_size"))
        self.gridLayout.addWidget(self.input_label_font_size, 20, 2, 1, 4)
        self.input_label_shift = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_label_shift.setFont(font)
        self.input_label_shift.setObjectName(_fromUtf8("input_label_shift"))
        self.gridLayout.addWidget(self.input_label_shift, 21, 2, 1, 4)
        self.input_chooser = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_chooser.setFont(font)
        self.input_chooser.setObjectName(_fromUtf8("input_chooser"))
        self.gridLayout.addWidget(self.input_chooser, 23, 2, 1, 4)
        self.input_hub = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_hub.setFont(font)
        self.input_hub.setObjectName(_fromUtf8("input_hub"))
        self.gridLayout.addWidget(self.input_hub, 24, 2, 1, 4)
        self.input_wait_interval = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_wait_interval.setFont(font)
        self.input_wait_interval.setObjectName(_fromUtf8("input_wait_interval"))
        self.gridLayout.addWidget(self.input_wait_interval, 26, 2, 1, 4)
        self.telescope = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.telescope.setFont(font)
        self.telescope.setObjectName(_fromUtf8("telescope"))
        self.gridLayout.addWidget(self.telescope, 8, 0, 1, 1)
        self.limb_first = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.limb_first.setFont(font)
        self.limb_first.setObjectName(_fromUtf8("limb_first"))
        self.gridLayout.addWidget(self.limb_first, 14, 0, 1, 1)
        self.input_camera_trigger_delay = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_camera_trigger_delay.setFont(font)
        self.input_camera_trigger_delay.setObjectName(_fromUtf8("input_camera_trigger_delay"))
        self.gridLayout.addWidget(self.input_camera_trigger_delay, 16, 2, 1, 4)
        self.telescope_lookup_precision = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.telescope_lookup_precision.setFont(font)
        self.telescope_lookup_precision.setObjectName(_fromUtf8("telescope_lookup_precision"))
        self.gridLayout.addWidget(self.telescope_lookup_precision, 28, 0, 1, 1)
        self.input_telescope_lookup_precision = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_telescope_lookup_precision.setFont(font)
        self.input_telescope_lookup_precision.setObjectName(_fromUtf8("input_telescope_lookup_precision"))
        self.gridLayout.addWidget(self.input_telescope_lookup_precision, 28, 2, 1, 4)
        self.protocol_to_file = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.protocol_to_file.setFont(font)
        self.protocol_to_file.setObjectName(_fromUtf8("protocol_to_file"))
        self.gridLayout.addWidget(self.protocol_to_file, 12, 0, 1, 1)
        self.input_protocol_to_file = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_protocol_to_file.setFont(font)
        self.input_protocol_to_file.setObjectName(_fromUtf8("input_protocol_to_file"))
        self.gridLayout.addWidget(self.input_protocol_to_file, 12, 2, 1, 4)
        self.protocol_level = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.protocol_level.setFont(font)
        self.protocol_level.setObjectName(_fromUtf8("protocol_level"))
        self.gridLayout.addWidget(self.protocol_level, 11, 0, 1, 1)
        self.input_protocol_level = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_protocol_level.setFont(font)
        self.input_protocol_level.setObjectName(_fromUtf8("input_protocol_level"))
        self.gridLayout.addWidget(self.input_protocol_level, 11, 2, 1, 4)
        self.guiding_interval = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.guiding_interval.setFont(font)
        self.guiding_interval.setObjectName(_fromUtf8("guiding_interval"))
        self.gridLayout.addWidget(self.guiding_interval, 25, 0, 1, 1)
        self.input_guiding_interval = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_guiding_interval.setFont(font)
        self.input_guiding_interval.setObjectName(_fromUtf8("input_guiding_interval"))
        self.gridLayout.addWidget(self.input_guiding_interval, 25, 2, 1, 4)
        self.max_autoalign_interval = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.max_autoalign_interval.setFont(font)
        self.max_autoalign_interval.setObjectName(_fromUtf8("max_autoalign_interval"))
        self.gridLayout.addWidget(self.max_autoalign_interval, 32, 0, 1, 1)
        self.min_autoalign_interval = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.min_autoalign_interval.setFont(font)
        self.min_autoalign_interval.setObjectName(_fromUtf8("min_autoalign_interval"))
        self.gridLayout.addWidget(self.min_autoalign_interval, 31, 0, 1, 1)
        self.input_min_autoalign_interval = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.input_min_autoalign_interval.setMinimumSize(QtCore.QSize(0, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_min_autoalign_interval.setFont(font)
        self.input_min_autoalign_interval.setObjectName(_fromUtf8("input_min_autoalign_interval"))
        self.gridLayout.addWidget(self.input_min_autoalign_interval, 31, 2, 1, 4)
        self.ALIGNMENT = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.ALIGNMENT.setFont(font)
        self.ALIGNMENT.setObjectName(_fromUtf8("ALIGNMENT"))
        self.gridLayout.addWidget(self.ALIGNMENT, 30, 0, 1, 1)
        self.input_max_autoalign_interval = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_max_autoalign_interval.setFont(font)
        self.input_max_autoalign_interval.setObjectName(_fromUtf8("input_max_autoalign_interval"))
        self.gridLayout.addWidget(self.input_max_autoalign_interval, 32, 2, 1, 4)
        self.input_max_alignment_error = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_max_alignment_error.setFont(font)
        self.input_max_alignment_error.setObjectName(_fromUtf8("input_max_alignment_error"))
        self.gridLayout.addWidget(self.input_max_alignment_error, 33, 2, 1, 4)
        self.max_alignment_error = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.max_alignment_error.setFont(font)
        self.max_alignment_error.setObjectName(_fromUtf8("max_alignment_error"))
        self.gridLayout.addWidget(self.max_alignment_error, 33, 0, 1, 1)
        self.foxus_on_star = QtGui.QLabel(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.foxus_on_star.setFont(font)
        self.foxus_on_star.setObjectName(_fromUtf8("foxus_on_star"))
        self.gridLayout.addWidget(self.foxus_on_star, 13, 0, 1, 1)
        self.input_focus_on_star = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.input_focus_on_star.setFont(font)
        self.input_focus_on_star.setObjectName(_fromUtf8("input_focus_on_star"))
        self.gridLayout.addWidget(self.input_focus_on_star, 13, 2, 1, 4)
        self.verticalLayout.addLayout(self.gridLayout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_2.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(ConfigurationDialog)
        self.buttonBox.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(ConfigurationDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), ConfigurationDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), ConfigurationDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ConfigurationDialog)
        ConfigurationDialog.setTabOrder(self.scrollArea, self.input_longitude)
        ConfigurationDialog.setTabOrder(self.input_longitude, self.input_latitude)
        ConfigurationDialog.setTabOrder(self.input_latitude, self.input_elevation)
        ConfigurationDialog.setTabOrder(self.input_elevation, self.input_timezone)
        ConfigurationDialog.setTabOrder(self.input_timezone, self.camera_chooser)
        ConfigurationDialog.setTabOrder(self.camera_chooser, self.edit_camera)
        ConfigurationDialog.setTabOrder(self.edit_camera, self.new_camera)
        ConfigurationDialog.setTabOrder(self.new_camera, self.delete_camera)
        ConfigurationDialog.setTabOrder(self.delete_camera, self.input_focal_length)
        ConfigurationDialog.setTabOrder(self.input_focal_length, self.input_protocol_level)
        ConfigurationDialog.setTabOrder(self.input_protocol_level, self.input_protocol_to_file)
        ConfigurationDialog.setTabOrder(self.input_protocol_to_file, self.input_focus_on_star)
        ConfigurationDialog.setTabOrder(self.input_focus_on_star, self.input_limb_first)
        ConfigurationDialog.setTabOrder(self.input_limb_first, self.input_camera_automation)
        ConfigurationDialog.setTabOrder(self.input_camera_automation, self.input_camera_trigger_delay)
        ConfigurationDialog.setTabOrder(self.input_camera_trigger_delay, self.input_fig_size_horizontal)
        ConfigurationDialog.setTabOrder(self.input_fig_size_horizontal, self.input_fig_size_vertical)
        ConfigurationDialog.setTabOrder(self.input_fig_size_vertical, self.input_label_font_size)
        ConfigurationDialog.setTabOrder(self.input_label_font_size, self.input_label_shift)
        ConfigurationDialog.setTabOrder(self.input_label_shift, self.input_chooser)
        ConfigurationDialog.setTabOrder(self.input_chooser, self.input_hub)
        ConfigurationDialog.setTabOrder(self.input_hub, self.input_guiding_interval)
        ConfigurationDialog.setTabOrder(self.input_guiding_interval, self.input_wait_interval)
        ConfigurationDialog.setTabOrder(self.input_wait_interval, self.input_polling_interval)
        ConfigurationDialog.setTabOrder(self.input_polling_interval, self.input_telescope_lookup_precision)
        ConfigurationDialog.setTabOrder(self.input_telescope_lookup_precision, self.input_min_autoalign_interval)
        ConfigurationDialog.setTabOrder(self.input_min_autoalign_interval, self.input_max_autoalign_interval)
        ConfigurationDialog.setTabOrder(self.input_max_autoalign_interval, self.input_max_alignment_error)
        ConfigurationDialog.setTabOrder(self.input_max_alignment_error, self.buttonBox)

    def retranslateUi(self, ConfigurationDialog):
        ConfigurationDialog.setWindowTitle(_translate("ConfigurationDialog", "Confgturation", None))
        self.fig_size_horizontal.setToolTip(_translate("ConfigurationDialog", "Horizontal dimension of tile visualization window in inches. Must be between 0. and 25.", None))
        self.fig_size_horizontal.setText(_translate("ConfigurationDialog", "Figure size horizontal (inch)", None))
        self.tile_visualization.setText(_translate("ConfigurationDialog", "Tile Visualization", None))
        self.camera_automation.setToolTip(_translate("ConfigurationDialog", "True, if FireCapture should be triggered automatically, False otherwise", None))
        self.camera_automation.setText(_translate("ConfigurationDialog", "Camera automation (True / False)", None))
        self.polling_interval.setToolTip(_translate("ConfigurationDialog", "Time interval between processing of two external device instructions, e.g. 0.1. Must be between 0. and 1.", None))
        self.polling_interval.setText(_translate("ConfigurationDialog", "Polling interval", None))
        self.timezone.setToolTip(_translate("ConfigurationDialog", "Daylight saving time is accounted for automatically", None))
        self.timezone.setText(_translate("ConfigurationDialog", "Timezone (e.g. Europe/Berlin)", None))
        self.longitude.setToolTip(_translate("ConfigurationDialog", "Geographical longitude, counted from Greenwich, in degrees plus decimal fraction. Must be between -360. and 360.", None))
        self.longitude.setText(_translate("ConfigurationDialog", "Longitude (degrees, east positiv)", None))
        self.name.setToolTip(_translate("ConfigurationDialog", "Any text to represent camera, must be unique in list", None))
        self.name.setText(_translate("ConfigurationDialog", "Brand / Name", None))
        self.hub.setToolTip(_translate("ConfigurationDialog", "ASCOM hub to connect more than one program to telescope driver, e.g. POTH.Telescope", None))
        self.hub.setText(_translate("ConfigurationDialog", "Hub", None))
        self.elevation.setToolTip(_translate("ConfigurationDialog", "Elevation above sea level in meters. Must be between -100 and 9000", None))
        self.elevation.setText(_translate("ConfigurationDialog", "Elevation (m)", None))
        self.latitude.setToolTip(_translate("ConfigurationDialog", "Geographical latitude, positive towards north, in degrees plus decimal fraction. Must be between -90. and 90.", None))
        self.latitude.setText(_translate("ConfigurationDialog", "Latitude (degrees)", None))
        self.chooser.setToolTip(_translate("ConfigurationDialog", "ASCOM chooser to select telescope driver, e.g. ASCOM.Utilities.Chooser", None))
        self.chooser.setText(_translate("ConfigurationDialog", "Chooser", None))
        self.label_shift.setToolTip(_translate("ConfigurationDialog", "0. for tile numbers to be centered in tiles. Larger values may be needed to avoid cluttering", None))
        self.label_shift.setText(_translate("ConfigurationDialog", "Label shift parameter (0.<=p<=1.)  ", None))
        self.geographical_position.setText(_translate("ConfigurationDialog", "Geographical Position", None))
        self.fig_size_vertical.setToolTip(_translate("ConfigurationDialog", "Vertical dimension of tile visualization window in inches. Must be between 0. and 25.", None))
        self.fig_size_vertical.setText(_translate("ConfigurationDialog", "Figure size vertical (inch)", None))
        self.label_font_size.setToolTip(_translate("ConfigurationDialog", "Font size for tile numbers in visualization window. Must be between 6 and 16", None))
        self.label_font_size.setText(_translate("ConfigurationDialog", "Font size for labels (points)", None))
        self.ASCOM.setText(_translate("ConfigurationDialog", "ASCOM", None))
        self.camera.setText(_translate("ConfigurationDialog", "Camera", None))
        self.workflow.setText(_translate("ConfigurationDialog", "Workflow", None))
        self.camera_trigger_delay.setToolTip(_translate("ConfigurationDialog", "Time between slewing to new tile and exposure start", None))
        self.camera_trigger_delay.setText(_translate("ConfigurationDialog", "Camera trigger delay (s)", None))
        self.focal_length.setToolTip(_translate("ConfigurationDialog", "Focal length of telescope system, including projection lens. Must be between 0. and 100000.", None))
        self.focal_length.setText(_translate("ConfigurationDialog", "Focal length (mm)", None))
        self.wait_interval.setToolTip(_translate("ConfigurationDialog", "Parameter to reduce polling frequency during telescope slewing, e.g. 1. Must be between 0. and 20.", None))
        self.wait_interval.setText(_translate("ConfigurationDialog", "Wait interval (s)", None))
        self.edit_camera.setToolTip(_translate("ConfigurationDialog", "Edit parameters of currently selected camera", None))
        self.edit_camera.setText(_translate("ConfigurationDialog", "Edit", None))
        self.camera_chooser.setToolTip(_translate("ConfigurationDialog", "List of cameras for which parameters have been entered", None))
        self.new_camera.setToolTip(_translate("ConfigurationDialog", "Enter parameters for new camera", None))
        self.new_camera.setText(_translate("ConfigurationDialog", "New", None))
        self.delete_camera.setToolTip(_translate("ConfigurationDialog", "Remove currently selected camera from list", None))
        self.delete_camera.setText(_translate("ConfigurationDialog", "Del", None))
        self.telescope.setText(_translate("ConfigurationDialog", "Telescope", None))
        self.limb_first.setToolTip(_translate("ConfigurationDialog", "True, if tiles at the bright Moon limb should be recorded first, False if to start at terminator", None))
        self.limb_first.setText(_translate("ConfigurationDialog", "Limb first (True / False)", None))
        self.telescope_lookup_precision.setToolTip(_translate("ConfigurationDialog", "Required precision (\") for lookup of telescope position. Must be between 0.1 and 10.", None))
        self.telescope_lookup_precision.setText(_translate("ConfigurationDialog", "Telescope position lookup precision (\")", None))
        self.protocol_to_file.setToolTip(_translate("ConfigurationDialog", "Append session protocol to file \"MoonPanoramaMaker.log\" in home directory", None))
        self.protocol_to_file.setText(_translate("ConfigurationDialog", "Write protocol to file (True / False)", None))
        self.protocol_level.setToolTip(_translate("ConfigurationDialog", "Select level of detail for session protocol (0=No protocol)", None))
        self.protocol_level.setText(_translate("ConfigurationDialog", "Session protocol level (0, 1, 2, 3)", None))
        self.guiding_interval.setToolTip(_translate("ConfigurationDialog", "Duration of guiding pulses during video exposure, e.g. 0.2. Must be between 0. and 3.", None))
        self.guiding_interval.setText(_translate("ConfigurationDialog", "Guide pulse duration (s)", None))
        self.max_autoalign_interval.setToolTip(_translate("ConfigurationDialog", "Maximum time between auto-alignments (s). Must be between 30. and 3600.", None))
        self.max_autoalign_interval.setText(_translate("ConfigurationDialog", "Maximum auto-alignment interval (s)", None))
        self.min_autoalign_interval.setToolTip(_translate("ConfigurationDialog", "Minimum time between auto-alignments (s). Must be between 20. and 1800.", None))
        self.min_autoalign_interval.setText(_translate("ConfigurationDialog", "Minimum auto-alignment interval (s)", None))
        self.ALIGNMENT.setText(_translate("ConfigurationDialog", "ALIGNMENT", None))
        self.max_alignment_error.setToolTip(_translate("ConfigurationDialog", "Maximum allowed auto-alignment error (% of overlap width). Must be between 10. and 60.", None))
        self.max_alignment_error.setText(_translate("ConfigurationDialog", "Max alignment error (%)", None))
        self.foxus_on_star.setText(_translate("ConfigurationDialog", "Focus on a star (True / False)", None))
        self.buttonBox.setToolTip(_translate("ConfigurationDialog", "Save all parameters to configuration file or discard all changes", None))
