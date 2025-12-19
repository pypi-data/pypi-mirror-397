# safegcd

Minimal `divstep(delta, f, g)` primitive for safegcd / Bernstein–Yang style experimentation.

## Install (dev)
```bash
python -m pip install -e .
```

## Usage
```python
from safegcd import divstep
print(divstep(1, 7, 10))
```
