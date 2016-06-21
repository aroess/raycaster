#!/usr/local/bin/python
# -*- coding: utf-8 -*-

class GameLevel(object):
    def __init__(self, file):
        #read game field
        self.table = []
        with open(file, "r") as f:
            for line in f: 
                self.table.append(line.split(","))
            for i in range(0, len(self.table)):
                for j in range(0, len(self.table[i])):
                    self.table[i][j] = int(self.table[i][j])
