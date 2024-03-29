#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 16:39:05 2019

@author: ben
"""

import os
import pickle

def save(grid, file):
    file = file + ".vw"
    with open(file, 'wb') as f:
         pickle.dump(grid, f)
    
def load(file):
    with open(file, 'rb') as f:
        return pickle.load(f)

def files():
    return [file for file in os.listdir('.') if file.endswith(".vw")]
    

