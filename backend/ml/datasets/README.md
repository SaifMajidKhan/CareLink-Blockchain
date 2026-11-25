# CareLink Synthetic Medication Adherence Dataset

## Dataset information

- Records: 5,000
- Input features: 8
- Target variable: non_adherent_next_7d
- Generation method: reproducible Python simulation
- Random seed: 42
- Source: CareLink synthetic dataset generator

## Target labels

- 0: Simulated adherent outcome
- 1: Simulated non-adherent outcome

## Purpose

This dataset supports the development and evaluation of
the CareLink medication adherence prediction pipeline.

The data does not contain real patient information.

## Limitations

The feature relationships and target outcomes are based
on assumed statistical relationships rather than
observed clinical outcomes.

Evaluation results demonstrate performance on synthetic
data only. The model is not clinically validated and
must not be used for medical decision-making.

## Reproduction

Run from the project root:

python -m backend.ml.generate_dataset