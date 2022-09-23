

from math import ceil
import numpy as np
import soundfile as sf
from bokeh.models import ColumnDataSource, LabelSet
from bokeh.plotting import figure
from bokeh.events import Tap
import audio


class WaveformEnvelope:

    def __init__(self, fname, time_range=46):
        print('Waveform Envelop INIT') 
        plotargs = dict(tools="", toolbar_location=None, outline_line_color='#595959')

        self.fname = fname
        isf = sf.SoundFile(fname, 'r')
        audio, srate = sf.read(fname)
        max_envelope = self.process(audio, 4096, block_process=self.max_absolute)
        time = np.linspace(0, len(audio) / srate, num=len(max_envelope))

        self.signal_source_pos = ColumnDataSource(data=dict(t=[], y=[]))
        self.signal_source_neg = ColumnDataSource(data=dict(t=[], y=[]))
        self.signal_plot = figure(plot_width=1000, plot_height=350,
                                  title="Signal",
                                  x_range=[0, time[-1] + 30],
                                  y_range=[-1.25, 1.25],
                                  x_axis_label='Time(secs)',
                                  y_axis_label='Amplitude', **plotargs)
        self.signal_plot.background_fill_color = "#eaeaea"

        self.signal_plot.vbar(x=time, bottom=-max_envelope,
                              top=max_envelope,
                              width=1.0 / len(time),
                              fill_color='gray',
                              fill_alpha=1.0)

        self.duration = len(audio) / srate
        self.length = len(max_envelope)        

        time = 0.0
        t = np.linspace(0, self.duration, self.length)
        y = np.zeros(len(t))

        self.signal_plot.line(x="t", y="y", line_color="green",
                              source=self.signal_source_pos, line_width=3.0)
        self.signal_plot.line(x="t", y="y", line_color="green",
                              source=self.signal_source_neg, line_width=3.0)

        # self.signal_plot.line(time, max_envelope, color='black', line_width=0.5, line_alpha=0.5)
        # self.signal_plot.line(time, -max_envelope, color='black', line_width=0.5, line_alpha=0.5)

        # self.signal_plot.on_event(Tap, tap_detected)
        



    def max_absolute(self, block):
        return np.max(np.abs(block))

    def process(self, signal, hopSize, block_process):
        winSize = hopSize
        offsets = np.arange(0, len(signal), hopSize)
        amp_track = np.zeros(len(offsets))
        for (m, o) in enumerate(offsets):
            frame = signal[o:o + winSize]
            amp_track[m] = block_process(frame)
        return amp_track

    def update(self, data):
        time = data['time']

        t = np.linspace(0, self.duration, self.length)
        y = np.zeros(len(t))
        if time is None:
            pass
        else:
            position = (time / self.duration) * self.length
            y[int(position)] = 1.5
            self.signal_plot.title.text = "Waveform Envelope\t" + self.fname

            self.signal_source_pos.data = dict(t=t, y=y)
            self.signal_source_neg.data = dict(t=t, y=-y)

 
            
    def get_plot(self):
        return self.signal_plot


class Time_Waveform:
    def __init__(self, time_range=46):
        plotargs = dict(tools="", toolbar_location=None,
                        outline_line_color='#595959')
        self.signal_source = ColumnDataSource(data=dict(t=[], y=[]))
        self.signal_plot = figure(plot_width=600, plot_height=200,
                                  title="Signal",
                                  x_range=[0, time_range],
                                  y_range=[-0.8, 0.8],
                                  x_axis_label='Time(msec)',
                                  y_axis_label='Amplitude', **plotargs)
        self.signal_plot.background_fill_color = "#eaeaea"
        self.signal_plot.line(x="t", y="y", line_color="#024768",
                              source=self.signal_source)

    def update(self, data):
        
        signal = data['signal']
        time = data['time']
        gain = data['gain']

        if signal is None:
            pass 
        else:
            t = np.linspace(0, 100, len(signal))            
            self.signal_source.data = dict(t=t, y=signal * gain)
            self.signal_plot.title.text = "Time Domain Waveform\t" + str(time)

    def get_plot(self):
        return self.signal_plot


class Spectrum:
    def __init__(self):
        plotargs = dict(tools="", toolbar_location=None,
                        outline_line_color='#595959')
        max_freq_khz = 22050 * 0.1
        self.spectrum_source = ColumnDataSource(data=dict(f=[], y=[]))
        self.spectrum_plot = figure(plot_width=600, plot_height=200,
                                    title="Power Spectrum",
                                    y_range=[10 ** (-4), 10 ** 3],
                                    x_range=[0, max_freq_khz],
                                    y_axis_type="log", **plotargs)
        self.spectrum_plot.background_fill_color = "#eaeaea"
        self.spectrum_plot.line(x="f", y="y", line_color="#024768",
                                source=self.spectrum_source)

    def update(self, data):
        if 'spectrum' in data: 
            spectrum = data['spectrum']
        else:
            return 
            
        time = data['time']
        max_freq_khz = 22050 * 0.1
        if spectrum is None:
            pass
        else:
            f = np.linspace(0, max_freq_khz, len(spectrum))
            self.spectrum_source.data = dict(f=f, y=spectrum)
        # spectrum_plot.x_range.end = freq.value*0.001

    def get_plot(self):
        return self.spectrum_plot


