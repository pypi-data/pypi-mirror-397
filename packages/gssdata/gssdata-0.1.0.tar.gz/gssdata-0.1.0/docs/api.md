# API Reference

## Functions

::: gss.trend

::: gss.variables

::: gss.info

## Examples

### Basic Usage

```python
import gss

# Get available variables
for var in gss.variables():
    info = gss.info(var)
    print(f"{var}: {info['description']}")
```

### Plotting Trends

```python
import gss
import matplotlib.pyplot as plt

# Get data
df = gss.trend("HOMOSEX")

# Plot
plt.figure(figsize=(10, 6))
plt.plot(df["year"], df["pct"], marker="o")
plt.xlabel("Year")
plt.ylabel("% Not Wrong at All")
plt.title("Acceptance of Same-Sex Relations (GSS)")
plt.grid(True, alpha=0.3)
plt.show()
```

### Comparing Variables

```python
import gss
import pandas as pd

# Compare multiple trends
vars_to_compare = ["HOMOSEX", "GRASS", "PREMARSX"]
dfs = []
for var in vars_to_compare:
    df = gss.trend(var)
    df["variable"] = var
    dfs.append(df)

combined = pd.concat(dfs)
pivot = combined.pivot(index="year", columns="variable", values="pct")
print(pivot.tail())
```
