def calc_diff_of_fields(file1, file2, diff_file_2_minus_1):
    '''
    # Args

    Calculates $ B_{file1} -  B_{file2} $ for every point in the input files and stores it to dff_file_2_mins_1

    - file1:string. Filename of a field csv-file. Format: X[mm],Y[mm],Z[mm],Bx[mT],By[mT],Bz[mT]

    - file2:string. Filename of a field csv-file. Format: X[mm],Y[mm],Z[mm],Bx[mT],By[mT],Bz[mT]

    - diff_file_2_minus_1:string. Filename for the result. Format of this csv-file: X[mm],Y[mm],Z[mm],Bx[mT],By[mT],Bz[mT]

    # Returns

    - None. But a diff field file will be written to your file system
    
    '''
    with open(file1, 'r') as f1:
        data_lines1 = []
        header_lines1 = []
        for line in f1:
            if line[0] == '#' or line[0] == '%' or line[0] == 'X':
                header_lines1.append(line)
            else:
                data_lines1.append(line)

    with open(file2, 'r') as f2:
        data_lines2 = []
        header_lines2 = []
        for line in f2:
            if line[0] == '#' or line[0] == '%' or line[0] == 'X':
                header_lines2.append(line)
            else:
                data_lines2.append(line)
    
    if not len(data_lines1)==len(data_lines2):
        raise Exception('Files do not match in number of data lines.')


    with open(diff_file_2_minus_1, 'w') as outfile:
        outfile.write(header_lines1[0])
        for i in range(len(data_lines1)):
            parts1 = data_lines1[i].strip().split(',')
            x1 = float(parts1[0])
            y1 = float(parts1[1])
            z1 = float(parts1[2])
            bx1 = float(parts1[3])
            by1 = float(parts1[4])
            bz1 = float(parts1[5])

            parts2 = data_lines2[i].strip().split(',')
            x2 = float(parts2[0])
            y2 = float(parts2[1])
            z2 = float(parts2[2])
            bx2 = float(parts2[3])
            by2 = float(parts2[4])
            bz2 = float(parts2[5])

            if not (x1==x2 and y1==y2 and z1==z2):
                raise Exception('Files do not have the same coordinate in line ' + str(i+2))
   
            bx_diff = bx2- bx1
            by_diff = by2- by1
            bz_diff = bz2- bz1

            outfile.write(format(x1, 'f') + ',' + format(y1, 'f') + ',' + format(z1, 'f') + ',' +  str(bx_diff) + ',' + str(by_diff) + ',' + str(bz_diff) + '\n')