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
from pkg_resources import resource_filename
import jams
import librosa
from threading import Thread, Event
from bokeh.plotting import figure, output_file, show
import numpy as np
from bokeh.models import ColumnDataSource, LabelSet, Button 
from bokeh.models import Span,Band
from bokeh.io import push_notebook, show, output_notebook
import tempfile
import os 
import IPython.display as ipd
import ipywidgets as widgets
import time
from time import sleep
import panel as pn
from functools import partial




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


def render(audio_input, widgets=[], playback_mode="pyaudio",
           notebook_url=None, width=600, height = 350,
           ref_jams_file="", prd_jams_file = ""):

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
    argv += [playback_mode]
    argv += [str(width), str(height)] 
    argv += [ref_jams_file, prd_jams_file]
    argv += widgets 

    path_to_widgets = resource_filename(__name__, 'audio_widgets')
    
    # create a Bokeh application from the audio_widgets directory
    handler = DirectoryHandler(filename=path_to_widgets, argv=argv)
    app = Application(handler)

    # show the application in the notebook 
    if notebook_url is None:
        notebook_url = get_notebook_url()
        print(notebook_url)
    output_notebook(resources=INLINE)
    show(app, notebook_url=notebook_url)

# short-hand calls for specific widgets 
    
def spectrum(audio_input, playback_mode = 'pyaudio', notebook_url=None, width=600, height=350, ref_jams_file="", prd_jams_file=""):
    """ Spectrum audio widget
    """
    render(audio_input, ['spectrum'], playback_mode, notebook_url, width, height, ref_jams_file, prd_jams_file)


def time_waveform(audio_input, playback_mode = 'pyaudio', notebook_url=None, width=400, height = 400, ref_jams_file="", prd_jams_file=""):
    """ Time domain waveform 
    """
    render(audio_input, ['time_waveform'], playback_mode, notebook_url, width, height, ref_jams_file, prd_jams_file)

    
def waveform_envelope(audio_input, playback_mode = 'pyaudio',
                      notebook_url=None, width=800, height=300,
                      ref_jams_file="", prd_jams_file=""):
    """ Waveform envelope 
    """
    render(audio_input, ['waveform_envelope'], playback_mode, notebook_url,width, height, ref_jams_file, prd_jams_file)

def circulareq(audio_input, playback_mode = 'pyaudio', notebook_url=None, width=300, height=300, ref_jams_file="", prd_jams_file=""):

    """ Circular equalizer 
    """
    
    render(audio_input, ['circulareq'], playback_mode, notebook_url, width, height, ref_jams_file, prd_jams_file)


def centroid(audio_input, playback_mode = 'pyaudio', notebook_url=None, width=800, height=200, ref_jams_file="", prd_jams_file=""):
    """ Spectrum audio widget
    """
    render(audio_input, ['centroid'], playback_mode, notebook_url, width, height, ref_jams_file, prd_jams_file)



def init_visualization(audio, srate):
    duration_secs = audio.shape[0] / srate
    plotargs = dict(tools="", toolbar_location=None, outline_line_color='#595959')
    signal_plot = figure(width=800, height=400,
                        title="Waveform Envelope",
                        x_range=[0, duration_secs],
                        y_range=[-1.5, 1.0],
                        x_axis_label='Time(secs)',
                        y_axis_label='Amplitude', **plotargs)
    signal_plot.background_fill_color = "#eaeaea"
    
    def max_absolute(block):
        return np.max(np.abs(block))

    def process(signal, hopSize, block_process):
        winSize = hopSize
        offsets = np.arange(0, len(signal), hopSize)
        amp_track = np.zeros(len(offsets))
        for (m, o) in enumerate(offsets):
            frame = signal[o:o + winSize]
            amp_track[m] = block_process(frame)
        return amp_track
    
    max_envelope = process(audio, 4096, max_absolute)

    times = np.linspace(0, len(audio) / srate, num=len(max_envelope))
    pos = 0.0 
    mpos_source = ColumnDataSource(data=dict(
                    xs=[[pos,pos,pos]],
                    ys=[[0.0, 1.0, -1.0]]
    ))
    signal_plot.multi_line(xs="xs", ys="ys", source=mpos_source, 
                     line_color="red", line_width=1)
    band_data = {}
    band_data['x'] = times
    band_data['lower'] = max_envelope
    band_data['upper'] = -max_envelope
    band_source = ColumnDataSource(data=band_data)
    band = Band(base='x', lower='lower', upper='upper', source = band_source, level='underlay', fill_alpha=1.0, line_width=1, line_color='black')
    signal_plot.add_layout(band)
    return (signal_plot, mpos_source)


