# Copyright 2021 University of Nottingham Ningbo China
# Author: Filippo Savi <filssavi@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
from scipy import signal
import matplotlib.pyplot as plt


def plot_response(taps, fs):
    w, h = signal.freqz(taps, [1], worN=2000, fs=fs)
    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.set_ylim(-80, 5)
    ax.grid(True)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Gain (dB)')
    ax.set_title("comparison")
    plt.show()
class FilterDesigner:

    @staticmethod
    def build_filter(filter_parameters: dict):
        fs = filter_parameters["sampling_frequency"] * 4
        if filter_parameters["type"] == "lp":
            taps = FilterDesigner.build_lp(filter_parameters)
        elif filter_parameters["type"] == "hp":
            taps = FilterDesigner.build_hp(filter_parameters)
        elif filter_parameters["type"] == "bp":
            taps = FilterDesigner.build_bp(filter_parameters)
        elif filter_parameters["type"] == "bs":
            taps = FilterDesigner.build_bs(filter_parameters)
        else:
            raise ValueError("Unknown filter type")

        fs = filter_parameters["sampling_frequency"]
        plot_data = signal.freqz(taps, [1], worN=2000, fs=fs)
        freq = np.squeeze(plot_data[0]).tolist()
        resp = 20 * np.log10(np.abs(plot_data[1])).tolist()
        taps = taps.tolist()
        return taps, {"frequency": freq, "response": resp}

    @staticmethod
    def build_lp(filter_parameters: dict):
        fs = filter_parameters["sampling_frequency"]
        pass_band = filter_parameters["pass_band_edge_1"]
        stop_band = filter_parameters["stop_band_edge_1"]

        n_taps =  filter_parameters["n_taps"]+1
        bands = [0, pass_band, stop_band, 0.5 * fs]
        desired = [1, 1, 0, 0]
        return signal.firls(n_taps, bands, desired, fs=fs)

    @staticmethod
    def build_hp(filter_parameters: dict):
        fs = filter_parameters["sampling_frequency"]
        pass_band = filter_parameters["stop_band_edge_1"]
        stop_band = filter_parameters["pass_band_edge_1"]

        n_taps = filter_parameters["n_taps"]+1
        bands = [0, stop_band, pass_band, 0.5 * fs]
        desired = [0, 0, 1, 1]
        return signal.firls(n_taps, bands, desired, fs=fs)

    @staticmethod
    def build_bp(filter_parameters: dict):
        fs = filter_parameters["sampling_frequency"]
        pass_band_1 = filter_parameters["pass_band_edge_1"]
        stop_band_1 = filter_parameters["stop_band_edge_1"]

        pass_band_2 = filter_parameters["pass_band_edge_2"]
        stop_band_2 = filter_parameters["stop_band_edge_2"]

        n_taps = filter_parameters["n_taps"]+1
        bands = [0, stop_band_1, pass_band_1, pass_band_2,stop_band_2, 0.5 * fs]
        desired = [0, 0, 1, 1, 0, 0]
        return signal.firls(n_taps, bands, desired, fs=fs)

    @staticmethod
    def build_bs(filter_parameters: dict):
        fs = filter_parameters["sampling_frequency"]
        pass_band_1 = filter_parameters["pass_band_edge_1"]
        stop_band_1 = filter_parameters["stop_band_edge_1"]

        pass_band_2 = filter_parameters["pass_band_edge_2"]
        stop_band_2 = filter_parameters["stop_band_edge_2"]

        n_taps =  filter_parameters["n_taps"]+1
        bands = [0, pass_band_1, stop_band_1, stop_band_2,pass_band_2, 0.5 * fs]
        desired = [1, 1, 0, 0, 1, 1]

        return signal.firls(n_taps, bands, desired, fs=fs)
