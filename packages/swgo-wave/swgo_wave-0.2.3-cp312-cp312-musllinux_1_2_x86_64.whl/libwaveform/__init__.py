# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from .libwaveform import *

import libwaveform as libwf
import importlib.resources as imp_r
import yaml
import numpy as np
from typing import Any

def make_flashcam() -> FlashCam:
    """
    Creates a FlashCam instance with the default settings.

    Returns
    -------
    FlashCam
        a FlashCam instance with the default settings
    """
    # load yaml from package
    files = imp_r.files(libwf)
    with imp_r.as_file(files.joinpath("flashcam.yaml")) as sf:
        with open(sf, 'r') as f:
            settings = yaml.safe_load(f)
    # update seed if -1
    if settings['seed'] == -1:
        import time # use time because numpy random is not available
        settings['seed'] = int((time.time() % 1) * 1e6)
    # move files to temp dir
    import tempfile
    with tempfile.NamedTemporaryFile("w") as amp, tempfile.NamedTemporaryFile("w") as time, tempfile.NamedTemporaryFile("w") as pulse:
        # copy file contents
        with imp_r.as_file(files.joinpath(settings['amplitude_spectrum'])) as sf:
            with open(sf,'r') as f:
                amp.write(f.read())
                amp.flush()
        with imp_r.as_file(files.joinpath(settings['time_spectrum'])) as sf:
            with open(sf,'r') as f:
                time.write(f.read())
                time.flush()
        with imp_r.as_file(files.joinpath(settings['pulse_shape'])) as sf:
            with open(sf,'r') as f:
                pulse.write(f.read())
                pulse.flush()
        # update settings
        settings['amplitude_spectrum'] = amp.name
        settings['time_spectrum'] = time.name
        settings['pulse_shape'] = pulse.name
        # create instance
        fc = FlashCam(**settings)
    return fc


def get_flashcam_settings() -> dict[str, Any]:
    """
    Gets the default FlashCam settings.
    These settings are used by `make_flashcam()`.

    Returns
    -------
    dict
        a dictionary containing the default FlashCam settings
    """
    files = imp_r.files(libwf)
    with imp_r.as_file(files.joinpath("flashcam.yaml")) as sf:
        with open(sf, 'r') as f:
            settings = yaml.safe_load(f)
    return settings


def get_amplitude_spectrum() -> tuple[np.ndarray, np.ndarray]:
    """
    Gets the default amplitude spectrum for FlashCam.

    Returns
    -------
    tuple of float arrays
        amplitude and probability arrays
    """
    # get settings
    settings = get_flashcam_settings()
    # load amplitude spectrum
    files = imp_r.files(libwf)
    with imp_r.as_file(files.joinpath(settings['amplitude_spectrum'])) as sf:
        data = np.loadtxt(sf, unpack=True)
    return data[0], data[1]


def get_time_spectrum() -> tuple[np.ndarray, np.ndarray]:
    """
    Gets the default time spectrum for FlashCam.
    The times are in seconds.

    Returns
    -------
    tuple of float arrays
        time and probability arrays
    """
    # get settings
    settings = get_flashcam_settings()
    # load time spectrum
    files = imp_r.files(libwf)
    with imp_r.as_file(files.joinpath(settings['time_spectrum'])) as sf:
        data = np.loadtxt(sf, unpack=True)
    return data[0], data[1]


def get_pulse_shape() -> tuple[np.ndarray, np.ndarray]:
    """
    Gets the default pulse shape for FlashCam.
    The times are in seconds.

    Returns
    -------
    tuple of float arrays
        time and amplitude arrays
    """
    # get settings
    settings = get_flashcam_settings()
    # load pulse shape
    files = imp_r.files(libwf)
    with imp_r.as_file(files.joinpath(settings['pulse_shape'])) as sf:
        data = np.loadtxt(sf, unpack=True)
    return data[0], data[1]


def make_multipmt() -> MultiPMT:
    """
    Creates a MultiPMT instance with the default settings.

    Returns
    -------
    MultiPMT
        a MultiPMT instance with the default settings
    
    Notes
    -----
    Currently uses the FlashCam default settings, this will be updated in the future.
    """
    # load yaml from package
    files = imp_r.files(libwf)
    with imp_r.as_file(files.joinpath("multipmt.yaml")) as sf:
        with open(sf, 'r') as f:
            settings = yaml.safe_load(f)
    # update seed if -1
    if settings['seed'] == -1:
        import time # use time because numpy random is not available
        settings['seed'] = int((time.time() % 1) * 1e6)
    # move files to temp dir
    import tempfile
    with tempfile.NamedTemporaryFile("w") as amp, tempfile.NamedTemporaryFile("w") as time, tempfile.NamedTemporaryFile("w") as adc_pulse:
        # copy file contents
        with imp_r.as_file(files.joinpath(settings['amplitude_spectrum'])) as sf:
            with open(sf,'r') as f:
                amp.write(f.read())
                amp.flush()
        with imp_r.as_file(files.joinpath(settings['time_spectrum'])) as sf:
            with open(sf,'r') as f:
                time.write(f.read())
                time.flush()
        with imp_r.as_file(files.joinpath(settings['adc_pulse_shape'])) as sf:
            with open(sf,'r') as f:
                adc_pulse.write(f.read())
                adc_pulse.flush()
        # update settings
        settings['amplitude_spectrum'] = amp.name
        settings['time_spectrum'] = time.name
        settings['adc_pulse_shape'] = adc_pulse.name
        settings['tot_pulse_shape'] = adc_pulse.name # TODO separate TOT pulse shape
        # create instance
        mpm = MultiPMT(**settings)
    return mpm