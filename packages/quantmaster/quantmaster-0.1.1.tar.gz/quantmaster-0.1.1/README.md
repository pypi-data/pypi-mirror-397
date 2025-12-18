# Quantmaster

Biblioteca de features quantitativas para adicionar colunas em `pandas.DataFrame` com dados OHLCV.

## Instalação (desenvolvimento)

```bash
pip install -e ".[dev]"
```

## Uso rápido

```python
from quantmaster.features.momentum import rsi
from quantmaster.features.volatility import har_rv

df["rsi_10"] = rsi(df, window=10)
df = df.join(har_rv(df))
```

## Importar features de uma vez

Se você quiser importar várias features sem ficar apontando para cada submódulo, use o namespace `quantmaster.features` (exporta as features públicas em `__all__`):

```python
from quantmaster.features import rsi, har_rv, yang_zhang_volatility, hurst_dfa
```

Você também pode fazer import wildcard (não recomendado em código de produção, mas útil em notebooks):

```python
from quantmaster.features import *
```

## Estrutura

- Features ficam em `src/quantmaster/features/` separadas por categoria (Momentum, Trend, Volatility, etc.).
- Cada feature é uma função que recebe `DataFrame` (ou `Series`) e retorna `Series` (ou `DataFrame`) alinhado ao índice.
