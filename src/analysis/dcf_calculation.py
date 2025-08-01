"""
Discounted Cash Flow (DCF) calculation utility for company intrinsic value analysis.

Implements:
- FCF projection (two-stage growth)
- Terminal value (Gordon Growth Model)
- Present value calculations
- Intrinsic value per share, value bands, and margin of safety

Inputs and formulas are based on the markdown template in data/templates/dcf-calculation.md.
"""

def dcf_intrinsic_valuation(
    base_fcf: float,
    fcf_growth_rate_5yr: float = 0.10,
    fcf_growth_rate_10yr: float = 0.05,
    terminal_growth_rate: float = 0.01,
    discount_rate: float = 0.12,
    total_debt: float = 0.0,
    cash_and_equivalents: float = 0.0,
    share_capital: float = 1.0,
    face_value: float = 1.0,
    model_error_leeway: float = 0.10,
    margin_of_safety: float = 0.30,
    years: int = 10
) -> dict:
    """
    Calculate DCF intrinsic value and related metrics for a company.
    Args:
        base_fcf: Starting Free Cash Flow (most recent year)
        fcf_growth_rate_5yr: FCF growth rate for first 5 years (as decimal)
        fcf_growth_rate_10yr: FCF growth rate for last 5 years (as decimal)
        terminal_growth_rate: Terminal growth rate after projection (as decimal)
        discount_rate: Discount rate (as decimal)
        total_debt: Total debt
        cash_and_equivalents: Cash and cash equivalents
        share_capital: Share capital (from balance sheet)
        face_value: Face value of each share
        model_error_leeway: Model error leeway (as decimal)
        margin_of_safety: Margin of safety (as decimal)
        years: Number of years to project (default 10)
    Returns:
        dict with all DCF and intrinsic value metrics
    """
    # Calculate number of shares
    number_of_shares = share_capital / face_value if face_value else 1.0
    # Project FCFs
    projected_fcfs = []
    for i in range(years):
        if i < 5:
            growth = fcf_growth_rate_5yr
        else:
            growth = fcf_growth_rate_10yr
        if i == 0:
            fcf = base_fcf * (1 + growth)
        else:
            fcf = projected_fcfs[-1] * (1 + growth)
        projected_fcfs.append(fcf)
    # PV of FCFs
    pv_fcfs = [fcf / ((1 + discount_rate) ** (i + 1)) for i, fcf in enumerate(projected_fcfs)]
    total_pv_fcfs = sum(pv_fcfs)
    terminal_year_cflow = projected_fcfs[-1]
    # Terminal Value
    terminal_value = terminal_year_cflow * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
    pv_terminal_value = terminal_value / ((1 + discount_rate) ** years)
    # Enterprise Value
    enterprise_value = total_pv_fcfs + pv_terminal_value
    net_debt = total_debt - cash_and_equivalents
    equity_value = enterprise_value - net_debt
    intrinsic_share_price = equity_value / number_of_shares
    # Intrinsic Value Band
    lower_band = intrinsic_share_price * (1 - model_error_leeway)
    upper_band = intrinsic_share_price * (1 + model_error_leeway)
    final_value_mos = intrinsic_share_price * (1 - margin_of_safety)
    return {
        "Projected FCFs": projected_fcfs,
        "Total PV of Cash Flows": total_pv_fcfs,
        "PV of Terminal Value": pv_terminal_value,
        "Total Enterprise Value": enterprise_value,
        "Total Debt": total_debt,
        "Cash & Cash Equivalents": cash_and_equivalents,
        "Net Debt": net_debt,
        "Equity Value": equity_value,
        "Share Capital": share_capital,
        "Face Value": face_value,
        "Number of Shares": number_of_shares,
        "Intrinsic Share Price": intrinsic_share_price,
        "Model Error Leeway (%)": model_error_leeway * 100,
        "Lower Intrinsic Value Band": lower_band,
        "Upper Intrinsic Value Band": upper_band,
        "Margin of Safety (%)": margin_of_safety * 100,
        "Final Value with Margin of Safety": final_value_mos,
        "Terminal Year Cash Flow": terminal_year_cflow,
        "Terminal Value": terminal_value,
        "Present Value of Terminal Value": pv_terminal_value,
    }

