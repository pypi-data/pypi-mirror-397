# PepQ

![PepQ logo](https://raw.githubusercontent.com/Vivi-tran/PepQ/main/data/pepq.png)

**PepQ** — Calibrated scoring function for peptide–protein complexes.

**Install**
```bash
pip install pepq
```

**Usage**
```python
from pepq.pepq import PepQ
from pepq.io import load_json
from pepq.data import build_data

pipe = PepQ.load()
data = load_json(data_path)
data = build_data(data, None)

conf = pipe.predict_confident(data, threshold=None)
y_pred = conf.confident_predictions
```