import numpy as np

def centerCut(field, axis):
    """return a slice of the data at the center for the specified axis"""
    dims = np.shape(field)
    return np.take(field, indices=int(dims[axis]/2), axis=axis)



def ptpPPM(field):
    min = np.nanmin(field)
    max = np.nanmax(field)
    mean = np.nanmean(field)
    
    return 1e6 * (max - min) / np.abs(mean)