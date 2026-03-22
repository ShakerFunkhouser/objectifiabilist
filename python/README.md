# objectifiabilist

Python implementation of [Objectifiabilism](https://github.com/ShakerFunkhouser/objectifiabilist), a constructivist metaethical framework that makes implicit moral priorities explicit, auditable, and comparable.

## Install

```bash
pip install git+https://github.com/ShakerFunkhouser/objectifiabilist.git#subdirectory=objectifiabilist/python
```

## Quick start

```python
from objectifiabilist import (
    QualitativeMagnitude, QualitativePreferability,
    calculate_all_moral_valences, calculate_preferabilities,
    calculate_divergence_signal, evaluate_sejp_output,
)
```

See the [worked example notebook](../sejp_demo.ipynb) for a full demonstration.
