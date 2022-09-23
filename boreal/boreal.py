import json
import re

import ipykernel
import requests
import soundfile as sf
from bokeh.application import Application
from bokeh.application.handlers import DirectoryHandler
from bokeh.io import show, output_notebook
from notebook import notebookapp
from requests.compat import urljoin
import sys
import numpy
import tempfile




def get_notebook_url():
    """ tries to find out what the notebook url is if running on a 
        local machine. 
    
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


def spectrum(audio_input, playback_mode = 'pyaudio', notebook_url=None):
    render(audio_input, ['spectrum'], playback_mode, notebook_url)


def time_waveform(audio_input, playback_mode = 'pyaudio', notebook_url=None):
    render(audio_input, ['time_waveform'], playback_mode, notebook_url)


def waveform_envelope(audio_input, playback_mode = 'pyaudio', notebook_url=None):
    render(audio_input, ['waveform_envelope'], playback_mode, notebook_url)

    
def circulareq(audio_input, playback_mode = 'pyaudio', notebook_url=None):
    render(audio_input, ['circulareq'], playback_mode, notebook_url)    

def render(audio_input, widgets=[], playback_mode="pyaudio", notebook_url=None):
    """ render audio widget visualizations for an audio file 

    Args:
        audio_fname (str): the audio file to be rendered (the format needs to be supported by PySoundfile
        widgets: a list of strings with widget names
        playback_mode (str): pyaudio or html
        notebook_url (str)
    """
    audio_fname = audio_input
    if type(audio_input) is tuple:
        audio, samplerate = audio_input
        temp_file_name = tempfile.NamedTemporaryFile(dir='/tmp',
                                              suffix='.wav',
                                              delete=False)
        sf.write(temp_file_name, audio, samplerate)        
        audio_fname = temp_file_name.name 

    argv = [audio_fname]
    argv = argv + [playback_mode] + widgets
    
    # create a Bokeh application from the audio_widgets directory
    handler = DirectoryHandler(filename='audio_widgets', argv=argv)
    app = Application(handler)

    # show the application in the notebook 
    if notebook_url is None:
        notebook_url = get_notebook_url()
        print(notebook_url)
    output_notebook()
    show(app, notebook_url=notebook_url)

