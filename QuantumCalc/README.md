# QuantumCalc
**Precision in Every Calculation.**

A Python desktop scientific calculator with a premium dark interface, safe expression parsing, calculation history, memory controls, DEG/RAD modes, and unit conversion.

## Requirements
- Windows 10/11
- Python 3.10+
- Internet only for installing the UI dependency; calculations work offline.

## Setup (Windows PowerShell)
```powershell
cd path\to\QuantumCalc
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

If PowerShell blocks activation, run this once in the current terminal:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Features
- Standard arithmetic, percentages, brackets, sign toggle and answer reuse
- Scientific functions: trigonometry and inverse trigonometry, hyperbolic functions, logarithms, roots, powers, factorial, absolute value, constants π and e
- DEG/RAD angle mode
- Memory: MC, MR, M+, M-
- SQLite-backed calculation history
- Length, mass, temperature, area and volume conversion
- Keyboard input and safe AST-based expression evaluation (no `eval`)
- Automated tests

## Run tests
```powershell
python -m pytest
```

## Notes
- Trigonometric functions use the selected angle mode.
- `log(x)` means base-10 logarithm; `ln(x)` means natural logarithm.
- The calculator works with real-valued results for its standard scientific functions.
- Results are displayed with a readable precision policy; calculations retain Python's numeric precision internally.
- No software can guarantee zero errors for every possible input. QuantumCalc validates supported expressions and reports invalid operations rather than crashing.
