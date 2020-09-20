import math
import numpy as np
import cv2
import itertools

'''
pr_x = List of x-coordinates of person
pr_depth = List of depth of person
agw = Horizontal angle of view(degree)
'''

# distance estimation
def human_distance(width, pr_x, pr_depth, agw) :
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
        Apr = math.tan(math.radians(agw/2)) * Adp / 1000 * 2 # photographing range of A(m)
        Bpr = math.tan(math.radians(agw/2)) * Bdp / 1000 * 2 # photographing range of B(m)
        Acf = Apr / width # photographing range per 1 pixel of A(m)
        Bcf = Bpr / width # photographing range per 1 pixel of A(m)
        print("Coefficient about A = " + str(Acf))
        print("Coefficient about B = " + str(Bcf))

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
