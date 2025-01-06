import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

app = QApplication(sys.argv)
web = QWebEngineView()

# Tambahkan konfigurasi keamanan
settings = web.settings()
web.resize(800, 600)
web.load(QUrl("https://app.sandbox.midtrans.com/snap/v4/redirection/830ac4a8-5413-4837-b547-2e2332515d84"))
web.show()

app.exec_()