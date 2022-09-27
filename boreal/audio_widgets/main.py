import argparse
from os.path import dirname, join
from threading import Thread, Event
import sys

from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox, gridplot
from bokeh.models import ColumnDataSource, Slider, Div, Button, FileInput 
from bokeh.events import Tap 

from audio_widgets import Time_Waveform, Spectrum, CircularEq, WaveformEnvelope
from audio_widgets import WaveformEnvelope, Centroid


import audio
import IPython.display as ipd
import time


audioThread_ = None 
audio_thread_started_ = False
visualize_callback_active_ = False 
callback_id_ = None 

def update():
    """
    Periodic callback for updating all visualizations
    of all the audio widgets
    """
    
    # add the gain value of the slider to the data 
    #audio.data['gain'] = gain.value 

    # update the visualizers with the features extracted from
    # the audio analysis and playback thread
    for k, v in audio_widgets_.items():
        v.update(audio.data)

def create_audio_widgets(audio_file_name):
    """
    Create the audio widgets that will be used for
    the reactive visualizations.
    """
    
    audio_widgets = {} 
    audio_widgets['spectrum'] = Spectrum()
    audio_widgets['time_waveform'] = Time_Waveform()
    audio_widgets['waveform_envelope'] = WaveformEnvelope(audio_file_name, waveform_click_detected)
    audio_widgets['circulareq'] = CircularEq()
    audio_widgets['centroid'] = Centroid() 
    return audio_widgets 



def file_input_handler(attr, old, new):
    """
    Handler that gets called when the user chooses a file
    Args:
        attr: 
        old: the old value of the file
        new: the new value of the file 
    """ 
    
    print('File input handler')
    print(file_input.filename)
    global audio_file_name_ 
    audio_file_name_  = file_input.filename
    
    
def play_handler():
    """
    Gets called when the play button is pressed
    and starts the audio playback
    """
    
    global callback_id_
    global audio_playing_
    global audio_thread_started_
    global visualize_callback_active_
    
    audio_close.clear()
    audio_playing_ = True
    if not audio_thread_started_:
        start_audio_thread(audio_file_name_)
        audio_thread_started_ = True

    if args.playback_mode == "html":
        s1 = "document.getElementById('myaudio').play();"
        ipd.display(ipd.Javascript(s1))
    audio_play.set()

    if (visualize_callback_active_ is False):
        callback_id_ = curdoc().add_periodic_callback(update, 60)
    visualize_callback_active_ = True


def pause_handler():
    """
    Pause the audio playback
    """
    global audio_playing_
    audio_playing_ = False
    if args.playback_mode == "html":
        s1 = "document.getElementById('myaudio').pause();"
        ipd.display(ipd.Javascript(s1))
    audio_play.clear()


def close_handler():
    """
    Stop the audio thread and the visualization callback
    """

    curdoc().remove_periodic_callback(callback_id_)
    if args.playback_mode == "html":
        s1 = "document.getElementById('myaudio').pause();"
        ipd.display(ipd.Javascript(s1))
    audio_play.clear()
    audio_close.set()
    global audioThread_
    if audioThread_:
        audioThread_.join
    global audio_thread_started_
    audio_thread_started_ = False
    audio_play.set()


def waveform_click_detected(event):
    """
    Seek a particular audio location based on event

    Args:
    event: contains the x,y coordinates of the mouse click in data
    coordinates
    """

    if args.playback_mode == "html":
        s1 = "document.getElementById('myaudio').currentTime = "
        + str(event.x) + ";"
        ipd.display(ipd.Javascript(s1))
    audio.set_current_time(event.x)
    audio_seek.set()


def start_audio_thread(audio_file_name):
    """
    Start the audio thread
    Args:
    audio_file_name (str): the audio file from which to read the samples
    """
    global audio_thread_started_
    audio_thread_started_ = True
    global audioThread_
    audioThread_ = Thread(target=audio.update_audio_data,
                          args=(audio_file_name,
                                args.playback_mode,
                                audio_play,
                                audio_close,
                                audio_seek))
    audioThread_.setDaemon(True)
    audioThread_.start()


audio_playing_ = False
parser = argparse.ArgumentParser()
parser.add_argument("audio_file_name",
                    type=str,
                    help="the audio file name"
                    )
parser.add_argument("playback_mode",
                    type=str,
                    choices=['pyaudio', 'html'],
                    default='pyaudio',
                    help="The playback mode. One of ['pyaudio', 'html']"
                    )
parser.add_argument("widgets",
                    nargs='+',
                    default=[],
                    choices=['time_waveform',
                             'spectrum',
                             'circulareq',
                             'waveform_envelope',
                             'centroid'],
                    help="The audio widget names."
                    )
args = parser.parse_args()
audio_file_name_ = args.audio_file_name

# preload the audio for html playback
if args.playback_mode == "html":
    s = '<audio id="myaudio" src="'
    + audio_file_name_ + '" preload="auto"></audio>'
    ipd.display(ipd.HTML(s))


# create visualizers
audio_widgets_ = create_audio_widgets(audio_file_name_)

# start audio thread - audio_play event controls play/pause
audio_play = Event()
audio_close = Event()
audio_seek = Event()


control_grid = []
# setup some sliders for controlling the widgets
max_freq = 22050
#freq = Slider(start=1, end=max_freq, value=max_freq, step=1, title="Frequency")
#gain = Slider(start=1, end=20, value=1, step=1, title="Gain")

#sound_control = [gain, freq]
#control_grid.append(sound_control)

# setup playback widgets
play_button = Button(label="Play", button_type="success")
pause_button = Button(label="Pause", button_type="success")
close_button = Button(label="Close", button_type="success")

playback_control = [play_button, pause_button, close_button]
play_button.on_click(play_handler)
pause_button.on_click(pause_handler)
close_button.on_click(close_handler)
control_grid.append(playback_control)


file_input_ = FileInput(accept=".wav")
file_input_.on_change('filename', file_input_handler)


# setup the document
filename = join(dirname(__file__), "description.html")
desc = Div(text=open(filename).read(), render_as_text=False, width=1000)
curdoc().add_root(desc)
curdoc().add_root(gridplot(control_grid))

# make a column of desired widgets
plots = [audio_widgets_[x].get_plot() for x in args.widgets]
#for p in plots: 
#    p.on_event(Tap, waveform_click_detected)

plot_column = column(plots)
curdoc().add_root(plot_column)
curdoc().add_root(file_input_)
