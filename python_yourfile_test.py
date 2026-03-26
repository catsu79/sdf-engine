import numpy as np
import math

#functions

#call coordinate plane
def coordinatePlane2D(xleft, xright, xstep, yleft, yright, ystep):
    return np.meshgrid(np.arange(xleft, xright, xstep), np.arange(yleft, yright, ystep))

#dist between points in 2D
def dist2DPoints(point1, point2):
    return ((point1[0]-point2[0])**2+(point1[1]-point2[1])**2)**0.5

#dist of any point to origin given x array and y array
def dist2DVector(arrayX, arrayY):
    return ((arrayX)**2+(arrayY)**2)**0.5

#Circle SDF
def circleSDF(center, radius, coordinatePlaneName):
    return(dist2DPoints(coordinatePlaneName, center) - radius)

#Rectangle SDF
def rectSDF(center, halfDimList, coordinatePlaneName):
   d = [np.subtract(np.abs(np.subtract(coordinatePlaneName[0], center[0])), halfDimList[0]), np.subtract(np.abs(np.subtract(coordinatePlaneName[1], center[1])), halfDimList[1])]
   return(dist2DVector(np.maximum(d[0],0), np.maximum(d[1], 0)) + np.minimum(np.maximum(d[0], d[1]), 0))

def main():
    sketch1 = coordinatePlane2D(-5,6,1, -5,6,1)
    print(np.round(np.minimum((rectSDF([-1,2], [3,2], sketch1)), circleSDF([0,0], 2, sketch1))))

main()
    
