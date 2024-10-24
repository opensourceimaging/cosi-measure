import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from postprocessing.utilities.utils import centerCut, ptpPPM


def plotSimple(data, FOV, fig, ax, cbar=True, circle_center=None, circle_radius=None, **args):

    # Plot the data
    im = ax.imshow(data, extent=FOV, origin="lower", **args)
    cs = ax.contour(data, colors='k', extent=FOV, origin="lower", linestyles="dotted")

    # Format contour labels
    class nf(float):
        def __repr__(self):
            s = f'{self:.1f}'
            return f'{self:.0f}' if s[-1] == '0' else s
    cs.levels = [nf(val) for val in cs.levels]
    
    if plt.rcParams["text.usetex"]:
        fmt = r'%r'
    else:
        fmt = '%r'
    ax.clabel(cs, cs.levels, inline=True, fmt=fmt, fontsize=10)
    
    if cbar:
        fig.colorbar(im, ax=ax)
    
    # Plot the red circle if circle_center and circle_radius are provided
    if circle_center is not None and circle_radius is not None:
        circle = patches.Circle(circle_center, circle_radius, edgecolor='red', facecolor='none', linewidth=2)
        ax.add_patch(circle)

    return im



def plot_center_slices(field, x_values, y_values, z_values, title="Z-component of $ B_0 $ field", unit=False, circle_center=None, circle_radius=None):
    '''
    plots the center slices of a field.

    # Args

    - field. np.ndarray. Data in mT

    - x_values. in mm

    - y_values. in mm

    - z_values. in mm

    # optional Args

    - title:str 

    - unit. can be either 'mT' or 'muT' or None. 

    - circle_center. tuple of float. in mm If circle_center and circle_radius is provided, a red circle will be plottet on top of data. 

    - circle radius:float. in mm

    # Returns 

    - None

    # Output

    - the center slices will be plotted. If unit=='mT' or unit=='muT', the mean field and PPM will be printed to stdout
    
    '''
    # display field

    if unit == 'muT':
        fieldfactor = 1e3
        title += ' in $\mu T$'
    elif unit == 'mT': 
        fieldfactor = 1
        title += ' in $mT$'
    else:
        fieldfactor = 1

    fig, ax = plt.subplots(1,3,figsize=(11,3))
    vmin = fieldfactor*np.nanmin(field); vmax = fieldfactor*np.nanmax(field)

    FOV_yz = (np.min(z_values), np.max(z_values), np.min(y_values), np.max(y_values))

    FOV_xz = (np.min(z_values), np.max(z_values), np.min(x_values), np.max(x_values))

    FOV_xy = (np.min(y_values), np.max(y_values), np.min(x_values), np.max(x_values))

    if circle_center is not None and circle_radius is not None:
        plotSimple(fieldfactor*centerCut(field, axis=0), FOV_yz, fig, ax[0] , vmin=vmin, vmax=vmax, circle_center=(circle_center[2],circle_center[1]) , circle_radius=circle_radius)
    else:
        plotSimple(fieldfactor*centerCut(field, axis=0), FOV_yz, fig, ax[0] , vmin=vmin, vmax=vmax)
    ax[0].set_xlabel('z axis in mm'); ax[0].set_ylabel('y axis in mm')

    if circle_center is not None and circle_radius is not None:
        plotSimple(fieldfactor*centerCut(field, axis=1), FOV_xz, fig, ax[1], vmin=vmin, vmax=vmax, circle_center=(circle_center[2],circle_center[0]), circle_radius=circle_radius)
    else:
        plotSimple(fieldfactor*centerCut(field, axis=1), FOV_xz, fig, ax[1], vmin=vmin, vmax=vmax)
    ax[1].set_xlabel('z axis in mm'); ax[1].set_ylabel('x axis in mm')

    if circle_center is not None and circle_radius is not None:
        plotSimple(fieldfactor*centerCut(field, axis=2), FOV_xy, fig, ax[2], vmin=vmin, vmax=vmax, circle_center=(circle_center[1],circle_center[0]), circle_radius=circle_radius)
    else:
        plotSimple(fieldfactor*centerCut(field, axis=2), FOV_xy, fig, ax[2], vmin=vmin, vmax=vmax)
    ax[2].set_xlabel('y axis in mm'); ax[2].set_ylabel('x axis in mm')

    plt.suptitle(title)
    plt.tight_layout()
    plt.show()
    
    if unit=='mT' or unit=='muT':
        print("B0 field homogeneity: " + str(int(ptpPPM(field))) + " PPM")
        print("mean field: " +  str(np.round(np.nanmean(field), 3)) + " mT")
