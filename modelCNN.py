# -*- coding: utf-8 -*-
"""
Created on Sun Feb  2 11:21:26 2020

@author: daimi
"""


import matplotlib.pyplot as plt
import keras
from keras.callbacks import ModelCheckpoint
import numpy as np
import csv
from keras.utils import to_categorical
from keras.models import Sequential, Model
from keras.layers import Input,Dense, Conv3D, Flatten, MaxPooling3D, BatchNormalization, GlobalAveragePooling3D, LeakyReLU, Dropout
from keras.regularizers import l2
from keras.models import load_model


#function for loading data
#loading microstructure 
def load_X1data(number=100,dim=100):
    X1data=np.empty((number,dim,dim,dim,1))
    X1data_temp=np.empty((dim,dim,dim,1))
    for n in range(0,number):
        structure_path='structure/struct_{:03d}.in'.format(n)
        structure=np.loadtxt(structure_path)
        
        for i in range(0,dim):
            for j in range(0,dim):
                for k in range(0,dim):
                    X1data_temp[i,j,k,0]=structure[k+j*dim+i*dim*dim,3]
        
        X1data[n,]=X1data_temp[:]
        
    return X1data

#loading interface conductivity    
def load_X2data(number=100):
    X2data=np.empty((number,1))
    with open('interface_conductivity.csv') as csv_file:
        X2data_file=csv.reader(csv_file)
        for i,sample in enumerate(X2data_file):
            X2data[i,0]=np.asarray(sample[:],dtype=np.float64)

    return X2data 

#loading conductivity
def load_Ydata(number=100):
    Ydata=np.empty((number,1))
    with open('conductivity.csv') as csv_file:
        Ydata_file=csv.reader(csv_file)
        for i,sample in enumerate(Ydata_file):
            Ydata[i,0]=np.asarray(sample[:],dtype=np.float64)

    return Ydata


#specify data dimension
dim=100   #dim of structure

#CNN model set
X1data_input=Input(shape=(dim,dim,dim,1))  #input1 shape
X2data_input=Input(shape=(1,))  #input2 shape

conv1=Conv3D(64, (3,3,3), activation='relu',data_format='channels_last')(X1data_input) # first CNN layer
#conv1=BatchNormalization()(conv1)
conv2=Conv3D(32, (3,3,3), activation='relu',kernel_regularizer=l2(0.01),activity_regularizer=l2(0.01))(conv1)# second CNN layer
#conv2=BatchNormalization()(conv2)
pooling1=MaxPooling3D(pool_size=(2, 2, 2), strides=None, padding='valid', data_format=None)(conv2) # maxPooling
conv3=Conv3D(16, (3,3,3), activation='relu',kernel_regularizer=l2(0.01),activity_regularizer=l2(0.01))(pooling1)
#conv3=BatchNormalization()(conv3)
pooling2=MaxPooling3D(pool_size=(2, 2, 2), strides=None, padding='valid', data_format=None)(conv3)

flatten=Flatten()(pooling2)  #flatten
#flatten=BatchNormalization()(flatten)
Dropout1=Dropout(rate=0.5)(flatten)
Dense1=Dense(256,activation="relu",kernel_regularizer=l2(0.01),activity_regularizer=l2(0.01))(Dropout1)
#Dense1=BatchNormalization()(Dense1)
Dropout2=Dropout(rate=0.5)(Dense1)
featuremap=Dense(16, activation= "relu")(Dropout2) # fully connected layer, output probablities
merged=keras.layers.concatenate([featuremap,X2data_input])  #add interface conductivity to feature map
result=Dense(1)(merged)  #final result
my_model=Model(inputs=[X1data_input,X2data_input],outputs=result) #specify input and output of the model
adam = keras.optimizers.Adam(lr=0.0001, beta_1=0.9, beta_2=0.999, amsgrad=False)
my_model.compile(loss='mean_squared_error', optimizer=adam, metrics=['mse']) #compile the model

#print summayr of the model
my_model.summary()


#load data
number=667   #number of data points
X1data=load_X1data(number,dim)   #size of X1data: (number,dim,dim,dim,1)
X2data=load_X2data(number)     #size of X2data: (number,1)
Ydata=load_Ydata(number)      #size of Ydata: (number,1)

#Specify training and testing set  
X1data_train=X1data[:-60]
X2data_train=X2data[:-60]
Ydata_train=Ydata[:-60]
X1data_test=X1data[-60:]
X2data_test=X2data[-60:]
Ydata_test=Ydata[-60:]

#main
checkpoint_name = 'Weights-{epoch:03d}--{val_loss:.5f}.hdf5' 
checkpoint = ModelCheckpoint(checkpoint_name, monitor='val_loss', verbose = 1, save_best_only = True, mode ='auto',period=1)
callbacks_list = [checkpoint]

#check input and output data shape
print(X1data_train.shape)
print(X2data_train.shape)
print(Ydata_train.shape)

#model fit
my_model.fit([X1data_train,X2data_train],Ydata_train, epochs=500, batch_size=32, validation_split = 0.1, callbacks=callbacks_list)

#
## Load wights file of the best model :
#wights_file = checkpoint_name # choose the best checkpoint 
#my_model.load_weights(wights_file) # load it
#my_model.compile(loss='mean_absolute_error', optimizer='adam', metrics=['mean_absolute_error'])
