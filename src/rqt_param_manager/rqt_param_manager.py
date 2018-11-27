# -*- coding: utf-8 -*-

import sys
import os
import rospy
import rospkg


from qt_gui.plugin import Plugin

from python_qt_binding import loadUi
from python_qt_binding import QtGui
from python_qt_binding.QtWidgets import (
    QWidget,
    QTableWidgetItem,
    QItemDelegate,
    QHeaderView,
)

LOG_HEADER = "<RqtParamManagerPlugin>"


class NotEditableDelegate(QItemDelegate):
    def __init__(self, *args):
        super(NotEditableDelegate, self).__init__(*args)

    def createEditor(self, parent, option, index):
        return None

    def editorEvent(self, event, model, option, index):
        return False


class RqtParamManagerPlugin(Plugin):
    def __init__(self, context):
        super(RqtParamManagerPlugin, self).__init__(context)

        # クラス変数初期化
        self.title = "不明"
        self.get_interval = 0
        self.dump_yaml_file_path = ""
        self.params = {}

        self.setObjectName('RqtParamManagerPlugin')

        resultLoadConfFile = self._loadConfFile(sys.argv)

        # Create QWidget
        self._widget = QWidget()
        ui_file = os.path.join(
            rospkg.RosPack().get_path('rqt_param_manager'),
            'resource',
            'RqtParamManagerPlugin.ui'
        )

        loadUi(ui_file, self._widget)

        self._widget.setObjectName('RqtParamManagerPluginUi')
        self._widget.setWindowTitle(self.title)

        serNum = context.serial_number()
        if serNum > 1:
            self._widget.setWindowTitle(
                self._widget.windowTitle() + (' (%d)' % serNum))

        context.add_widget(self._widget)

        self._setupParamsTable(self._widget.tblParams)

    def _setupParamsTable(self, table):
        table.setColumnCount(3)

        # dummy data
        table.setRowCount(200)
        table.setItem(0, 0, QTableWidgetItem("ABC"))
        table.setItem(0, 1, QTableWidgetItem("CDE"))
        table.setItem(0, 2, QTableWidgetItem("GHI"))

        # 列1,2は編集不可
        noEditDelegate = NotEditableDelegate()
        table.setItemDelegateForColumn(0, noEditDelegate)
        table.setItemDelegateForColumn(1, noEditDelegate)

        # header columns
        headerCol1 = QTableWidgetItem()
        headerCol1.setText("パラメータ名")
        table.setHorizontalHeaderItem(0, headerCol1)

        headerCol2 = QTableWidgetItem()
        headerCol2.setText("現在値")
        table.setHorizontalHeaderItem(1, headerCol2)

        headerCol3 = QTableWidgetItem()
        headerCol3.setText("更新値")
        table.setHorizontalHeaderItem(2, headerCol3)

        # header resize
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        table.setColumnWidth(1, 120)
        table.setColumnWidth(2, 120)

        table.verticalHeader().hide()

    def shutdown_plugin(self):
        # TODO unregister all publishers here
        pass

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        # instance_settings.set_value(k, v)
        pass

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        # v = instance_settings.value(k)
        pass

    # def trigger_configuration(self):
        # Comment in to signal that the plugin has a way
        # to configure
        # This will enable a setting button (gear icon)
        # in each dock widget title bar
        # Usually used to open a modal configuration dialog

    def _loadConfFile(self, argv):
        result = False

        if not len(sys.argv) > 1:
            rospy.logerr("%s argv '_conffile' is not specified.", LOG_HEADER)
        else:
            tokens = sys.argv[1].split(":=")
            if len(tokens) == 2 and tokens[0] == "_conffile":
                confFilePath = tokens[1]
                result = self._parseConfFile(confFilePath)
            else:
                rospy.logerr(
                    "%s argv '_conffile' is wrong format. %s",
                    LOG_HEADER,
                    sys.argv[1]
                )

        return result

    def _parseConfFile(self, confFilePath):
        result = False

        rospy.loginfo("%s load conf file. path=%s", LOG_HEADER, confFilePath)
        import json
        try:
            f = open(confFilePath, 'r')
            json_dict = json.load(f)
            # print('json_dict:{}'.format(type(json_dict)))
            # print json_dict["title"]
            self.title = json_dict["title"]
            self.get_interval = json_dict["getInterval"]
            self.dump_yaml_file_path = json_dict["dumpYaml"]

            rospy.loginfo(
                "%s title=%s",
                LOG_HEADER,
                self.title.encode('utf-8')
            )
            rospy.loginfo(
                "%s getInterval=%s",
                LOG_HEADER,
                self.get_interval
            )
            rospy.loginfo(
                "%s dumpYaml=%s",
                LOG_HEADER,
                self.dump_yaml_file_path.encode('utf-8')
            )

            self.params = json_dict["params"]
        except IOError as e:
            print (e)
            rospy.logerr("%s json file load failed. %s", LOG_HEADER, e)

        return result
