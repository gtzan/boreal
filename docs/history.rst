.. include:: ../HISTORY.rst

HISTORY
=======


Motivation
----------

The project was started in 2020 by George Tzanetakis to support the
teaching of music information retrieval (MIR) using Jupyter
notebooks. Jupyter notebooks support exploratory programming and are
great for explaining concepts.  When describing MIR algorithms it is
common practice and very useful to show various plots that convey
different types of information about the underyling audio signal.
Examples of such plots include time domain waveform, spectrograms,
and volume meters. Python (and the associated Jupyter notebooks) have
excellent support for plotting with well established libraries such as
Matplotlib and Bokeh. When they are used with audio the common
practice is to show the plot and then have an audio player under it in
order to hear the audio. The plot is static and not affected when the
audio is playing. 

A common alternative is to use any of the plethora of audio viewing
and editing programs available such as the Sonic Visualizer, Audacity,
or Reaper but these typically only provide a fixed set of possible
visualizations. It is also possible to build custom reactive visualizations
using gaming or audio software frameworks such as Juce or Unity but
similarly to using external software, such tools are not integrated
with the workflow of using Jupyter notebooks.

Boreal (**Bo**\ keh **Re**\ active **A**\ udio Widget **L**\ ibrary)
was created to facilitate the creation of custom audio reactive visualizations
that integrate nicely with the workflow of using Jupyter notebooks including
scenarios in which the notebook is hosted on a remote machine.





