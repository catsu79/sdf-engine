#importing public python libraries
import numpy as np
import math
import tkinter as tk
from tkinter import ttk

#distance between points in 2D using Pythagorean Theorem (use for vectors too)
def dist2DPoints(point1, point2):
    return ((point1[0]-point2[0])**2+(point1[1]-point2[1])**2)**0.5

#represents the instructions for the composite shape (Scene and Grid are married: one instance of each is paired to the other)
#add adds primitives and their operation to the composite creation instructions
#remove removes a primitive with its operation
#compute recursively puts NumPy methods to make the instructions executable for the Signed Distance Field (SDF) composite
class Scene():
    def __init__(self, grid):
        self.entries = []
        self.grid = grid
    
    def add(self, shape, operation):
        self.entries.append((shape, operation))

    def remove(self, index):
        self.entries.pop(index)

    def compute(self, i = None):
        if (i == None):
            i = len(self.entries) - 1
        if (i == 0):
            shapeID1 = self.entries[0][0].evaluate(self.grid)
        else:
            shapeID1 = self.compute(i = i - 1)
        shapeID2 = self.entries[i][0].evaluate(self.grid)
        opToNumPy = {'union': np.minimum(shapeID1, shapeID2), 
        'subtraction': np.maximum(shapeID1, -1 * shapeID2), 
        'intersection': np.maximum(shapeID1, shapeID2)}
        return opToNumPy[self.entries[i][1]]
    
