import math
import numpy as np
import cv2
import itertools

'''
pr_x = List of x-coordinates of person
pr_depth = List of depth of person
isw = width of image sensor(mm)
flc = Focal length(mm)
'''

# distance estimation
def human_distance(width, pr_x, pr_depth, isw, fcl) :
    # Define image data
    Hwidth = width / 2;  #Median of image width

    # Enumerate combinations of people
    comb = list(itertools.combinations(range(0,len(pr_x)), 2))

    # distace initialization
    dis = []

    for a, b in comb:
        # data loading
        Ax = int(pr_x[a]) # Median of personA's square width
        Adp = int(pr_depth[a]) # depth of personA(mm)
        Bx = int(pr_x[b]) # Median of personB's square width
        Bdp = int(pr_depth[b]) # depth of personB(mm)

        #Length from Median of image width
        Ahw = Ax - Hwidth
        Bhw = Bx - Hwidth
        #print("Length from Median of image width about A = " + str(Ahw));
        #print("Length from Median of image width about B = " + str(Bhw));

        #Coefficient of width
        cf = isw / fcl / width
        Acf = Adp * cf / 1000  #Coefficient of A(m)
        Bcf = Bdp * cf / 1000  #Coefficient of B(m)
        #print("Coefficient about A = " + str(Acf))
        #print("Coefficient about B = " + str(Bcf))

        #Real length(Distance)
        Ads = Ahw * Acf
        Bds = Bhw * Bcf
        #print("Distance from median about A = " + str(Ads))
        #print("Distance ftom median about B = " + str(Bds))

        #Distance between two people;
        Rdx = float(abs(Ads - Bds))
        Rdy = float(abs(Adp - Bdp))
        Rdy = Rdy / 1000
        Rds = math.sqrt(pow(Rdx, 2) + pow(Rdy, 2))
        #print("Distance between 2 about x = " + str(Rdx))
        #print("Distance between 2 about y = " + str(Rdy))
        #print("Distance between 2 people = " + str(Rds))

        dis.append(Rds) # save distace

    return comb, dis
