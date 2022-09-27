import json
import re

import ipykernel
import requests
import soundfile as sf
from bokeh.application import Application
from bokeh.resources import INLINE
from bokeh.application.handlers import DirectoryHandler
from bokeh.io import show, output_notebook
from notebook import notebookapp
from requests.compat import urljoin
import tempfile


def get_notebook_url():
    
    """Tries to find out what the notebook url is
    
    Returns:
        a string with the notebook url 
    """

    servers = list(notebookapp.list_running_servers())

    # find kernel id 
    kernel_id = re.search('kernel-(.*).json',
                          ipykernel.connect.get_connection_file()).group(1)

    # look through the servers and try to match kernel id 
    notebook_url = ""
    for ss in servers:
        response = requests.get(urljoin(ss['url'], 'api/sessions'),
                                params={'token': ss.get('token', '')})
        kernels = json.loads(response.text)
        for nn in kernels:
            if 'kernel' in nn:
                if nn['kernel']['id'] == kernel_id:
                    notebook_url = ss['url']
    return notebook_url[:-1]


def render(audio_input, widgets=[], playback_mode="pyaudio", notebook_url=None):
 
    audio_fname = audio_input
    if type(audio_input) is tuple:     # audio data input 
        audio, samplerate = audio_input
        temp_file_name = tempfile.NamedTemporaryFile(dir='/tmp',
                                              suffix='.wav',
                                              delete=False)
        # write a temporary file for the audio data 
        sf.write(temp_file_name, audio, samplerate)        
        audio_fname = temp_file_name.name 

    # set up the command line arguments passed to the application 
    argv = [audio_fname]
    argv = argv + [playback_mode] + widgets
    
    # create a Bokeh application from the audio_widgets directory
    handler = DirectoryHandler(filename='audio_widgets', argv=argv)
    app = Application(handler)

    # show the application in the notebook 
    if notebook_url is None:
        notebook_url = get_notebook_url()
        print(notebook_url)
    output_notebook(resources=INLINE)
    show(app, notebook_url=notebook_url)


# short-hand calls for specific widgets 
    
def spectrum(audio_input, playback_mode = 'pyaudio', notebook_url=None):
    """ Spectrum audio widget
    """
    render(audio_input, ['spectrum'], playback_mode, notebook_url)


def time_waveform(audio_input, playback_mode = 'pyaudio', notebook_url=None):
    """ Time domain waveform 
    """
    render(audio_input, ['time_waveform'], playback_mode, notebook_url)

    
def waveform_envelope(audio_input, playback_mode = 'pyaudio', notebook_url=None):
    """ Waveform envelope 
    """
    render(audio_input, ['waveform_envelope'], playback_mode, notebook_url)

def circulareq(audio_input, playback_mode = 'pyaudio', notebook_url=None):

    """ Circular equalizer 
    """
    
    render(audio_input, ['circulareq'], playback_mode, notebook_url)


def centroid(audio_input, playback_mode = 'pyaudio', notebook_url=None):
    """ Spectrum audio widget
    """
    render(audio_input, ['centroid'], playback_mode, notebook_url)
    
