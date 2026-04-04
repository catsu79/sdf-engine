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
#onAddShape pulls widget values and adds the new shape as a tuple of shape_instance and operation to the Scene() instructions
#sdfToPixelColor walks the SDF to convert values into hex colors for TKinter's .put method to show user viewable PhotoImage
#renderSDF renders the converted SDF as a TKinter canvas widget in the window
class App():
    def __init__(self, canvasDims, scene):
        self.root = tk.Tk()
        self.root.title('SDF Engine')
        self.scene = scene
        self.shapeCounts = {'Circle': 0, 'Rectangle': 0, 'Line Segment': 0, 
                           'Triangle': 0, 'Arc': 0, 'Polygon': 0, 
                           'Ellipse': 0, 'Parabola': 0, 'Hyperbola': 0}

        #ttk dark theme setup
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Sidebar.TFrame', background='#2b2b2b')
        self.style.configure('Sidebar.TLabel', background='#2b2b2b', foreground='white')
        self.style.configure('Header.TLabel', background='#2b2b2b', foreground='white',
                             font=('Arial', 14, 'bold'))
        self.style.configure('Sidebar.TButton', padding=5)
        self.style.configure('Canvas.TFrame', background='#1a1a1a')
        self.style.configure('SceneHeader.TFrame', background='#353535')
        self.style.configure('SceneHeader.TLabel', background='#353535', foreground='white',
                             font=('Arial', 10))
        self.style.configure('SceneDetail.TFrame', background='#303030')
        self.style.configure('SceneDetail.TLabel', background='#303030', foreground='#cccccc',
                             font=('Arial', 9))
        self.style.configure('Delete.TButton', padding=2)
        self.style.configure('SubHeader.TLabel', background='#2b2b2b', foreground='white',
                             font=('Arial', 12, 'bold'))

        #The following GUI code is written by Claude AI Opus 4.6 by Anthropic
        # sidebar on the left, canvas on the right
        self.sidebarFrame = ttk.Frame(self.root, width=260, style='Sidebar.TFrame')
        self.sidebarFrame.pack(side='left', fill='y')
        self.sidebarFrame.pack_propagate(False)
        self.canvasFrame = ttk.Frame(self.root, style='Canvas.TFrame')
        self.canvasFrame.pack(side='right', fill='both', expand=True)

        self.canvas = tk.Canvas(self.canvasFrame, width=canvasDims[0], height=canvasDims[1], bg='#1a1a1a')
        self.canvas.pack()

        # ---- ADD SHAPE SECTION ----
        ttk.Label(self.sidebarFrame, text='Add Shape', style='Header.TLabel').pack(pady=(20, 10))

        # shape type dropdown
        self.shapeVar = tk.StringVar(value='Select...')
        self.shapeDropdown = ttk.Combobox(self.sidebarFrame, textvariable=self.shapeVar,
                                          values=['Circle', 'Rectangle', 'Line Segment', 
                                                  'Triangle', 'Arc', 'Polygon', 
                                                  'Ellipse', 'Parabola', 'Hyperbola'], 
                                          state='readonly', width=20)
        self.shapeDropdown.pack(pady=5)
        self.shapeVar.trace_add('write', self.onShapeSelected)

        # container for dynamically generated parameter fields
        self.paramFrame = ttk.Frame(self.sidebarFrame, style='Sidebar.TFrame')
        self.paramFrame.pack(pady=5, padx=15, fill='x')

        # boolean operation dropdown
        ttk.Label(self.sidebarFrame, text='Operation', style='Sidebar.TLabel').pack(pady=(10, 2))
        self.opVar = tk.StringVar(value='union')
        self.opDropdown = ttk.Combobox(self.sidebarFrame, textvariable=self.opVar,
                                       values=['union', 'subtraction', 'intersection'], state='readonly', width=20)
        self.opDropdown.pack(pady=5)

        # add shape button
        ttk.Button(self.sidebarFrame, text='Add to Scene', width=20,
                   style='Sidebar.TButton', command=self.onAddShape).pack(pady=20)

        # dict storing references to parameter Entry widgets
        self.paramEntries = {}

        # ---- COLORS SECTION ----
        ttk.Separator(self.sidebarFrame, orient='horizontal').pack(fill='x', pady=10, padx=10)
        ttk.Label(self.sidebarFrame, text='Colors', style='SubHeader.TLabel').pack(pady=(0, 5))
        self.colorEntries = {}
        for colorLabel, colorDefault in [('Interior', '#4488ff'), ('Boundary', '#000000'), ('Exterior', '#ffa500')]:
            row = ttk.Frame(self.sidebarFrame, style='Sidebar.TFrame')
            row.pack(fill='x', padx=15, pady=1)
            ttk.Label(row, text=colorLabel, style='Sidebar.TLabel', width=8).pack(side='left')
            entry = ttk.Entry(row, width=9)
            entry.insert(0, colorDefault)
            entry.pack(side='left', padx=(5, 0))
            self.colorEntries[colorLabel] = entry

        # ---- SCENE LIST SECTION ----
        ttk.Separator(self.sidebarFrame, orient='horizontal').pack(fill='x', pady=10, padx=10)
        ttk.Label(self.sidebarFrame, text='Scene List', style='SubHeader.TLabel').pack(pady=(0, 5))
        #scrollable frame pattern: canvas + inner frame + scrollbar
        self.sceneListContainer = ttk.Frame(self.sidebarFrame, style='Sidebar.TFrame')
        self.sceneListContainer.pack(fill='both', expand=True, padx=5, pady=(0, 10))
        self.sceneListCanvas = tk.Canvas(self.sceneListContainer, bg='#2b2b2b',
                                         highlightthickness=0, width=240)
        self.sceneListScrollbar = ttk.Scrollbar(self.sceneListContainer, orient='vertical',
                                                 command=self.sceneListCanvas.yview)
        self.sceneListFrame = ttk.Frame(self.sceneListCanvas, style='Sidebar.TFrame')
        self.sceneListFrame.bind('<Configure>',
            lambda e: self.sceneListCanvas.configure(scrollregion=self.sceneListCanvas.bbox('all')))
        self.sceneListCanvas.create_window((0, 0), window=self.sceneListFrame, anchor='nw')
        self.sceneListCanvas.configure(yscrollcommand=self.sceneListScrollbar.set)
        self.sceneListCanvas.pack(side='left', fill='both', expand=True)
        self.sceneListScrollbar.pack(side='right', fill='y')
        #track which entries are expanded (index -> bool)
        self.expandedEntries = {}

    #rebuilds the entire scene list UI from self.scene.entries
    def _refreshSceneList(self):
        for widget in self.sceneListFrame.winfo_children():
            widget.destroy()
        self.expandedEntries = {}
        for i, (shape, op) in enumerate(self.scene.entries):
            entryFrame = ttk.Frame(self.sceneListFrame, style='Sidebar.TFrame')
            entryFrame.pack(fill='x', pady=1)
            #clickable header row
            header = ttk.Frame(entryFrame, style='SceneHeader.TFrame')
            header.pack(fill='x')
            arrow = ttk.Label(header, text='\u25b6', style='SceneHeader.TLabel', width=2)
            arrow.pack(side='left', padx=(5, 0))
            nameLabel = ttk.Label(header, text=shape.name + ' (' + op + ')',
                                  style='SceneHeader.TLabel')
            nameLabel.pack(side='left', padx=5)
            deleteBtn = ttk.Button(header, text='\u2715', width=3, style='Delete.TButton',
                                   command=lambda idx=i: self._removeEntry(idx))
            deleteBtn.pack(side='right', padx=5)
            #collapsible detail panel with shape parameters (hidden by default)
            detail = ttk.Frame(entryFrame, style='SceneDetail.TFrame')
            typeName = type(shape).__name__
            ttk.Label(detail, text='Type: ' + typeName,
                      style='SceneDetail.TLabel').pack(anchor='w', padx=15)
            for paramLabel, paramValue in shape.describe():
                ttk.Label(detail, text=paramLabel + ': ' + str(paramValue),
                          style='SceneDetail.TLabel').pack(anchor='w', padx=15)
            #bind click on header elements to toggle detail visibility
            self.expandedEntries[i] = False
            def makeToggle(idx, arrowWidget, detailWidget):
                def toggle(event=None):
                    self._toggleEntry(idx, arrowWidget, detailWidget)
                return toggle
            toggleCmd = makeToggle(i, arrow, detail)
            header.bind('<Button-1>', toggleCmd)
            arrow.bind('<Button-1>', toggleCmd)
            nameLabel.bind('<Button-1>', toggleCmd)

    #expands or collapses a scene list entry's detail panel
    def _toggleEntry(self, index, arrow, detail):
        if self.expandedEntries.get(index, False):
            detail.pack_forget()
            arrow.configure(text='\u25b6')
            self.expandedEntries[index] = False
        else:
            detail.pack(fill='x')
            arrow.configure(text='\u25bc')
            self.expandedEntries[index] = True

    #removes a scene entry by index, refreshes the list, and re-renders
    def _removeEntry(self, index):
        self.scene.remove(index)
        self._refreshSceneList()
        if len(self.scene.entries) > 0:
            self.renderSDF(self.scene.compute())
        else:
            self.canvas.delete('all')

    #helper to build a labeled row of two coordinate entries with parentheses
    def _makePointRow(self, parent, label, keyX, keyY):
        ttk.Label(parent, text=label, style='Sidebar.TLabel').pack(anchor='w', pady=(8, 0))
        row = ttk.Frame(parent, style='Sidebar.TFrame')
        row.pack(fill='x', pady=2)
        ttk.Label(row, text='(', style='Sidebar.TLabel').pack(side='left')
        self.paramEntries[keyX] = ttk.Entry(row, width=6)
        self.paramEntries[keyX].pack(side='left')
        ttk.Label(row, text=',', style='Sidebar.TLabel').pack(side='left')
        self.paramEntries[keyY] = ttk.Entry(row, width=6)
        self.paramEntries[keyY].pack(side='left')
        ttk.Label(row, text=')', style='Sidebar.TLabel').pack(side='left')

    #helper to build a labeled single value entry
    def _makeSingleEntry(self, parent, label, key):
        ttk.Label(parent, text=label, style='Sidebar.TLabel').pack(anchor='w', pady=(8, 0))
        self.paramEntries[key] = ttk.Entry(parent, width=6)
        self.paramEntries[key].pack(anchor='w', pady=2)

    def onShapeSelected(self, *args):
        # clear old parameter fields
        for widget in self.paramFrame.winfo_children():
            widget.destroy()
        self.paramEntries = {}
        shape = self.shapeVar.get()
        self.shapeCounts[shape] = self.shapeCounts.get(shape, 0) + 1
        defaultName = shape.lower().replace(' ', '') + str(self.shapeCounts[shape])
        ttk.Label(self.paramFrame, text='Name', style='Sidebar.TLabel').pack(anchor='w')
        self.paramEntries['name'] = ttk.Entry(self.paramFrame, width=15)
        self.paramEntries['name'].insert(0, defaultName)
        self.paramEntries['name'].pack(anchor='w', pady=2)

        if shape == 'Circle':
            self._makePointRow(self.paramFrame, 'Center', 'cx', 'cy')
            self._makeSingleEntry(self.paramFrame, 'Radius', 'r')

        elif shape == 'Rectangle':
            self._makePointRow(self.paramFrame, 'Center', 'cx', 'cy')
            ttk.Label(self.paramFrame, text='Dimensions (W, H)', style='Sidebar.TLabel').pack(anchor='w', pady=(8, 0))
            dimsRow = ttk.Frame(self.paramFrame, style='Sidebar.TFrame')
            dimsRow.pack(fill='x', pady=2)
            ttk.Label(dimsRow, text='(', style='Sidebar.TLabel').pack(side='left')
            self.paramEntries['w'] = ttk.Entry(dimsRow, width=6)
            self.paramEntries['w'].pack(side='left')
            ttk.Label(dimsRow, text=',', style='Sidebar.TLabel').pack(side='left')
            self.paramEntries['h'] = ttk.Entry(dimsRow, width=6)
            self.paramEntries['h'].pack(side='left')
            ttk.Label(dimsRow, text=')', style='Sidebar.TLabel').pack(side='left')

        elif shape == 'Line Segment':
            self._makePointRow(self.paramFrame, 'Point A', 'ax', 'ay')
            self._makePointRow(self.paramFrame, 'Point B', 'bx', 'by')
            self._makeSingleEntry(self.paramFrame, 'Thickness', 'th')

        elif shape == 'Triangle':
            self._makePointRow(self.paramFrame, 'Point A', 'ax', 'ay')
            self._makePointRow(self.paramFrame, 'Point B', 'bx', 'by')
            self._makePointRow(self.paramFrame, 'Point C', 'tcx', 'tcy')

        elif shape == 'Arc':
            self._makePointRow(self.paramFrame, 'Center', 'cx', 'cy')
            self._makeSingleEntry(self.paramFrame, 'Radius', 'r')
            self._makeSingleEntry(self.paramFrame, 'Start Angle (deg)', 'sa')
            self._makeSingleEntry(self.paramFrame, 'End Angle (deg)', 'ea')
            self._makeSingleEntry(self.paramFrame, 'Thickness', 'th')

        elif shape == 'Polygon':
            ttk.Label(self.paramFrame, text='Vertices (x,y x,y ...)', style='Sidebar.TLabel').pack(anchor='w', pady=(8, 0))
            self.paramEntries['verts'] = ttk.Entry(self.paramFrame, width=20)
            self.paramEntries['verts'].pack(anchor='w', pady=2)

        elif shape == 'Ellipse':
            self._makePointRow(self.paramFrame, 'Center', 'cx', 'cy')
            self._makeSingleEntry(self.paramFrame, 'Semi-Axis A', 'sa')
            self._makeSingleEntry(self.paramFrame, 'Semi-Axis B', 'sb')

        elif shape == 'Parabola':
            self._makeSingleEntry(self.paramFrame, 'a (coefficient)', 'pa')
            self._makeSingleEntry(self.paramFrame, 'b (coefficient)', 'pb')
            self._makeSingleEntry(self.paramFrame, 'c (coefficient)', 'pc')
            self._makeSingleEntry(self.paramFrame, 'Width', 'pw')
            self._makeSingleEntry(self.paramFrame, 'Thickness', 'th')

        elif shape == 'Hyperbola':
            self._makePointRow(self.paramFrame, 'Center', 'cx', 'cy')
            self._makeSingleEntry(self.paramFrame, 'k (shape)', 'hk')
            self._makeSingleEntry(self.paramFrame, 'Height Extent', 'he')
            self._makeSingleEntry(self.paramFrame, 'Thickness', 'th')
    #This is the end of the GUI code written by Claude AI Opus 4.6 by Anthropic

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
            elif (shape == 'Line Segment'):
                pointA = [float(self.paramEntries['ax'].get()), float(self.paramEntries['ay'].get())]
                pointB = [float(self.paramEntries['bx'].get()), float(self.paramEntries['by'].get())]
                thickness = float(self.paramEntries['th'].get())
                self.scene.add(LineSegment(name, pointA, pointB, thickness), self.opVar.get())
            elif (shape == 'Triangle'):
                pointA = [float(self.paramEntries['ax'].get()), float(self.paramEntries['ay'].get())]
                pointB = [float(self.paramEntries['bx'].get()), float(self.paramEntries['by'].get())]
                pointC = [float(self.paramEntries['tcx'].get()), float(self.paramEntries['tcy'].get())]
                self.scene.add(Triangle(name, pointA, pointB, pointC), self.opVar.get())
            elif (shape == 'Arc'):
                center = [float(self.paramEntries['cx'].get()), float(self.paramEntries['cy'].get())]
                radius = float(self.paramEntries['r'].get())
                startAngle = float(self.paramEntries['sa'].get())
                endAngle = float(self.paramEntries['ea'].get())
                thickness = float(self.paramEntries['th'].get())
                self.scene.add(Arc(name, center, radius, startAngle, endAngle, thickness), self.opVar.get())
            elif (shape == 'Polygon'):
                vertStr = self.paramEntries['verts'].get().strip().split(' ')
                vertices = []
                for v in vertStr:
                    coords = v.split(',')
                    vertices.append([float(coords[0]), float(coords[1])])
                self.scene.add(Polygon(name, vertices), self.opVar.get())
            elif (shape == 'Ellipse'):
                center = [float(self.paramEntries['cx'].get()), float(self.paramEntries['cy'].get())]
                semiA = float(self.paramEntries['sa'].get())
                semiB = float(self.paramEntries['sb'].get())
                self.scene.add(Ellipse(name, center, semiA, semiB), self.opVar.get())
            elif (shape == 'Parabola'):
                a = float(self.paramEntries['pa'].get())
                b = float(self.paramEntries['pb'].get())
                c = float(self.paramEntries['pc'].get())
                width = float(self.paramEntries['pw'].get())
                thickness = float(self.paramEntries['th'].get())
                self.scene.add(Parabola(name, a, b, c, width, thickness), self.opVar.get())
            elif (shape == 'Hyperbola'):
                center = [float(self.paramEntries['cx'].get()), float(self.paramEntries['cy'].get())]
                k = float(self.paramEntries['hk'].get())
                he = float(self.paramEntries['he'].get())
                thickness = float(self.paramEntries['th'].get())
                self.scene.add(Hyperbola(name, center, k, he, thickness), self.opVar.get())
            self._refreshSceneList()
            self.renderSDF(self.scene.compute())
        except Exception as error:
            print(str(error) + ' error when adding shape')

    def sdfToPixelColor(self, sdfArray):
        interiorColor = self.colorEntries['Interior'].get()
        boundaryColor = self.colorEntries['Boundary'].get()
        exteriorColor = self.colorEntries['Exterior'].get()
        pixelColorArray = []
        for y in reversed(range(0, len(sdfArray))):
            pixelColorListx = []
            for x in range(0, len(sdfArray[y])):
                if (sdfArray[y][x] < -3):
                    pixelColorListx.append(interiorColor)
                elif (sdfArray[y][x] >= -3 and sdfArray[y][x] <= 0):
                    pixelColorListx.append(boundaryColor)
                elif (sdfArray[y][x] > 0):
                    pixelColorListx.append(exteriorColor)
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

    def describe(self):
        raise NotImplementedError

