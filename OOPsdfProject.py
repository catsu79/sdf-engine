#importing libraries
import numpy as np
import math
import tkinter as tk
from tkinter import ttk

#functions

#dist between points in 2D
def dist2DPoints(point1, point2):
    return ((point1[0]-point2[0])**2+(point1[1]-point2[1])**2)**0.5

class Grid():
    xLeft 
    xRight
    xStep
    yLower
    yUpper
    ystep
    def create(xLeft, xRight, xStep, yLower, yUpper, yStep):
        return np.meshgrid(np.arange(xLeft, xRight, xStep), np.arange(yLower, yUpper, yStep))

class Shape():

    def evaluate(grid):
        raise NotImplementedError

    class Circle(Shape):
        center 
        radius 

        def evaluate(grid, center, radius):
            return(dist2DPoints(grid, center) - radius)

    class Rectangle(Shape):
        center 
        length 
        width
        
        def evaluate(grid, center, lengthWidthList):
            d = [np.subtract(np.abs(np.subtract(grid[0], center[0])), halfDimList[0]/2), np.subtract(np.abs(np.subtract(grid[1], center[1])), halfDimList[1]/2)]
            return dist2DPoints([np.maximum(d[0],0), np.maximum(d[1], 0)], [0,0]) + np.minimum(np.maximum(d[0], d[1]), 0)

