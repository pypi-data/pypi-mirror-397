# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from typing import Any, Sequence, Union, overload
from pathlib import Path
from numpy import ndarray

# Vector type aliases exposed by the pybind11 module
DoubleVector = list[float]
IntVector = list[int]
uint16Vector = list[int]
FlashCamTriggerVector = list["FlashCamTrigger"]
MultiPMTTriggerVector = list["MultiPMTTrigger"]


class FlashCamTrigger:
	"""A single trigger produced by :class:`FlashCam`.

	Attributes
	----------
	channel: int
		Channel number
	trigger_time_s: int
		Seconds since run start (uint32)
	trigger_time_ticks: int
		Ticks since last full second (uint32), tick = 4ns
	baseline: float
		Baseline in LSB
	intsum: float
		Waveform sum in LSB
	waveform: list[int]
		ADC samples in LSB (uint16 values represented as ints)
	"""

	channel: int
	trigger_time_s: int
	trigger_time_ticks: int
	baseline: float
	intsum: float
	waveform: uint16Vector

	def __init__(self, channel: int = 0, trigger_time_s: int = 0, trigger_time_ticks: int = 0, baseline: float = 0.0, intsum: float = 0.0, waveform: uint16Vector | None = None) -> None: ...



class FlashCam:
	"""
	Simulation of the FlashCam electronics chain.
    Simulates PMT and ADC response based on input photo electron times.
    Applies the FlashCam trigger logic to generate triggers.

	Parameters
	----------
	time_spectrum : Path
		Path to the time spectrum of the PMT
	amplitude_spectrum : Path
		Path to the amplitude spectrum of the PMT
	pmt_time_step : float
		Time step of the PMT waveform in seconds
	adc_step : float
		The time step for the ADC in seconds
	pulse_shape : Path
		Path to the pulse shape of the electronics
	jitter : int
		Offset of ADC samples relative to simulation times, 0 for no jitter, -1 for random jitter
	gain : float
		ADC gain (scale factor of normalized amplitude) in LSB
	offset : float
		ADC offset in LSB
	preamp_clip : float
		Upper bound of ADC samples before noise is applied in LSB
	noise : float
		Standard deviation of gaussian noise in LSB
	clip : float
		Upper bound of ADC samples after noise is applied in LSB
	waveform_samples : int
		number of waveform samples per trigger
	retrigger_offset : int
		minimum number of samples between two triggers
	trigger_kernel : list[int]
		kernel to convolve the waveform with before applying the threshold
	adc_threshold : int
		trigger threshold in LSB
	trigger_norm : int
		divide the trigger signal by this value before applying the threshold
	trigger_offset : int
		offset of the waveform start relative to the trigger time in number of ADC steps
	seed : int
		Random generator seed

	"""
	def __init__(
		self,
		time_spectrum: Union[str, Path],
		amplitude_spectrum: Union[str, Path],
		pmt_time_step: float,
		adc_step: float,
		pulse_shape: Union[str, Path],
		jitter: int,
		gain: float,
		offset: float,
		preamp_clip: float,
		noise: float,
		clip: float,
		waveform_samples: int,
		retrigger_offset: int,
		trigger_kernel: IntVector,
		adc_threshold: int,
		trigger_norm: int,
		trigger_offset: int,
		seed: int,
	) -> None: ...

	@overload
	def simulate(self, pe_times: Sequence[float], channel: int = 0) -> FlashCamTriggerVector: ...

	@overload
	def simulate(self, pe_times: Any, channel: int = 0) -> FlashCamTriggerVector: ...

	def simulate(self, pe_times: Any, channel: int = 0) -> FlashCamTriggerVector:
		"""Simulates the FlashCam triggers for the given PE times.

		Parameters
		----------
		pe_times : list[float] or numpy.ndarray
			A vector/array of photo electron times in seconds. The binding accepts
			either a Python sequence of floats or a numpy.ndarray of dtype float64.
		channel : int, optional
			The channel number of the PMT (default is 0)

		Returns
		-------
		list[FlashCamTrigger]
			A vector of FlashCamTrigger objects containing the simulated triggers
		"""
	
	def simulate_pe_list(self, pe_list: list[tuple[int, list[float]]]) -> FlashCamTriggerVector:
		"""Simulates the FlashCam triggers for a list of PE times per channel.
		This function is meant to directly take the output of the background simulation as input.

		Parameters
		----------
		pe_list : list of tuples
			A list where each tuple contains a channel number (int) and a list of photo electron times (list of float) in seconds.

		Returns
		-------
		list[FlashCamTrigger]
			A vector of FlashCamTrigger objects containing the simulated triggers
		"""

	def calibrate_delay(self, num_pes: int, num_sim: int) -> float:
		"""Calibrates the delay between PE times and trigger times.

		Parameters
		----------
		num_pes : int
			Number of PEs to simulate
		num_sim : int
			Number of simulations to run

		Returns
		-------
		float
			The average delay in seconds

		Raises
		------
		RuntimeError
			If too many simulations do not produce a valid trigger
		"""


def make_flashcam() -> FlashCam:
	"""
    Creates a FlashCam instance with the default settings.

    Returns
    -------
    FlashCam
        a FlashCam instance with the default settings
    """


def get_flashcam_settings() -> dict[str, Any]:
	"""
    Gets the default FlashCam settings.
    These settings are used by `make_flashcam()`.

    Returns
    -------
    dict
        a dictionary containing the default FlashCam settings
    """


def get_amplitude_spectrum() -> tuple[ndarray, ndarray]:
	"""
    Gets the default amplitude spectrum for FlashCam.

    Returns
    -------
    tuple of float arrays
        amplitude and probability arrays
    """


