import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidgetItem
from string import Formatter

con = sqlite3.connect('project.sqlite')
cur = con.cursor()


# Классы для реализации диалоговых окон/--------------------------------------------------------------------------------

# Диалоги, для добавления и удаления новых пользователей в бд/----------------------------------------------------------
class AddUserDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('admindialog.ui', self)
        self.initUI()
        self.setWindowTitle(' ')

    def initUI(self):
        self.f = True

        self.comboBox.activated.connect(self.activ)

        self.buttonBox.accepted.connect(self.OkAd)
        self.buttonBox.rejected.connect(self.Reject)

    def activ(self):
        self.t = self.comboBox.currentText()
        if self.t == 'Ученик':
            self.classs.show()
            self.f = True
        elif self.t == 'Преподаватель':
            self.classs.hide()
            self.f = False

    def OkAd(self):
        if self.f:
            chec = cur.execute(
                f"SELECT DISTINCT login from students where login like '{self.login.text()}'").fetchall()
            if not len(chec):
                cur.execute(
                    f"""INSERT INTO students(login,password,Class) VALUES('{self.login.text()}',
                    '{self.passww.text()}','{self.classs.text()}')""").fetchall()

                con.commit()
                self.close()
            else:
                error = Dialog('Ошибка!', 'Такой пользователь уже зарегистрирован!', QMessageBox.Warning)
                error.messbox()
        else:
            chec = cur.execute(
                f"SELECT DISTINCT login from Teachers where login like '{self.login.text()}'").fetchall()
            if not len(chec):
                cur.execute(
                    f"""INSERT INTO Teachers(login,password) VALUES('{self.login.text()}',
                                '{self.passww.text()}')""").fetchall()
                con.commit()
                self.close()
            else:
                error = Dialog('Ошибка!', 'Такой пользователь уже зарегистрирован!', QMessageBox.Warning)
                error.messbox()

    def Reject(self):
        self.close()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('DeleteUserDialog.ui', self)
        self.initUI()
        self.setWindowTitle(' ')
        self.bd = 'students'

    def initUI(self):
        self.comboBox.activated.connect(self.activ)
        self.delete_btn.clicked.connect(self.delet)

    def activ(self):
        self.t = self.comboBox.currentText()
        if self.t == 'Ученик':
            self.bd = 'students'
        else:
            self.bd = 'Teachers'

    def delet(self):
        chec = cur.execute(
            f"SELECT DISTINCT login from {self.bd} where login like '{self.LoginText.text()}'").fetchall()
        if len(chec):
            cur.execute(
                f"""DELETE from {self.bd} WHERE login = '{self.LoginText.text()}'""").fetchall()
            con.commit()
            diolog = Dialog('Успешно!', 'Пользователь успешно удалён!', QMessageBox.Information)
            diolog.messbox()
            self.LoginText.setText('')
        else:
            error = Dialog('Ошибка!', 'Такого пользователя нет в базе данных!', QMessageBox.Warning)
            error.messbox()


# ----------------------------------------------------------------------------------------------------------------------

# Классы, для просмотра статистики выбранного класса по выбранному предмету/--------------------------------------------
class ComboBox(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('dialogue_statistics.ui', self)
        self.initUI()
        self.setWindowTitle(' ')
        with open('Classes.txt', 'r', encoding='utf-8') as f:
            a = f.readlines()
            a = list(map(str.strip, a))
            for i in a:
                self.comboBox.addItem(i)
        with open('subject.txt', 'r', encoding='utf-8') as f:
            a = f.readlines()
            a = list(map(str.strip, a))
            for i in a:
                self.comboBox_2.addItem(i)

    def initUI(self):
        self.buttonBox.accepted.connect(self.OkAd)
        self.buttonBox.rejected.connect(self.Reject)

    def OkAd(self):
        if self.comboBox_2.currentText() == 'Русский язык':
            self.ratings = 'ru_ratings'
        elif self.comboBox_2.currentText() == 'Математика':
            self.ratings = 'math_ratings'
        elif self.comboBox_2.currentText() == 'Окружающий мир':
            self.ratings = 'okr_ratings'
        pupils = cur.execute(
            f"SELECT DISTINCT login from students where Class like '{self.comboBox.currentText()}'").fetchall()
        if len(pupils):
            self.close()
            sts = StaticTabl(pupils, self.ratings)
            sts.exec_()
        else:
            error = Dialog('Ошибка!', 'В выбранном классе отсутствуют учащиеся!', QMessageBox.Warning)
            error.messbox()

    def Reject(self):
        self.close()


class StaticTabl(QDialog):
    def __init__(self, pupils, rat):
        super().__init__()
        uic.loadUi('Static.ui', self)
        self.pupils = pupils
        self.ratings = rat
        self.initUI()
        self.setWindowTitle(' ')

    def initUI(self):
        self.pupils = [str(*i) for i in self.pupils]
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(len(self.pupils))
        self.tableWidget.setVerticalHeaderLabels(self.pupils)
        self.tableWidget.setHorizontalHeaderLabels(['Оценки', 'Средний балл'])
        for t, i in enumerate(self.pupils):
            rat = cur.execute(
                f"SELECT DISTINCT {self.ratings} from students where login = '{i}'").fetchall()
            self.tableWidget.setItem(t, 0, QTableWidgetItem(*rat[0]))
            srball = list(map(int, ''.join(list(*rat[0])).split()))
            try:
                fmt = Fmt()
                b = fmt.format('{0:.2p}', round(sum(srball) / len(srball), 2))
                self.tableWidget.setItem(t, 1, QTableWidgetItem(b))
            except ZeroDivisionError:
                self.tableWidget.setItem(t, 1, QTableWidgetItem('0'))


# ----------------------------------------------------------------------------------------------------------------------

# Класс для реализации предупреждений/----------------------------------------------------------------------------------
class Dialog:
    def __init__(self, title, mess, icon):
        self.title = title
        self.mess = mess
        self.icon = icon

    def messbox(self):
        msg = QMessageBox()
        msg.setWindowTitle(self.title)
        msg.setText(self.mess)
        msg.setIcon(self.icon)
        msg.exec_()


# ---------------------------------------------------------------------------------------------------------------------\


# ---------------------------------------------------------------------------------------------------------------------\

# Класс для реализации красивого вывода дробных чисел/------------------------------------------------------------------
class Fmt(Formatter):
    def format_field(self, value, spec):
        if spec[-1] == 'p':
            spec = '{0}f'.format(spec[:-1])
            return super(Fmt, self).format_field(value, spec).rstrip('0').rstrip('.')
        return super(Fmt, self).format_field(value, spec)

# ----------------------------------------------------------------------------------------------------------------------
