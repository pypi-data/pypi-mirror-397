# autopolicy

```python
import pandas as pd
from autogluon.tabular import TabularPredictor
from autopolicy import AutoPolicy

train = pd.DataFrame({
    "amount": [100, 220, 80, 160, 300],
    "x1": [0.4, -0.1, 0.9, 0.2, -0.6],
    "x2": [2.1, 1.8, 2.9, 2.3, 1.4],
    "label": [1, 0, 1, 1, 0],
})

predictor = TabularPredictor(label="label", problem_type="binary").fit(train)

auto = AutoPolicy(
    predictor=predictor,
    label="label",
    bin_col="amount",
    n_jobs=-1,
)

policy = auto.fit(train)
decisions = policy.apply(train)  # Series with {1, 0, -1}
policy.save("artifacts/policy")
```