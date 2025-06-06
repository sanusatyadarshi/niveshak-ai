
---

## 🧾 Terminal Value Calculation

| Metric | Value | Formula |
|--------|-------|---------|
| Terminal Year Cash Flow | 205.55 | Last projected FCF |
| Terminal Value | 1887.29 | = Terminal CF × (1 + g) / (r - g) |
| Present Value of Terminal Value | 607.66 | = Terminal Value / (1 + r)^n |

- Where:
  - g = terminal growth rate (1.00%)
  - r = discount rate (12.00%)
  - n = number of years (10)

---

## 🧮 Intrinsic Value Calculation (INR Cr, unless noted)

| Item                    | Value        | Formula                                     |
| ----------------------- | ----------- | ------------------------------------------- |
| Total PV of Cash Flows  | 851.91 | Sum of all PVs above                        |
| PV of Terminal Value    | 607.66 | From above                                  |
| Total Enterprise Value  | 1459.56 | = PV of Cash Flows + PV of Terminal Value   |
| Total Debt              | 50.00 | From balance sheet                          |
| Cash & Cash Equivalents | 20.00 | From balance sheet                          |
| Net Debt                | 30.00 | = Total Debt - Cash                         |
| Equity Value            | 1429.56 | = Enterprise Value - Net Debt               |
| Number of Shares        | 10 | Fully diluted                               |
| Intrinsic Share Price   | 142.96 | = Equity Value / No. of Shares              |

---

## 📉 Intrinsic Value Band (with Margin of Safety)

| Metric                            | Value        | Notes                      |
| --------------------------------- | ----------- | -------------------------- |
| Model Error Leeway (%)            | 10.0% | Adjust based on confidence |
| Lower Intrinsic Value Band        | 128.66 | Conservative estimate      |
| Upper Intrinsic Value Band        | 157.25 | Optimistic estimate        |
| Margin of Safety (%)              | 30.0% | User-defined               |
| Final Value with Margin of Safety | 100.07 |                          |

---

## 📌 Notes

- All values in INR Cr unless stated otherwise
- This model assumes a consistent FCF growth and ignores cyclical volatility

---