#represents circle objects
#evaluate computes the SDF of the circle
class Circle(Shape):
    def __init__(self, name, center, radius):
        self.name = name
        self.center = center
        self.radius = radius

    def describe(self):
        return [('Center', self.center), ('Radius', self.radius)]

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

    def describe(self):
        return [('Center', self.center), ('Dims', self.dims)]

    #The logic for the following function was derived from https://iquilezles.org/articles/distfunctions2d/
    def evaluate(self, grid):
        d = [np.subtract(np.abs(np.subtract(grid[0], self.center[0])), self.dims[0]/2),
             np.subtract(np.abs(np.subtract(grid[1], self.center[1])), self.dims[1]/2)]
        return dist2DPoints([np.maximum(d[0],0), np.maximum(d[1], 0)], [0,0]) + np.minimum(np.maximum(d[0], d[1]), 0)

#represents line segment objects with thickness
#evaluate projects query point onto segment (clamped to endpoints) and subtracts thickness
class LineSegment(Shape):
    def __init__(self, name, pointA, pointB, thickness):
        self.name = name
        self.pointA = pointA
        self.pointB = pointB
        self.thickness = thickness

    def describe(self):
        return [('Point A', self.pointA), ('Point B', self.pointB), ('Thickness', self.thickness)]

    #The logic for the following function was derived from https://iquilezles.org/articles/distfunctions2d/
    def evaluate(self, grid):
        pax = grid[0] - self.pointA[0]
        pay = grid[1] - self.pointA[1]
        bax = self.pointB[0] - self.pointA[0]
        bay = self.pointB[1] - self.pointA[1]
        h = np.clip((pax * bax + pay * bay) / (bax**2 + bay**2), 0.0, 1.0)
        dx = pax - bax * h
        dy = pay - bay * h
        return np.sqrt(dx**2 + dy**2) - self.thickness

