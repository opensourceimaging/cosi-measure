'''rst@FU 221017
tune picture module for EMRE
rst030@protonmail.com'''
from datetime import datetime
from scipy.signal import savgol_filter  # great invention
from scipy.optimize import curve_fit  # for fitting the dip
import numpy as np

timeToFrequencyConversionFactor = 6.94e4  # MHz/<tunepicunit>

class tp():
    '''Tunepicture object. creted by scope on lyra or by Emre.'''

    tunepicture = [] # make it a real float array
    time = [] # make it a real float array
    frequency = 0 # millivolts per second
    datetime = datetime.now
    tpFile = 0 # a file where cv is stored

    # --- Q fit stuff ---
    dip = []
    dipfreq = []
    FWHM_in_hz = 0

    tunepicFit = []
    frequencyFit = []

    def __init__(self,filename=''):

        # --- set parameters ---
        self.low_time_point = 0
        self.high_time_point = 0

        # --- measure parameters ---
        self.tunepicture = []
        self.time = []
        self.filename = ''

        # --- from here on - import from file ---
        # if filename was given, user wants to import that cv
        if filename == '':
            filename = './dummies/TP.csv'
            print('ever got here?')

        self.tpFile = open(filename)  # open the file
        # populate the fields of the cv object from that csv file
        self.tpFile = open(filename)  # open the file
        self.filename = str(filename.split('/')[-1])
        tpf = self.tpFile  # for short
        datafile = tpf.readlines()
        linecounter = 0
        lineWhereDataStarts = 0

        for line in datafile:
            print(line)
            relTime = float(line.split(',')[-3])
            tunePicValue = float(line.split(',')[-2])
            self.time.append(relTime)
            self.tunepicture.append(tunePicValue)

        self.frequency =  np.asarray(self.time,float)*timeToFrequencyConversionFactor
        self.tunepicture = np.asarray(self.tunepicture)


    def saveAs(self,filename: str):
        fout = open('%s.csv' % filename, 'w')
        i = 0
        for symb in self.tunepicture:
            if i == 0:
                fout.write('datetime,00.00.0000,00:00:00.000,%.12f, %.5f\n' % (float(self.time[i]), float(symb)))
                continue

            fout.write(',,,%.12f, %.5f\n' % (float(self.time[i]), float(symb)))
            i = i + 1
        fout.close()

    def fitDip(self):
        print('cutting the dip of the tunepicture')

        # subtract the constant offset
        lofst = np.mean(self.tunepicture[0:32])
        self.tunepicFit = self.tunepicture - lofst # to play around
        self.tunepicture_blcorr = self.tunepicFit # to use later

        # 1. get derivative of the smoothed tunepicture

        smoothtp = savgol_filter(self.tunepicture_blcorr,41,3)
        derivativeTP = savgol_filter(np.diff(smoothtp),41,3)
        derivativeFrequency = self.frequency[1:]

        # 2. find max of derivative - there the sharp peak is
        indexMaxDeriv = derivativeTP.argmax() + 48 # max derivative is the left step of TP


        leftLimTP = indexMaxDeriv

        if leftLimTP > len(self.frequency):
            return

        print('TP starts at idx ',leftLimTP,'at ',self.frequency[leftLimTP],' MHz')


        for i in range(indexMaxDeriv+48):
            derivativeTP[i] = 0

        # find the right limit of the TP
        rightLimTp = 0
        noiselevel = max(smoothtp)*0.1 # if 10% of height, then it is the end
        for i in range(indexMaxDeriv+48,len(smoothtp)):
            if smoothtp[i] < noiselevel:
                rightLimTp = i
                print(rightLimTp)
                break
        print('TP ends at idx ', rightLimTp, 'at ', self.frequency[rightLimTp], ' MHz')

        # nill the derivative outside the TP

        for i in range(rightLimTp-64,len(derivativeTP)):
            derivativeTP[i] = 0

        # find maximum of the nulled derivativeTP
        print('TP ends at idx ', rightLimTp, 'at ', self.frequency[rightLimTp], ' MHz')
        dipRightIdx = derivativeTP.argmax()
        print('DIP right at idx ', dipRightIdx, 'at ', self.frequency[dipRightIdx], ' MHz')
        dipLeftIdx = derivativeTP[:dipRightIdx].argmin()
        print('DIP left at idx ', dipLeftIdx, 'at ', self.frequency[dipLeftIdx], ' MHz')
        # searching dip center
        dipCenterIdx = derivativeTP[dipLeftIdx:dipRightIdx].argmin()
        print('DIP center at idx ', dipCenterIdx, 'at ', self.frequency[dipLeftIdx], ' MHz')
        # widening the dip region
        dipWidthIdx = dipRightIdx-dipLeftIdx
        print('initial DIP width [idx] ', dipWidthIdx, 'of ', self.frequency[dipRightIdx]-self.frequency[dipLeftIdx], ' MHz')
        # widen the noise
        if dipRightIdx + dipWidthIdx < rightLimTp:
            dipRightIdx = dipRightIdx + dipWidthIdx
        if dipLeftIdx - dipWidthIdx > leftLimTP:
            dipLeftIdx = dipLeftIdx - dipWidthIdx
        else:
            dipLeftIdx = dipWidthIdx+1

        # cutout the noise and the dip:
        tunepicHumpOnly = np.concatenate((self.tunepicture_blcorr[leftLimTP:dipLeftIdx],self.tunepicture_blcorr[dipRightIdx:rightLimTp]))
        frequencyHumpOnly = np.concatenate((self.frequency[leftLimTP:dipLeftIdx], self.frequency[dipRightIdx:rightLimTp]))

        # fit the parabola
        bgFit_coeffs = get_parabola_coefs(frequencyHumpOnly,tunepicHumpOnly+lofst)
        bgParabola = get_background(self.frequency,bgFit_coeffs)


        # for plotting fitted dip
        dip = (self.tunepicture - bgParabola)[dipLeftIdx:dipRightIdx]
        dipFrequencies = self.frequency[dipLeftIdx:dipRightIdx]

        self.dip = dip
        self.dipFreq = dipFrequencies

        popt_lorentz, pcov_lorentz = curve_fit(_lorentzian, dipFrequencies, dip, p0=[-0.1, 1.6, 0.1])  # fit with Lorentz
        lorentz_fit = _lorentzian(self.frequency, popt_lorentz[0], popt_lorentz[1], popt_lorentz[2])
        FWHM_lorentz = 2 * popt_lorentz[2] * 1e6 # Hz
        print('Q fit params:', popt_lorentz)
        print('FWHM of dip %.3f Hz' % FWHM_lorentz)
        print('FWHM = %.2f Hz' % FWHM_lorentz)


        self.tunepicFit = lorentz_fit + bgParabola
        self.frequencyFit = self.frequency

        self.FWHM_in_hz = FWHM_lorentz