def dcf_intrinsic_valuation_and_report(
    company_name: str,
    year: str,
    base_fcf: float,
    fcf_growth_rate_5yr: float = 0.10,
    fcf_growth_rate_10yr: float = 0.05,
    terminal_growth_rate: float = 0.01,
    discount_rate: float = 0.12,
    total_debt: float = 0.0,
    cash_and_equivalents: float = 0.0,
    share_capital: float = 1.0,
    face_value: float = 1.0,
    model_error_leeway: float = 0.10,
    margin_of_safety: float = 0.30,
    years: int = 10,
    reports_dir: str = "reports"
) -> dict:
    """
    Extended DCF function: computes values and writes a markdown report to /reports.
    """
    import os
    os.makedirs(reports_dir, exist_ok=True)
    result = dcf_intrinsic_valuation(
        base_fcf=base_fcf,
        fcf_growth_rate_5yr=fcf_growth_rate_5yr,
        fcf_growth_rate_10yr=fcf_growth_rate_10yr,
        terminal_growth_rate=terminal_growth_rate,
        discount_rate=discount_rate,
        total_debt=total_debt,
        cash_and_equivalents=cash_and_equivalents,
        share_capital=share_capital,
        face_value=face_value,
        model_error_leeway=model_error_leeway,
        margin_of_safety=margin_of_safety,
        years=years
    )
    # Format markdown
    md = f"""
---

## 🧾 Terminal Value Calculation

| Metric | Value | Formula |
|--------|-------|---------|
| Terminal Year Cash Flow | {result['Terminal Year Cash Flow']:.2f} | Last projected FCF |
| Terminal Value | {result['Terminal Value']:.2f} | = Terminal CF × (1 + g) / (r - g) |
| Present Value of Terminal Value | {result['Present Value of Terminal Value']:.2f} | = Terminal Value / (1 + r)^n |

- Where:
  - g = terminal growth rate ({terminal_growth_rate*100:.2f}%)
  - r = discount rate ({discount_rate*100:.2f}%)
  - n = number of years ({years})

---

## 🧮 Intrinsic Value Calculation (INR Cr, unless noted)

| Item                    | Value        | Formula                                     |
| ----------------------- | ----------- | ------------------------------------------- |
| Total PV of Cash Flows  | {result['Total PV of Cash Flows']:.2f} | Sum of all PVs above                        |
| PV of Terminal Value    | {result['PV of Terminal Value']:.2f} | From above                                  |
| Total Enterprise Value  | {result['Total Enterprise Value']:.2f} | = PV of Cash Flows + PV of Terminal Value   |
| Total Debt              | {result['Total Debt']:.2f} | From balance sheet                          |
| Cash & Cash Equivalents | {result['Cash & Cash Equivalents']:.2f} | From balance sheet                          |
| Net Debt                | {result['Net Debt']:.2f} | = Total Debt - Cash                         |
| Equity Value            | {result['Equity Value']:.2f} | = Enterprise Value - Net Debt               |
| Number of Shares        | {result['Number of Shares']:.0f} | Fully diluted                               |
| Intrinsic Share Price   | {result['Intrinsic Share Price']:.2f} | = Equity Value / No. of Shares              |

---

## 📉 Intrinsic Value Band (with Margin of Safety)

| Metric                            | Value        | Notes                      |
| --------------------------------- | ----------- | -------------------------- |
| Model Error Leeway (%)            | {result['Model Error Leeway (%)']:.1f}% | Adjust based on confidence |
| Lower Intrinsic Value Band        | {result['Lower Intrinsic Value Band']:.2f} | Conservative estimate      |
| Upper Intrinsic Value Band        | {result['Upper Intrinsic Value Band']:.2f} | Optimistic estimate        |
| Margin of Safety (%)              | {result['Margin of Safety (%)']:.1f}% | User-defined               |
| Final Value with Margin of Safety | {result['Final Value with Margin of Safety']:.2f} |                          |

---

## 📌 Notes

- All values in INR Cr unless stated otherwise
- This model assumes a consistent FCF growth and ignores cyclical volatility

---
"""
    # Write to file
    safe_company = company_name.replace(" ", "_").replace("/", "-")
    out_path = os.path.join(reports_dir, f"{safe_company}-dcf-{year}.md")
    with open(out_path, "w") as f:
        f.write(md)
    result["report_path"] = out_path
    return result
