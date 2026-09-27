# Scientific method

## Purpose

`Final_burst_characteristics.py` measures reproducible timing landmarks within a manually selected X-ray burst interval. Manual selection keeps the analyst responsible for deciding which part of the observation contains the relevant pre-burst, burst, and post-burst emission. The threshold rules then make the reported timing measurements explicit and repeatable.

## Data model

The analysis uses the `TIME`, `RATE`, and `ERROR` columns from the first FITS table extension. The supplied rates and uncertainties are assumed to have already been produced through an appropriate mission-specific reduction workflow.

The selected interval should include:

1. representative pre-burst persistent emission;
2. the full burst rise and decay; and
3. representative post-burst emission.

## Operational definitions

Let `R_max` be the maximum observed count rate within the selected interval.

### Principal start candidate

The program searches backward from the maximum for the last bin with an observed rate below `0.25 R_max`. The following bin is the principal start candidate.

### Earlier-onset search

The program examines the 15 s immediately preceding the principal start candidate. A bin is accepted as an earlier onset candidate when both conditions are met:

- its observed rate is at least the background mean plus `3.5` background standard deviations; and
- its observed rate is at least `0.10 R_max`.

The first 100 bins of the complete input light curve define the background sample. This sample must therefore represent persistent pre-burst emission for the background estimate to be meaningful.

### Peak and maximum

The peak landmark is the first pre-maximum bin reaching `0.90 R_max`. The maximum landmark is the bin containing `R_max`. The rise time is the difference between the peak-landmark time and the accepted start time.

### E-folding point

The e-folding landmark is the first post-maximum bin with an observed rate at or below `R_max/e`. The reported e-folding time is measured from the maximum to this landmark.

### Burst end

The end is set to one bin after the first post-maximum bin at or below `0.25 R_max`.

## Important interpretation boundaries

- Thresholds are applied to observed rates without subtracting the persistent level.
- These are operational timing definitions, not universal physical definitions of burst onset or duration.
- The earlier-onset search flags a rate pattern compatible with an earlier feature; it does not by itself establish superexpansion or another physical mechanism.
- The analysis does not determine whether an event is thermonuclear, accretion-driven, instrumental, or caused by background variability.
- Results depend on light-curve binning, screening, the selected interval, statistical fluctuations, and the validity of the first-100-bin background sample.
- GTI output identifies the measured interval; it does not certify data quality outside the analysis criteria.

## Review checklist

Before using a reported result, verify that:

- the input product was screened and calibrated correctly;
- the required FITS extensions and columns are present;
- the first 100 bins are suitable persistent emission;
- the selected interval contains the complete event and adequate context;
- the e-folding and end thresholds are crossed inside the selected interval; and
- the annotated plot agrees with the intended scientific interpretation.