#represents filled triangle objects
#evaluate computes signed distance using clamped edge projections and winding number for inside/outside
class Triangle(Shape):
    def __init__(self, name, pointA, pointB, pointC):
        self.name = name
        self.pointA = pointA
        self.pointB = pointB
        self.pointC = pointC

    def describe(self):
        return [('Point A', self.pointA), ('Point B', self.pointB), ('Point C', self.pointC)]

    #The logic for the following function was derived from https://iquilezles.org/articles/distfunctions2d/
    def evaluate(self, grid):
        p0, p1, p2 = self.pointA, self.pointB, self.pointC
        #edge vectors
        e0x, e0y = p1[0] - p0[0], p1[1] - p0[1]
        e1x, e1y = p2[0] - p1[0], p2[1] - p1[1]
        e2x, e2y = p0[0] - p2[0], p0[1] - p2[1]
        #vectors from each vertex to query point
        v0x = grid[0] - p0[0]
        v0y = grid[1] - p0[1]
        v1x = grid[0] - p1[0]
        v1y = grid[1] - p1[1]
        v2x = grid[0] - p2[0]
        v2y = grid[1] - p2[1]
        #clamped projections onto each edge
        h0 = np.clip((v0x * e0x + v0y * e0y) / (e0x**2 + e0y**2), 0.0, 1.0)
        pq0x = v0x - e0x * h0
        pq0y = v0y - e0y * h0
        h1 = np.clip((v1x * e1x + v1y * e1y) / (e1x**2 + e1y**2), 0.0, 1.0)
        pq1x = v1x - e1x * h1
        pq1y = v1y - e1y * h1
        h2 = np.clip((v2x * e2x + v2y * e2y) / (e2x**2 + e2y**2), 0.0, 1.0)
        pq2x = v2x - e2x * h2
        pq2y = v2y - e2y * h2
        #winding sign
        s = np.sign(e0x * e2y - e0y * e2x)
        #squared distances to each edge and cross products for inside/outside
        d0 = pq0x**2 + pq0y**2
        d1 = pq1x**2 + pq1y**2
        d2 = pq2x**2 + pq2y**2
        c0 = s * (v0x * e0y - v0y * e0x)
        c1 = s * (v1x * e1y - v1y * e1x)
        c2 = s * (v2x * e2y - v2y * e2x)
        #component-wise min: smallest squared distance and smallest cross product
        dMin = np.minimum(np.minimum(d0, d1), d2)
        cMin = np.minimum(np.minimum(c0, c1), c2)
        return -np.sqrt(dMin) * np.sign(cMin)

