---

## 🧾 Terminal Value Calculation

| Metric | Value | Formula |
|--------|-------|---------|
| Terminal Year Cash Flow |         | Last projected FCF |
| Terminal Value |         | `= Terminal CF × (1 + g) / (r - g)` |
| Present Value of Terminal Value |         | `= Terminal Value / (1 + r)^n` |

- Where:
  - `g = terminal growth rate`
  - `r = discount rate`
  - `n = number of years`

---

## 🧮 Intrinsic Value Calculation (INR Cr, unless noted)

| Item                    | Value | Formula                                     |
| ----------------------- | ----- | ------------------------------------------- |
| Total PV of Cash Flows  |       | Sum of all PVs above                        |
| PV of Terminal Value    |       | From above                                  |
| Total Enterprise Value  |       | `= PV of Cash Flows + PV of Terminal Value` |
| Total Debt              |       | From balance sheet                          |
| Cash & Cash Equivalents |       | From balance sheet                          |
| Net Debt                |       | `= Total Debt - Cash`                       |
| Equity Value            |       | `= Enterprise Value - Net Debt`             |
| Number of Shares        |       | Fully diluted                               |
| Intrinsic Share Price   |       | `= Equity Value / No. of Shares`            |

---

## 📉 Intrinsic Value Band (with Margin of Safety)

| Metric                            | Value                            | Notes                      |
| --------------------------------- | -------------------------------- | -------------------------- |
| Model Error Leeway (%)            | `10%`                            | Adjust based on confidence |
| Lower Intrinsic Value Band        | `= Share Price * (1 - Leeway)`   | Conservative estimate      |
| Upper Intrinsic Value Band        | `= Share Price * (1 + Leeway)`   | Optimistic estimate        |
| Margin of Safety (%)              | `30%`                            | User-defined               |
| Final Value with Margin of Safety | `= Intrinsic Price * (1 - MoS%)` |

---

## 📌 Notes

- All values in INR Cr unless stated otherwise
- This model assumes a consistent FCF growth and ignores cyclical volatility

---
