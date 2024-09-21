import os
import numpy as np

def convert_to_magnet_coordinate_frame(rawdat_filename):
    '''
    in the same directory of rawdat_filename should be a file with the cosi-coordinates of the centerposition, which is named 'centerpoint.csv'.
    '''
    if rawdat_filename.endswith(".txt"):
        print("Interpreting as pathfile")
        is_pathfile = True
    else:
        is_pathfile = False

    rawdat_directory = os.path.dirname(rawdat_filename)
    rawdat_basename = os.path.basename(rawdat_filename)
    
    if is_pathfile:
        filename_magnetcoordinates = os.path.join(rawdat_directory,rawdat_basename.replace(".txt", "_magnet_coords.txt"))
    else:
        filename_magnetcoordinates = os.path.join(rawdat_directory,rawdat_basename.replace(".csv", "_magnet_coords.csv"))

    filename_centerpoint = os.path.join(rawdat_directory, 'centerpoint.csv')

    center_point = np.loadtxt(filename_centerpoint)

    with open(rawdat_filename, 'r') as rawfile:
        data_lines = []
        header_lines = []
        for line in rawfile:
            if line[0] == '#' or line[0] == '%' or line[0] == 'X':
                header_lines.append(line)
            else:
                data_lines.append(line)

    with open(filename_magnetcoordinates, 'w') as outfile:
        if not is_pathfile:
            outfile.write(header_lines[0])

        for i in range(len(data_lines)):
            parts = data_lines[i].strip().split(',')
            x_cosy = float(parts[0])
            y_cosy = float(parts[1])
            z_cosy = float(parts[2])

            if not is_pathfile:
                bx_probe = float(parts[3])
                by_probe = float(parts[4])
                bz_probe = float(parts[5])

            x_magnet = y_cosy - center_point[1]
            y_magnet = z_cosy - center_point[2]
            z_magnet = -x_cosy + center_point[0]
            if not is_pathfile:
                bx_magnet = -bz_probe
                by_magnet = -by_probe
                bz_magnet = -bx_probe

            if is_pathfile:
                outfile.write(format(x_magnet, 'f') + ',' + format(y_magnet, 'f') + ',' + format(z_magnet, 'f') + '\n')
            else:
                outfile.write(format(x_magnet, 'f') + ',' + format(y_magnet, 'f') + ',' + format(z_magnet, 'f') + ',' +  str(bx_magnet) + ',' + str(by_magnet) + ',' + str(bz_magnet) + '\n')
                
    
    print('Centerpoint in cosi coords:' + str(center_point))
    print('Converted '+ rawdat_filename + ' into magnet coordinates.') 
    print('File was written to ' + filename_magnetcoordinates)

    return filename_magnetcoordinates