#represents arc objects with thickness
#uses start/end angle in unit circle notation (0 deg = positive x-axis, counterclockwise)
#internally rotates grid to align arc midpoint with IQ's y-axis-symmetric formula
class Arc(Shape):
    def __init__(self, name, center, radius, startAngle, endAngle, thickness):
        self.name = name
        self.center = center
        self.radius = radius
        self.startAngle = startAngle
        self.endAngle = endAngle
        self.thickness = thickness

    def describe(self):
        return [('Center', self.center), ('Radius', self.radius),
                ('Start', self.startAngle), ('End', self.endAngle), ('Thickness', self.thickness)]

    #The logic for the following function was derived from https://iquilezles.org/articles/distfunctions2d/
    def evaluate(self, grid):
        #translate to center
        px = grid[0] - self.center[0]
        py = grid[1] - self.center[1]
        #mid angle and half angle from start/end
        midRad = math.radians((self.startAngle + self.endAngle) / 2.0)
        halfRad = math.radians(abs(self.endAngle - self.startAngle) / 2.0)
        #rotate grid so arc midpoint aligns with positive y-axis (IQ's convention)
        rotAngle = math.pi / 2.0 - midRad
        cosR = math.cos(rotAngle)
        sinR = math.sin(rotAngle)
        rpx = px * cosR - py * sinR
        rpy = px * sinR + py * cosR
        #IQ's arc formula (symmetric about y-axis)
        rpx = np.abs(rpx)
        scx = math.sin(halfRad)
        scy = math.cos(halfRad)
        endDist = np.sqrt((rpx - scx * self.radius)**2 + (rpy - scy * self.radius)**2)
        ringDist = np.abs(np.sqrt(rpx**2 + rpy**2) - self.radius)
        return np.where(scy * rpx > scx * rpy, endDist, ringDist) - self.thickness