class CircularEq:
    def __init__(self):
        num_bins = 16
        eq_clamp = 20
        plotargs = dict(tools="", toolbar_location=None,
                        outline_line_color='#595959')
        self.eq_range = np.arange(eq_clamp, dtype=np.float64)
        eq_angle = 2 * np.pi / num_bins

        eq_data = dict(
            inner=np.tile(self.eq_range + 2, num_bins),
            outer=np.tile(self.eq_range + 2.95, num_bins),
            start=np.hstack([np.ones_like(self.eq_range) * eq_angle * (i + 0.05) for i in range(num_bins)]),
            end=np.hstack([np.ones_like(self.eq_range) * eq_angle * (i + 0.95) for i in range(num_bins)]),
            alpha=np.tile(np.zeros_like(self.eq_range), num_bins),
        )
        self.eq_source = ColumnDataSource(data=eq_data)
        self.eq_plot = figure(plot_width=400, plot_height=400,
                              x_axis_type=None, y_axis_type=None,
                              x_range=[-20, 20], y_range=[-20, 20], **plotargs)
        self.eq_plot.background_fill_color = "#eaeaea"
        self.eq_plot.annular_wedge(x=0, y=0, fill_color="#024768",
                                   fill_alpha="alpha",
                                   line_color=None, inner_radius="inner",
                                   outer_radius="outer", start_angle="start",
                                   end_angle="end",
                                   source=self.eq_source)

    def update(self, data):
        if "bins" in data: 
            bins = data['bins']
        else:
            return 
        time = data['time']
        alphas = []
        if (bins is None):
            pass 
        else: 
            for x in bins:
                a = np.zeros_like(self.eq_range)
                N = int(ceil(x))
                a[:N] = (1 - self.eq_range[:N] * 0.05)
                alphas.append(a)
            self.eq_source.data['alpha'] = np.hstack(alphas)

    def get_plot(self):
        return self.eq_plot




class Centroid:
    def __init__(self):
        plotargs = dict(tools="", toolbar_location=None,
                        outline_line_color='#595959')

        self.centroid_source = ColumnDataSource(data=dict(t=[], y=[]))
        self.scentroid_source = ColumnDataSource(data=dict(t=[], y=[]))
        self.centroid_plot = figure(plot_width=800, plot_height=200,
                                    title="Centroid", x_range=[0, 100],
                                    y_range=[0, 200], **plotargs)
        self.centroid_plot.background_fill_color = "#eaeaea"
        self.centroid_plot.line(x="t", y="y", line_color="blue",
                                source=self.centroid_source)
        self.centroid_plot.line(x="t", y="y", line_color="red",
                                source=self.scentroid_source, line_width=3)

        self.scentroid_plot = figure(plot_width=800, plot_height=200,
                                     title="Smoothed Centroid (mean of previous 20 values)", x_range=[0, 100],
                                     y_range=[0, 200], **plotargs)
        self.scentroid_plot.background_fill_color = "#eaeaea"
        self.scentroid_plot.line(x="t", y="y", line_color="red",
                                 source=self.scentroid_source)

    def update(self, data):
        centroid_track = data['centroid_track']
        scentroid_track = data['scentroid_track']

        t = np.linspace(0, 100, len(centroid_track))
        self.centroid_source.data = dict(t=t, y=centroid_track)
        self.scentroid_source.data = dict(t=t, y=scentroid_track)

    def get_plot(self):
        return self.centroid_plot


class PitchHistogram:
    def __init__(self):
        self.histo_source = ColumnDataSource(data=dict(histo=[],
                                                       left=[],
                                                       right=[]))
        self.shisto_source = ColumnDataSource(data=dict(sx=[], sy=[]))
        plotargs = dict(tools="", toolbar_location=None,
                        outline_line_color='#595959')
        self.histo_plot = figure(plot_width=800, plot_height=200,
                                 title="Histogram", x_range=[40, 80],
                                 y_range=[0, 1.2], **plotargs)
        self.histo_plot.background_fill_color = "#eaeaea"
        self.histo_plot.quad(top="histo", bottom=0, left="left",
                             right="right", fill_color="cyan",
                             line_color="#033649", line_alpha=0.6,
                             source=self.histo_source)

        self.histo_plot.line(x="sx", y="sy", line_color='blue',
                             line_width=2, source=self.shisto_source)

        self.note_source = ColumnDataSource({
            'x_mult': [[], []],
            'y_mult': [[], []],
        })

        self.text_source = ColumnDataSource(data=dict(x=[50.0], y=[0.5],
                                                      names=['']))

        self.note_labels = LabelSet(x='x', y='y', text='names', level='glyph',
                                    x_offset=1.0, source=self.text_source)
        self.histo_plot.add_layout(self.note_labels)
        self.histo_plot.multi_line('x_mult', 'y_mult', line_color='red',
                                   line_width=2, source=self.note_source)

    def update(self, data):
        histo, edges, sx, sy = data['histo']
        notes = data['notes']
        time = data['time']
        # pitch histogram 
        self.histo_source.data = dict(histo=histo,
                                      left=edges[:-1], right=edges[1:])
        self.shisto_source.data = dict(sx=sx, sy=sy)

        # grid of red lines for autotuning scale 
        xnotes = []
        ynotes = []
        for n in notes:
            xnotes.append([n, n])
            xnotes.append([n - 12, n - 12])
            xnotes.append([n - 24, n - 24])
            xnotes.append([n - 36, n - 36])
            ynotes.append([0.0, 1.2])
            ynotes.append([0.0, 1.2])
            ynotes.append([0.0, 1.2])
            ynotes.append([0.0, 1.2])
        note_names = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']
        self.note_labels = [note_names[np.mod(n, 12)] for n in notes]
        self.note_source.data = dict(x_mult=xnotes, y_mult=ynotes)
        self.text_source.data = dict(x=notes, y=[1.0] * len(notes),
                                     names=self.note_labels)

        # show time in titles
        self.histo_plot.title.text = str(time)

    def get_plot(self):
        return self.histo_plot
