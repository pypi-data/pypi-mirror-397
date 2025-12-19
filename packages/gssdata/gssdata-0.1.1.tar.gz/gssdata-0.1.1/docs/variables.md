# Available Variables

The package includes 17 frequently-studied GSS variables spanning social attitudes, political views, and trust.

## Social/Moral Issues

| Variable | Description | First Year |
|----------|-------------|------------|
| HOMOSEX | Attitudes toward same-sex relations | 1973 |
| GRASS | Marijuana legalization support | 1973 |
| PREMARSX | Premarital sex attitudes | 1972 |
| ABANY | Abortion for any reason | 1977 |

## Gender & Politics

| Variable | Description | First Year |
|----------|-------------|------------|
| FEPOL | Women suited for politics | 1974 |
| CAPPUN | Death penalty opposition | 1972 |
| GUNLAW | Gun permit requirement support | 1972 |
| POLVIEWS | Self-identified liberal | 1974 |

## Government Spending

| Variable | Description | First Year |
|----------|-------------|------------|
| NATRACE | Support for spending on race issues | 1973 |
| NATEDUC | Support for spending on education | 1973 |
| NATENVIR | Support for spending on environment | 1973 |
| NATHEAL | Support for spending on health | 1973 |

## Economic Views

| Variable | Description | First Year |
|----------|-------------|------------|
| EQWLTH | Support for government reducing inequality | 1978 |
| HELPPOOR | Support for government helping poor | 1975 |

## Social Trust

| Variable | Description | First Year |
|----------|-------------|------------|
| TRUST | Most people can be trusted | 1972 |
| FAIR | People try to be fair | 1972 |

## Religion

| Variable | Description | First Year |
|----------|-------------|------------|
| PRAYER | Approve of school prayer ban | 1974 |

## Variable Details

To get full details for any variable:

```python
import gssdata

info = gssdata.info("NATEDUC")
print(info["question"])
# Full question text

print(info["responses"])
# {1: "Too little", 2: "About right", 3: "Too much"}

print(info["first_year"])
# 1973
```