#represents filled polygon objects with arbitrary vertex count
#evaluate computes signed distance using edge projections and winding number parity
#vertices entered as space-separated x,y pairs (e.g. "0,50 -50,-25 50,-25")
class Polygon(Shape):
    def __init__(self, name, vertices):
        self.name = name
        self.vertices = vertices

    def describe(self):
        return [('Vertices', len(self.vertices))]

    #The logic for the following function was derived from https://iquilezles.org/articles/distfunctions2d/
    def evaluate(self, grid):
        n = len(self.vertices)
        #initialize with squared distance to first vertex
        dx = grid[0] - self.vertices[0][0]
        dy = grid[1] - self.vertices[0][1]
        d = dx**2 + dy**2
        s = np.ones_like(grid[0])
        j = n - 1
        for i in range(n):
            #edge vector from vertex i to vertex j
            ex = self.vertices[j][0] - self.vertices[i][0]
            ey = self.vertices[j][1] - self.vertices[i][1]
            #vector from vertex i to query point
            wx = grid[0] - self.vertices[i][0]
            wy = grid[1] - self.vertices[i][1]
            #clamped projection onto edge
            h = np.clip((wx * ex + wy * ey) / (ex**2 + ey**2), 0.0, 1.0)
            bx = wx - ex * h
            by = wy - ey * h
            d = np.minimum(d, bx**2 + by**2)
            #winding number sign flips
            c1 = grid[1] >= self.vertices[i][1]
            c2 = grid[1] < self.vertices[j][1]
            c3 = ex * wy > ey * wx
            cond = (c1 & c2 & c3) | (~c1 & ~c2 & ~c3)
            s = np.where(cond, -s, s)
            j = i
        return s * np.sqrt(d)

