import sys
from PyQt5.QtWidgets import QPushButton, QLineEdit, QDateEdit, QDateTimeEdit, QDialog, QMessageBox
from bson.objectid import ObjectId
import datetime

class Detail(QDialog):
    def __init__(self):
        super().__init__()

    # handle event save
    def save(self, parent):
        editMode = self.editMode
        if editMode == 0:
            self.insert(parent)
        else:
            self.update(parent)

    def insert(self, parent):
        dicType = str(parent.cboTabDataCategory.currentText())
        if dicType == 'StockPrice':
            tickerCodeVal = self.txtticker.text()
            tickerId  = self.database.ticker.find_one({'ticker_code': tickerCodeVal})
            if tickerId: 
                openVal = self.txtopen.text()
                highVal = self.txthigh.text()
                lowVal = self.txtlow.text()
                closeVal = self.txtclose.text()
                volumeVal = self.txtvolume.text()
                qdateVal = self.txtdate.dateTime()

                # part qdatetime to datetime.datetime
                qdatetime = QDateTimeEdit()
                qdatetime.setDisplayFormat("MM/dd/yyyy")
                strDate = qdatetime.textFromDateTime(qdateVal)
                dateVal =  datetime.datetime.strptime(strDate, '%m/%d/%Y')
                # quyery insert
                stockPrice = self.database.stock_price
                queryInsert = {
                    'ticker_id': tickerId['_id'],
                    'date': dateVal,
                    'open': openVal,
                    'high': highVal,
                    'low': lowVal,
                    'close': closeVal,
                    'volume': volumeVal,
                }
                result = stockPrice.insert_one(queryInsert)
                print(result.inserted_id)
            else :
                 QMessageBox.information(self, 'Lỗi', 'Mã cổ phiếu không tồn tại trong danh mục.', QMessageBox.Ok)
        elif dicType == 'StockExchange':           
             exchangeCode = self.txtstock_exchange_code.text()
             exchangeName = self.txtstock_exchange_name.text() 
             #  query insert   
             stockExchange = self.database.stock_exchange
             queryInsert = {
                'stock_exchange_code': exchangeCode,
                'stock_exchange_name': exchangeName
             }
             result = stockExchange.insert_one(queryInsert)

        elif dicType == 'Ticker':
             exchangeCode = self.txtstock_exchange_code.text()
             exchangeId = self.database.stock_exchange.find_one({'stock_exchange_code': exchangeCode})['_id']
             tickerCode = self.txtticker_code.text()
             companyName = self.txtcompany_name.text()
             #  query insert   
             ticker = self.database.ticker
             queryInsert = {
                'ticker_code': tickerCode,
                'company_name': companyName,
                'stock_exchange_id': exchangeId
             }
             result = ticker.insert_one(queryInsert)

        # user
        else : 
             userName = self.txtuser_name.text()
             passWord = self.txtpass_word.text()
             firstName = self.txtfirst_name.text()
             lastName = self.txtlast_name.text()
             role = str(self.cboRole.currentIndex())
             active = str(self.cbActive.isChecked())
             #  query update
             user = self.database.user
             queryInsert = {
                 "user_name": userName,
                 "pass_word": passWord,
                 "first_name": firstName,
                 "last_name": lastName,
                 "role": role,
                 "active" : active
             }
             result = user.insert_one(queryInsert)
        # close form detail
        self.close()
        # load lại dữ liệu cho table
        parent.loadData()

    def update(self, parent):
        # id row edit
        id = self.id
        dicType = str(parent.cboTabDataCategory.currentText())
        if dicType == 'StockPrice':
            openVal = self.txtopen.text()
            highVal = self.txthigh.text()
            lowVal = self.txtlow.text()
            closeVal = self.txtclose.text()
            volumeVal = self.txtvolume.text()
            qdateVal = self.txtdate.dateTime()
            # part qdatetime => datetime
            qdatetime = QDateTimeEdit()
            qdatetime.setDisplayFormat("MM/dd/yyyy")
            strDate = qdatetime.textFromDateTime(qdateVal)
            dateVal =  datetime.datetime.strptime(strDate, '%m/%d/%Y')

            # quyery update
            stockPrice = self.database.stock_price
            stockPrice.update_one(
                {'_id': ObjectId(str(id))},
                {
                    "$set":
                    {
                    "date": dateVal,
                    "open": openVal,
                    "high": highVal,
                    "low": lowVal,
                    "close": closeVal,
                    "volume": volumeVal
                    },
                },
                upsert=False)

        elif dicType == 'StockExchange':
             exchangeCode = self.txtstock_exchange_code.text()
             exchangeName = self.txtstock_exchange_name.text() 
             #  query update   
             stockExchange = self.database.stock_exchange
             stockExchange.update_one(
                {'_id': ObjectId(str(id))},
                {
                    "$set":
                    {
                    "stock_exchange_code": exchangeCode,
                    "stock_exchange_name": exchangeName
                    },
                },
                upsert=False) 
        elif dicType == 'Ticker':
             tickerCode = self.txtticker_code.text()
             companyName = self.txtcompany_name.text()
             # query update
             ticker = self.database.ticker
             ticker.update_one(
                {'_id': ObjectId(str(id))},
                {
                    "$set":
                    {
                    "ticker_code": tickerCode,
                    "company_name": companyName
                    },
                },
                upsert=False
             )
        #  user
        else :
             userName = self.txtuser_name.text()
             passWord = self.txtpass_word.text()
             firstName = self.txtfirst_name.text()
             lastName = self.txtlast_name.text()
             role = str(self.cboRole.currentIndex())
             active = str(self.cbActive.isChecked())
             #  query update
             user = self.database.user
             user.update_one(
                 {'_id': ObjectId(str(id))},
                {
                    "$set":
                    {
                    "user_name": userName,
                    "pass_word": passWord,
                    "first_name": firstName,
                    "last_name": lastName,
                    "role": role,
                    "active" : active
                    },
                },
                upsert=False
             )

        # close form detail
        self.close()
        # load lại dữ liệu cho table
        parent.loadData()

    def initEventHandleButton(self, parent):
        # handle btnCancel
        btnCancel = self.btnCancel
        btnCancel.clicked.connect(lambda: self.close())
        # handle btnSave
        btnSave = self.btnSave
        btnSave.clicked.connect(lambda: self.save(parent))

    # func clear data form detail
    # @author : nvan - 30/7/2020
    def clearData(self):
        for item in  self.findChildren(QLineEdit):
            item.setText("")
