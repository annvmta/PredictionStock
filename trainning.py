import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"] = ""

#import packages
import pandas as pd
import numpy as np

#to plot within notebook
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, LSTM
import datetime
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QDateTimeEdit, QMessageBox
from bson.objectid import ObjectId

#setting figure size
from matplotlib.pylab import rcParams

#for normalizing data
from sklearn.preprocessing import MinMaxScaler

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width = 16, height = 8, linewidth = 1.0, dpi=200):
        fig = Figure(figsize=(width, height), linewidth = linewidth, dpi=dpi)
        self.axes = fig.add_subplot(111)
        
        super(MplCanvas, self).__init__(fig)

def exculteTrainning(self):
    # rcParams['figure.figsize'] = 30,20
    scaler = MinMaxScaler(feature_range=(0, 1))
    sc = MplCanvas(self, width = 16, height = 8, linewidth = 1.0, dpi=200)
    sc.setSizePolicy(
            1250, 760)
    sc.updateGeometry()

    # mã cổ phiếu thực hiện trainning
    tikcerTrainning = self.cboTrainningTicker.currentText()
    dbticker = self.database.ticker
    dataTicker = dbticker.find_one({'ticker_code': tikcerTrainning})
    queryDataTrainning = {'ticker_id': ObjectId(str(dataTicker['_id']))}       
    dataTrainning =  self.database.stock_price.find(queryDataTrainning)

    # phần dữ liệu trainning
    sizeTrainning = self.spbTrainning.value()
    # phần dữ liệu testting
    sizeTesting = self.spbTesting.value()
    df = pd.DataFrame(list(dataTrainning))
    df.index = df['date']
    #print the head
    df.head()
    # số dòng dữ liệu
    totalRow = len(df)
    if sizeTrainning == 0 or int(totalRow * (sizeTrainning / 100)) < 60:
        QMessageBox.information(self, 'Lỗi', 'số dòng dữ liệu trainning phải lớn hơn 60.', QMessageBox.Ok)
    else: 
        lenTraining = int(totalRow * (sizeTrainning / 100))
        print(lenTraining)
        # convert close to float
        df['close'] = df['close'].astype(float)
        df['date'] = pd.to_datetime(df['date'], format="%m/%d/%Y")

        data = df.sort_index(ascending=True, axis=0)
        new_data = pd.DataFrame(index=range(0,len(df)), columns=['date', 'close'])
        for i in range(0,len(data)):
            new_data['date'][i] = data['date'][i]
            new_data['close'][i] = data['close'][i]

        #setting index
        new_data.index = new_data.date
        new_data.drop('date', axis=1, inplace=True)

        #creating train and test sets
        dataset = new_data.values
        train = dataset[0:lenTraining,:]
        valid = dataset[lenTraining:,:]

        #converting dataset into x_train and y_train
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(dataset)

        x_train, y_train = [], []
        for i in range(60,len(train)):
            x_train.append(scaled_data[i-60:i,0])
            y_train.append(scaled_data[i,0])
        x_train, y_train = np.array(x_train), np.array(y_train)

        x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))

        # create and fit the LSTM network
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1],1)))
        model.add(LSTM(units=50))
        model.add(Dense(1))

        model.compile(loss='mean_squared_error', optimizer='adam')
        model.fit(x_train, y_train, epochs=1, batch_size=1, verbose=2)

        modelFileName = 'Model\{0}.h5'.format(tikcerTrainning)
        model.save(modelFileName)

        #predicting 246 values, using past 60 from the train data
        inputs = new_data[len(new_data) - len(valid) - 60:].values
        inputs = inputs.reshape(-1,1)
        inputs  = scaler.transform(inputs)
        X_test = []

        for i in range(60,inputs.shape[0]):
            X_test.append(inputs[i-60:i,0])
        X_test = np.array(X_test)

        X_test = np.reshape(X_test, (X_test.shape[0],X_test.shape[1],1))
        closing_price = model.predict(X_test)
        closing_price = scaler.inverse_transform(closing_price)

        rms=np.sqrt(np.mean(np.power((valid-closing_price),2)))
        rms
        print('Test RMSE: %.3f' % rms)

        train = new_data[:lenTraining]
        valid = new_data[lenTraining:]
        valid['Predictions'] = closing_price
        # plt.plot(train['close'])
        # plt.plot(valid[['close','Predictions']])

        #  xóa biểu đồ cũ khi trainning
        for i in reversed(range(self.layoutResultTrainning.count())): 
            self.layoutResultTrainning.itemAt(i).widget().deleteLater()

        self.layoutResultTrainning.addWidget(sc)
        # np.arange(step=5)
        train.plot(y= 'close', ax=sc.axes)
        valid.plot(y = ['close', 'Predictions'], ax=sc.axes)

