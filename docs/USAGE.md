# Usage guide

## Requirements

- Python 3.10 or newer
- A desktop session capable of displaying Matplotlib windows
- A screened FITS light curve matching the structure described in the README

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the program

```bash
python Final_burst_characteristics.py
```

At the prompt, enter the input FITS light-curve path. Tab completion is enabled for files in the current directory.

## Select the analysis interval

1. Inspect the complete light curve in the upper panel.
2. Drag horizontally across an interval containing pre-burst, burst, and post-burst emission.
3. Confirm the selected data in the lower panel.
4. Repeat the selection if necessary.
5. Close the interactive window to calculate the landmarks and write the outputs.

Run the program from a dedicated results directory if you want its four fixed-name outputs kept separately from other analyses.

## Reading the outputs

`Burst_characteristics.txt` reports the accepted start, peak, maximum, e-folding, and end landmarks together with rise and e-folding times. `Burst_characteristics.png` provides the visual quality-control product. `Burst_gti` and `Burst_gti.fits` contain the interval after applying `TIMEZERO`.

Always inspect the plot before using the numerical values in a scientific result.

## Troubleshooting

### No graphical window appears

The program requires an interactive Matplotlib backend. Run it inside a graphical desktop session rather than a non-interactive remote shell, or configure X forwarding where appropriate.

### A required column or extension is missing

Confirm that the file is a light-curve product containing `TIME`, `RATE`, and `ERROR` in HDU 1 and a GTI-compatible header in HDU 2.

### A threshold is never crossed

The selected interval may not include enough pre-burst or post-burst context, or the event morphology may not satisfy the operational definitions. Expand or reconsider the interval and inspect the light curve; do not force a numerical result.

### Existing output files are present

The FITS GTI is overwritten by design. Other fixed-name outputs are also replaced when opened for writing or saved. Move valuable earlier products or run each analysis in a separate directory.