def update_audio_data(fname, plot_handle, mpos_source, audio_play, duration_secs): 
    k = 0 
    blockSize = 1024
    isf = sf.SoundFile(fname, 'r')
    srate = sf.info(fname).samplerate
    len_samples = len(isf)
    len_blocks = int(len_samples / blockSize)
    
    ctime = 0; 
    print("STARTING PLAYBACK\n")
  
    while(1):
        audio_play.wait()        
        t0 = time.perf_counter()
        sfdata = isf.read(blockSize, always_2d=True).astype(np.float32)
        # convert to mono 
        sfdata =  sfdata.sum(axis=1) / 2
        block_duration = float(blockSize) / srate 
        ctime += block_duration

        t1 = time.perf_counter()
        if block_duration > (t1 - t0):
            sleep(block_duration - (t1 - t0))
        else:
            sleep(t1 - t0)
        k = k + 1 
        if (ctime > duration_secs): 
            print("AUDIO PLAYBACK ENDED")
            return
        
        
def update_visual_data(plot_handle, mpos_source, audio_play, duration_secs):
    k = 0
    ctime = 0; 
    print("STARTING PLAYBACK VISUAL\n")
    block_duration = 0.05 
    while(1):
        audio_play.wait()        
        t0 = time.perf_counter()
        mpos_source.data = dict(xs = [[ctime,ctime,ctime]], ys=[[0.0, 1.0, -1.0]])
        push_notebook(handle=plot_handle)
        ctime += block_duration
        t1 = time.perf_counter()
        if block_duration > (t1 - t0):
            sleep(block_duration - (t1 - t0))
        else:
            sleep(t1 - t0)
        k = k + 1 
        if (ctime > duration_secs): 
            print("VISUAL PLAYBACK ENDED")
            return 



        
        
def time_domain_waveform(audio, srate):
    duration_secs = audio.shape[0] / srate
    
    audio_play = Event()
    temp_file = tempfile.NamedTemporaryFile(dir='.',
                                            suffix='.wav',
                                            delete=False)
    sf.write(temp_file.name, audio, srate)
    audio_fname = temp_file.name 
    
    (signal_plot, mpos_source) = init_visualization(audio, srate)
    output_notebook()    
    plot_handle = show(signal_plot, notebook_handle=True)
    push_notebook(handle=plot_handle) 
    
    # start visualization thread 
    visualThread = Thread(target=update_visual_data, args=[plot_handle, mpos_source, audio_play, duration_secs])
    visualThread.setDaemon(True)

    # start audio analysis thread 
    audioThread = Thread(target=update_audio_data, args=[audio_fname, plot_handle, mpos_source, audio_play, duration_secs])
    audioThread.setDaemon(True)
    print("AUDIO THREAD LIVE", audioThread.is_alive())


    def callback(audioThread, visualThread, audio_play, *events):
        for event in events:
            if event.name == 'value':
                new_time = (event.new / 100.0) * 30.0
                audio_perc = int((audio.time / 30.0) * 100.0)
                if (abs(event.new - event.old) > 1): 

                    audio.time = new_time 
                    audio.paused = True 
                    player.pause()
            elif event.name == 'direction':
                info_pane.object = 'DIRECTION' 
                if (event.new == 1):
                    info_pane.object = 'HERE' 
                    audio.paused = False
                    audio.autoplay = True
                    if (audioThread.is_alive() == False):
                        audioThread.start()
                    if (visualThread.is_alive() == False):
                        visualThread.start()
                    audio_play.set()
                elif (event.new ==0): 
                    audio.paused = True
                    audio.autoplay = True
                    audio_play.clear()
                    
    pn.extension()
    audio = pn.pane.Audio(audio_fname, name='Audio')
    audio.autoplay = False 
    audio.visible = False
    player = pn.widgets.Player(name='Player', start=0, end=100, value=0, loop_policy='once', interval=1000)
    info_pane = pn.pane.Markdown(object='INIT')
    player.interval = int(30.0 * 1000.0 / 100.0)
    
    
    watcher = player.param.watch(partial(callback,audioThread,visualThread,audio_play), ['value','direction'], onlychanged=True)
    # display(info_pane)
    display(info_pane)
    display(player)
    display(audio)
    
    # start html audio playback 
    #s = '<audio id="myaudio" src="' + os.path.basename(audio_fname) + '" preload="auto"></audio>'
    #ipd.display(ipd.HTML(s))
    
    













    