def excultePredictions(self):
    todate = pd.to_datetime("07/08/2020", format="%d/%m/%Y")
    fromDate = todate - datetime.timedelta(150) 
     # mã cổ phiếu thực hiện trainning
    tikcerPrediction = self.cboForcastTicker.currentText()
    dbticker = self.database.ticker
    dataTicker = dbticker.find_one({'ticker_code': tikcerPrediction}) 

    query = {'date': {'$gte': fromDate, '$lt': todate },
            'ticker_id': ObjectId(str(dataTicker['_id']))}
    dataPredictions =  self.database.stock_price.find(query)   
    df = pd.DataFrame(list(dataPredictions))    
    df.index = df['date']
    df['close'] = df['close'].astype(float)
    data = df.sort_index(ascending=True, axis=0)

    new_data = pd.DataFrame(index=range(0,len(df)),columns=['date', 'close'])
    for i in range(0,len(data)):
        new_data['date'][i] = data['date'][i]
        new_data['close'][i] = data['close'][i]

    qdatetime = QDateTimeEdit()
    qdatetime.setDisplayFormat("MM/dd/yyyy")   
    # get from date
    qfromDateVal = self.forecastFromDate.dateTime()
    # part qdatetime to datetime.datetime
    strFromDate = qdatetime.textFromDateTime(qfromDateVal)
    fromDateVal = datetime.datetime.strptime(strFromDate, '%m/%d/%Y')

    # get to date
    qToDateVal = self.forecastToDate.dateTime()
    # part qdatetime to datetime.datetime
    strtoDate = qdatetime.textFromDateTime(qToDateVal)
    toDateVal = datetime.datetime.strptime(strtoDate, '%m/%d/%Y')
    distance = (toDateVal - fromDateVal).days
 
    # add date prediction to newData
    for i in range(0 , distance + 1):
        new_data = new_data.append({'date': fromDateVal + datetime.timedelta(i), 'close': 0}, ignore_index=True)

    # custom data để hiển thị kết quả
    customData = new_data[0:]
    #setting index
    new_data.index = new_data.date
    new_data.drop('date', axis=1, inplace=True)
    #creating test sets
    dataset = new_data.values
    # size data dự báo
    valid = dataset[(len(new_data) - distance -1):,:]

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit_transform(dataset)
    modelFile = "Model\{0}.h5".format(tikcerPrediction)
    model =  load_model(modelFile)

    inputs = new_data[len(new_data) - len(valid) - 60:].values
    inputs = inputs.reshape(-1,1)
    inputs  = scaler.transform(inputs)
    X_test = []

    for i in range(60,inputs.shape[0]):
        X_test.append(inputs[i-60:i,0])

    X_test = np.array(X_test)

    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1],1))
    closing_price = model.predict(X_test)
    closing_price = scaler.inverse_transform(closing_price)
    closing_price = list(closing_price)
    
    real = customData[(len(new_data) - distance - 1):]
    table = self.tblResultPrediction
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeToContents)
    header.setStretchLastSection(True)

    table.setColumnCount(2)
    table.setRowCount(distance + 1)
    horHeaders = ['Date', 'Prediction close price']
    table.setHorizontalHeaderLabels(horHeaders)
    rowPrice = 0
    for item in closing_price :
        newitem = QTableWidgetItem(str(item[0]))      
        table.setItem(rowPrice, 1, newitem)
        rowPrice = rowPrice + 1

    rowDate = 0
    for item in list(real['date']):
        dateVal = QDateTimeEdit()
        dateVal.setDisplayFormat("MM/dd/yyyy")
        strDate = dateVal.textFromDateTime(item)
        newitem = QTableWidgetItem(strDate)      
        table.setItem(rowDate, 0, newitem)
        rowDate = rowDate + 1

    # input form predict
    # using past 60 day from the train data






