'''rst@PTB 240409 rst030@protonmail.com'''
import numpy as np

class osi2magnet():
    '''magnet object. created for cosi.'''

    # the position of the magnet is defined by 3 euler angles and 3 coordinates
    alpha = 0
    beta = 0 
    gamma = 0

    xcenter = 0
    ycenter = 0
    zcenter = 0

    vec_length = 32 # vectors are 32 mm long
    bore_radius = 150 # mm - adjust!
    bore_depth = 500

    xvector = 0
    yvector = 0
    zvector = 0

    def __init__(self):
        # initially the magnet is aligned with the lab frame
        self.set_origin(0,0,0)


    def set_origin(self,x,y,z):
        self.origin = np.array([x,y,z])
        self.xvector = np.array([1,0,0])*self.bore_radius
        self.yvector = np.array([0,1,0])*self.bore_radius
        self.zvector = np.array([0,0,1])*self.bore_radius

        t = np.linspace(0, 2*np.pi, 64)
        self.bore_X = np.sin(t)*self.bore_radius+self.origin[0]
        self.bore_Y = t*0+self.origin[1]
        self.bore_Z = np.cos(t)*self.bore_radius+self.origin[2]

        self.bore_back_X = np.sin(t)*self.bore_radius+self.origin[0]
        self.bore_back_Y = t*0+self.origin[1]+self.bore_depth
        self.bore_back_Z = np.cos(t)*self.bore_radius+self.origin[2]
