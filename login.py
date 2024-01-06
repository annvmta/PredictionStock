import sys
from PyQt5.QtWidgets import QPushButton, QLineEdit, QMessageBox, QDialog
from PyQt5 import uic
class Register(QDialog): 
    def __init__(self):
        super().__init__()

    # init even click button
    def initHandleClickButton(self):
        # handle click button cancel
        self.btnCancel.clicked.connect(lambda: self.close())  
        # handle click button register
        self.btnRegister.clicked.connect(lambda: self.submitRegister())

    # submit đăng ký tài khoản
    def submitRegister(self):
        userName = self.txtuser_name.text()
        passWord = self.txtpass_word.text()
        firstName = self.txtfirst_name.text()
        lastName = self.txtlast_name.text()
        
        # validate username/password
        user = self.parent.database.user
        query = {
            'user_name': userName,
            'pass_word': passWord
        }

        existUser = user.find_one(query)
        if existUser :
            self.lbRegisterErr.setText("Đăng ký không thành công. tài khoản đã tồn tại.")
        else :
            insertQuery = {
            'user_name': userName,
            'pass_word': passWord,
            "first_name": firstName,
            "last_name": lastName,
            "role": '1',
            "active" : 'False'
            }
            result = user.insert_one(insertQuery)
            if result :
                self.close()
                self.parent.show()
                reply = QMessageBox.information(self.parent, 'information', 'Đăng ký thành công. Vui lòng đợi hệ thống xác nhận.', QMessageBox.Ok)
                #if reply == QMessageBox.Ok:

    # handle click button cancel   
    def close(self):
        super().close()
        self.parent.show()

    def closeEvent(self, event): 
        super().closeEvent(event)
        self.parent.show()  

class Login(QDialog):
    def __init__(self):
        super().__init__()

    def handleClickButton(self, parent):
        # handle btnCancel
        self.btnCancel.clicked.connect(lambda: self.close())
        # handle btnSave
        self.btnLogin.clicked.connect(lambda: self.login(parent))
        # handle btnRegister
        self.btnRegister.clicked.connect(lambda : self.funcRegister(parent))

    def login(self, parent):
        userName = self.txtUserName.text()
        passWord = self.txtPassWord.text()
        user = self.database.user
        query = {
            'user_name': userName,
            'pass_word': passWord
        }
        existUser = user.find_one(query)

        if existUser and existUser['active'] =='True': 
            self.userRole = existUser['role']
            self.lbLoginErr.setText("")
            self.close()
            parent.show()           
            # init gui for permission
            parent.initUIPermission()       
        else :
            self.lbLoginErr.setText("Đăng nhập thất bại. Tài khoản/mật khẩu không đúng")

    def funcRegister(self, parent):
        register = Register()
        uic.loadUi("GUI/register.ui", register)
        self.close()
        register.show()
        register.txtpass_word.setEchoMode(QLineEdit.Password) 
        register.parent = self
        register.initHandleClickButton()
        parent.register = register
        
