import numpy as np

def csv_import(filename, position_b0=5):
    '''
    # Args

    - filename:string. Name of a field file. Format: X[mm],Y[mm],Z[mm],Bx[mT],By[mT],Bz[mT]. The first 3 coloums are fixed as x,y,z and the following coloums can be different. Which one is the main B0-component shall be defined by position_b0.

    - position_b0:int Position of the main component of the field inside the csv file. Default: 5

    # Returns

    - Bz_array. 3D-array which cointains the measurement data in point. Only the main component as defined by position_b0 is returned.

    - x_values. np.ndarary. The X-values along the x-axis on which the measurement data is accquired.

    - y_values. See above.

    - z_values. See above.

    '''
    # reading B-field file into list
    try:
        with open(filename, 'r') as file:
            bfield_lines = []
            header_lines = []
            for line in file:
                if line[0] == '#' or line[0] == '%' or line[0] == 'X':
                    header_lines.append(line)
                else:
                    bfield_lines.append(line)

    except FileNotFoundError:
        print("File not found.")
        return
    
    # Parse the data into a list of tuples
    data = []
    for i in range(len(bfield_lines)):
        parts = bfield_lines[i].strip().split(',')
        x = float(parts[0])
        y = float(parts[1])
        z = float(parts[2])
        bz = float(parts[position_b0])
        data.append((x, y, z, bz))
    
    # Extract unique x, y, z coordinates to determine the shape of the 3D array
    x_values = sorted(set([d[0] for d in data]))
    y_values = sorted(set([d[1] for d in data]))
    z_values = sorted(set([d[2] for d in data]))
    
    # Create a 3D array initialized with zeros
    B0_array = np.zeros((len(x_values), len(y_values), len(z_values)))
    
    # Create dictionaries to map coordinates to indices
    x_to_index = {x: i for i, x in enumerate(x_values)}
    y_to_index = {y: i for i, y in enumerate(y_values)}
    z_to_index = {z: i for i, z in enumerate(z_values)}
    
    # Populate the 3D array with bz values
    for x, y, z, bz in data:
        i = x_to_index.get(x, None)
        j = y_to_index.get(y, None)
        k = z_to_index.get(z, None)
        
        # Check if the mapping is correct
        if i is not None and j is not None and k is not None:
            #print(f"Mapping (x, y, z) = ({x}, {y}, {z}) to (i, j, k) = ({i}, {j}, {k}) and storing bz = {bz}")
            B0_array[i, j, k] = bz
        else:
            print(f"Error mapping (x, y, z) = ({x}, {y}, {z})")

    B0_array[B0_array == 0] = np.nan
    
    return B0_array, np.array(x_values), np.array(y_values), np.array(z_values)