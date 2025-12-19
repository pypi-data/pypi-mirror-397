# 🏎️ Monaco Report – F1 Monaco 2018 Qualification Report

This package builds a report on the results of the **first qualifying session (Q1)** of the 2018 Formula 1 Monaco Grand Prix.

## 📌 Task

- Input files:
  - `start.log` – the start time of the best lap for each driver.
  - `end.log` – the end time of the best lap.
  - `abbreviations.txt` – mapping of driver abbreviations to full names and teams.

**Example line in `start.log`:**

- `SVF` — driver's abbreviation  
- `2018-05-24` — date  
- `12:02:58.917` — time

## ⚙️ Installation

### Install locally (development mode)

```bash```
pip install -e .

### Install from PyPi
pip install -i https://test.pypi.org/simple/ monaco-f1-report


## 🚀 Usage examples

### Run from source
python -m monaco_report --files data --asc

### Run after installation
monaco-report --files data --asc

### Show specific driver
monaco-report --driver "Sebastian Vettel"

### How to use test:
pytest -v



### Output example:
1. Daniel Ricciardo   | RED BULL RACING TAG HEUER | 1:12.013
2. Sebastian Vettel   | FERRARI                   | 1:12.415
3. ...

------------------------------------------------------------------------

14. Brendon Hartley   | SCUDERIA TORO ROSSO HONDA | 1:13.179
15. Marcus Ericsson   | SAUBER FERRARI            | 1:13.265

## 📖 License
MIT License