def get_time_spectrum() -> tuple[ndarray, ndarray]:
	"""
    Gets the default time spectrum for FlashCam.
    The times are in seconds.

    Returns
    -------
    tuple of float arrays
        time and probability arrays
    """


def get_pulse_shape() -> tuple[ndarray, ndarray]:
	"""
    Gets the default pulse shape for FlashCam.
    The times are in seconds.

    Returns
    -------
    tuple of float arrays
        time and amplitude arrays
    """

class MultiPMTTrigger:
	"""A single trigger produced by :class:`MultiPMT`.

	Attributes
	----------
	time: float
		Trigger time in seconds
	channel: int
		Channel number
	time_over_threshold: float
		Time over threshold in seconds
	adc_sample: int
		ADC sample in LSB (uint16 represented as int)
	"""

	time: float
	channel: int
	time_over_threshold: float
	adc_sample: int

	def __init__(self, time: float = 0.0, channel: int = 0, time_over_threshold: float = 0.0, adc_sample: int = 0) -> None: ...


class MultiPMT:
	"""
	Simulation of the Multi-PMT electronics chain.
	Simulates PMT, ToT and ADC response based on input photo electron times.
	Uses the ToT start time as trigger for the ADC readout.

	Parameters
	----------
	time_spectrum : Path
		Path to the time spectrum of the PMT
	amplitude_spectrum : Path
		Path to the amplitude spectrum of the PMT
	pmt_time_step : float
		Time step of the PMT waveform in seconds
	tot_step : float
		The time step of the ToT simulation TDC in seconds
	tot_pulse_shape : Path
		Path to the pulse shape of the ToT electronics
	tot_threshold : float
		The threshold for ToT measurement
	tot_dead_time : float
		The dead time for ToT measurement in seconds
	tot_noise : float
		Standard deviation of gaussian noise of the signal in the ToT simulation
	tot_jitter : float
		Standard deviation of the time measurement in seconds in the ToT simulation
	adc_step : float
		The time step for the ADC in seconds
	adc_pulse_shape : Path
		Path to the pulse shape of the ADC electronics
	adc_jitter : int
		Offset of ADC samples relative to simulation times, 0 for no jitter, -1 for random jitter
	adc_gain : float
		ADC gain (scale factor of normalized amplitude) in LSB
	adc_offset : float
		ADC offset in LSB
	adc_noise : float
		Standard deviation of gaussian noise in LSB
	adc_clip : float
		Upper bound of ADC samples after noise is applied in LSB
	sample_delay : float
		Delay of the ADC readout relative to the ToT start time in seconds
	seed : int
		Random generator seed
	"""

	def __init__(
		self,
		time_spectrum: Union[str, Path],
		amplitude_spectrum: Union[str, Path],
		pmt_time_step: float,
		tot_step: float,
		tot_pulse_shape: Union[str, Path],
		tot_threshold: float,
		tot_dead_time: float,
		tot_noise: float,
		tot_jitter: float,
		adc_step: float,
		adc_pulse_shape: Union[str, Path],
		adc_jitter: int,
		adc_gain: float,
		adc_offset: float,
		adc_noise: float,
		adc_clip: float,
		sample_delay: float,
		seed: int,
	) -> None: ...

	@overload
	def simulate(self, pe_times: Sequence[float], channel: int = 0) -> MultiPMTTriggerVector: ...

	@overload
	def simulate(self, pe_times: Any, channel: int = 0) -> MultiPMTTriggerVector: ...

	def simulate(self, pe_times: Any, channel: int = 0) -> MultiPMTTriggerVector:
		"""Simulates the MultiPMT triggers for the given PE times.

        Parameters
        ----------
        pe_times : list[float] or numpy.ndarray
			A vector/array of photo electron times in seconds. The binding accepts
			either a Python sequence of floats or a numpy.ndarray of dtype float64.
        channel : int, optional
            The channel number of the PMT

        Returns
        -------
        List[MultiPMTTrigger]
            A vector of MultiPMTTrigger objects containing the simulated triggers
		"""
	
	def simulate_pe_list(self, pe_list: list[tuple[int, list[float]]]) -> MultiPMTTriggerVector:
		"""Simulates the MultiPMT triggers for a list of PE times per channel.
		This function is meant to directly take the output of the background simulation as input.

		Parameters
		----------
		pe_list : list of tuples
			A list where each tuple contains a channel number (int) and a list of photo electron times (list of float) in seconds.

		Returns
		-------
		list[MultiPMTTrigger]
			A vector of MultiPMTTrigger objects containing the simulated triggers
		"""
		...

	def calibrate_delay(self, num_pes: int, num_sim: int) -> float:
		"""Calibrates the delay between PE times and trigger times.

		Parameters
		----------
		num_pes : int
			Number of PEs to simulate
		num_sim : int
			Number of simulations to run

		Returns
		-------
		float
			The average delay in seconds

		Raises
		------
		RuntimeError
			If too many simulations do not produce a valid trigger
		"""


def generate_pe_list(num_channels: int, pes_per_channel: int, time_interval: float) -> list[tuple[int, list[float]]]:
	"""Generates a PE list for testing purposes.

    Parameters
    ----------
    num_channels : int
        Number of channels to generate PEs for
    pes_per_channel : int
        Number of PEs per channel
    time_interval : float
        Time interval between PEs in seconds

    Returns
    -------
    List[Tuple[int, List[float]]]
        A list of tuples containing the channel number and a vector of photo electron times in seconds
	"""


__all__ = [
	"FlashCam",
	"FlashCamTrigger",
	"MultiPMT",
	"MultiPMTTrigger",
	"DoubleVector",
	"IntVector",
	"uint16Vector",
	"FlashCamTriggerVector",
	"MultiPMTTriggerVector",
]

