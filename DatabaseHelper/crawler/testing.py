'''
Created on May 30, 2017

@author: Choony
'''
import pickle
import pprint

from DataType.iPolyCourse import iPolyCourse

PolyList = []
try:
    with open("./PolyData.pkl",'rb') as file:
        while True:                          # loop indefinitely
            PolyList.append(pickle.load(file))  # add each item from the file to a list
except EOFError:  
    pass
for test in PolyList:
    pprint.pprint(test.name)