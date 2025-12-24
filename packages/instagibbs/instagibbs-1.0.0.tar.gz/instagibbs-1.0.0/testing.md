
run

```
solara run instagibbs\web\app.py
```


```python
cache_dir = Path(r"C:\Users\jhsmi\repos\mine\HDX-MS-datasets-private\datasets")
vault = DataVault(cache_dir=cache_dir)

import pandas as pd

DATABASE_DF = pd.read_csv(cache_dir / "index.csv")
```

a = solara.reactive(1)
b = solara.reactive(2)


@solara.lab.computed
def my_result():
