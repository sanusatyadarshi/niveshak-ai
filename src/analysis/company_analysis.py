import re
from src.ingestion.reports import ReportExtractor
from src.analysis.output_formatter import AnalysisFormatter
import pdfplumber
import requests

ABOUT_QUESTIONS = [
    "What does the company do?",
    "Who are its promoters? What are their backgrounds?",
    "What do they manufacture?",
    "How many plants do they have and where?",
    "Are they running plants at full capacity?",
    "What kind of raw material is required?",
    "Who are the company's clients or end users?",
    "Who are their competitors?",
    "Who are the major shareholders of the company?",
    "Do they plan to launch any new products?",
    "Do they plan to expand to other countries?",
    "What is the revenue mix? Which product sells the most?",
    "Do they operate under a heavy regulatory environment?",
    "Who are their bankers, auditors?",
    "How many employees do they have? Labour issues?",
    "What are the entry barriers for new participants?",
    "Are products easily replicable in cheap-labor countries?",
    "Too many subsidiaries?"
]

FINANCIAL_METRICS = [
    "Gross Profit Margin (GPM)",
    "Revenue Growth",
    "EPS",
    "Debt Level",
    "Inventory",
    "Sales vs Receivables",
    "Cash Flow from Operations",
    "Return on Equity (ROE)",
    "Business Diversity",
    "Subsidiaries"
]

RATIOS = [
    "Quick Ratio",
    "Current Ratio",
    "P/E Ratio",
    "ROCE (%)",
    "Return on Assets (%)",
    "ROE (%)",
    "Dividend Yield (%)",
    "Debt to Equity",
    "Interest Coverage Ratio",
    "Price to Book Value Ratio",
    "Price to Sales Ratio"
]

class CompanyAnalyzer:
    def __init__(self, llm_judgement_fn=None):
        self.llm_judgement_fn = llm_judgement_fn

    def analyze(self, pdf_path, csv_path=None, company_name="Unknown", year="Unknown"):
        text_sections = ReportExtractor.extract_text_sections(pdf_path)
        tables = ReportExtractor.extract_tables(pdf_path)
        csv_data = ReportExtractor.extract_csv(csv_path) if csv_path else None

        about = []
        for q in ABOUT_QUESTIONS:
            answer = self.rule_based_answer(q, text_sections, tables, csv_data)
            judgement = self.llm_judgement_fn(q, answer) if self.llm_judgement_fn else ""
            about.append({"question": q, "answer": answer, "judgement": judgement})

        financial_metrics = []
        for metric in FINANCIAL_METRICS:
            answer = self.rule_based_metric(metric, tables, csv_data, text_sections)
            judgement = self.llm_judgement_fn(metric, answer) if self.llm_judgement_fn else ""
            financial_metrics.append({"metric": metric, "answer": answer, "judgement": judgement})

        ratios = []
        for ratio in RATIOS:
            value = self.rule_based_ratio(ratio, tables, csv_data, text_sections)
            judgement = self.llm_judgement_fn(ratio, value) if self.llm_judgement_fn else ""
            notes = ""  # Optionally, use LLM for notes too
            ratios.append({"ratio": ratio, "value": value, "judgement": judgement, "notes": notes})

        analysis = {
            "about": about,
            "financial_metrics": financial_metrics,
            "ratios": ratios
        }
        markdown = AnalysisFormatter.full_report(analysis, company_name, year)
        return markdown

    def rule_based_answer(self, question, text_sections, tables, csv_data):
        text = text_sections.get('full_text', '').lower()
        # Map each question to a regex/keyword search
        patterns = {
            "What does the company do?": r"(company (is|engaged in|operates|does).*?\.)",
            "Who are its promoters? What are their backgrounds?": r"promoter[s]?:?.*?\.",
            "What do they manufacture?": r"manufactur.*?\.",
            "How many plants do they have and where?": r"plant[s]?.*?\.",
            "Are they running plants at full capacity?": r"full capacity.*?\.",
            "What kind of raw material is required?": r"raw material.*?\.",
            "Who are the company's clients or end users?": r"client[s]?|end user[s]?.*?\.",
            "Who are their competitors?": r"competitor[s]?.*?\.",
            "Who are the major shareholders of the company?": r"shareholder[s]?.*?\.",
            "Do they plan to launch any new products?": r"launch.*?product[s]?.*?\.",
            "Do they plan to expand to other countries?": r"expand.*?countr.*?\.",
            "What is the revenue mix? Which product sells the most?": r"revenue mix.*?\.",
            "Do they operate under a heavy regulatory environment?": r"regulat.*?environment.*?\.",
            "Who are their bankers, auditors?": r"auditor[s]?|banker[s]?.*?\.",
            "How many employees do they have? Labour issues?": r"employe.*?labour.*?\.",
            "What are the entry barriers for new participants?": r"entry barrier[s]?.*?\.",
            "Are products easily replicable in cheap-labor countries?": r"replicabl.*?cheap.*?countr.*?\.",
            "Too many subsidiaries?": r"subsidiar.*?\.",
        }
        pat = patterns.get(question, None)
        if pat:
            match = re.search(pat, text)
            if match:
                return match.group(0).strip()
        return "[Not found]"

    def rule_based_metric(self, metric, tables, csv_data, text_sections):
        # Try to find the metric in tables or CSV
        metric_map = {
            "Gross Profit Margin (GPM)": ["gross profit margin", "gpm"],
            "Revenue Growth": ["revenue growth", "revenue"],
            "EPS": ["eps", "earnings per share"],
            "Debt Level": ["debt", "borrowings"],
            "Inventory": ["inventory"],
            "Sales vs Receivables": ["receivable", "sales"],
            "Cash Flow from Operations": ["cash flow from operations", "cfo"],
            "Return on Equity (ROE)": ["roe", "return on equity"],
            "Business Diversity": ["business diversity", "segment"],
            "Subsidiaries": ["subsidiar"]
        }
        for df in tables:
            for col in df.columns:
                if col is None:
                    continue
                for key in metric_map.get(metric, []):
                    if key in str(col).lower():
                        if not df.empty and len(df[col]) > 0:
                            value = df[col].iloc[0]
                            return str(value)
        # Fallback: search in text
        text = text_sections.get('full_text', '').lower()
        for key in metric_map.get(metric, []):
            match = re.search(rf"{key}.*?(\d+[\d,.]*)", text)
            if match:
                return match.group(0)
        return "[Not found]"

    def rule_based_ratio(self, ratio, tables, csv_data, text_sections):
        # Try to find the ratio in tables or CSV
        ratio_map = {
            "Quick Ratio": ["quick ratio"],
            "Current Ratio": ["current ratio"],
            "P/E Ratio": ["p/e", "price to earnings"],
            "ROCE (%)": ["roce", "return on capital employed"],
            "Return on Assets (%)": ["roa", "return on assets"],
            "ROE (%)": ["roe", "return on equity"],
            "Dividend Yield (%)": ["dividend yield"],
            "Debt to Equity": ["debt to equity", "d/e"],
            "Interest Coverage Ratio": ["interest coverage"],
            "Price to Book Value Ratio": ["price to book", "p/b"],
            "Price to Sales Ratio": ["price to sales", "p/s"]
        }
        for df in tables:
            for col in df.columns:
                if col is None:
                    continue
                for key in ratio_map.get(ratio, []):
                    if key in str(col).lower():
                        if not df.empty and len(df[col]) > 0:
                            value = df[col].iloc[0]
                            return str(value)
        # Fallback: search in text
        text = text_sections.get('full_text', '').lower()
        for key in ratio_map.get(ratio, []):
            match = re.search(rf"{key}.*?(\d+[\d,.]*)", text)
            if match:
                return match.group(0)
        return "[Not found]"

    def save_report(self, pdf_path, csv_path=None, company_name="Unknown", year="Unknown", out_path=None):
        markdown = self.analyze(pdf_path, csv_path, company_name, year)
        if not out_path:
            safe_name = company_name.replace(" ", "_").replace("/", "_")
            out_path = f"reports/{safe_name}-{year}.md"
        with open(out_path, "w") as f:
            f.write(markdown)
        return out_path

