import numpy as np
import math
import tkinter as tk
from tkinter import ttk

#functions

#call coordinate plane
def coordinatePlane2D(xleft, xright, xstep, yleft, yright, ystep):
    return np.meshgrid(np.arange(xleft, xright, xstep), np.arange(yleft, yright, ystep))

#dist between points in 2D
def dist2DPoints(point1, point2):
    return ((point1[0]-point2[0])**2+(point1[1]-point2[1])**2)**0.5

#Circle SDF
def circleSDF(center, radius, coordinatePlaneName):
    return(dist2DPoints(coordinatePlaneName, center) - radius)

#Rectangle SDF
def rectSDF(center, halfDimList, coordinatePlaneName):
   d = [np.subtract(np.abs(np.subtract(coordinatePlaneName[0], center[0])), halfDimList[0]), np.subtract(np.abs(np.subtract(coordinatePlaneName[1], center[1])), halfDimList[1])]
   return dist2DPoints([np.maximum(d[0],0), np.maximum(d[1], 0)], [0,0]) + np.minimum(np.maximum(d[0], d[1]), 0)

def updateCanvas(coordinatePlaneName):
    pixelColorArray = []
    for y in reversed(range(0, len(coordinatePlaneName))):
        pixelColorListx = []
        for x in range(0, len(coordinatePlaneName[y])):
            if (coordinatePlaneName[y][x] < -1):
                pixelColorListx.append('#4488ff ')
            elif (coordinatePlaneName[y][x] >= -1 and coordinatePlaneName[y][x] <= 1):
                pixelColorListx.append('#000000 ')
            elif (coordinatePlaneName[y][x] > 1):
                pixelColorListx.append('#ffa500 ')    
            else:
                print('FATAL ERROR')
                return None
        pixelColorArray.append('{' + ' '.join(pixelColorListx) + '}')
    return ' '.join(pixelColorArray)

def initTk():
    root = tk.Tk()
    root.title('Canvas Demo')

    canvas = tk.Canvas(root, width=1800, height=1000, bg='white')
    canvas.pack(anchor=tk.CENTER, expand=True)


    root.mainloop()

def renderSDF(root, sdfArray):
    colorString = updateCanvas(sdfArray)
    
    canvas = tk.Canvas(root, width=1000, height=800)
    canvas.pack()
    
    img = tk.PhotoImage(width=len(sdfArray[0]), height=len(sdfArray))
    img.put(colorString)
    img = img.zoom(1)
    
    canvas.create_image(0, 0, anchor='nw', image=img)
    canvas.img = img 

def main():
    sketch1 = coordinatePlane2D(-700, 700, 1, -300, 300, 1)
    sdfResult = np.minimum(rectSDF([-1, 2], [50, 30], sketch1), circleSDF([0, 0], 30, sketch1))
    
    root = tk.Tk()
    root.title('SDF Engine')
    renderSDF(root, sdfResult)
    root.mainloop()

main()