#represents filled ellipse objects (exact SDF)
#evaluate uses IQ's analytic cubic solver for closest point on ellipse
#handles the two-branch discriminant case with np.where for element-wise branching
class Ellipse(Shape):
    def __init__(self, name, center, semiA, semiB):
        self.name = name
        self.center = center
        self.semiA = semiA
        self.semiB = semiB

    def describe(self):
        return [('Center', self.center), ('Semi-A', self.semiA), ('Semi-B', self.semiB)]

    #The logic for the following function was derived from https://iquilezles.org/articles/distfunctions2d/
    #and https://iquilezles.org/articles/ellipsedist/
    def evaluate(self, grid):
        px = np.abs(grid[0] - self.center[0])
        py = np.abs(grid[1] - self.center[1])
        a = self.semiA
        b = self.semiB
        #swap so that semi-axis b >= a (p.x <= p.y in IQ's convention)
        #per-element swap since it depends on point coordinates
        swap = px > py
        spx = np.where(swap, py, px)
        spy = np.where(swap, px, py)
        sa = np.where(swap, b, a)
        sb = np.where(swap, a, b)
        #IQ's ellipse SDF cubic solver
        l = sb**2 - sa**2
        #guard against degenerate case (circle) where l = 0
        l = np.where(np.abs(l) < 1e-10, 1e-10, l)
        m = sa * spx / l
        m2 = m * m
        n = sb * spy / l
        n2 = n * n
        c = (m2 + n2 - 1.0) / 3.0
        c3 = c * c * c
        q = c3 + m2 * n2 * 2.0
        d = c3 + m2 * n2
        g = m + m * n2
        #branch d < 0: trigonometric solution
        h_neg = np.arccos(np.clip(q / np.where(np.abs(c3) < 1e-20, -1e-20, c3), -1.0, 1.0)) / 3.0
        s_neg = np.cos(h_neg)
        t_neg = np.sin(h_neg) * np.sqrt(3.0)
        rx_neg = np.sqrt(np.maximum(-c * (s_neg + t_neg + 2.0) + m2, 0.0))
        ry_neg = np.sqrt(np.maximum(-c * (s_neg - t_neg + 2.0) + m2, 0.0))
        co_neg = (ry_neg + np.sign(l) * rx_neg + np.abs(g) / np.maximum(rx_neg * ry_neg, 1e-10) - m) / 2.0
        #branch d >= 0: algebraic solution
        h_pos = 2.0 * m * n * np.sqrt(np.maximum(d, 0.0))
        qph = q + h_pos
        qmh = q - h_pos
        s_pos = np.sign(qph) * np.abs(qph) ** (1.0 / 3.0)
        u_pos = np.sign(qmh) * np.abs(qmh) ** (1.0 / 3.0)
        rx_pos = -s_pos - u_pos - c * 4.0 + 2.0 * m2
        ry_pos = (s_pos - u_pos) * np.sqrt(3.0)
        rm_pos = np.sqrt(rx_pos**2 + ry_pos**2)
        co_pos = (ry_pos / np.sqrt(np.maximum(rm_pos - rx_pos, 1e-10)) + 2.0 * g / np.maximum(rm_pos, 1e-10) - m) / 2.0
        #select branch
        co = np.where(d < 0, co_neg, co_pos)
        co = np.clip(co, 0.0, 1.0)
        #closest point on ellipse and signed distance
        rx = sa * co
        ry = sb * np.sqrt(np.maximum(1.0 - co * co, 0.0))
        return np.sqrt((rx - spx)**2 + (ry - spy)**2) * np.sign(spy - ry)

