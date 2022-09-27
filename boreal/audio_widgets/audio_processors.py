import numpy as np
from scipy import fft
from scipy.integrate import simps


class Spectrum:

    name = 'Spectrum' 
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



class SpectralCentroid:
    name = 'SpectralCentroid' 
    def __init__(self, len_blocks):
        """
        Process a spectrum and returns the corresponding centroid 
        """

        self.len_blocks = len_blocks
        self.centroid_track = np.zeros(len_blocks+1)
        self.scentroid_track = np.zeros(len_blocks+1)
        self.k = 0 
        
    def process(self, data):
        """
        Process spectrum input and add the centroid to
        the data dictionary 
        Args:
            data (ndarray): the data containing the audio samples
        """
        spectrum = data['spectrum']
        
        if (np.sum(spectrum) != 0.0):
            norm_spectrum = spectrum / np.sum(spectrum)
        else:
            norm_spectrum = spectrum 
        # centroid extraction
        fbins = np.arange(0.0, float(len(norm_spectrum)))
        centroid = np.dot(fbins, norm_spectrum)
        data['centroid_track'][self.k] = centroid
        
        if (self.k > 20):
            data['scentroid_track'][self.k] = np.sum(data['centroid_track'][self.k - 20:self.k]) / 20

        self.k += 1




class SpectrumBins:
    name = 'SpectrumBins' 
    def __init__(self, circBins):
        """
        Process the spectrum and a smaller number of bins summarizing it  
        Args:
            bins (int): number of bins for circular equalizer
        """
        
        self.circBins = circBins
        
    def process(self, data):
        """
        Process the spectrum input and add the circular bins to
        the data dictionary 
        Args:
            data (ndarray): the data containing the audio samples
        """
        
        spectrum = data['spectrum']
        bins = simps(np.split(spectrum, self.circBins))
        data['bins'] = bins 

        
