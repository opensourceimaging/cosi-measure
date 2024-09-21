import numpy as np
from scipy.special import sph_harm

def create_field_from_path(pathfile:str, output_file:str, bz_in = 0, gradient_z=0):
    '''
    to do
    '''
    # reading B-field file into list
    try:
        with open(pathfile, 'r') as file:
            data_lines = []
            header_lines = []
            for line in file:
                if line[0] == '#' or line[0] == '%' or line[0] == 'X':
                    header_lines.append(line)
                else:
                    data_lines.append(line)
    except FileNotFoundError:
        print("Pathfile not found at " + str(pathfile))
        return

    header = 'X[mm],Y[mm],Z[mm],Bx[mT],By[mT],Bz[mT]\n'

    try:
        with open(output_file, 'w') as outfile:
            outfile.write(header)

            for i in range(len(data_lines)):

                parts = data_lines[i].strip().split(',')

                x = float(parts[0])
                y = float(parts[1])
                z = float(parts[2])

                bx = 0
                by = 0
                bz = bz_in + z*gradient_z

                outfile.write(format(x, 'f') + ',' + format(y, 'f') + ',' + format(z, 'f') + ',' +  str(bx) + ',' + str(by) + ',' + str(bz) + '\n')

    except IOError:
        print("Error writing to file.")
        return
    
    print('converted file')

