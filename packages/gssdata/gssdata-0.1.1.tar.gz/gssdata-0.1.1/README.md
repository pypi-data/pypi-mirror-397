# gssdata

[![PyPI version](https://badge.fury.io/py/gssdata.svg)](https://badge.fury.io/py/gssdata)
[![CI](https://github.com/MaxGhenis/gss/actions/workflows/ci.yml/badge.svg)](https://github.com/MaxGhenis/gss/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://maxghenis.github.io/gss)

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
print(info["responses"])
# {1: "Too little", 2: "About right", 3: "Too much"}
```

## Features

- **Simple API**: `trend()`, `variables()`, `info()` - that's it
- **Pre-computed trends**: Fast access to time series for key variables
- **Full metadata**: Question text, response options, first year asked

## Available Variables

The package includes 17 frequently-studied GSS variables spanning social attitudes, political views, and trust:

| Variable | Description |
|----------|-------------|
| HOMOSEX | Attitudes toward same-sex relations |
| GRASS | Marijuana legalization support |
| PREMARSX | Premarital sex attitudes |
| ABANY | Abortion for any reason |
| FEPOL | Women suited for politics |
| CAPPUN | Death penalty opposition |
| GUNLAW | Gun permit support |
| NATRACE | Spending on race issues |
| NATEDUC | Spending on education |
| NATENVIR | Spending on environment |
| NATHEAL | Spending on health |
| EQWLTH | Government reduce inequality |
| HELPPOOR | Government help poor |
| TRUST | Social trust |
| FAIR | People try to be fair |
| POLVIEWS | Political ideology |
| PRAYER | School prayer ban approval |

## Documentation

Full documentation: [maxghenis.github.io/gss](https://maxghenis.github.io/gss)

## License

MIT
