import os
import time
from time import sleep
import numpy as np
from scipy import fft 
import soundfile as sf
from scipy.integrate import simps
from audio_processors import Spectrum, SpectrumBins, SpectralCentroid

# These are the values extracted on every block
# of audio that is being processed 
data = {'time': 0.0,
        'signal': None,
        'gain': None}


# information about the audio file 
audio_info = {'duration': None,
              'samplerate': None,
              'blockSize': None}


ctime_ = 0.0 
    

def update_audio_data(fname, playback_mode, audio_play,
                      audio_close, audio_seek):

    """ Thread that reads and processes the audio data using audio processors 

    Args:
        fname (str) : the file from which the audio is read 
        playback_mode (str): pyaudio or html  
        playback_mode (str): pyaudio or html
        audio_play (Event): event for starting/pausing playback
        audio_close(Event): event for stopping the audio thread
        audio_seek(Event): event for audio seeking 
    """
 
    
    k = 0
    pyaudio_available = False

    # initialize stuff at first iteration 
    if k == 0:
        current_time = data['time']
        blockSize = 2048
        circBins = 16

        # open sound file and get info about it 
        isf = sf.SoundFile(fname, 'r')
        audio_info['duration'] = sf.info(fname).duration
        audio_info['samplerate'] = sf.info(fname).samplerate
        audio_info['blockSize'] = blockSize
        block_duration = float(blockSize) / audio_info['samplerate']
        
        # allocate arrays 
        signal = np.zeros(blockSize)
        html_data = signal.astype(np.float32)
        len_samples = len(isf)
        len_blocks = int(len_samples / blockSize)

        # initialize data dictionary 
        data['signal'] = signal
        data['spectrum'] = np.zeros(blockSize)
        data['bins'] = np.zeros(circBins) 
        data['centroid_track'] = np.zeros(len_blocks)
        data['scentroid_track'] = np.zeros(len_blocks)        
        
        # initialize processors 
        spectrum_processor = Spectrum(blockSize)
        spectrum_bins_processor = SpectrumBins(circBins)
        centroid_processor = SpectralCentroid(len_blocks)
        
        # initialize pyaudio 
        try:
            import pyaudio
            # setup audio playback stream 
            pa = pyaudio.PyAudio()
            stream = pa.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=int(audio_info['samplerate']),
                input=False,
                output=True,
                frames_per_buffer=audio_info['blockSize']
            )
            pyaudio_available = True
        except:
            pyaudio_available = False

    while True:
        current_time = data['time']
        try:
            t0 = time.perf_counter()
            
            # wait on event to start audio playback 
            audio_play.wait()

            # read from input sound file 
            sfdata = isf.read(blockSize, always_2d=True).astype(np.float32)
            # convert to mono 
            sfdata =  sfdata.sum(axis=1) / 2

            # seek if needed 
            if audio_seek and audio_seek.isSet():
                set_time = ctime_
                set_frame = int(set_time*audio_info['samplerate'])
                isf.seek(set_frame)
                current_time = set_time
                audio_seek.clear()

            # write audio to stream
            if playback_mode == "html":
                stream.write(html_data.tostring())
            elif playback_mode == "pyaudio":
                if pyaudio_available:                    
                    stream.write(sfdata.tostring())
            else:
                print('playback_mode', playback_mode)
                print("Unsupported playback_mode")

            # apply the different processors
            # notice that the spectrum_bins_processor
            # needs to come after the spectrum processor
            # as it requires the spectrum to be present
            # in data. Essentially each processor adds
            # new information to the data dictionary 
            spectrum_processor.process(data)
            spectrum_bins_processor.process(data)
            centroid_processor.process(data)
            
            # advance time
            current_time += block_duration
            t1 = time.perf_counter()

            data['time'] = current_time                
            data['signal'] = sfdata

            # sleep for approximately the right number
            # of time for processing a block
            # in order for the html/javascript playback
            # to work on remote notebooks
            
            if not pyaudio_available:
                if block_duration > (t1 - t0):
                    sleep(block_duration - (t1 - t0))
                else:
                    sleep(t1 - t0)

            # deal with end of file with looping to the start 
            k = k + 1
            if k >= len_blocks:
                print("End of file")
                set_current_time(0.0)
                k = 0
                isf.seek(0)

            # deal with closing/terminating the audio thread 
            if audio_close.isSet():
                print("Terminating audio analysis/playback")
                set_current_time(0.0)
                k = 0
                isf.seek(0)                                
                return 
        except:
            continue


        
def get_current_time():
    """ Return the current time in seconds  
    """
    return data['time']

def set_current_time(t):
    """ Set the current time
    Args:
       t (float): the time in seconds 
    """
    
    data['time'] = t
    global ctime_ 
    ctime_ =  t
