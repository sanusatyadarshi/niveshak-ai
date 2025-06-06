class AnalysisFormatter:
    """
    Formats company analysis results into Markdown.
    """

    @staticmethod
    def about_section(about_list, company_name, year):
        md = f"## 🏢 About the Company – {company_name} ({year})\n\n"
        md += "| Question | Answer | Judgement/Notes |\n"
        md += "|---|---|---|\n"
        for item in about_list:
            md += f"| {item['question']} | {item['answer']} | {item.get('judgement', '')} |\n"
        md += "\n"
        return md

    @staticmethod
    def financial_metrics_section(metrics_list, company_name, year):
        md = f"## 📊 Financial Metrics ({year}) – {company_name}\n\n"
        md += "| Metric | Answer (From AR) | Judgement |\n"
        md += "|---|---|---|\n"
        for item in metrics_list:
            md += f"| {item['metric']} | {item['answer']} | {item.get('judgement', '')} |\n"
        md += "\n"
        return md

    @staticmethod
    def ratios_section(ratios_list, company_name, year):
        md = f"## 📈 Ratio Analysis – {company_name} {year}\n\n"
        md += "| Ratio | Value | Interpretation / Judgement | Notes / Observations |\n"
        md += "|---|---|---|---|\n"
        for item in ratios_list:
            md += f"| {item['ratio']} | {item['value']} | {item.get('judgement', '')} | {item.get('notes', '')} |\n"
        md += "\n"
        return md

    @staticmethod
    def full_report(analysis, company_name, year):
        md = AnalysisFormatter.about_section(analysis['about'], company_name, year)
        md += "---\n\n"
        md += AnalysisFormatter.financial_metrics_section(analysis['financial_metrics'], company_name, year)
        md += "---\n\n"
        md += AnalysisFormatter.ratios_section(analysis['ratios'], company_name, year)
        return md 