class CompanyAnalyzerLLM:
    def __init__(self, ollama_url="http://localhost:11434/api/chat", model="deepseek-r1:7b"):
        self.ollama_url = ollama_url
        self.model = model

    def ollama_chat(self, prompt):
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        response = requests.post(self.ollama_url, json=payload)
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "")

    def analyze(self, pdf_path, company_name, year):
        # Extract full text from PDF
        with pdfplumber.open(pdf_path) as pdf:
            full_text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        # Truncate if too long for context window
        max_len = 8000
        context_text = full_text[:max_len]

        about = []
        for q in ABOUT_QUESTIONS:
            prompt = f"You are an expert equity analyst. Given the following annual report text, answer this question as precisely as possible.\n\nQuestion: {q}\n\nAnnual Report Text:\n{context_text}"
            answer = self.ollama_chat(prompt)
            about.append({"question": q, "answer": answer, "judgement": ""})

        financial_metrics = []
        for metric in FINANCIAL_METRICS:
            prompt = f"You are an expert equity analyst. Given the following annual report text, extract the value for this financial metric as precisely as possible.\n\nMetric: {metric}\n\nAnnual Report Text:\n{context_text}"
            answer = self.ollama_chat(prompt)
            financial_metrics.append({"metric": metric, "answer": answer, "judgement": ""})

        ratios = []
        for ratio in RATIOS:
            prompt = f"You are an expert equity analyst. Given the following annual report text, extract the value for this financial ratio as precisely as possible.\n\nRatio: {ratio}\n\nAnnual Report Text:\n{context_text}"
            value = self.ollama_chat(prompt)
            ratios.append({"ratio": ratio, "value": value, "judgement": "", "notes": ""})

        analysis = {
            "about": about,
            "financial_metrics": financial_metrics,
            "ratios": ratios
        }
        markdown = AnalysisFormatter.full_report(analysis, company_name, year)
        return markdown

    def save_report(self, pdf_path, company_name="Unknown", year="Unknown", out_path=None):
        markdown = self.analyze(pdf_path, company_name, year)
        if not out_path:
            safe_name = company_name.replace(" ", "_").replace("/", "_")
            out_path = f"reports/{safe_name}-{year}.md"
        with open(out_path, "w") as f:
            f.write(markdown)
        return out_path

if __name__ == "__main__":
    analyzer = CompanyAnalyzerLLM(model="deepseek-r1:7b")
    pdf_path = "data/annual_reports/ITC-2024.pdf"
    company_name = "ITC Limited"
    year = "2023-24"
    out_path = analyzer.save_report(pdf_path, company_name=company_name, year=year)
    print(f"LLM-based report saved to {out_path}") 