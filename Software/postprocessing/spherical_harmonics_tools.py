import pyshtools
import numpy as np
import pandas as pd
from scipy.special import sph_harm
from scipy.interpolate import RegularGridInterpolator, griddata


def calcAngles(phiNumber, thetaNumber):
    """returns the angles of phi and theta for a given number of phi and theta angles
    the theta angles are set to be gauss legendre points and theta are equidistant"""
    samplePoints, weights = np.polynomial.legendre.leggauss(thetaNumber)
    samplePoints  = samplePoints[::-1]
    weights       = weights[::-1]
    
    thetaRad      = np.arccos(samplePoints) - np.pi/2
    
    phiMin        = 0    #[rad] Longitude limits
    phiMax        = 2*np.pi*(1-1/phiNumber)     
    phiRad        = np.linspace(phiMin,   phiMax,   phiNumber)

    return phiRad, thetaRad


def toCarthesianCoords(r, phi, theta):
    x = r*np.sin(theta)*np.cos(phi)
    y = r*np.sin(theta)*np.sin(phi)
    z = r*np.cos(theta)
    return x,y,z


def spherical_to_cartesian(r, theta, phi):
    """
    Convert spherical coordinates to Cartesian coordinates.
    
    Parameters:
    r (float or np.ndarray): Radius
    theta (float or np.ndarray): Colatitude (0 at North Pole, pi at South Pole)
    phi (float or np.ndarray): Longitude
    
    Returns:
    x, y, z (np.ndarray): Cartesian coordinates
    """
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    
    return x, y, z


# Calculating the Spherical Harmonics Coefficients of the Measured Field
# If the field is measured in a regular grid, we interpolate
def interpolMeshToSphere(field, phiRad, thetaRad, radius, _min, _max):
    """interpolatates a field with a given resolution on a sphere"""
    xAxis = np.linspace(_min, _max, field.shape[0]) 
    yAxis = np.linspace(_min, _max, field.shape[1]) 
    zAxis = np.linspace(_min, _max, field.shape[2]) 
    interpol = RegularGridInterpolator((xAxis, yAxis, zAxis), field)
    fielddata = []
    for _phi in phiRad:
        for _theta in thetaRad:
            # theta must be in rotated as co or- not co- (latitude longitude)
            fielddata.append( interpol( toCarthesianCoords(radius, _phi, _theta + np.pi/2)) )

    fielddata = np.array(fielddata, dtype = float)    
    fielddata = np.reshape(fielddata, (len(phiRad), len(thetaRad)))
    # fielddata = np.reshape(fielddata, (phiNumber, thetaNumber))
    return fielddata


def interpolSphereToMesh(sphericalField, phiRad, thetaRad, axis_values):
    """
    Interpolates a spherical field back onto a Cartesian grid.
    
    Parameters:
    sphericalField: np.array
        The spherical field data.
    phiRad: np.array
        Array of azimuthal angles (phi).
    thetaRad: np.array
        Array of polar angles (theta).
    radius: float
        The radius at which the spherical data is defined.
    _min: float
        The minimum value for the Cartesian grid axes.
    _max: float
        The maximum value for the Cartesian grid axes.
    grid_shape: tuple
        Shape of the Cartesian grid (e.g., (nx, ny, nz)).
    
    Returns:
    field: np.array
        The Cartesian-sampled field.
    """
    
    # Convert spherical field to interpolator
    interpol_spherical = RegularGridInterpolator((phiRad, thetaRad), sphericalField, bounds_error=False, fill_value=None)
    
    # Create Cartesian grid
    xAxis = axis_values.copy()
    yAxis = axis_values.copy()
    zAxis = axis_values.copy()

    _min = np.min(xAxis)
    _max = np.max(xAxis)
    
    # Initialize the Cartesian field
    field = np.zeros((xAxis.shape[0], yAxis.shape[0], zAxis.shape[0]))
    
    # Convert Cartesian coordinates to spherical coordinates and interpolate
    for i, x in enumerate(xAxis):
        for j, y in enumerate(yAxis):
            for k, z in enumerate(zAxis):
                r = np.sqrt(x**2 + y**2 + z**2)
                if r > 0:
                    theta = np.arccos(z / r)  # Polar angle
                    phi = np.arctan2(y, x)    # Azimuthal angle
                    
                    if _min <= r <= _max:
                        field[i, j, k] = interpol_spherical([phi, theta])
                    else:
                        field[i, j, k] = np.nan  # Points outside the spherical region
                else:
                    field[i, j, k] = np.nan  # The origin (undefined spherical coordinates)

    return field


