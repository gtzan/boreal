
import numpy as np
from scipy import fft
from scipy.integrate import simps


class Spectrum:

    name = 'spectrum' 
    def __init__(self, blockSize):
        self.blockSize = blockSize 
        
    def process(self, data):
        signal = data['signal'] 
        cspectrum = fft.fft(signal)
        spectrum = abs(cspectrum)[:int(self.blockSize / 2)]
        power = spectrum ** 2
        data['spectrum'] = power



class SpectrumBins:
    name = 'bins' 
    def __init__(self, circBins):
        self.circBins = circBins
        
    def process(self, data):
        spectrum = data['spectrum']
        bins = simps(np.split(spectrum, self.circBins))
        data['bins'] = bins 

        
