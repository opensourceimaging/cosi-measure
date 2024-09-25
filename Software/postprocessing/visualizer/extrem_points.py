from ..utilities.csv_importer import csv_import
from postprocessing.visualizer.plot_slices import plot_center_slices

def evaluate_extrempoints(file_extrema_before, file_extrema_after, description='', position_b0=3):
    '''
    wrapper for quickly plotting values of extrempoints in different ways.

    # Args

    - file_extrema_before:str path to file

    - file_extrema_after:str path to file

    - description:str, optional. This will be added to the titles of the plots.

    - position_bz:int, optional. The position of the main B0-field inside the csv data.

    # Returns

    - None. Plots will be shown.
    
    '''
    field_before, x_values, y_values, z_values = csv_import(file_extrema_before, position_b0=position_b0)
    field_after, x_values, y_values, z_values = csv_import(file_extrema_after, position_b0=position_b0)
    diff_field = field_after - field_before
    diff_ppm = ((field_after-field_before)/field_before) * 1e6

    plot_center_slices(diff_field, x_values, y_values, z_values, title=description +'Diff of Extrempoints: $Bz_{after}-Bz_{before}$', unit='muT')
    plot_center_slices(diff_ppm, x_values, y_values, z_values, title=description +'Difference in PPM')
    plot_center_slices(field_before, x_values, y_values, z_values, title=description +'Extrempoints Before', unit='mT')
    plot_center_slices(field_after, x_values, y_values, z_values, title=description +'Extrempoints After', unit='mT')