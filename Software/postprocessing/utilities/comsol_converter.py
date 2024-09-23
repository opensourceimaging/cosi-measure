def comsol_out_2_bfieldfile(bfieldfile, output_file):
    # reading B-field file into list
    try:
        with open(bfieldfile, 'r') as file:
            bfield_lines = []
            header_lines = []
            for line in file:
                if line[0] == '%':
                    header_lines.append(line)
                else:
                    bfield_lines.append(line)

    except FileNotFoundError:
        print("File not found.")
        return

    # write data to file
    try:
        with open(output_file, 'w') as outfile:
            outfile.write('X[mm],Y[mm],Z[mm],Bx[mT],By[mT],Bz[mT]\n')

            for i in range(len(bfield_lines)):
                # extract coordinates
                parts = bfield_lines[i].strip().split(',')
                x = round(float(parts[0])*1e3, 8)
                y = round(float(parts[1])*1e3, 8)
                z = round(float(parts[2])*1e3, 8)


                bx = 0
                by = 0
                bz = round(float(parts[3]), 4)
                # write to csv-file
                outfile.write(str(x) + ',' + str(y) + ',' + str(z) + ',' +  str(bx) + ',' + str(by) + ',' + str(bz) + '\n')
                #outfile.write(str(x) + ', ' + str(y) + ', ' + str(z) + '\n')

    except IOError:
        print("Error writing to file.")
        return
    


def pathfile_2_comsol_coordinatefile(pathfile, comsol_coordinatefile=None):
    '''
    comsol wants the coordinate file exactly as the pathfile, but in [m], not in [mm]. 

    this function multiplies x, y and z in the .txt with 1e-3 and writes it to the output file
    '''
    try:
        with open(pathfile, 'r') as file:
            bfield_lines = []
            header_lines = []
            for line in file:
                bfield_lines.append(line)

    except FileNotFoundError:
        print("File not found.")
        return

    # write data to file
    try:
        with open(comsol_coordinatefile, 'w') as outfile:
            #outfile.write('X[m],Y[m],Z[m],Bx[T],By[T],Bz[T]\n')

            for i in range(len(bfield_lines)):
                # extract coordinates
                parts = bfield_lines[i].strip().split(',')
                x = round(float(parts[0]) * 1e-3, 8)
                y = round(float(parts[1]) * 1e-3, 8)
                z = round(float(parts[2]) * 1e-3, 8)

                # write to txt-file
                outfile.write(str(x) + ', ' + str(y) + ', ' + str(z) + '\n')

    except IOError:
        print("Error writing to file.")
        return