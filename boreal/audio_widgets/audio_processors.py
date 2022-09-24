import numpy as np
from scipy import fft
from scipy.integrate import simps


class Spectrum:

    name = 'spectrum' 
    def __init__(self, blockSize):
        """
        Process audio input and return the corresponding power spectrum 
        Args:
            blockSize (int): the size in samples of the block to be processed
        """
        self.blockSize = blockSize 
        
    def process(self, data):
        """
        Process audio input and add the corresponding power spectrum
        to the data dictionary 
        
        Args:
            data (ndarray): the data containing the audio samples
        """
        
        signal = data['signal'] 
        cspectrum = fft.fft(signal)
        spectrum = abs(cspectrum)[:int(self.blockSize / 2)]
        power = spectrum ** 2
        data['spectrum'] = power



class SpectrumBins:
    name = 'bins' 
    def __init__(self, circBins):
        """
        Process audio input and return the corresponding power spectrum 
        Args:
            bins (int): number of bins for circular equalizer
        """
        
        self.circBins = circBins
        
    def process(self, data):
        """
        Process audio input and add the circular bins to
        the data dictionary 
        Args:
            data (ndarray): the data containing the audio samples
        """
        
        spectrum = data['spectrum']
        bins = simps(np.split(spectrum, self.circBins))
        data['bins'] = bins 

        
