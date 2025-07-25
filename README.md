# nuplytics
nuplytics is a lightweight Python library for analyzing Net Unrealized Profit/Loss (NUPL) from real-time crypto market data using Yahoo Finance.

```python
from nuplytics.utils import NUPLCalculator

nupl = NUPLCalculator()
nupl.calculate(start='2022-01-01')
print(nupl.get_latest_json())
```

```bash
{
  "date": "2025-07-24",
  "price": 61500.75,
  "realized_price": 28870.15,
  "nupl": 0.5312,
  "status": "Greed",
  "message": "Market is overheating. Be cautious.",
  "signal": "SELL"
}
```