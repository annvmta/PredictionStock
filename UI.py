# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 14:52:40 2020

@author: AN AN
"""

from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QDateEdit, QDateTimeEdit, QTableWidget, QTableWidgetItem, QHeaderView, QWidget, QDesktopWidget, QDialog, QMessageBox
from PyQt5.QtGui import QCloseEvent
from PyQt5 import uic
import sys
from pymongo import MongoClient
import pymongo
from bson.objectid import ObjectId
from PyQt5 import QtWidgets
import csv
import json
import pandas as pd
import datetime
from dateutil.parser import parse
import getopt
from detail import *
from login import *
from trainning import exculteTrainning, excultePredictions

class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        # init connetion database
        self.connectDatabase()

        login = Login()
        uic.loadUi("GUI/login.ui", login)
        login.show()
        login.txtPassWord.setEchoMode(QLineEdit.Password)

        self.login = login
        self.login.database = self.database
        self.login.handleClickButton(self)
        uic.loadUi("GUI/mainframe.ui", self)

        # init tab Data
        self.initTabData()
        # init tab forecast
        self.initTabForecast()
        # init tab training
        self.initTabTrainning()
        #  init detail by category
        self.initDetail()
        # load data for table
        self.loadData()
        # init event click button
        self.handleClickButton()
        # init event change selected item combo
        self.handleComboSelectionChange()
        # init event change dateEdit
        self.handleDateChange()
        # init event change spinbox
        self.handleSpinBoxChange()
        # show GUI to center
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

    def initUIPermission(self):
        if self.login.userRole == '1':
            # hide tab trainning
            self.ctrTab.setTabVisible(2, False)
            # hide button add, edit, delete, import
            self.btnAdd.hide()
            self.btnEdit.hide()
            self.btnDelete.hide()
            self.btnImport.hide()
            # user không được xem danh sách người dùng
            self.cboTabDataCategory.removeItem(3)

        else:
            self.ctrTab.setTabVisible(2, True)

    # init detail by category
    def initDetail(self):
        detail = Detail()
        dicType = str(self.cboTabDataCategory.currentText())
        if dicType == 'StockPrice':
            uic.loadUi("GUI/detailxx.ui", detail)
        elif dicType == 'StockExchange':
            uic.loadUi("GUI/detailExchange.ui", detail)
        elif dicType == 'Ticker':
            uic.loadUi("GUI/detailTicker.ui", detail)
        # user
        else:
            uic.loadUi("GUI/detailUser.ui", detail)
            # load data combo role
            roles = ['Admin', 'User']
            detail.cboRole.addItems(roles)

        # init form detail
        self.edit_form = detail
        # call init event button
        self.edit_form.initEventHandleButton(self)
        # database
        self.edit_form.database = self.database

    # init data for tab data
    def initTabData(self):
        options = ["StockPrice", "StockExchange", "Ticker", "User"]
        # load data for combobox danh mục
        self.cboTabDataCategory.clear()
        for item in options:
            self.cboTabDataCategory.addItem(item)

        # load data combo sàn giao dịch chứng khoán
        self.cboTabDataExchange.clear()
        dataExchange = self.database.stock_exchange
        for row, exchange in enumerate(dataExchange.find()):
            self.cboTabDataExchange.addItem(exchange["stock_exchange_code"])

        # call load data combo ticker code
        self.loadDataComboTicker(
            self.cboTabDataTickerCode, self.cboTabDataExchange)
        self.initDateRangeTabData()

    # init date range cho tab data
    def initDateRangeTabData(self):
        currentTickerCode = self.cboTabDataTickerCode.currentText()
        currentTicker = self.database.ticker.find_one({'ticker_code': currentTickerCode})
         # load tata for fromDate, todate
        dateVal = QDateTimeEdit()
        dateVal.setDisplayFormat("MM/dd/yyyy")
        if currentTicker:
            # get max date in stock_price
            rowmaxDate = self.database.stock_price.find({'ticker_id':currentTicker['_id']}).sort([('date', -1)]).limit(1)
            maxDate = datetime.datetime.today()
            for row, item in enumerate(rowmaxDate):
                maxDate = item['date']
            fromDate = maxDate - datetime.timedelta(50) 
            # det data to control
            self.tabDataFromDate.setDateTime(fromDate)
            self.tabDataToDate.setDateTime(maxDate)

    def initTabForecast(self):
        # load data combo sàn giao dịch chứng khoán
        self.cboForecastExchange.clear()
        dataExchange = self.database.stock_exchange
        for row, exchange in enumerate(dataExchange.find()):
            self.cboForecastExchange.addItem(exchange["stock_exchange_code"])
        # load data combo ticker
        self.loadDataComboTicker(
            self.cboForcastTicker, self.cboForecastExchange)

        self.initDateRangeTabForecast()    

    # init date range cho tab forecast
    def initDateRangeTabForecast(self):
        currentTickerCode = self.cboForcastTicker.currentText()
        currentTicker = self.database.ticker.find_one({'ticker_code': currentTickerCode})
        qdatetime = QDateTimeEdit()
        qdatetime.setDisplayFormat("MM/dd/yyyy")
        if currentTicker:
            
            # get max date in stock_price
            rowmaxDate = self.database.stock_price.find({'ticker_id':currentTicker['_id']}).sort([('date', -1)]).limit(1)
            maxDate = datetime.datetime.today()
            for row, item in enumerate(rowmaxDate):
                maxDate = item['date']
            fromDate = maxDate - datetime.timedelta(5) 
            self.forecastFromDate.setDateTime(fromDate)
            self.forecastToDate.setDateTime(maxDate)

    # init tab trainning
    def initTabTrainning(self):
        # load data combo sàn giao dịch chứng khoán
        self.cboTrainningExchange.clear()
        dataExchange = self.database.stock_exchange
        for row, exchange in enumerate(dataExchange.find()):
            self.cboTrainningExchange.addItem(exchange["stock_exchange_code"])

        # load data combo ticker
        self.loadDataComboTicker(
            self.cboTrainningTicker, self.cboTrainningExchange)
        options = ["LSTM", "ARIMA"]
        self.cboMethod.addItems(options)
        self.initDateRangeTabTrainning()
        #  init size trainning, testing
        self.spbTrainning.setValue(70)
        self.spbTesting.setValue(30)

    # init date range cho tab trainning
    def initDateRangeTabTrainning(self):
        currentTickerCode = self.cboTrainningTicker.currentText()
        currentTicker = self.database.ticker.find_one({'ticker_code': currentTickerCode})
        qdatetime = QDateTimeEdit()
        qdatetime.setDisplayFormat("MM/dd/yyyy")
        if currentTicker:
            dbStockPrice = self.database.stock_price
            # get max date in stock_price
            rowmaxDate = dbStockPrice.find({'ticker_id':currentTicker['_id']}).sort([('date', -1)]).limit(1)
            maxDate = datetime.datetime.today()
            for row, item in enumerate(rowmaxDate):
                maxDate = item['date']

            # get min date in stock_price
            rowminDate = dbStockPrice.find({'ticker_id':currentTicker['_id']}).sort([('date', 1)]).limit(1)
            minDate = datetime.datetime.today()
            for row, item in enumerate(rowminDate):
                minDate = item['date']

            self.trainningFromDate.setDateTime(minDate)
            self.trainningToDate.setDateTime(maxDate)

    # init event handle click button
    def handleClickButton(self):
        # even edit
        self.btnEdit.clicked.connect(lambda: self.editRow())
        # even delete
        self.btnDelete.clicked.connect(lambda: self.deleteRow())
        # event Add
        self.btnAdd.clicked.connect(lambda: self.addRow())
        # event import
        self.btnImport.clicked.connect(lambda: self.importData())
        # event trainning
        self.btnExetrainning.clicked.connect(lambda: exculteTrainning(self)) 
        # event exe Predictions
        self.btnExeForecast.clicked.connect(lambda: excultePredictions(self))

    # handle event change selection combo
    def handleComboSelectionChange(self):
        # ****** Tab data******
        # init event select item combo category tab data
        self.cboTabDataCategory.currentIndexChanged.connect(
            lambda: self.selectedCategory())

        # init event select item combo exchange tab data
        self.cboTabDataExchange.currentIndexChanged.connect(
            lambda: self.selectedExchange())
        
        # init event selected item combo ticker code
        self.cboTabDataTickerCode.currentIndexChanged.connect(
            lambda: self.loadData()
        )
        #  **** tab trainning ****
        #  init event select item combo exchange tab trainning
        self.cboTrainningExchange.currentIndexChanged.connect(
            lambda: self.loadDataComboTicker(
                self.cboTrainningTicker, self.cboTrainningExchange))

        #  *** tab forecast
        self.cboForecastExchange.currentIndexChanged.connect(
            lambda: self.loadDataComboTicker(
                self.cboForcastTicker, self.cboForecastExchange))

    def handleDateChange(self):
        self.tabDataFromDate.dateChanged.connect(lambda: self.loadData())
        self.tabDataToDate.dateChanged.connect(lambda: self.loadData())

    def handleSpinBoxChange(self):
        self.spbTrainning.valueChanged.connect(lambda: self.changeSpinBox('train'))
        self.spbTesting.valueChanged.connect(lambda: self.changeSpinBox('test'))
    
    def changeSpinBox(self, spbName):
        if spbName == 'train':
            currentVal = self.spbTrainning.value()
            self.spbTesting.setValue(100 - currentVal)
        elif spbName == 'test':
             currentVal = self.spbTesting.value()
             self.spbTrainning.setValue(100 - currentVal)

    # handele event change selection combo category
    def selectedCategory(self):
        #  init detail by category
        self.initDetail()

        # show/hide group box fileter with category
        dicType = str(self.cboTabDataCategory.currentText())
        if dicType != 'StockPrice':
            self.tabDatagrBox.hide()
        else:
            self.tabDatagrBox.show()

        # load data with category
        self.loadData()

    # handle event selected item combo exchange
    def selectedExchange(self):
        # call load data combo ticker code
        self.loadDataComboTicker(
            self.cboTabDataTickerCode, self.cboTabDataExchange)
        # load data table
        self.loadData()

    # load data combo ticker code
    def loadDataComboTicker(self, combo, comboRelate):
        dataExchange = self.database.stock_exchange
        # load data combo mã cổ phiếu
        selectedExchangeText = str(comboRelate.currentText())
        selectedExchange = dataExchange.find_one(
            {'stock_exchange_code': selectedExchangeText})
        selectedExchangeId = selectedExchange["_id"]
        dataTicker = self.database.ticker.find(
            {'stock_exchange_id': ObjectId(str(selectedExchangeId))})
        # clear data combo
        combo.clear()
        for row, data in enumerate(dataTicker):
            combo.addItem(data["ticker_code"])

    # func connect database
    # @author nvan - 30/7/2020
    def connectDatabase(self):
        client = MongoClient('localhost', 27017)
        db = client.StockPriceDB
        self.database = db

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, 'Window Close', 'Bạn có chắc chắn muốn thoát chương trình?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
            print('Window closed')
        else:
            event.ignore()

    # func AddRow
    # @author : nvan - 22/7/2020
    def addRow(self):
        self.edit_form.show()
        self.edit_form.editMode = 0
        self.edit_form.clearData()
        dicType = str(self.cboTabDataCategory.currentText())
        if dicType == 'StockPrice':
            self.edit_form.txtticker.setReadOnly(False)
        elif dicType == 'Ticker':
            self.edit_form.txtstock_exchange_code.setReadOnly(False)

    # eidt row
    # @author : nvan - 22/7/2020
    def editRow(self):
        dicType = str(self.cboTabDataCategory.currentText())
        self.edit_form.show()
        self.edit_form.editMode = 1

        if dicType == 'StockPrice':
            self.edit_form.txtticker.setReadOnly(True)
            collection = self.database.stock_price
        elif dicType == 'StockExchange':
            collection = self.database.stock_exchange
        elif dicType == 'Ticker':
            self.edit_form.txtstock_exchange_code.setReadOnly(True)
            collection = self.database.ticker
        else:
            collection = self.database.user

        table = self.tableData
        for dataRow in sorted(table.selectionModel().selectedRows()):
            row = dataRow.row()
            # find id of recored eidt
            id = self.ids[row]
            self.edit_form.id = id

            # query select row of eidt from database
            data = collection.find_one({'_id': ObjectId(str(id))})

            # binding data to form detail
            # for row, record in enumerate(data):
            for col, key in enumerate(data.keys()):
                if key != '_id':
                    if key == 'date':
                        controlDate = self.edit_form.findChild(
                            QDateEdit, 'txt'+key)
                        # det data to control
                        controlDate.setDateTime(data[key])
                    elif key == 'ticker_id':
                        #  get ticker_code by id
                        dataTicker = self.database.ticker.find_one(
                            {'_id': ObjectId(str(data[key]))})
                        self.edit_form.txtticker.setText(
                            str(dataTicker["ticker_code"]))
                    elif key == 'stock_exchange_id':
                        # get stock_exchange_code
                        dataExchange = self.database.stock_exchange.find_one(
                            {'_id': ObjectId(str(data[key]))})
                        self.edit_form.txtstock_exchange_code.setText(
                            str(dataExchange['stock_exchange_code']))
                    elif key == 'active':
                        if data[key] == 'True':
                            self.edit_form.cbActive.setChecked(True)
                        else:
                            self.edit_form.cbActive.setChecked(False)
                    elif key == 'role':
                        self.edit_form.cboRole.setCurrentIndex(int(data[key]))
                        # if data[key] == '0':
                        #     # self.edit_form.cboRole.findText('Admin')
                        # else :
                        #     self.edit_form.cboRole.setCurrentIndex(self.edit_form.cboRole.findText('User'))
                    else:
                        ctrText = self.edit_form.findChild(
                            QLineEdit, 'txt'+key)
                        if ctrText:
                            ctrText.setText(data[key])
                        else:
                            self.edit_form.findChild(
                                QLineEdit).setText(data[key])

        #table.item(row, 0).text()

    def deleteRow(self):
        table = self.tableData
        for dataRow in sorted(table.selectionModel().selectedRows()):
            row = dataRow.row()
            # find id of recored delete
            id = self.ids[row]
            dicType = str(self.cboTabDataCategory.currentText())
            err = False
            if dicType == 'StockPrice':
                # query delete data
                collection = self.database.stock_price
            elif dicType == 'StockExchange':
                collection = self.database.stock_exchange
                # nếu danh mục đã phát sinh 
                if self.database.ticker.find_one({'stock_exchange_id': ObjectId(str(id))}):
                     QMessageBox.information(self, 'Lỗi', 'Danh mục đã có phát sinh, bạn không thể xóa.', QMessageBox.Ok)
                     err = True
            elif dicType == 'Ticker':
                collection = self.database.ticker
                if self.database.stock_price.find_one({'ticker_id': ObjectId(str(id))}):
                    QMessageBox.information(self, 'Lỗi', 'Danh mục đã có phát sinh, bạn không thể xóa.', QMessageBox.Ok)
                    err = True
            else:
                collection = self.database.user

            if err == False:
                reply = QMessageBox.question(
                    self, 'Delete confirm', 'Bạn có chắc chắn muốn xóa dòng này?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                  collection.delete_one({'_id': ObjectId(str(id))})
                  # load lại dữ liệu cho table
                  self.loadData()
                else:
                  pass

    def importData(self):
        # nhập khẩu dữ liệu cho danh mục
        dicType = str(self.cboTabDataCategory.currentText())
        # nhập khẩu cho mã cổ phiếu
        strTicker = str(self.cboTabDataTickerCode.currentText())
        if dicType == 'StockPrice':
            # read file excle
            fileName = 'D://dataticker/historical-price-{0}.xls'.format(strTicker)
            reader = pd.read_excel(fileName)
            header = ["date", "open",
                      "high", "low", "close", "volume"]
            for i in reader.index:
                row = {}
                errRow = False
                ticker = self.database.ticker
                dataTicker = ticker.find_one(
                {'ticker_code': strTicker})
                if dataTicker:
                    row['ticker_id'] = ObjectId(str(dataTicker['_id']))
                else:
                    print(
                     "mã cổ phiếu " + str(reader[field][i]) + "không có trong danh mục")
                    errRow = True
                for field in header:
                    if field == 'date':
                        # row[field] = datetime.datetime.strptime(reader[field][i], '%m/%d/%Y')
                        stringDate = str(reader[field][i]).replace(" 00:00:00", "")

                        try:
                          date = pd.to_datetime(stringDate, format="%d/%m/%Y")
                        except ValueError:
                          date = pd.to_datetime(stringDate, format="%Y-%d-%m")

                        row[field] = date
                        # parse(stringDate)
                    else:
                        row[field] = str(reader[field][i])
                if errRow == False:
                    self.database.stock_price.insert(row)

        elif dicType == 'Ticker':
            # read file excle
            reader = pd.read_excel(
                'D://dataticker/ticker.xlsx')
            header = ["stock_exchange_code", "ticker_code", "company_name"]
            for i in reader.index:
                row = {}
                errRow = False
                for field in header:
                    if field == "stock_exchange_code":
                        stockExchange = self.database.stock_exchange
                        dataExchange = stockExchange.find(
                            {'stock_exchange_code': reader[field][i]})
                        if dataExchange.count() > 0:
                            row["stock_exchange_id"] = ObjectId(
                                str(dataExchange[0]["_id"]))
                        else:
                            print("Sàn giao dịch chứng khoán: " +
                                  str(reader[field][i]) + " không tồn tại trong danh mục")
                            errRow = True
                    else:
                        row[field] = reader[field][i]
                if errRow == False:
                    self.database.ticker.insert(row)

        elif dicType == 'StockExchange':
            print("import stock exchange")
        else:
            print("import user")

        # load table data after import
        self.loadData()

    # load data to table
    def loadData(self):
        self.ids = []
        self.tableData = self.tblData
        table = self.tableData
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)

        # filter data
        # get selected exchange
        dataTicker = self.database.ticker
        selectTickerText = str(self.cboTabDataTickerCode.currentText())

        # get from date
        qfromDateVal = self.tabDataFromDate.dateTime()
        # part qdatetime to datetime.datetime
        qdatetime = QDateTimeEdit()
        qdatetime.setDisplayFormat("MM/dd/yyyy")
        strDate = qdatetime.textFromDateTime(qfromDateVal)
        fromDateVal = datetime.datetime.strptime(strDate, '%m/%d/%Y')

        # get todate
        qtoDateVal = self.tabDataToDate.dateTime()
        # part qdatetime to datetime.datetime
        qdatetime = QDateTimeEdit()
        qdatetime.setDisplayFormat("MM/dd/yyyy")
        strDate = qdatetime.textFromDateTime(qtoDateVal)
        toDateVal = datetime.datetime.strptime(strDate, '%m/%d/%Y')

        # load dữ liệu cho danh mục
        countCol = 0
        dicType = str(self.cboTabDataCategory.currentText())
        if dicType == 'StockPrice':
            # table query
            stockPrice = self.database.stock_price
            # set count col
            if stockPrice.find_one():
                countCol = len(stockPrice.find_one().keys())

            filter = {}
            # get id ticker
            if dataTicker.find().count() > 0:
                selectTicker = (dataTicker.find_one(
                    {'ticker_code': selectTickerText}))
                if selectTicker:
                    selectTickerId = selectTicker['_id']
                    if fromDateVal == toDateVal: 
                        filter = {
                            'ticker_id': selectTickerId,
                            'date': fromDateVal 
                            }  
                    else : 
                        filter = {
                            'ticker_id': selectTickerId,
                            'date': {'$gte': fromDateVal, '$lte': toDateVal }  
                            }   

            # các column ẩn
            hiddenCol = ['_id', 'ticker_id']
            dataTable = stockPrice.find(filter)

        elif dicType == 'StockExchange':
            # table query
            stockExchange = self.database.stock_exchange
            # count col
            if stockExchange.find_one():
                countCol = len(stockExchange.find_one().keys())

            # set hidden col
            hiddenCol = ['_id']
            dataTable = stockExchange.find({})

        elif dicType == 'Ticker':
            # table query
            ticker = self.database.ticker
            # count col
            if ticker.find_one():
                countCol = len(ticker.find_one().keys())
            # set hidden col
            hiddenCol = ['_id', 'stock_exchange_id']
            dataTable = ticker.find({})
        # list user
        else:
            # table query
            user = self.database.user
            # count col
            if user.find_one():
                countCol = len(user.find_one().keys())
            # {qdatetime.dateTimeFromText("date"): {"$gt": fromDateVal}}
            hiddenCol = ['_id']
            dataTable = user.find({})

        # set col count
        table.setColumnCount(countCol - len(hiddenCol))
        # set count row
        countRow = dataTable.count()
        table.setRowCount(countRow)
        horHeaders = []
        for row, record in enumerate(dataTable):
            for col, key in enumerate(record.keys()):
                if not hiddenCol.__contains__(key):
                    if key == 'date':
                        horHeaders.append(key)
                        if(type(record[key]) == datetime.datetime):
                            dateVal = QDateTimeEdit()
                            dateVal.setDisplayFormat("MM/dd/yyyy")
                            strDate = dateVal.textFromDateTime(record[key])
                            newitem = QTableWidgetItem(strDate)
                            table.setItem(row, col - len(hiddenCol), newitem)
                        else:
                            newitem = QTableWidgetItem(record[key])
                            table.setItem(row, col - len(hiddenCol), newitem)
                    else:
                        horHeaders.append(key)
                        newitem = QTableWidgetItem(record[key])
                        table.setItem(row, col - len(hiddenCol), newitem)
                elif key == '_id':
                    self.ids.append(record[key])

        table.setHorizontalHeaderLabels(horHeaders)


app = QApplication(sys.argv)
window = Main()
app.exec_()
