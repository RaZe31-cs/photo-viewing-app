import math
import os
import sqlite3
import sys
import hashlib
from PyQt5.QtCore import QTimer
from PIL import Image, ImageOps
from PyQt5 import uic
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QPushButton, QMessageBox, \
    QLineEdit, QTextEdit, QWidget, QLabel, QColorDialog

FOLDER_PATH = os.getcwd().replace('\\', '/')[:-5] + '/photo_open_In_Folder/open_folder.ui'
HOME_PATH = os.getcwd().replace('\\', '/')[:-5] + '/home/home.ui'
PROTO_OPEN = os.getcwd().replace('\\', '/')[:-5] + '/photo_open/phot_open.ui'
LOGIN = os.getcwd().replace('\\', '/')[:-5] + '/login/login_Window.ui'
DECORATE = os.getcwd().replace('\\', '/')[:-5] + '/photo_open/Widget_Change_Photo.ui'

con = sqlite3.Connection(os.getcwd().replace('\\', '/')[:-5] + "/Photo_Manager.sqlite")
cur = con.cursor()


class Login(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        uic.loadUi(LOGIN, self)

        self.pushButton.clicked.connect(self.reg)
        self.pushButton_2.clicked.connect(self.log)

        self.lineEdit.setMaxLength(15)
        self.lineEdit_2.setEchoMode(QLineEdit.EchoMode.Password)
        self.login = ''

    def log(self):
        if self.lineEdit.text().strip() != '' and self.lineEdit_2.text().strip() != '':
            try:
                res = (cur.execute(f"SELECT password FROM Users WHERE Users.login = '{self.lineEdit.text().strip()}'").
                       fetchall())[0]
                password = self.lineEdit_2.text().strip() + '5gz'
                login = self.lineEdit.text().strip()
                hash_password = hashlib.md5(password.encode()).hexdigest()
                if hash_password == res[0]:
                    self.ex = Home(self, login)
                    self.ex.show()
                    self.close()
                else:
                    self.statusBar().showMessage('Неверный пароль')
                    QTimer.singleShot(7000, lambda: self.statusBar().showMessage(''))
            except Exception:
                self.statusBar().showMessage('Нет пользователя с таким логином')
        else:
            self.statusBar().showMessage(
                'Проверьте, содержит ли ваше поле Пароль минимум 8 символов, и что бы поле Логин не был пустой')
            QTimer.singleShot(7000, lambda: self.statusBar().showMessage(''))

    def reg(self):
        if self.lineEdit.text().strip() != '' and len(self.lineEdit_2.text()) >= 8:
            password = self.lineEdit_2.text().strip() + '5gz'
            login = self.lineEdit.text().strip()
            hash_password = hashlib.md5(password.encode()).hexdigest()
            try:
                cur.execute(f"INSERT INTO Users(login, password) VALUES('{login}', '{hash_password}')")
                con.commit()
                self.statusBar().showMessage('Вы успешно зарегистрировались!')
            except sqlite3.IntegrityError:
                self.statusBar().showMessage('Пользователь с таким логином уже существует')
        else:
            self.statusBar().showMessage(
                'Проверьте, содержит ли ваше поле Пароль минимум 8 символов, и что бы поле Логин не был пустой')
        QTimer.singleShot(7000, lambda: self.statusBar().showMessage(''))


class Decorate(QWidget):
    def __init__(self, object_photo):
        super().__init__()
        uic.loadUi(DECORATE, self)
        self.object_photo = object_photo
        self.initUi()

    def frame(self, path):
        img_old = Image.open(path)
        color = QColorDialog.getColor()
        return ImageOps.expand(img_old, border=30, fill=(color.red(), color.green(), color.blue()))

    def white_black(self, path):
        img_old = Image.open(path)
        return img_old.convert('L')

    def initUi(self):
        self.list_chekbox = [self.checkBox_2, self.checkBox]
        self.pushButton.clicked.connect(self.check)

    def check(self):
        for i in self.list_chekbox:
            if i.isChecked():
                dlg = QMessageBox(self)
                dlg.setInformativeText("Вы действительно хотите изменить фото. Фото будет нельзя вернуть")
                dlg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                dlg.show()
                dlg.exec()
                if dlg.clickedButton().text() == 'OK':
                    self.changePhoto()
                self.close()

    def changePhoto(self):
        for i in self.list_chekbox:
            if i.isChecked():
                if i.text() == 'Рамка':
                    try:
                        image_new = self.frame(self.object_photo.dict_sender_photo[self.object_photo.a])
                        image_new.save(self.object_photo.dict_sender_photo[self.object_photo.a], format='PNG')
                    except Exception as e:
                        with open(os.getcwd().replace('\\', '/')[:-5] + '/warning.txt', mode='w', encoding='utf8') as f:
                            f.write(str(e))
                elif i.text() == 'Черно белое':
                    image_new = self.white_black(self.object_photo.dict_sender_photo[self.object_photo.a])
                    image_new.save(self.object_photo.dict_sender_photo[self.object_photo.a])
        self.object_photo.pixmap = QPixmap(self.object_photo.dict_sender_photo[self.object_photo.a])
        self.object_photo.pixmap = self.object_photo.pixmap.scaled(QSize(self.object_photo.label.width(),
                                                                         self.object_photo.label.height()),
                                                                   Qt.KeepAspectRatio,
                                                                   Qt.SmoothTransformation)
        self.object_photo.label.setPixmap(self.object_photo.pixmap)


class AddBd(QWidget):
    def __init__(self, p):
        super().__init__()
        self.p = p
        self.setGeometry(500, 500, 200, 150)
        self.setStyleSheet("""background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(108, 
        73, 0, 255), stop:1 rgba(52, 0, 50, 255));""")
        self.initUi()

    def initUi(self):
        self.setMouseTracking(True)
        self.style_widget = """
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(108, 100, 0, 255), stop:1 rgba(52, 0, 50, 255));
        border-radius: 13px;
        border: 2px solid;
        color: rgb(255, 85, 255);
        font-color: rgb(255, 85, 255);"""
        self.txt_widget = QTextEdit(self)
        self.txt_widget.setGeometry(0, 0, 200, 100)
        self.lbl = QLabel('Напишите заметку для данного фото', self)
        self.lbl.setGeometry(0, 100, 200, 20)
        self.txt_widget.setStyleSheet(self.style_widget)

        self.btn_ok = QPushButton('OK', self)
        self.btn_ok.setStyleSheet(self.style_widget)
        self.btn_cancel = QPushButton('Cancel', self)
        self.btn_cancel.setStyleSheet(self.style_widget)
        self.btn_cancel.clicked.connect(self.dont_bd)
        self.btn_ok.setGeometry(0, 120, 50, 30)
        self.btn_ok.clicked.connect(self.add_to_bd)
        self.btn_cancel.setGeometry(150, 120, 50, 30)

    def add_to_bd(self):
        id = cur.execute(f"""
        SELECT id FROM Users
        WHERE login = '{self.p.parent.login}'
        """).fetchone()
        cur.execute("""
        INSERT INTO Photo(user_id, photo, comment) 
        VALUES(?, ?, ?)
        """, (id[0], self.p.dict_sender_photo[self.p.a], self.txt_widget.toPlainText()))
        con.commit()
        self.p.statusBar().showMessage('Фотография успешно загружена в базу данных')
        QTimer.singleShot(5000, lambda: self.p.statusBar().showMessage(''))
        self.close()

    def dont_bd(self):
        self.close()


class Photo_widget(QMainWindow):
    def __init__(self, dict_sender_photo, a=1, parent=None, flag=False):
        super().__init__()
        uic.loadUi(PROTO_OPEN, self)
        self.flag = flag
        self.dict_sender_photo = dict_sender_photo
        self.a = a
        self.parent = parent
        self.initUi()

    def initUi(self):
        self.textEdit.hide()
        res = cur.execute("""SELECT comment FROM Photo WHERE photo = ? AND user_id = (SELECT id FROM Users
        WHERE login = ?)""",
                          (self.dict_sender_photo[self.a], self.parent.login)).fetchone()
        if res is not None:
            self.textEdit.show()
            self.textEdit.setPlainText(res[0])
            self.textEdit.setReadOnly(True)

        self.statusBar().setStyleSheet('color: rgb(66, 100, 185);')

        self.btn_back.setIcon(QIcon(os.getcwd().replace('\\', '/')[:-5] + '/icon/back.png'))
        self.btn_back.clicked.connect(self.go_back)

        self.btn_delete.setIcon(QIcon(os.getcwd().replace('\\', '/')[:-5] + '/icon/recycle-bin.png'))
        self.btn_delete.clicked.connect(self.delete)

        self.btn_rotate_270.setIcon(
            QIcon(os.getcwd().replace('\\', '/')[:-5] + '/icon/icons8-поверните-против-часовой-стрелки-50.png'))
        self.btn_rotate_270.clicked.connect(self.rotate270)

        self.btn_rotate_90.setIcon(
            QIcon(os.getcwd().replace('\\', '/')[:-5] + '/icon/imgonline-com-ua-Mirror-JyRoM3atKQ.png'))
        self.btn_rotate_90.clicked.connect(self.rotate90)

        self.btn_zoom.setIcon(QIcon(os.getcwd().replace('\\', '/')[:-5] + '/icon/zoom.png'))
        self.btn_zoom.clicked.connect(self.zoom)

        self.btn_unzoom.setIcon(QIcon(os.getcwd().replace('\\', '/')[:-5] + '/icon/unzoom.png'))
        self.btn_unzoom.clicked.connect(self.unzoom)

        self.btn_decorate.setIcon(QIcon(os.getcwd().replace('\\', '/')[:-5] + '/icon/image-editing.png'))

        self.pixmap = QPixmap(str(self.dict_sender_photo[self.a]))
        self.pixmap = self.pixmap.scaled(QSize(self.label.width(),
                                               self.label.height()),
                                         Qt.KeepAspectRatio,
                                         Qt.SmoothTransformation)
        self.label.setPixmap(self.pixmap)
        self.label.setAlignment(Qt.AlignCenter)

        self.btn_save.setIcon(QIcon(os.getcwd().replace('\\', '/')[:-5] + '/icon/save.png'))
        self.btn_save.clicked.connect(self.save_photo)

        self.btn_add_bd.clicked.connect(self.add_photo_TO_bd)

        self.btn_decorate.clicked.connect(self.decorate_photo)

        self.flag_zoom = False

    def decorate_photo(self):
        self.decorate_Widget = Decorate(self)
        self.decorate_Widget.show()

    def add_photo_TO_bd(self):
        self.widget_add_bd = AddBd(p=self)
        self.widget_add_bd.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.go_back()

    def unzoom(self):
        self.label.setPixmap(self.pixmap)

    def zoom(self):
        self.setCursor(Qt.PointingHandCursor)
        self.flag_zoom = True

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.flag_zoom:
            imageX = (self.label.x() + self.label.width() // 2) - (self.pixmap.width() // 2)
            imageY = ((self.label.y() + self.label.height() // 2) - (self.pixmap.height() // 2))
            self.pixmapzoom = self.pixmap.copy(event.x() - imageX - 60,
                                               event.y() - imageY - 60, 200, 200)
            self.pixmapzoom = self.pixmapzoom.scaled(QSize(self.label.width(),
                                                           self.label.height()),
                                                     Qt.KeepAspectRatio,
                                                     Qt.SmoothTransformation)
            self.label.setPixmap(self.pixmapzoom)
            self.setCursor(Qt.ArrowCursor)
            self.flag_zoom = False

    def go_back(self):
        self.hide()

    def rotate90(self):
        t = QtGui.QTransform().rotate(90)
        self.pixmap = self.pixmap.transformed(t)
        # self.pixmap = self.pixmap.scaled(QSize(self.label.width(),
        #                                        self.label.height()),
        #                                  Qt.KeepAspectRatio,
        #                                  Qt.SmoothTransformation)
        self.label.setPixmap(self.pixmap)

    def rotate270(self):
        t = QtGui.QTransform().rotate(270)
        self.pixmap = self.pixmap.transformed(t)
        # self.pixmap = self.pixmap.scaled(QSize(self.label.width(),
        #                                        self.label.height()),
        #                                  Qt.KeepAspectRatio,
        #                                  Qt.SmoothTransformation)
        self.label.setPixmap(self.pixmap)

    def delete(self):
        self.dlg = QMessageBox()
        self.dlg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.dlg.show()
        self.dlg.setWindowTitle("Удаление")
        self.dlg.setInformativeText("Удалить текущее фото?")
        self.dlg.exec()
        if self.dlg.clickedButton().text() == 'OK':
            os.remove(str(self.dict_sender_photo[self.a]))
            if self.parent != None:
                self.parent.dict_sender_photo.pop(self.a)
                self.parent.write_photo_in_file_after_delete()
            self.go_back()

    def save_photo(self):
        file_name, flag = QFileDialog.getSaveFileName(self, "Save File", "", "All Files(*);;Text Files(*.txt)")
        if file_name is True:
            self.statusBar().showMessage('Фото успешно сохранено')
            QTimer.singleShot(4000, lambda: self.statusBar().showMessage(''))


class Home(QMainWindow):
    def __init__(self, parent, login):
        super().__init__()
        uic.loadUi(HOME_PATH, self)
        self.login = login
        self.initUI_home()
        self.dict_sender_photo = {}
        self.dirlist = None

    def initUI_home(self):
        self.openFolder_button.clicked.connect(self.open_folder)
        self.openPhoto_button.clicked.connect(self.open_photo_home)
        self.btn_open_photo_in_bd.clicked.connect(self.open_private_photo)

    def initUI_folder(self):
        self.home_button.setIcon(QIcon(os.getcwd().replace('\\', '/')[:-5] + '/icon/Home-icon.svg.png'))
        self.home_button.setIconSize(QSize(30, 30))
        self.home_button.clicked.connect(self.open_home)
        self.files_no_photo.setReadOnly(True)

        self.gridLayout_4.setSpacing(30)

        self.open_newFolder_button.clicked.connect(self.open_folder)

    def open_private_photo(self):
        self.dirlist = None
        uic.loadUi(FOLDER_PATH, self)
        self.initUI_folder()
        self.files_no_photo.hide()
        self.open_newFolder_button.hide()
        res = [i[0] for i in cur.execute("""SELECT photo FROM Photo WHERE user_id = 
        (SELECT id FROM Users WHERE login = ?)""", (self.login,)).fetchall()]
        res_matrix = []
        while res != []:
            res_matrix.append(res[:5])
            res = res[5:]
        with open(os.getcwd().replace('\\', '/')[:-5] + '/filename_photo.txt', mode='w', encoding='utf8') as f:
            for i in res_matrix:
                f.write('\t'.join(i) + '\n')
        self.display_photo_in1page()

    def open_folder(self, flag_open=False):
        if not flag_open:
            self.dirlist = QFileDialog.getExistingDirectory(self,
                                                            "Выбрать папку",
                                                            ".")
        if self.dirlist:
            uic.loadUi(FOLDER_PATH, self)  # загрузка интерфейса
            self.initUI_folder()  # инит окна с фотками из папок

            dict_page = {}  # словарь где ключ страница, значение фотки
            files_list_no_PHOTO = []
            self.files_list_list = []
            files_list = os.listdir(self.dirlist)
            files_list_chekable = []
            for i in range(len(files_list)):  # проверка, является ли файл фото
                try:
                    Image.open(self.dirlist + '/' + files_list[i])
                    files_list_chekable.append(files_list[i])
                except Exception:
                    files_list_no_PHOTO.append(files_list[i])

            seperator = '\n'
            # установка в виджет текста название файлов которые не являются фото
            self.files_no_photo.setPlainText(f'Не являются фотками :\n{seperator.join(files_list_no_PHOTO)}')
            while files_list_chekable != []:
                self.files_list_list.append(files_list_chekable[:5])
                files_list_chekable = files_list_chekable[5:]
            with open(os.getcwd().replace('\\', '/')[:-5] + '/filename_photo.txt', mode='w', encoding='utf8') as f:
                for number, i in enumerate(self.files_list_list):
                    f.write('\t'.join(i) + '\n')
            self.display_photo_in1page()

    def write_photo_in_file_after_delete(self):
        os.remove(os.getcwd().replace('\\', '/')[:-5] + '/filename_photo.txt')
        self.open_folder(flag_open=True)

    def display_photo_in1page(self):
        with open(os.getcwd().replace('\\', '/')[:-5] + '/filename_photo.txt', encoding='utf8') as f:
            data = f.read().split('\n')
            files_list_list = []
            for i in data:
                files_list_list.append(i.split('\t'))
        for number_row, photo_list in enumerate(files_list_list):
            if number_row == 5 or photo_list == ['']:
                break
            for number_col, photo in enumerate(photo_list):
                # pix = QPixmap(dirlist + '/' + photo)
                # lbl = QLabel(self)
                # lbl.setPixmap(pix)
                btn = QPushButton(self)
                if self.dirlist == '' or self.dirlist == None:
                    self.dict_sender_photo[btn] = photo
                    btn.setIcon(QIcon(photo))
                else:
                    self.dict_sender_photo[btn] = self.dirlist + '/' + photo
                    btn.setIcon(QIcon(self.dirlist + '/' + photo))
                btn.clicked.connect(self.open_photo)
                btn.setStyleSheet("""
                QPushButton:hover {
                background-color: rgba(247, 148, 60, 10);
                stretch;
                }
                """)
                btn.setIconSize(QSize(92, 92))
                # btn.setStyleSheet()
                # btn.setIconSize(QSize(btn.size()[0], btn.size()[1]))
                self.gridLayout_4.addWidget(btn,
                                            number_row,
                                            number_col)
        if len(files_list_list) > 1:
            for i in range(math.ceil(len(files_list_list) / 5)):
                btn = QPushButton(str(i + 1), self)
                btn.setStyleSheet("""
                color: rgb(66, 100, 185);
                """)
                btn.clicked.connect(self.change_page)
                self.horizontalLayout_2.addWidget(btn)

    def change_page(self):
        while self.gridLayout_4.count():
            item = self.gridLayout_4.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        btn = int(self.sender().text())

        with open(os.getcwd().replace('\\', '/')[:-5] + '/filename_photo.txt', encoding='utf8') as f:
            file_names = f.read().split('\n')
            photo_in_page = file_names[(btn - 1) * 5:((btn - 1) * 5) + 5]

        for i, line in enumerate(photo_in_page):
            line_list = line.split('\t')
            for j, photo in enumerate(line_list):
                if photo != '':
                    btn = QPushButton(self)
                    self.dict_sender_photo[btn] = self.dirlist + '/' + photo
                    btn.clicked.connect(self.open_photo)

                    btn.setStyleSheet("""QPushButton:hover {
                                    background-color: rgba(247, 148, 60, 10);}""")

                    btn.setIcon(QIcon(self.dirlist + '/' + photo))
                    btn.setIconSize(QSize(90, 90))
                    self.gridLayout_4.addWidget(btn, i, j)

    def open_home(self):
        uic.loadUi(HOME_PATH, self)
        self.initUI_home()

    def open_photo(self):
        a = self.sender()
        self.ex2 = Photo_widget(self.dict_sender_photo, a, parent=self)
        self.ex2.show()

    def open_photo_home(self):
        self.dirlist_photo = QFileDialog.getOpenFileName(self,
                                                         "Выбрать фото",
                                                         ".")
        if self.dirlist_photo[0]:
            self.dict_sender_photo[1] = self.dirlist_photo[0]
            self.ex2 = Photo_widget(self.dict_sender_photo, parent=self)
            self.ex2.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    log = Login()
    log.show()
    sys.exit(app.exec_())
