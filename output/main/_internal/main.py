import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QWidget, QInputDialog
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWinExtras import QtWin
from numpy import arange
from Dialogue import *
from theme import *

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

con = sqlite3.connect('project.sqlite')
cur = con.cursor()
COUNT_TOPIC = 0


# Форма входа в аккаунт/------------------------------------------------------------------------------------------------
class Test(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('untitled.ui', self)
        self.initUI()
        self.setWindowTitle('Жёлто-синий автобус')
        self.tabl = 'students'

    def initUI(self):
        # Кнопка входа/-------------------------------------------------------------------------------------------------
        self.pushButton.clicked.connect(self.checked_Login_Password)
        self.Admin_login_btn.clicked.connect(self.checked_Login_Password)
        # -------------------------------------------------------------------------------------------------------------\

        # Кнопка отображения пароля/------------------------------------------------------------------------------------
        self.eye.clicked.connect(self.Change_icons)
        self.count = 0
        # -------------------------------------------------------------------------------------------------------------\

    def checked_Login_Password(self):
        # Проверка входных данных/--------------------------------------------------------------------------------------
        if self.sender().text() == 'Войти':
            self.tabl = 'students'
            self.f = True
        if self.sender().text() == 'Вход для учителей':
            self.tabl = 'Teachers'
            self.f = False
        if self.login.text() == '' or self.password.text() == '':
            error = Dialog("Ошибка!", "Вы не заполнили одно из обязательных полей!", QMessageBox.Warning)
            error.messbox()
        else:
            name = cur.execute(
                f"SELECT DISTINCT s.login from {self.tabl} as s where s.login like '{self.login.text()}'").fetchall()
            passw = cur.execute(
                f"SELECT DISTINCT s.password from {self.tabl} as s where s.login like '{self.login.text()}'").fetchall()
            if len(name) != 0:
                if str(*passw[0]) == self.password.text():
                    if self.f:
                        self.second_form = SecondForm(self.login.text())
                        self.close()
                        self.second_form.show()
                    else:
                        self.adm = Admin(self.login.text())
                        self.close()
                        self.adm.show()
                else:
                    error = Dialog("Ошибка!", "Неверный логин или пароль!", QMessageBox.Warning)
                    error.messbox()
            else:
                error = Dialog("Ошибка!", "Неверный логин или пароль!", QMessageBox.Warning)
                error.messbox()
        # -------------------------------------------------------------------------------------------------------------\

    def Change_icons(self):
        # Проверка на звездочки в пароли/-------------------------------------------------------------------------------
        if self.count % 2 == 0:
            self.eye.setIcon(QtGui.QIcon('open_eye.png'))
            self.password.setEchoMode(QLineEdit.Normal)
        else:
            self.eye.setIcon(QtGui.QIcon('close_eye.png'))
            self.password.setEchoMode(QLineEdit.Password)
        self.count += 1
        # -------------------------------------------------------------------------------------------------------------\


# ----------------------------------------------------------------------------------------------------------------------

# Основное меню/--------------------------------------------------------------------------------------------------------
class SecondForm(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name = name
        uic.loadUi('secondF.ui', self)
        self.initUI()
        self.setWindowTitle('Основное меню')

    def initUI(self):
        # Кнопки предметов/---------------------------------------------------------------------------------------------
        for i in [self.rus_btn, self.math_btn, self.okrmir_bnt]:
            i.clicked.connect(self.test_form)
        # -------------------------------------------------------------------------------------------------------------\

        # Кнопка возврата/----------------------------------------------------------------------------------------------
        self.return_bnt.clicked.connect(self.rtn)
        # -------------------------------------------------------------------------------------------------------------\

        # Кнопка настроек/----------------------------------------------------------------------------------------------
        self.settings_btn.clicked.connect(self.settinds)
        # -------------------------------------------------------------------------------------------------------------\

        self.user_btn.clicked.connect(self.User_test)

    def rtn(self):
        # Функция возврата на первую форму/-----------------------------------------------------------------------------
        self.close()
        self.Test = Test()
        self.Test.show()
        # -------------------------------------------------------------------------------------------------------------\

    def settinds(self):
        # Функция открытия окна с настройками/--------------------------------------------------------------------------
        self.close()
        self.sett = Settings(self.name)
        self.sett.show()
        # -------------------------------------------------------------------------------------------------------------\

    def test_form(self):
        # Функция открытия третьей формы/-------------------------------------------------------------------------------

        # Выбор предмета/-----------------------------------------------------------------------------------------------
        if self.sender().text() == 'Русский Язык':
            self.n = 'russian_lang'
            self.chectest = 'ru_tests'
            self.ratings = 'ru_ratings'
        elif self.sender().text() == 'Математика':
            self.n = 'math'
            self.chectest = 'math_tests'
            self.ratings = 'math_ratings'
        elif self.sender().text() == 'Окружающий мир':
            self.n = 'okr_mir'
            self.chectest = 'okr_tests'
            self.ratings = 'okr_ratings'
        # -------------------------------------------------------------------------------------------------------------\

        # Проверка на повторное прохождение теста/----------------------------------------------------------------------
        chec = cur.execute(
            f"SELECT DISTINCT {self.chectest} from students where login like '{self.name}'").fetchall()
        if int(*chec[0]):
            self.Test_Form = TestForm(self.name, self.n, self.chectest, self.ratings)
            self.close()
            self.Test_Form.show()
        else:
            error = Dialog("Ошибка!", "Вы уже проходили этот тест!", QMessageBox.Warning)
            error.messbox()
        # -------------------------------------------------------------------------------------------------------------\

    def User_test(self):
        idd, ok_pressed = QInputDialog.getText(self, "Капибара", "Введите id теста")
        if ok_pressed:
            self.conn = sqlite3.connect('User_Test.sqlite')
            self.cursor = self.conn.cursor()
            f = True
            try:
                self.cursor.execute(f"SELECT DISTINCT question from [{idd}]").fetchall()
            except sqlite3.OperationalError:
                error = Dialog('Ошибка!', 'Теста с таким id не обнаружено!', QMessageBox.Warning)
                error.messbox()
                f = False
            if f:
                user = self.cursor.execute(f"SELECT DISTINCT already_past from [{idd}]").fetchall()
                user = ''.join([i for i in list(*user)]).split()
                if self.name in user:
                    error = Dialog("Ошибка!", "Вы уже проходили этот тест!", QMessageBox.Warning)
                    error.messbox()
                else:
                    self.usertest = Usertest(self.name, idd)
                    self.close()
                    self.usertest.show()


# ---------------------------------------------------------------------------------------------------------------------\

# Панель админа/--------------------------------------------------------------------------------------------------------
class Admin(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name = name
        uic.loadUi('Admin.ui', self)
        self.initUI()
        self.setWindowTitle('Панель админа')

    def initUI(self):
        # Кнопка настроек/----------------------------------------------------------------------------------------------
        self.settings_btn.clicked.connect(self.settinds)
        # -------------------------------------------------------------------------------------------------------------\

        # Кнопка возврата/----------------------------------------------------------------------------------------------
        self.return_bnt.clicked.connect(self.rtn)
        # -------------------------------------------------------------------------------------------------------------\

        # Кнопка добавления нового пользователя/------------------------------------------------------------------------
        self.AddUser_btn.clicked.connect(self.AddUser)
        # --------------------------------------------------------------------------------------------------------------

        # Кнопка вызыва функции статистики/-----------------------------------------------------------------------------
        self.ClassStatic_btn.clicked.connect(self.StaticClass)
        # -------------------------------------------------------------------------------------------------------------\

        # Кнопка удаления пользователей из бд/--------------------------------------------------------------------------
        self.DeleteUser_btn.clicked.connect(self.deleteUser)
        # --------------------------------------------------------------------------------------------------------------
        self.AddTest_btn.clicked.connect(self.AddTest)

    def StaticClass(self):
        # Функция выведения статистики класса по предмету/--------------------------------------------------------------
        self.stat = ComboBox()
        self.stat.exec_()
        # --------------------------------------------------------------------------------------------------------------

    def AddTest(self):
        with open('subject.txt', 'r', encoding='utf8') as f:
            a = f.readlines()
            a = list(map(str.strip, a))
            obj, ok_pressed = QInputDialog.getItem(self, "Выберите предмет теста", "Предмет:", a, 0, False)
        self.createtest = CreateTest(self.name, obj)
        self.createtest.show()
        self.close()

    def AddUser(self):
        # Функция добавления нового пользователя/-----------------------------------------------------------------------
        self.addialog = AddUserDialog()
        self.addialog.exec_()
        # -------------------------------------------------------------------------------------------------------------\

    def deleteUser(self):
        # Функция удаление пользователей из бд/-------------------------------------------------------------------------
        self.deletdialog = DeleteDialog()
        self.deletdialog.exec_()
        # -------------------------------------------------------------------------------------------------------------\

    def settinds(self):
        # Функция открытия окна с настройками/--------------------------------------------------------------------------
        self.close()
        self.sett = Settings(self.name, True)
        self.sett.show()
        # -------------------------------------------------------------------------------------------------------------\

    def rtn(self):
        # Функция возврата на первую форму/-----------------------------------------------------------------------------
        self.close()
        self.Test = Test()
        self.Test.show()
        # -------------------------------------------------------------------------------------------------------------\


# ---------------------------------------------------------------------------------------------------------------------\

# Форма для создания тестов/--------------------------------------------------------------------------------------------
class CreateTest(QWidget):
    def __init__(self, name, obj):
        super().__init__()
        self.name = name
        self.obj = obj
        uic.loadUi('TestCreate.ui', self)
        self.setWindowTitle('Создание теста')
        self.initUI()

    def initUI(self):
        self.count = 0
        # Кнопки "Далее" и "Завершить тест"/----------------------------------------------------------------------------
        self.Further_btn.clicked.connect(self.Further)
        self.exit_bnt.clicked.connect(self.exit)
        # --------------------------------------------------------------------------------------------------------------

    def CreateTable(self):
        # Функция создания таблицы в БД/--------------------------------------------------------------------------------
        with open('usedid.txt', 'r') as f:
            a = f.readlines()
            a = list(map(str.strip, a))
            idd = int(a[-1]) + 1
        with open('usedid.txt', 'a') as f:
            self.idd = str(idd)
            f.write(f'\n{self.idd}')

        self.conn = sqlite3.connect('User_Test.sqlite')
        self.cursor = self.conn.cursor()
        self.cursor.execute(f'''CREATE TABLE [{self.idd}] (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        question       TEXT    DEFAULT (''),
        all_options    TEXT    DEFAULT (''),
        correct_option TEXT    DEFAULT (''),
        already_past   TEXT    DEFAULT (''),
        subject        TEXT    DEFAULT ('') 
        );''')
        # -------------------------------------------------------------------------------------------------------------\

    def Further(self):
        # Функция для кнопки "Далее". Проверяет входные данные, создает БД и записывает данные в БД/--------------------
        checaktiv = []
        for i in [self.option1, self.option2, self.option3, self.option4]:
            checaktiv.append(i.isChecked())
        if any(checaktiv):
            chectext = []
            for i in [self.answer1, self.answer2, self.answer3, self.answer4]:
                chectext.append(i.text())
            chectext1 = ';'.join(chectext)
            if all(chectext):
                if self.plainTextEdit.toPlainText():
                    corect_btn = -1
                    for i in [self.option1, self.option2, self.option3, self.option4]:
                        if i.isChecked():
                            corect_btn = [self.option1, self.option2, self.option3, self.option4].index(i)
                    corect = [self.answer1, self.answer2, self.answer3, self.answer4][corect_btn].text()
                    if not self.count:
                        self.CreateTable()
                    self.cursor.execute(
                        f"""INSERT INTO [{self.idd}](question,all_options,correct_option,subject) 
                        VALUES('{self.plainTextEdit.toPlainText()}', 
                        '{chectext1}','{corect}','{self.obj}')""").fetchall()
                    self.conn.commit()
                    self.count += 1
                    self.plainTextEdit.setPlainText('')
                    for i in [self.answer1, self.answer2, self.answer3, self.answer4]:
                        i.setText('')
                else:
                    error = Dialog('Ошибка!', 'Вы не ввели вопрос!', QMessageBox.Warning)
                    error.messbox()
            else:
                error = Dialog('Ошибка!', 'Вы указали не все возможные варианты ответов!', QMessageBox.Warning)
                error.messbox()
        else:
            error = Dialog('Ошибка!', 'Вы не выбрали правильного ответа на вопрос!', QMessageBox.Warning)
            error.messbox()
        # --------------------------------------------------------------------------------------------------------------

    def exit(self):
        # Функция для кнопки "Завершить тест". Выводит сообщение об успешном сохранении теста/--------------------------
        if self.count:
            diolog = Dialog('Успешно!', f'Ваш тест успешно сохранен под id {self.idd}!', QMessageBox.Information)
            diolog.messbox()
            self.adm = Admin(self.name)
            self.close()
            self.adm.show()
        else:
            diolog = Dialog('Ошибка!', 'Вы не добавили ни одного вопроса в тест!', QMessageBox.Warning)
            diolog.messbox()
            self.adm = Admin(self.name)
            self.close()
            self.adm.show()
        # --------------------------------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------------------------------------\

# Форма с настройками/--------------------------------------------------------------------------------------------------
class Settings(QWidget):
    def __init__(self, name, f=False):
        super().__init__()
        self.name = name
        self.f = f
        uic.loadUi('settings.ui', self)
        self.initUI()
        self.setWindowTitle('Настройки')

    def initUI(self):
        # Установка имени пользователя, пароля и количество решенных тестов/--------------------------------------------
        if not self.f:
            self.tabl = 'students'
        elif self.f:
            self.tabl = 'Teachers'
        self.passwd = cur.execute(
            f"SELECT DISTINCT r.password from {self.tabl} as r where r.login like '{self.name}'").fetchall()
        self.versia.setText('Версия 1.0')
        self.namee.setText(f'Login: {self.name}')
        self.passw.setText(f'Пароль: {len(str(*self.passwd[0])) * "*"}')
        if not self.f:
            c = cur.execute(
                f"SELECT DISTINCT r.count_tests from students as r where r.login like '{self.name}'").fetchall()
            self.countt.setText(f'Кол-во пройденных тестов: {str(*c[0])}')
        # -------------------------------------------------------------------------------------------------------------\

        # Изменение режима отображения пароля/--------------------------------------------------------------------------
        self.pasmode.clicked.connect(self.Change_icons)
        self.count = 0
        # -------------------------------------------------------------------------------------------------------------\

        # Кнопка назад/-------------------------------------------------------------------------------------------------
        self.ret.clicked.connect(self.returnn)
        # -------------------------------------------------------------------------------------------------------------\

        # Кнопка смены пароля/------------------------------------------------------------------------------------------
        self.changpass.clicked.connect(self.ChangePassword)
        # -------------------------------------------------------------------------------------------------------------\

        # Кнопка смены темы/--------------------------------------------------------------------------------------------
        self.ChangingTopic_bnt.clicked.connect(self.Changing_the_topic)

        # --------------------------------------------------------------------------------------------------------------

    def Change_icons(self):
        # Проверка на звездочки в пароли/-------------------------------------------------------------------------------
        if self.count % 2 == 0:
            self.pasmode.setIcon(QtGui.QIcon('open_eye.png'))
            self.passw.setText(f'Пароль: {str(*self.passwd[0])}')
        else:
            self.pasmode.setIcon(QtGui.QIcon('close_eye.png'))
            self.passw.setText(f'Пароль: {len(str(*self.passwd[0])) * "*"}')
        self.count += 1
        # -------------------------------------------------------------------------------------------------------------\

    def returnn(self):
        # Функция возвращения на вторую форму/--------------------------------------------------------------------------
        if not self.f:
            self.second_form = SecondForm(self.name)
            self.close()
            self.second_form.show()
        else:
            self.admin = Admin(self.name)
            self.close()
            self.admin.show()
        # -------------------------------------------------------------------------------------------------------------\

    def ChangePassword(self):
        # Функция смены пароля/-----------------------------------------------------------------------------------------
        text, ok = QInputDialog.getText(self, 'Смена пароля', 'Введите ваш новый пароль: ')
        if ok:
            cur.execute(
                f"""update {self.tabl} SET password = {text} WHERE login = '{self.name}' """).fetchall()
            con.commit()
            inf = Dialog('Успешно!', 'Ваш пароль успешно изменен!', QMessageBox.Information)
            inf.messbox()
        # -------------------------------------------------------------------------------------------------------------\

    def Changing_the_topic(self):
        global COUNT_TOPIC
        # Функция смены темы/-------------------------------------------------------------------------------------------
        if COUNT_TOPIC % 2 == 0:
            app.setStyle("Fusion")
            QApplication.setPalette(dark_palette)
        else:
            app.setStyle("windowsvista")
            QApplication.setPalette(QPalette())
        COUNT_TOPIC += 1
        # --------------------------------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------------------------------------\

# Форма с самими тестами/-----------------------------------------------------------------------------------------------
class TestForm(QWidget):
    def __init__(self, name, obj, chectest, ratings):
        super().__init__()
        self.name = name
        self.n = obj
        self.chectest = chectest
        self.ratings = ratings
        uic.loadUi('TestForm.ui', self)
        self.initUI()
        self.setWindowTitle('Окно теста')

    def initUI(self):
        self.progress = []
        self.count = 1
        self.id = cur.execute(
            f"SELECT DISTINCT r.id from {self.n} as r").fetchall()
        self.id = [str(*i) for i in self.id]
        # Кнопка далее/-------------------------------------------------------------------------------------------------
        self.further.clicked.connect(self.Next)
        self.FillingOInf()
        # -------------------------------------------------------------------------------------------------------------\

    def FillingOInf(self):
        # Функция определения вопроса и вариантов ответа/---------------------------------------------------------------
        option = cur.execute(
            f"SELECT DISTINCT r.all_options from {self.n} as r where r.id like '{self.count}'").fetchall()
        option = str(*option[0]).split(';')
        name = cur.execute(
            f"SELECT DISTINCT r.question from {self.n} as r where r.id like '{self.count}'").fetchall()
        self.corr = cur.execute(
            f"SELECT DISTINCT r.correct_option from {self.n} as r where r.id like '{self.count}'").fetchall()
        self.corr = str(*self.corr[0])
        self.qname.setText(*name[0])
        self.option1.setText(option[0])
        self.option2.setText(option[1])
        self.option3.setText(option[2])
        self.option4.setText(option[3])
        self.Questions.setText(f'Вопрос {self.id[self.count - 1]}/{self.id[-1]}')
        # -------------------------------------------------------------------------------------------------------------\

    def answerChoice(self):
        # Проверка корректности ответа пользователя/--------------------------------------------------------------------
        for i in [self.option1, self.option2, self.option3, self.option4]:
            if i.isChecked():
                if i.text() == self.corr:
                    self.progress.append(1)
                else:
                    self.progress.append(0)
        # -------------------------------------------------------------------------------------------------------------\

    def Next(self):
        # Кнопка далее/-------------------------------------------------------------------------------------------------
        self.answerChoice()
        qwe = []
        for i in [self.option1, self.option2, self.option3, self.option4]:
            qwe.append(i.isChecked())
        if not any(qwe):
            error = Dialog("Пустой ответ!", "Вы не выбрали ни один из вариантов ответа!", QMessageBox.Warning)
            error.messbox()
        else:
            if self.count < len(self.id):
                self.count += 1
                self.FillingOInf()
            else:
                try:
                    percent = round((sum(self.progress) / len(self.progress)) * 100, 2)
                    a = f'Вы прошли тест на {percent}%'
                except ZeroDivisionError:
                    percent = 0.0
                    a = f'Вы прошли тест на {percent}%'
                cur.execute(
                    f"""update students SET {self.chectest} = 0 WHERE login = '{self.name}' """).fetchall()
                cur.execute(
                    f"""update students SET count_tests = count_tests+1 WHERE login = '{self.name}' """).fetchall()
                # Открытие формы с результатом/-------------------------------------------------------------------------
                with open('notes.txt', 'r') as f:
                    b = f.readlines()
                    for i in b:
                        n, r = i.split(' -- ')
                        minx, maxx = r.split(', ')
                        if percent in [round(i, 2) for i in arange(int(minx), int(maxx), 0.1)]:
                            break
                rat = cur.execute(
                    f"SELECT DISTINCT {self.ratings} from students where login = '{self.name}'").fetchall()
                rat = f'{str(*rat[0])} {str(n)}'
                cur.execute(
                    f"""update students SET {self.ratings} = '{rat}' WHERE login = '{self.name}' """).fetchall()
                con.commit()
                self.Form = Result(self.name, a, n)
                self.close()
                self.Form.show()
                # -----------------------------------------------------------------------------------------------------\

        # -------------------------------------------------------------------------------------------------------------\


# ---------------------------------------------------------------------------------------------------------------------\

# Форма с пользовательскими тестами/------------------------------------------------------------------------------------
class Usertest(QWidget):
    def __init__(self, name, idd):
        super().__init__()
        self.name = name
        self.idd = idd
        uic.loadUi('TestForm.ui', self)
        self.initUI()
        self.setWindowTitle(f'id-{self.idd}')

    def initUI(self):
        self.conn = sqlite3.connect('User_Test.sqlite')
        self.cursor = self.conn.cursor()
        self.ratings = self.cursor.execute(
            f"SELECT DISTINCT subject from [{self.idd}]").fetchall()
        self.ratings = str(*self.ratings[0])
        if self.ratings == 'Русский язык':
            self.ratings = 'ru_ratings'
        elif self.ratings == 'Математика':
            self.ratings = 'math_ratings'
        elif self.ratings == 'Окружающий мир':
            self.ratings = 'okr_ratings'
        self.progress = []
        self.count = 1
        self.id = self.cursor.execute(
            f"SELECT DISTINCT id from [{self.idd}]").fetchall()
        self.id = [str(*i) for i in self.id]
        # Кнопка далее/-------------------------------------------------------------------------------------------------
        self.further.clicked.connect(self.Next)
        self.FillingOInf()
        # -------------------------------------------------------------------------------------------------------------\

    def FillingOInf(self):
        # Функция определения вопроса и вариантов ответа/---------------------------------------------------------------
        option = self.cursor.execute(
            f"SELECT DISTINCT all_options from [{self.idd}] where id like '{self.count}'").fetchall()
        option = str(*option[0]).split(';')
        name = self.cursor.execute(
            f"SELECT DISTINCT question from [{self.idd}]  where id like '{self.count}'").fetchall()
        self.corr = self.cursor.execute(
            f"SELECT DISTINCT correct_option from [{self.idd}] where id like '{self.count}'").fetchall()
        self.corr = str(*self.corr[0])
        self.qname.setText(*name[0])
        self.option1.setText(option[0])
        self.option2.setText(option[1])
        self.option3.setText(option[2])
        self.option4.setText(option[3])
        self.Questions.setText(f'Вопрос {self.id[self.count - 1]}/{self.id[-1]}')
        # -------------------------------------------------------------------------------------------------------------\

    def answerChoice(self):
        # Проверка корректности ответа пользователя/--------------------------------------------------------------------
        for i in [self.option1, self.option2, self.option3, self.option4]:
            if i.isChecked():
                if i.text() == self.corr:
                    self.progress.append(1)
                else:
                    self.progress.append(0)
        # -------------------------------------------------------------------------------------------------------------\

    def Next(self):
        # Кнопка далее/-------------------------------------------------------------------------------------------------
        self.answerChoice()
        qwe = []
        for i in [self.option1, self.option2, self.option3, self.option4]:
            qwe.append(i.isChecked())
        if not any(qwe):
            error = Dialog("Пустой ответ!", "Вы не выбрали ни один из вариантов ответа!", QMessageBox.Warning)
            error.messbox()
        else:
            if self.count < len(self.id):
                self.count += 1
                self.FillingOInf()
            else:
                try:
                    percent = round((sum(self.progress) / len(self.progress)) * 100, 2)
                    a = f'Вы прошли тест на {percent}%'
                except ZeroDivisionError:
                    percent = 0.0
                    a = f'Вы прошли тест на {percent}%'
                cur.execute(
                    f"""update students SET count_tests = count_tests+1 WHERE login = '{self.name}' """).fetchall()
                # Открытие формы с результатом/-------------------------------------------------------------------------
                with open('notes.txt', 'r') as f:
                    b = f.readlines()
                    for i in b:
                        n, r = i.split(' -- ')
                        minx, maxx = r.split(', ')
                        if percent in [round(i, 2) for i in arange(int(minx), int(maxx), 0.01)]:
                            break
                rat = cur.execute(
                    f"SELECT DISTINCT {self.ratings} from students where login = '{self.name}'").fetchall()
                rat = f'{str(*rat[0])} {str(n)}'
                cur.execute(
                    f"""update students SET {self.ratings} = '{rat}' WHERE login = '{self.name}' """).fetchall()
                alpast = self.cursor.execute(
                    f"SELECT DISTINCT already_past from [{self.idd}]").fetchall()
                alpast = f'{str(*alpast[0])} {self.name}'
                self.cursor.execute(
                    f"""update [{self.idd}] SET already_past = '{alpast}' """).fetchall()
                con.commit()
                self.conn.commit()
                self.Form = Result(self.name, a, n)
                self.close()
                self.Form.show()
                # -----------------------------------------------------------------------------------------------------\

        # -------------------------------------------------------------------------------------------------------------\


# ----------------------------------------------------------------------------------------------------------------------

# Окно с результатами/--------------------------------------------------------------------------------------------------
class Result(QWidget):
    def __init__(self, name, res, note):
        super().__init__()
        self.name = name
        self.res = res
        self.note = note
        uic.loadUi('result.ui', self)
        self.initUI()
        self.setWindowTitle('Результат')

    def initUI(self):
        # Отображение результата и картинки/----------------------------------------------------------------------------
        self.result.setText(self.res)
        self.notee.setText(f'Ваша оценка: {str(self.note)}')
        # -------------------------------------------------------------------------------------------------------------\

        # Кнопка назад/-------------------------------------------------------------------------------------------------
        self.returnbtn.clicked.connect(self.ret)
        # -------------------------------------------------------------------------------------------------------------\

    def ret(self):
        # Возвращение на форму с тестами/-------------------------------------------------------------------------------
        self.second_form = SecondForm(self.name)
        self.close()
        self.second_form.show()
        # -------------------------------------------------------------------------------------------------------------\


# ---------------------------------------------------------------------------------------------------------------------\

if __name__ == '__main__':
    myappid = 'mycompany.myproduct.subproduct.version'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('ёж2.png'))
    ex = Test()
    ex.setWindowIcon(QtGui.QIcon('ёж2.png'))
    ex.show()
    sys.exit(app.exec())
