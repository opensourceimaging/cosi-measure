import numpy as np

class ball_path(object):
    points = np.array([]) # 0,0,0; 1,1,1; 2,2,2; ...

    def __init__(self,filename_input,center_point_input,radius_input,radius_npoints_input) -> None:
        self.filename = filename_input
        self.center = center_point_input
        self.radius = radius_input
        self.radius_npoints = radius_npoints_input

        # writes to a file already
        self.make_ball(center = self.center, radius = self.radius, radius_npoints = self.radius_npoints)



    def make_ball(self, center, radius:float, radius_npoints:int):
        x = np.linspace(start=(center[0]-radius),stop=(center[0]+radius),num=2*radius_npoints)
        y = np.linspace(start=(center[1]-radius),stop=(center[1]+radius),num=2*radius_npoints)
        z = np.linspace(start=(center[2]-radius),stop=(center[2]+radius),num=2*radius_npoints)


        zslices = []

        for z_ in z:
    
            slc = xySlice()
            slc.slice_height = z_
    
            for y_ in y:
                for x_ in x:
                    if (x_-center[0])**2 + (y_-center[1])**2 + (z_-center[2])**2 < radius**2:
                        slc.xpts_in_slice = np.append(slc.xpts_in_slice,x_)
                        slc.ypts_in_slice = np.append(slc.ypts_in_slice,y_)
                        #print('slice z=',z_,' : ',x_,y_)
                        #input('point in ball')
        
            
            zslices.append(slc)


        fileID = self.filename


        with open(fileID, 'w+') as f:

            for slc in zslices:
                for x1 in slc.xpts_in_slice:
                    for y1 in slc.ypts_in_slice:
                        z1 = slc.slice_height
                        g0 = 'x%.2f y%.2f z%.2f\n'%(x1,y1,z1)
                        #print('ball path gen: ', g0)
                        f.write(g0) 


class xySlice(object):
    xpts_in_slice = np.array([])
    ypts_in_slice = np.array([])
    slice_height = None
    def __init__(self) -> None:
        pass
    

