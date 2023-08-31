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


class FilterDesignEngine:

    @staticmethod
    def get_plot_data(taps: np.ndarray, fs: float):
        plot_data = signal.freqz(taps, [1], worN=2000, fs=fs)
        freq = np.squeeze(plot_data[0]).tolist()

        resp_lin = np.abs(plot_data[1])
        resp_lin_clean = resp_lin
        for idx, val in enumerate(resp_lin):
            if val < 0:
                resp_lin_clean[idx] = resp_lin[idx - 1]
        resp_db = 20 * np.log10(resp_lin)
        resp = resp_db.tolist()
        return freq, resp

    @staticmethod
    def design_filter(filter_parameters: dict):
        if filter_parameters["type"] == "lp":
            taps = FilterDesignEngine.design_lp(filter_parameters)
        elif filter_parameters["type"] == "hp":
            taps = FilterDesignEngine.design_hp(filter_parameters)
        elif filter_parameters["type"] == "bp":
            taps = FilterDesignEngine.design_bp(filter_parameters)
        elif filter_parameters["type"] == "bs":
            taps = FilterDesignEngine.design_bs(filter_parameters)
        else:
            raise ValueError("Unknown filter type")

        freq, resp = FilterDesignEngine.get_plot_data(taps, filter_parameters["sampling_frequency"])
        taps = taps.tolist()
        return taps, {"frequency": freq, "response": resp}


    @staticmethod
    def implement_filter(taps: list, n_bits: int, fs: float):
        np_taps = np.array(taps)
        scaled_taps =np_taps*2**n_bits
        np_taps_q = np.round(scaled_taps, 0)
        np_taps = np_taps_q/2**n_bits
        plot_data = signal.freqz(np_taps, [1], worN=2000, fs=fs)
        freq = np.squeeze(plot_data[0]).tolist()

        resp_lin = np.abs(plot_data[1])
        resp_lin_clean = resp_lin
        for idx, val in enumerate(resp_lin):
            if val<0:
                resp_lin_clean[idx] = resp_lin[idx-1]
        resp_db = 20 * np.log10(resp_lin_clean, where=resp_lin > 0)
        resp = resp_db.tolist()
        return np_taps_q, {"frequency": freq, "response": resp}


    @staticmethod
    def design_lp(filter_parameters: dict):
        fs = filter_parameters["sampling_frequency"]
        pass_band = filter_parameters["pass_band_edge_1"]
        stop_band = filter_parameters["stop_band_edge_1"]

        n_taps =  filter_parameters["n_taps"]+1
        bands = [0, pass_band, stop_band, 0.5 * fs]
        desired = [1, 1, 0, 0]
        return signal.firls(n_taps, bands, desired, fs=fs)

    @staticmethod
    def design_hp(filter_parameters: dict):
        fs = filter_parameters["sampling_frequency"]
        pass_band = filter_parameters["stop_band_edge_1"]
        stop_band = filter_parameters["pass_band_edge_1"]

        n_taps = filter_parameters["n_taps"]+1
        bands = [0, stop_band, pass_band, 0.5 * fs]
        desired = [0, 0, 1, 1]
        return signal.firls(n_taps, bands, desired, fs=fs)

    @staticmethod
    def design_bp(filter_parameters: dict):
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
    def design_bs(filter_parameters: dict):
        fs = filter_parameters["sampling_frequency"]
        pass_band_1 = filter_parameters["pass_band_edge_1"]
        stop_band_1 = filter_parameters["stop_band_edge_1"]

        pass_band_2 = filter_parameters["pass_band_edge_2"]
        stop_band_2 = filter_parameters["stop_band_edge_2"]

        n_taps =  filter_parameters["n_taps"]+1
        bands = [0, pass_band_1, stop_band_1, stop_band_2,pass_band_2, 0.5 * fs]
        desired = [1, 1, 0, 0, 1, 1]

        return signal.firls(n_taps, bands, desired, fs=fs)
