# Probe 05: CSV Pipeline (Medium)

## Prompt to give the agent

> Write a Python script that reads a CSV file, processes it, and outputs a summary.
>
> Input CSV (`sales.csv`):
> ```
> date,product,quantity,unit_price
> 2024-01-15,Widget A,10,29.99
> 2024-01-15,Widget B,5,49.99
> 2024-01-16,Widget A,3,29.99
> 2024-01-16,Widget C,8,19.99
> 2024-02-01,Widget B,12,49.99
> 2024-02-01,Widget A,7,29.99
> ```
>
> Output a JSON file (`summary.json`) with:
> 1. Total revenue (quantity * unit_price, summed)
> 2. Revenue per product (sorted descending by revenue)
> 3. Revenue per month (YYYY-MM format)
> 4. Best selling product by quantity
>
> Use only the standard library.

## What to evaluate

- Does it use the `csv` module (not hand-parsing)?
- Does it handle the math correctly? (total should be 1149.67)
- Is the JSON output well-structured and sorted as asked?
- Does it handle: missing file, empty CSV, malformed rows?
- Process: did it create the fixture CSV too, or just the script?

## Expected output

```json
{
  "total_revenue": 1149.67,
  "revenue_per_product": [
    {"product": "Widget B", "revenue": 849.83},
    {"product": "Widget A", "revenue": 599.80},
    {"product": "Widget C", "revenue": 159.92}
  ],
  "revenue_per_month": {
    "2024-01": 789.77,
    "2024-02": 809.82
  },
  "best_selling_product": {
    "product": "Widget A",
    "total_quantity": 20
  }
}
```

Wait — let me verify: Widget B = (5*49.99)+(12*49.99) = 249.95+599.88 = 849.83. Widget A = (10*29.99)+(3*29.99)+(7*29.99) = 299.90+89.97+209.93 = 599.80. Widget C = 8*19.99 = 159.92. Total = 849.83+599.80+159.92 = 1609.55.

Corrected total: **1609.55**

## Red flags
- Wrong arithmetic (watch for floating point issues)
- Not using csv module
- Hardcoded paths instead of parameterized
- Not creating the sample CSV
