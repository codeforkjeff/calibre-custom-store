
import base64

from PyQt5 import QtCore, QtWidgets
from PyQt5.Qt import QWidget

from . import config
from .auth import get_all_login_handlers

class CustomStoreConfigWidget(QWidget):
    """
    Config widget displayed for this plugin under Preferences -> Plugins
    """

    def __init__(self):
        QWidget.__init__(self)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):

        self.setObjectName("Form")
        self.resize(600, 300)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        row = 1

        self.label_name_note = QtWidgets.QLabel(self)
        self.label_name_note.setObjectName("label_name_note")
        self.label_name_note.setStyleSheet("QLabel { color : red; }")
        self.gridLayout.addWidget(self.label_name_note, row, 0, 1, 2)

        row += 1

        self.label_name = QtWidgets.QLabel(self)
        self.label_name.setObjectName("label_name")
        self.label_name.setFixedWidth(200)
        self.gridLayout.addWidget(self.label_name, row, 0, 1, 1)

        self.name = QtWidgets.QLineEdit(self)
        self.name.setObjectName("name")
        self.name.setFixedWidth(350)
        self.gridLayout.addWidget(self.name, row, 1, 1, 1)

        row += 1

        self.label_desc = QtWidgets.QLabel(self)
        self.label_desc.setObjectName("label_desc")
        self.gridLayout.addWidget(self.label_desc, row, 0, 1, 1)

        self.desc = QtWidgets.QLineEdit(self)
        self.desc.setObjectName("desc")
        self.gridLayout.addWidget(self.desc, row, 1, 1, 1)

        row += 1

        self.label_opensearch_url = QtWidgets.QLabel(self)
        self.label_opensearch_url.setObjectName("label_opensearch_url")
        self.gridLayout.addWidget(self.label_opensearch_url, row, 0, 1, 1)

        self.opensearch_url = QtWidgets.QLineEdit(self)
        self.opensearch_url.setObjectName("opensearch_url")
        self.gridLayout.addWidget(self.opensearch_url, row, 1, 1, 1)

        row += 1

        self.label_auth_required = QtWidgets.QLabel(self)
        self.label_auth_required.setObjectName("label_auth_required")
        self.gridLayout.addWidget(self.label_auth_required, row, 0, 1, 1)

        self.auth_required = QtWidgets.QCheckBox(self)
        self.auth_required.setObjectName("auth_required")
        self.gridLayout.addWidget(self.auth_required, row, 1, 1, 1)

        row += 1

        self.label_auth_url = QtWidgets.QLabel(self)
        self.label_auth_url.setObjectName("label_auth_url")
        self.gridLayout.addWidget(self.label_auth_url, row, 0, 1, 1)

        self.auth_url = QtWidgets.QLineEdit(self)
        self.auth_url.setObjectName("auth_url")
        self.gridLayout.addWidget(self.auth_url, row, 1, 1, 1)

        row += 1

        self.label_login = QtWidgets.QLabel(self)
        self.label_login.setObjectName("label_login")
        self.gridLayout.addWidget(self.label_login, row, 0, 1, 1)

        self.login = QtWidgets.QLineEdit(self)
        self.login.setObjectName("login")
        self.gridLayout.addWidget(self.login, row, 1, 1, 1)

        row += 1

        self.label_password = QtWidgets.QLabel(self)
        self.label_password.setObjectName("label_password")
        self.gridLayout.addWidget(self.label_password, row, 0, 1, 1)

        self.password = QtWidgets.QLineEdit(self)
        self.password.setObjectName("password")
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.gridLayout.addWidget(self.password, row, 1, 1, 1)

        row += 1

        self.label_login_handler = QtWidgets.QLabel(self)
        self.label_login_handler.setObjectName("label_login_handler")
        self.gridLayout.addWidget(self.label_login_handler, row, 0, 1, 1)

        self.login_handler_options = [login_handler.__name__ for login_handler in get_all_login_handlers()]

        self.login_handler = QtWidgets.QComboBox(self)
        self.login_handler.setObjectName("login_handler")
        for login_handler_name in self.login_handler_options:
            self.login_handler.addItem(login_handler_name)
        self.gridLayout.addWidget(self.login_handler, row, 1, 1, 1)

        self.retranslate_ui()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslate_ui(self):
        self.setWindowTitle(_("Form"))
        self.label_name_note.setText(_("NOTE: You'll need to restart calibre for Store Name changes to take effect"))
        self.label_name.setText(_("Store Name:"))
        self.label_desc.setText(_("Description:"))
        self.label_opensearch_url.setText(_("OpenSearch Desc URL:"))
        self.label_auth_required.setText(_("Auth Required:"))
        self.label_auth_url.setText(_("Auth URL:"))
        self.label_login.setText(_("Login:"))
        self.label_password.setText(_("Password:"))

    def load_settings(self):
        self.name.setText(config.get('name'))
        self.desc.setText(config.get('description'))
        self.opensearch_url.setText(config.get('opensearch_url'))
        self.auth_required.setChecked(config.get('auth_required'))
        self.auth_url.setText(config.get('auth_url'))
        self.login.setText(config.get('login'))
        # don't load password
        login_handler_name = config.get('login_handler')
        if login_handler_name in self.login_handler_options:
            self.login_handler.setCurrentIndex(
                    self.login_handler_options.index(login_handler_name))

    def save_settings(self):
        config['name'] = unicode(self.name.text())
        config['description'] = unicode(self.desc.text())
        config['opensearch_url'] = unicode(self.opensearch_url.text())
        config['auth_required'] = self.auth_required.isChecked()
        config['auth_url'] = unicode(self.auth_url.text())
        config['login'] = unicode(self.login.text())
        config['login_handler'] = unicode(self.login_handler.currentText())
        if self.password.text():
            config['password'] = base64.b64encode(unicode(self.password.text()))
