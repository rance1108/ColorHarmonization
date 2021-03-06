#! python3

import cv2
import numpy as np
import matplotlib.pyplot as plt

canvas_h = 600
canvas_w = 600
yc = int(canvas_h/2)
xc = int(canvas_w/2)
circle_r = 250
H_cycle = 180

def normalized_gaussian(X, mu, S):
    X = np.asarray(X).astype(np.float64)
    S = np.asarray(S).astype(np.float64)
    D = np.deg2rad(X - mu)
    S = np.deg2rad(S)
    D2 = np.multiply(D, D)
    S2 = np.multiply(S, S)
    return np.exp( -D2/(2*S2) )

def deg_modulus(x):
    return np.remainder(x, 360)

def deg_distance(a, b):
    d1 = np.abs(a - b)
    d2 = np.abs(360-d1)
    d = np.minimum(d1, d2)
    return d

def deg_closest_direction(a, b):
    #a = np.remainder(a, 360)
    #b = np.remainder(b, 360)
    d1 = np.remainder(a-b, 360)
    d2 = np.remainder(-d1, 360)
    direction = np.argmin((np.abs(d1), np.abs(d2)), axis=0)
    #print("x", direction)
    direction = (direction-0.5)*2
    #print("y", direction)
    return direction

def count_hue_histogram(X):
    N = 360
    H = X[:, :, 0].astype(np.int32) * 2
    S = X[:, :, 1].astype(np.float64) / 255.0
    H_flat = H.flatten()
    S_flat = S.flatten()
    
    histo = np.zeros(N)
    for i in range(len(H_flat)):
        histo[ H_flat[i] ] += S_flat[i]
    return histo

def draw_polar_histogram(histo):
    N = 360
    histo = histo.astype(float)
    #histo = np.log2(histo+1)
    histo /= np.max(histo)
    histo *= circle_r
    canvas = np.zeros((canvas_h, canvas_w, 3))
    cv2.circle(canvas, (yc, xc), circle_r, (255,255,255), -1)
    for i in range(N):
        theta = -i * np.pi / 180
        count = histo[i]
        y1 = yc - int(circle_r * np.sin(theta))
        x1 = xc + int(circle_r * np.cos(theta))
        y2 = yc - int((circle_r-histo[i]) * np.sin(theta))
        x2 = xc + int((circle_r-histo[i]) * np.cos(theta))

        color_HSV = np.zeros((1,1,3), dtype=np.uint8)
        color_HSV[0,0,:] = [int(i/2),255,255]
        color_BGR = cv2.cvtColor(color_HSV, cv2.COLOR_HSV2BGR)
        B = int(color_BGR[0,0,0])
        G = int(color_BGR[0,0,1])
        R = int(color_BGR[0,0,2])
        cv2.line(canvas, (x1,y1), (x2,y2), (B,G,R), 3)
    cv2.circle(canvas, (yc, xc), circle_r+5, (255,255,255), 5)
    return canvas

   
def draw_harmonic_scheme(harmonic_scheme, canvas):
    overlay = canvas.copy()
    for sector in harmonic_scheme.sectors:
        center = sector.center
        width  = sector.width
        #print(center, width)
        start  = (center + width/2)
        end    = (center - width/2)
        print('a', center, width, start, end)
        cv2.ellipse(overlay, (yc, xc), (circle_r,circle_r), 0, start, end, (0,0,0), -1)
    return overlay

def length(v):
    return math.sqrt(v[0]**2+v[1]**2)

def dot_product(v,w):
   return v[0]*w[0]+v[1]*w[1]

def determinant(v,w):
   return v[0]*w[1]-v[1]*w[0]

def inner_angle(v,w):
   cosx=dot_product(v,w)/(length(v)*length(w))
   rad=math.acos(cosx) # in radians
   return rad*180/math.pi # returns degrees
   
def angle_clockwise(A, B):
    inner=inner_angle(A,B)
    det = determinant(A,B)
    if det<0: #this is a property of the det. If the det < 0 then B is clockwise of A
        return inner
    else: # if the det > 0 then A is immediately clockwise of B
        return 360-inner