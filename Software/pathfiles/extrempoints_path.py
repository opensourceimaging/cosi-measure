def create_extrempoints_pathfile(center_point, radius:float, filename:str):
    '''
    creates a path file in cosi coordinates for extrem points. 

    # Args

    - center_point:array_like. X, Y, Z -coordinates of magnet-center in cosi coordinates
    
    - radius:float. Distance from center_point to the extrema in mm.

    - filename:string. Path to the file that shall be created.

    # Returns

    - None. But a pathfile will be written to your file system.
    '''
    front = center_point + (0, radius, 0)
    left = center_point + (radius, 0, 0)
    back = center_point + (0, -radius, 0)
    right = center_point + (-radius, 0, 0)
    bottom = center_point + (0, 0, -radius)
    center = center_point
    top = center_point + (0, 0, radius)

    coordinates = [front, left, back, right, top, center, bottom]

    with open(filename, 'w') as f:
    #rawdatfile.write('X[mm],Y[mm],Z[mm],Bx[mT],By[mT],Bz[mT]\n')
        for i in range(len(coordinates)):
        
            line = '%.2f, %.2f, %.2f\n'%(coordinates[i][0],coordinates[i][1],coordinates[i][2])
            f.write(line)
    
    print('A path_file for the extrem_points was written: ' + str(filename))