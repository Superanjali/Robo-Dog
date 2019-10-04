# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 19:20:55 2019

@author: User
"""

from playsound import playsound
import time

'''
d = int(input())
i = int(input())

if direct == 'right':
    d = 0
elif direct == 'left':
    d = 1
else:
    print('direction not found')
'''
def soundplay(d,deg):    
    if not d:
        for i in range(deg):
            playsound('beep-01a.wav')
    elif d == 1:
        for i in range(deg):
            playsound('beep-02.wav')
    else:
        playsound('button-30.wav')
        
        
        
inputs = [(0,1), (0,2), (0,3),(1,1),(0,1),(1,2),(2,0)]

for i in inputs:
    soundplay(i[0],i[1])
    time.sleep(2)