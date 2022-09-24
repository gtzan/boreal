======
Boreal
======


.. image:: https://img.shields.io/pypi/v/boreal.svg
        :target: https://pypi.python.org/pypi/boreal

.. image:: https://img.shields.io/travis/gtzan/boreal.svg
        :target: https://travis-ci.com/gtzan/boreal

.. image:: https://readthedocs.org/projects/boreal/badge/?version=latest
        :target: https://boreal.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status





.. image:: https://github.com/gtzan/boreal/blob/main/images/boreal_logo.png


	      
**Bo**\ keh **Re**\ active **A**\ udio Widget **L**\ ibrary


* Free software: MIT license
* Documentation: https://boreal.readthedocs.io.

Boreal is a library for creating plots that react to audio while the
audio is playing. The reactive audio widgets can be used as part of a
stand-alone Bokeh application but the primary goal of the framework is
to support the exploratory coding process when using Jupyter notebooks
for audio research.

The library is designed to be extensible and supports the addition of
new audio reactive widgets as well as audio processors that extract
information from the underlying audio signal. Playback controls can be
used to play, pause, and seek the underlying audio and associated
visuals.

Installation
------------

**Building from source**

To build boreal from source try::

  python setup.py build

Then to install::
  
  python setup.py install

If all went well, you should be able to run the following command in Python::
  
  import boreal 



Get started
-----------
To see how Boreal works try the following notebook (also part of the package):

https://github.com/gtzan/boreal/blob/main/boreal/audio_widgets_notebook.ipynb





Features
--------

* Bokeh application for audio reactive plots 
* Example audio widgets: time domain, spectrum, waveform envelope, circularEQ
* Support for both real-time computation of visuals as well as pre-computation
* Ability to use html audio for playback on a local machine when notebook
  is hosted remotely 
* Straighforward to add new audio widgets and audio processors 

TODO
====

Boreal is under development and there is a lot of additinal work planned.
Some examples include:

*  More audio widgets
*  Better documentation
*  Support for multi-channel audio 
  

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