#represents the TKinter window and all GUI things are processed here
#most GUI configuration is done by AI due to high volume of TKinter widget configuration code
#onShapeSelected handles widget popups and mapping when selecting and inputting shape and shape parameters (by AI)
#onAddShape pulls widget values and adds the new shape as a tuple of shape_instance and operation to the Scene() instuctions
#sdfToPixelColor walks the SDF to convert values into hex colors for TKinter's .put method to show user viewable PhotoImage
#renderSDF renders the converted SDF as a TKinter canvas widget in the window
class App():
    def __init__(self, canvasDims, scene):
        self.root = tk.Tk()
        self.root.title('SDF Engine')
        self.scene = scene
        self.shapeCounts = {'Circle': 0, 'Rectangle': 0}

        #The following lines 53 - 142 are written by Claude AI Opus 4.6 by Anthropic
        # sidebar on the left, canvas on the right
        self.sidebarFrame = tk.Frame(self.root, width=260, bg='#2b2b2b')
        self.sidebarFrame.pack(side='left', fill='y')
        self.sidebarFrame.pack_propagate(False)
        self.canvasFrame = tk.Frame(self.root)
        self.canvasFrame.pack(side='right', fill='both', expand=True)

        self.canvas = tk.Canvas(self.canvasFrame, width=canvasDims[0], height=canvasDims[1], bg='#1a1a1a')
        self.canvas.pack()

        # ---- ADD SHAPE SECTION ----
        tk.Label(self.sidebarFrame, text='Add Shape', bg='#2b2b2b', fg='white',
                 font=('Arial', 14, 'bold')).pack(pady=(20, 10))

        # shape type dropdown
        self.shapeVar = tk.StringVar(value='Select...')
        self.shapeDropdown = ttk.Combobox(self.sidebarFrame, textvariable=self.shapeVar,
                                          values=['Circle', 'Rectangle'], state='readonly', width=20)
        self.shapeDropdown.pack(pady=5)
        self.shapeVar.trace_add('write', self.onShapeSelected)

        # container for dynamically generated parameter fields
        self.paramFrame = tk.Frame(self.sidebarFrame, bg='#2b2b2b')
        self.paramFrame.pack(pady=5, padx=15, fill='x')

        # boolean operation dropdown
        tk.Label(self.sidebarFrame, text='Operation', bg='#2b2b2b', fg='white').pack(pady=(10, 2))
        self.opVar = tk.StringVar(value='union')
        self.opDropdown = ttk.Combobox(self.sidebarFrame, textvariable=self.opVar,
                                       values=['union', 'subtraction', 'intersection'], state='readonly', width=20)
        self.opDropdown.pack(pady=5)

        # add shape button
        tk.Button(self.sidebarFrame, text='Add to Scene', width=20,
                  command=self.onAddShape).pack(pady=20)

        # dict storing references to parameter Entry widgets
        self.paramEntries = {}

    def onShapeSelected(self, *args):
        # clear old parameter fields
        for widget in self.paramFrame.winfo_children():
            widget.destroy()
        self.paramEntries = {}
        shape = self.shapeVar.get()
        self.shapeCounts[shape] = self.shapeCounts.get(shape, 0) + 1
        defaultName = shape.lower() + str(self.shapeCounts[shape])
        tk.Label(self.paramFrame, text='Name', bg='#2b2b2b', fg='white').pack(anchor='w')
        self.paramEntries['name'] = tk.Entry(self.paramFrame, width=15)
        self.paramEntries['name'].insert(0, defaultName)
        self.paramEntries['name'].pack(anchor='w', pady=2)

        if shape == 'Circle':
            tk.Label(self.paramFrame, text='Center', bg='#2b2b2b', fg='white').pack(anchor='w', pady=(8, 0))
            centerRow = tk.Frame(self.paramFrame, bg='#2b2b2b')
            centerRow.pack(fill='x', pady=2)
            tk.Label(centerRow, text='(', bg='#2b2b2b', fg='white').pack(side='left')
            self.paramEntries['cx'] = tk.Entry(centerRow, width=6)
            self.paramEntries['cx'].pack(side='left')
            tk.Label(centerRow, text=',', bg='#2b2b2b', fg='white').pack(side='left')
            self.paramEntries['cy'] = tk.Entry(centerRow, width=6)
            self.paramEntries['cy'].pack(side='left')
            tk.Label(centerRow, text=')', bg='#2b2b2b', fg='white').pack(side='left')

            tk.Label(self.paramFrame, text='Radius', bg='#2b2b2b', fg='white').pack(anchor='w', pady=(8, 0))
            self.paramEntries['r'] = tk.Entry(self.paramFrame, width=6)
            self.paramEntries['r'].pack(anchor='w', pady=2)

        elif shape == 'Rectangle':
            tk.Label(self.paramFrame, text='Center', bg='#2b2b2b', fg='white').pack(anchor='w', pady=(8, 0))
            centerRow = tk.Frame(self.paramFrame, bg='#2b2b2b')
            centerRow.pack(fill='x', pady=2)
            tk.Label(centerRow, text='(', bg='#2b2b2b', fg='white').pack(side='left')
            self.paramEntries['cx'] = tk.Entry(centerRow, width=6)
            self.paramEntries['cx'].pack(side='left')
            tk.Label(centerRow, text=',', bg='#2b2b2b', fg='white').pack(side='left')
            self.paramEntries['cy'] = tk.Entry(centerRow, width=6)
            self.paramEntries['cy'].pack(side='left')
            tk.Label(centerRow, text=')', bg='#2b2b2b', fg='white').pack(side='left')

            tk.Label(self.paramFrame, text='Dimensions (W, H)', bg='#2b2b2b', fg='white').pack(anchor='w', pady=(8, 0))
            dimsRow = tk.Frame(self.paramFrame, bg='#2b2b2b')
            dimsRow.pack(fill='x', pady=2)
            tk.Label(dimsRow, text='(', bg='#2b2b2b', fg='white').pack(side='left')
            self.paramEntries['w'] = tk.Entry(dimsRow, width=6)
            self.paramEntries['w'].pack(side='left')
            tk.Label(dimsRow, text=',', bg='#2b2b2b', fg='white').pack(side='left')
            self.paramEntries['h'] = tk.Entry(dimsRow, width=6)
            self.paramEntries['h'].pack(side='left')
            tk.Label(dimsRow, text=')', bg='#2b2b2b', fg='white').pack(side='left')
    #This is the end of the lines 53 - 142 written by Claude AI Opus 4.6 by Anthropic

    def onAddShape(self):
        try:
            shape = self.shapeVar.get()
            name = str(self.paramEntries['name'].get())
            if (shape == 'Circle'):
                center = [float(self.paramEntries['cx'].get()), float(self.paramEntries['cy'].get())]
                radius = float(self.paramEntries['r'].get())
                self.scene.add(Circle(name, center, radius), self.opVar.get())
            elif (shape == 'Rectangle'):
                center = [float(self.paramEntries['cx'].get()), float(self.paramEntries['cy'].get())]
                dims = [float(self.paramEntries['w'].get()), float(self.paramEntries['h'].get())]        
                self.scene.add(Rectangle(name, center, dims), self.opVar.get())
            self.renderSDF(self.scene.compute())
        except Exception as error:
            print(str(error) + ' error when adding shape')

    def sdfToPixelColor(self, sdfArray):
        pixelColorArray = []
        for y in reversed(range(0, len(sdfArray))):
            pixelColorListx = []
            for x in range(0, len(sdfArray[y])):
                if (sdfArray[y][x] < -3):
                    pixelColorListx.append('#4488ff')
                elif (sdfArray[y][x] >= -3 and sdfArray[y][x] <= 0):
                    pixelColorListx.append('#000000')
                elif (sdfArray[y][x] > 0):
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
        self.canvas.delete('all')
        self.canvas.create_image(0, 0, anchor='nw', image=img)
        self.canvas.img = img