#represents parabola segment objects with thickness
#takes quadratic coefficients (a, b, c for y = ax^2 + bx + c) plus width and thickness
#internally computes vertex and converts to IQ's centered form
class Parabola(Shape):
    def __init__(self, name, a, b, c, width, thickness):
        self.name = name
        self.a = a
        self.b = b
        self.c = c
        self.width = width
        self.thickness = thickness

    def describe(self):
        return [('a', self.a), ('b', self.b), ('c', self.c),
                ('Width', self.width), ('Thickness', self.thickness)]

    #The logic for the following function was derived from https://iquilezles.org/articles/distfunctions2d/
    def evaluate(self, grid):
        #vertex of y = ax^2 + bx + c
        vx = -self.b / (2.0 * self.a)
        vy = self.c - self.b**2 / (4.0 * self.a)
        #translate to vertex
        px = np.abs(grid[0] - vx)
        py = grid[1] - vy
        #if parabola opens upward (a > 0), flip y so IQ's downward-opening formula works
        if (self.a > 0):
            py = -py
        #effective height from vertex to baseline at width extent
        he = abs(self.a) * self.width**2
        wi = self.width
        #IQ's parabola segment formula
        ik = wi**2 / he
        p = ik * (he - py - 0.5 * ik) / 3.0
        q = px * ik**2 * 0.25
        h = q**2 - p**3
        r = np.sqrt(np.abs(h))
        #cubic solve with two branches
        xPos = np.cbrt(q + r) - np.sign(r - q) * np.cbrt(np.abs(q - r))
        xNeg = 2.0 * np.cos(np.arctan2(r, q) / 3.0) * np.sqrt(np.maximum(p, 0.0))
        x = np.where(h > 0, xPos, xNeg)
        x = np.minimum(x, wi)
        return np.sqrt((px - x)**2 + (py - (he - x**2 / ik))**2) - self.thickness

