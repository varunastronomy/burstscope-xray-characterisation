#!/usr/bin/python3

import os
import readline
from astropy.io import fits
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector

plt.rcParams["font.family"] = "Times New Roman"

# ----------------- Tab completion for filenames -----------------
def completer(text, state):
    # List files in CWD starting with 'text'
    options = [f for f in os.listdir('.') if f.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

# Input file with tab-completion
input_file = input("Enter the burst lightcurve: ")

# ----------------- Load FITS file -----------------
with fits.open(input_file, memmap=False) as hdul:
    data = hdul[1].data
    timezero = hdul[1].header.get("TIMEZERO", 0)
    gti_header = hdul[2].header

# Extract time, rate, error
TIME = data["TIME"].byteswap().newbyteorder()
RATE = data["RATE"].byteswap().newbyteorder()
ERROR = data["ERROR"].byteswap().newbyteorder()

selected_data = pd.DataFrame(columns=["TIME", "RATE", "ERROR"])

# ----------------- Interactive plot -----------------
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

ax1.errorbar(TIME, RATE, yerr=ERROR, fmt=".", markersize=2)
ax1.set_ylabel("Intensity (Counts/s)", fontsize=16)


def plot_burst_data(df):
    ax2.errorbar(
        df["TIME"], df["RATE"], yerr=df["ERROR"], fmt=".", markersize=2, color="purple"
    )
    plt.draw()


def onselect(vmin, vmax):
    mask = (TIME >= vmin) & (TIME <= vmax)
    selected_time = TIME[mask]
    selected_rate = RATE[mask]
    selected_error = ERROR[mask]

    ax2.clear()
    ax2.errorbar(selected_time, selected_rate, yerr=selected_error, fmt=".", markersize=2)
    ax2.set_xlabel("Time", fontsize=16)
    ax2.set_ylabel("Intensity (Counts/s)", fontsize=16)
    ax2.set_title("Selected Data", fontsize=16, color="purple")
    plt.draw()

    global selected_data
    selected_data = pd.DataFrame(
        {"TIME": selected_time, "RATE": selected_rate, "ERROR": selected_error}
    )

    plot_burst_data(selected_data)


span_selector = SpanSelector(ax1, onselect, "horizontal", useblit=True)

ax1.tick_params(axis="both", which="both", direction="in", width=1, length=4)
ax1.tick_params(axis="both", which="both", length=6, top=True, right=True)
ax2.tick_params(axis="both", which="both", direction="in", width=1, length=4)
ax2.tick_params(axis="both", which="both", length=6, top=True, right=True)

plt.show()

# ----------------- Burst Analysis -----------------
max_rate = selected_data["RATE"].max()
max_rate_index = selected_data["RATE"].idxmax()
max_rate_time = selected_data.loc[max_rate_index, "TIME"]

pre_max = selected_data.iloc[: max_rate_index + 1]
post_max = selected_data.iloc[max_rate_index:]

# --- Burst Onset (Two–Stage Method) ---
threshold = 0.25 * max_rate

# Stage 1: last bin below threshold (search backwards), then step forward
below_thresh_indices = pre_max.index[pre_max["RATE"] < threshold]
if not below_thresh_indices.empty:
    last_below_index = below_thresh_indices.max()
    candidate_start_index = last_below_index + 1
else:
    candidate_start_index = pre_max.index.min()

candidate_start_time = pre_max.loc[candidate_start_index, "TIME"]

# Stage 2: search 15 s earlier for superexpansion
background = RATE[:100].mean()  # pre-burst background
background_std = RATE[:100].std()

time_window_mask = (pre_max["TIME"] >= candidate_start_time - 15) & (
    pre_max["TIME"] < candidate_start_time
)
superexp_window = pre_max[time_window_mask]

superexp_candidates = superexp_window[
    (superexp_window["RATE"] >= background + 3.5 * background_std)
    & (superexp_window["RATE"] >= 0.10 * max_rate)
]

if not superexp_candidates.empty:
    start_rate_index = superexp_candidates.index.min()
else:
    start_rate_index = candidate_start_index

start_time = pre_max.loc[start_rate_index, "TIME"]
start_rate = pre_max.loc[start_rate_index, "RATE"]

# --- Peak ---
peak_rate_index = pre_max.index[pre_max["RATE"] >= 0.9 * max_rate].min()
peak_time = pre_max.loc[peak_rate_index, "TIME"]
peak_rate = pre_max.loc[peak_rate_index, "RATE"]

# --- E-folding ---
efolding_rate_condition = (1 / np.e) * max_rate
efolding_rate_index = post_max.index[post_max["RATE"] <= efolding_rate_condition].min()
efolding_time = post_max.loc[efolding_rate_index, "TIME"]
efolding_rate = post_max.loc[efolding_rate_index, "RATE"]

# --- Stop ---
stop_rate_condition = threshold
stop_rate_index = post_max.index[post_max["RATE"] <= stop_rate_condition].min() + 1
stop_time = post_max.loc[stop_rate_index, "TIME"]
stop_rate = post_max.loc[stop_rate_index, "RATE"]

# --- Timescales ---
rise_time = peak_time - start_time
burst_efolding_time = efolding_time - max_rate_time

# --- Segments ---
start_data = selected_data.loc[start_rate_index : peak_rate_index - 1]
peak_data = selected_data.loc[peak_rate_index : max_rate_index - 1]
efolding_data = selected_data.loc[max_rate_index : efolding_rate_index - 1]
stop_data = selected_data.loc[efolding_rate_index:stop_rate_index]

# --- Results ---
result_string = (
    f"Burst start time t = {start_time} s --- Countrate = {start_rate} counts/s\n\n"
    f"Burst peak time t = {peak_time} s --- Countrate = {peak_rate} counts/s\n\n"
    f"Burst rise time t = {rise_time} s\n\n"
    f"Burst max time t = {max_rate_time} --- Countrate = {max_rate} counts/s\n\n"
    f"Burst e-fold time t = {efolding_time} s --- Countrate = {efolding_rate} counts/s\n\n"
    f"Burst e-folding time = {burst_efolding_time} s\n\n"
    f"Burst end time t = {stop_time} s"
)

print(result_string)

with open("Burst_characteristics.txt", "w") as file:
    file.write(result_string)

# ----------------- Plot annotated burst -----------------
def plot_with_error_bars(data, label, ecolor):
    if not data.empty:
        plt.errorbar(
            data["TIME"],
            data["RATE"],
            yerr=data["ERROR"],
            label=label,
            color="black",
            ecolor=ecolor,
            markersize=1,
            fmt=".",
            alpha=0.5,
        )


plot_with_error_bars(start_data, "Start Data", "blue")
plot_with_error_bars(peak_data, "Peak Data", "green")
plot_with_error_bars(efolding_data, "Efolding Data", "red")
plot_with_error_bars(stop_data, "Stop Data", "purple")

plt.xlabel("Time")
plt.ylabel("Intensity (Counts/s)")
legend_labels = [f"Rise time: {rise_time} s", f"Burst Efolding Time: {burst_efolding_time} s"]
plt.legend(legend_labels)
plt.savefig("Burst_characteristics.png")

# ----------------- GTI and FITS outputs -----------------
start_time_gti = start_time + timezero
stop_time_gti = stop_time + timezero

with open("Burst_gti", "w") as gti_file:
    gti_file.write(f"{start_time_gti}\t{stop_time_gti}")

primary_hdu = fits.PrimaryHDU()
gti_hdu = fits.BinTableHDU.from_columns(
    [
        fits.Column(name="START", format="D", array=[start_time_gti]),
        fits.Column(name="STOP", format="D", array=[stop_time_gti]),
    ],
    header=gti_header,
    name="GTI",
)

hdu_list = fits.HDUList([primary_hdu, gti_hdu])
hdu_list.writeto("Burst_gti.fits", overwrite=True)

plt.show()
