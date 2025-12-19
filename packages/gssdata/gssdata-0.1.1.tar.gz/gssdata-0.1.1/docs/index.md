# gssdata

Python client for [General Social Survey (GSS)](https://gss.norc.org/) data.

## Installation

```bash
pip install gssdata
```

## Quick Start

```python
import gssdata

# Get time series for a variable
df = gssdata.trend("NATEDUC")
print(df.head())
#    year  pct
# 0  1973   49
# 1  1974   52
# 2  1975   51
# ...

# List all available variables
variables = gssdata.variables()
print(len(variables))  # 17 core variables

# Get variable metadata
info = gssdata.info("NATEDUC")
print(info["question"])
# "Are we spending too much, too little, or about the right amount on education?"
```

## Features

- **Simple API**: Just three functions: `trend()`, `variables()`, `info()`
- **Pre-computed trends**: Fast access to time series for 17 key variables
- **Full metadata**: Question text, response options, first year asked
- **Zero dependencies on GSS servers**: Data bundled with package

## Why gssdata?

The General Social Survey is one of the most important sources of data on American public opinion, running continuously since 1972. However, accessing GSS data programmatically in Python has historically required:

1. Downloading large data files from the GSS website
2. Parsing Stata/SPSS formats
3. Computing weighted percentages
4. Understanding variable coding

**gssdata** eliminates this friction by providing pre-computed time series for the most commonly studied variables.

## Data Source

Data is extracted from the GSS cumulative data file (1972-2024) using unweighted respondent counts. All percentages represent the proportion of respondents giving the "liberal" or "progressive" response for each variable.