#represents hyperbola objects (curve xy = k in 45-degree-rotated coordinates) with thickness
#k controls shape (larger k = wider separation), he limits vertical extent
class Hyperbola(Shape):
    def __init__(self, name, center, k, he, thickness):
        self.name = name
        self.center = center
        self.k = k
        self.he = he
        self.thickness = thickness

    def describe(self):
        return [('Center', self.center), ('k', self.k),
                ('Height', self.he), ('Thickness', self.thickness)]

    #The logic for the following function was derived from https://iquilezles.org/articles/distfunctions2d/
    def evaluate(self, grid):
        px = np.abs(grid[0] - self.center[0])
        py = np.abs(grid[1] - self.center[1])
        #rotate 45 degrees into IQ's coordinate system
        sqrt2 = math.sqrt(2.0)
        rpx = (px - py) / sqrt2
        rpy = (px + py) / sqrt2
        #IQ's hyperbola formula
        x2 = rpx * rpx / 16.0
        y2 = rpy * rpy / 16.0
        k = self.k
        r = k * (4.0 * k - rpx * rpy) / 12.0
        q = (x2 - y2) * k * k
        h = q * q + r * r * r
        #branch h < 0: trigonometric
        m_neg = np.sqrt(np.maximum(-r, 0.0))
        u_neg = m_neg * np.cos(np.arccos(np.clip(q / np.where(np.abs(r * m_neg) < 1e-20, -1e-20, r * m_neg), -1.0, 1.0)) / 3.0)
        #branch h >= 0: algebraic
        m_pos = np.cbrt(np.sqrt(np.maximum(h, 0.0)) - q)
        u_pos = np.where(np.abs(m_pos) < 1e-10, 0.0, (m_pos - r / m_pos) / 2.0)
        #select branch
        u = np.where(h < 0, u_neg, u_pos)
        w = np.sqrt(np.maximum(u + x2, 0.0))
        b = k * rpy - x2 * rpx * 2.0
        t = rpx / 4.0 - w + np.sqrt(np.maximum(2.0 * x2 - u + b / np.where(np.abs(w) < 1e-10, 1e-10, w) / 4.0, 0.0))
        #clamp t to height extent
        t = np.maximum(t, np.sqrt(self.he**2 * 0.5 + k) - self.he / sqrt2)
        #distance to closest point on hyperbola curve
        d = np.sqrt((rpx - t)**2 + (rpy - k / np.where(np.abs(t) < 1e-10, 1e-10, t))**2)
        #sign: inside when xy > k (in rotated coords)
        return d - self.thickness

#main code: stores the Grid, creates the arrays, creates the Scene, launches and configures the window, and persists it
sketch1 = Grid(-500, 500, 1, -500, 500, 1)
sketch1.create()
sketch1Scene = Scene(sketch1.meshgrid)
test1 = App([1000, 1000], sketch1Scene)
test1.root.mainloop()