def integrate(integrand, phiRad, thetaNumber):
    """Integrates a descrete function
    constant        - constant factor multiplied to the integral
    phiRad          - the phi angles the integrand is sampled on
    the theta angles are set by gauss legendre
    
    the integral along axis 1 is with gauss legendre
    and along axis 2 with trapzoids
    """
    from numpy.polynomial.legendre import leggauss
    samplePoints, weights = leggauss(thetaNumber)

    # padd integrand
    integrand_padded = np.vstack((integrand, integrand[0]))
    # calculate phis for trapz
    phis = np.append(phiRad,phiRad[-1]+phiRad[1]-phiRad[0])
    # integrate over phi with trapezoidal rule
    integration1 = np.trapz(integrand_padded, x=phis, axis=0)
    # integrate over theta with gauss legendre 
    integration2 = np.dot(integration1, weights)
    return integration2


def calcMaxSHdegree(thetaNumber, phiNumber):
    lmax = int((thetaNumber - 1)/2 - 1) # 35
    mmax = int(phiNumber/2 - 1) # lmax # 35
    # or - 1/2?
    return lmax, mmax


def calcSHcoefficents(field, lat, lon, phiRad, thetaNumber, lmax, mmax, threshold = None):
    """returns the sh coefficients of a given field sampled at lat, lon
    as a pyshtools class"""

    normalization = 'ortho' # Konstantin: 'ortho'

    # initialize pyshtools 
    clmRecon = pyshtools.SHCoeffs.from_zeros(lmax=lmax, normalization=normalization)

    for l in range(lmax+1):
        for m in range(-l,l+1):
            if abs(m) <= mmax:
                clm = pyshtools.SHCoeffs.from_zeros(lmax=lmax, normalization=normalization)
                clm.set_coeffs(1., l, m)    # Betrachtung auf Einheitskreis?
                Ylm = clm.expand(lat=lat, lon=lon) # initialize SHMagGrid and SHMag Tensor class instances
                coeff = integrate(Ylm * field, phiRad, thetaNumber) # field must be in spherical coordinates, sampled at lat, lon
                if threshold != None:
                    if abs(coeff) < threshold: 
                        clmRecon.set_coeffs(0, l, m)
                    else:
                        clmRecon.set_coeffs(coeff, l, m)
                else:
                    clmRecon.set_coeffs(coeff, l, m)
    
    return clmRecon


def reconstruct_field_from_shcoeffs(sh_file, lat, lon):
    """
    ###############
    # !!!!!NOT YET WORKING!!!! #
    ###############
    
    Reconstructs a field from spherical harmonic coefficients.

    Parameters:
    sh_file (str): Path to the .csv file containing the spherical harmonic coefficients (output of pyshtools.SHCoeffs.to_file()).
    latitudes (array-like): latitudes, on which the field shall be sampled
    longitudes (array-like): longitudes, on which the field shall be sampled

    Returns:
    field (numpy.ndarray): Reconstructed field values at the specified coordinates.
    """
    # Load the spherical harmonic coefficients from the .sh file
    clm = pyshtools.SHCoeffs.from_file(sh_file)
    #clm.expand()
    
    # Load the coordinates from the csv file
    #coords = pd.read_csv(coord_file)
    #latitudes = coords['latitude'].to_numpy()
    #longitudes = coords['longitude'].to_numpy()
    
    # Convert spherical harmonic coefficients back to field values
    #field = clm.expand(lat=latitudes, lon=longitudes)
    field_grid = clm.expand(grid='DH', lat=lat, lon=lon)  # 'DH' for Driscoll-Healy grid, which is standard
    #field_grid = clm.expand(grid='DH')
    # Extract the field values at the desired latitudes and longitudes
    #field = field_grid.interp(longitudes, latitudes)

    #pyshtools.SHGrid.to_array

    dat = field_grid#.to_array()
    
    return dat