def get_derivative(x, y): # get derivative of x by y, smoothen, adjust vector lengths
    smooth_y = savgol_filter(y, 37, 3)  # sav-gol(data,window,order)
    return x[1:], savgol_filter(np.diff(smooth_y), 37, 3)
def get_background(frequencies, fit_coefs): # render a parabola of 2th degree on frequencies vector from the fit_coef coefficients
    crds = frequencies
    parabola = crds**2*fit_coefs[0] + crds**1*fit_coefs[1] + crds**0*fit_coefs[2]
    return parabola

def get_parabola_coefs(frequencies, tunepicturearray):
    ''' fits a 2nd degree parabola on the tunepicturearray with frequencies coordinates'''
    '''first detect and cut out the dip, then use this nethod'''
    '''then fit the picture without dip with a 4-deg pol'''
    fit_coefs = np.polyfit(frequencies, tunepicturearray, 2)  # fit the bg only, without the dip. Gives fit coefs.

    return fit_coefs

def _lorentzian(x, amp, cen, wid): # for curve_fit of numpy
    return amp/np.pi*(wid/((x-cen)**2+wid**2))





def low_pass_filter(adata: np.ndarray, bandlimit: int = 1000, sampling_rate: int = 44100) -> np.ndarray:
    # translate bandlimit from Hz to dataindex according to sampling rate and data size
    bandlimit_index = int(bandlimit * adata.size / sampling_rate)

    fsig = np.fft.fft(adata)

    for i in range(bandlimit_index + 1, len(fsig) - bandlimit_index):
        fsig[i] = 0

    adata_filtered = np.fft.ifft(fsig)

    return np.real(adata_filtered)

