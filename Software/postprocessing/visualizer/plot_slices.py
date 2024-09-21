import matplotlib.pyplot as plt
import numpy as np
from postprocessing.utilities.utils import centerCut, ptpPPM

def plotSimple(data, FOV, fig, ax, cbar=True, **args):

    #im = ax.imshow(data, extent=FOV, origin="upper", **args)
    #cs = ax.contour(data, colors='k', extent=FOV, origin="upper", linestyles="dotted")
    im = ax.imshow(data, extent=FOV, origin="lower", **args)
    cs = ax.contour(data, colors='k', extent=FOV, origin="lower", linestyles="dotted")

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
    if cbar == True:
        fig.colorbar(im, ax=ax)
    return im



def plot_center_slices(field, x_values, y_values, z_values, title="Z-component of $ B_0 $ field", unit=False):
    '''
    
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

    plotSimple(fieldfactor*centerCut(field, axis=0), FOV_yz, fig, ax[0] , vmin=vmin, vmax=vmax)
    #ax[0].set_xlabel('z axis in mm'); ax[0].set_ylabel('x axis in mm')
    #ax[0].set_xlabel('z axis in mm'); ax[0].set_ylabel('y axis in mm')
    # orginal : 
    ax[0].set_xlabel('z axis in mm'); ax[0].set_ylabel('y axis in mm')
    plotSimple(fieldfactor*centerCut(field, axis=1), FOV_xz, fig, ax[1], vmin=vmin, vmax=vmax)
    #ax[1].set_xlabel('z axis in mm'); ax[1].set_ylabel('y axis in mm')
    #orginal: 
    ax[1].set_xlabel('z axis in mm'); ax[1].set_ylabel('x axis in mm')
    plotSimple(fieldfactor*centerCut(field, axis=2), FOV_xy, fig, ax[2], vmin=vmin, vmax=vmax)
    #ax[2].set_xlabel('x axis in mm'); ax[2].set_ylabel('y axis in mm')
    # orginal: 
    ax[2].set_xlabel('y axis in mm'); ax[2].set_ylabel('x axis in mm')

    plt.suptitle(title)
    plt.tight_layout()
    #plt.savefig("Bilder/2-coils-B0-center.png")
    plt.show()
    
    if unit=='mT' or unit=='muT':
        print("B0 field homogeneity: " + str(int(ptpPPM(field))) + " PPM")
        print("mean field: " +  str(np.round(np.nanmean(field), 3)) + " mT")



def plot_extrema_cross(field, x_values, y_values, z_values, title="Extrempoints of $B_0$ field$", muT=False):
    '''
    
    '''
    # display field

    if muT:
        fieldfactor = 1e3
        title += ' in $\mu T$'
    else: 
        fieldfactor = 1
        title += ' in $mT$'

    fig, ax = plt.subplots(1,3,figsize=(11,3))
    vmin = fieldfactor*np.nanmin(field); vmax = fieldfactor*np.nanmax(field)

    FOV_yz = (np.min(z_values), np.max(z_values), np.min(y_values), np.max(y_values))

    FOV_xz = (np.min(z_values), np.max(z_values), np.min(x_values), np.max(x_values))

    FOV_xy = (np.min(y_values), np.max(y_values), np.min(x_values), np.max(x_values))

    plotSimple(fieldfactor*centerCut(field, axis=0), FOV_yz, fig, ax[0] , vmin=vmin, vmax=vmax)
    #ax[0].set_xlabel('z axis in mm'); ax[0].set_ylabel('x axis in mm')
    #ax[0].set_xlabel('z axis in mm'); ax[0].set_ylabel('y axis in mm')
    # orginal : 
    ax[0].set_xlabel('z axis in mm'); ax[0].set_ylabel('y axis in mm')
    plotSimple(fieldfactor*centerCut(field, axis=1), FOV_xz, fig, ax[1], vmin=vmin, vmax=vmax)
    #ax[1].set_xlabel('z axis in mm'); ax[1].set_ylabel('y axis in mm')
    #orginal: 
    ax[1].set_xlabel('z axis in mm'); ax[1].set_ylabel('x axis in mm')
    plotSimple(fieldfactor*centerCut(field, axis=2), FOV_xy, fig, ax[2], vmin=vmin, vmax=vmax)
    #ax[2].set_xlabel('x axis in mm'); ax[2].set_ylabel('y axis in mm')
    # orginal: 
    ax[2].set_xlabel('y axis in mm'); ax[2].set_ylabel('x axis in mm')

    plt.suptitle(title)
    plt.tight_layout()
    #plt.savefig("Bilder/2-coils-B0-center.png")
    plt.show()
    
    print("B0 field homogeneity: " + str(int(ptpPPM(field))) + " PPM")
    print("mean field: " +  str(np.round(np.nanmean(field), 3)) + " mT")