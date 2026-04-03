#importing libraries
import numpy as np
import math
import tkinter as tk
from tkinter import ttk

#dist between points in 2D
def dist2DPoints(point1, point2):
    return ((point1[0]-point2[0])**2+(point1[1]-point2[1])**2)**0.5

class Scene():
    def __init__(self):
        self.entries = []

    def add(self, shape, operation):
        self.entries.append((shape, operation))

    def remove(self, index):
        self.entries.remove(index)

    def evaluate(self, grid, shapeID1, shapeID2):
        opToNumPy = {'union': 'np.minimum(' + shapeID1 + ', ' + shapeID2 + ')', 
        'subtraction': 'np.minimum(' + shapeID1 + ', -1 * ' + shapeID2 + ')', 
        'intersection': 'np.maximum(' + shapeID1 + ', ' + shapeID2 + ')'} 

class App():
    def __init__(self, dims):
        self.root = tk.Tk()
        self.canvas = tk.Canvas(self.root, width=dims[0], height=dims[1])
        self.img = None
        self.scene = []
        self.canvas.pack()

    def sdfToPixelColor(self, sdfArray):
        pixelColorArray = []
        for y in reversed(range(0, len(sdfArray))):
            pixelColorListx = []
            for x in range(0, len(sdfArray[y])):
                if (sdfArray[y][x] < -2):
                    pixelColorListx.append('#4488ff')
                elif (sdfArray[y][x] >= -2 and sdfArray[y][x] <= 2):
                    pixelColorListx.append('#000000')
                elif (sdfArray[y][x] > 2):
                    pixelColorListx.append('#ffa500')
                else:
                    print('FATAL ERROR')
                    return None
            pixelColorArray.append('{' + ' '.join(pixelColorListx) + '}')
        return ' '.join(pixelColorArray)

    def renderSDF(self, sdfArray):
        colorString = self.sdfToPixelColor(sdfArray)
        img = tk.PhotoImage(width=len(sdfArray[0]), height=len(sdfArray))
        img.put(colorString)
        img = img.zoom(1)
        self.canvas.create_image(0, 0, anchor='nw', image=img)
        self.canvas.img = img

class Grid():
    def __init__(self, xLeft, xRight, xStep, yLower, yUpper, yStep):
        self.xLeft = xLeft
        self.xRight = xRight
        self.xStep = xStep
        self.yLower = yLower
        self.yUpper = yUpper
        self.yStep = yStep
        self.meshgrid = None

    def create(self):
        self.meshgrid = np.meshgrid(
            np.arange(self.xLeft, self.xRight, self.xStep),
            np.arange(self.yLower, self.yUpper, self.yStep)
        )
        return self.meshgrid

class Shape():
    def __init__(self):
        pass

    def evaluate(self, grid):
        raise NotImplementedError

class Circle(Shape):
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def evaluate(self, grid):
        return(dist2DPoints(grid, self.center) - self.radius)

class Rectangle(Shape):
    def __init__(self, center, dims):
        self.center = center
        self.dims = dims

    def evaluate(self, grid):
        d = [np.subtract(np.abs(np.subtract(grid[0], self.center[0])), self.dims[0]/2),
             np.subtract(np.abs(np.subtract(grid[1], self.center[1])), self.dims[1]/2)]
        return dist2DPoints([np.maximum(d[0],0), np.maximum(d[1], 0)], [0,0]) + np.minimum(np.maximum(d[0], d[1]), 0)

sketch1 = Grid(-500, 500, 1, -500, 500, 1).create()
rect1 = Rectangle([0,10], [50,75])
circle1 = Circle([0,1], 40)
sdfRender = np.minimum(rect1.evaluate(sketch1), circle1.evaluate(sketch1))
window1 = App([1000, 1000])
window1.renderSDF(sdfRender)
window1.root.mainloop()