#represents the SDF itself (Scene and Grid are married: see line 11)
#create creates the SDF's base state of a meshgrid with x and y values held to perform initial distance calculations
class Grid():
    def __init__(self, xLeft, xRight, xStep, yLower, yUpper, yStep):
        self.xLeft = xLeft
        self.xRight = xRight
        self.xStep = xStep
        self.yLower = yLower
        self.yUpper = yUpper
        self.yStep = yStep
        self.meshgrid = None
        self.scene = None

    def create(self):
        self.meshgrid = np.meshgrid(
            np.arange(self.xLeft, self.xRight, self.xStep),
            np.arange(self.yLower, self.yUpper, self.yStep)
        )
        self.scene = Scene(self.meshgrid)
        return self.meshgrid

#a parent class representing all shapes
#evaluate raises an error if someone tries to evaluate an ambiguous shape
class Shape():
    def __init__(self):
        pass

    def evaluate(self, grid):
        raise NotImplementedError

#represents circle objects
#evaluate computes the SDF of the circle
class Circle(Shape):
    def __init__(self, name, center, radius):
        self.name = name
        self.center = center
        self.radius = radius

    #The logic for the following function was derived from https://iquilezles.org/articles/distfunctions2d/
    def evaluate(self, grid):
        return(dist2DPoints(grid, self.center) - self.radius)

#represents rectangle objects
#evaluate computes the SDF of the rectangle
class Rectangle(Shape):
    def __init__(self, name, center, dims):
        self.name = name
        self.center = center
        self.dims = dims

    #The logic for the following function was derived from https://iquilezles.org/articles/distfunctions2d/
    def evaluate(self, grid):
        d = [np.subtract(np.abs(np.subtract(grid[0], self.center[0])), self.dims[0]/2),
             np.subtract(np.abs(np.subtract(grid[1], self.center[1])), self.dims[1]/2)]
        return dist2DPoints([np.maximum(d[0],0), np.maximum(d[1], 0)], [0,0]) + np.minimum(np.maximum(d[0], d[1]), 0)

#main code: stores the Grid, creates the arrays, creates the Scene, launches and configues the window, and persists it
sketch1 = Grid(-500, 500, 1, -500, 500, 1)
sketch1.create()
sketch1Scene = Scene(sketch1.meshgrid)
test1 = App([1000,1000], sketch1Scene)
test1.root.mainloop()