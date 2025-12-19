# API Reference

## Functions

::: gssdata.trend

::: gssdata.variables

::: gssdata.info

## Examples

### Basic Usage

```python
import gssdata

# Get available variables
for var in gssdata.variables():
    info = gssdata.info(var)
    print(f"{var}: {info['description']}")
```

### Plotting Trends

```python
import gssdata
import matplotlib.pyplot as plt

# Get data
df = gssdata.trend("NATEDUC")

# Plot
plt.figure(figsize=(10, 6))
plt.plot(df["year"], df["pct"], marker="o")
plt.xlabel("Year")
plt.ylabel("% Too Little Spending")
plt.title("Support for Education Spending (GSS)")
plt.grid(True, alpha=0.3)
plt.show()
```

### Comparing Variables

```python
import gssdata
import pandas as pd

# Compare multiple trends
vars_to_compare = ["NATEDUC", "NATHEAL", "NATENVIR"]
dfs = []
for var in vars_to_compare:
    df = gssdata.trend(var)
    df["variable"] = var
    dfs.append(df)

combined = pd.concat(dfs)
pivot = combined.pivot(index="year", columns="variable", values="pct")
print(pivot.tail())
```
