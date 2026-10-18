"""FastAPI app exposing the skin clinic campaign analysis."""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

from analysis import run_analysis

app = FastAPI(
    title="Skin Clinic Campaign Analysis API",
    description="Response rate (%) by customer segment for a 10,000 customer marketing campaign.",
    version="1.0.0",
)

RESULTS = run_analysis()  # computed once at start-up

CSS = """
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;max-width:900px;margin:32px auto;padding:0 16px;color:#1f2937;background:#f9fafb}
h1{margin-bottom:4px} .sub{color:#6b7280;margin-top:0}
h2{margin-top:36px;font-size:1.15rem;border-left:4px solid #0d9488;padding-left:10px}
table{border-collapse:collapse;width:100%;background:#fff;box-shadow:0 1px 3px rgba(0,0,0,.08)}
th,td{padding:10px 14px;text-align:left;border-bottom:1px solid #e5e7eb}
th{background:#0d9488;color:#fff;font-weight:600}
td:nth-child(n+2),th:nth-child(n+2){text-align:right}
tr:hover td{background:#f0fdfa}
.best td{font-weight:700}
ul{line-height:1.7} footer{margin:40px 0;color:#9ca3af;font-size:.85rem}
"""


def table_html(df):
    best = df["Response Rate (%)"].idxmax()
    head = "".join(f"<th>{c}</th>" for c in df.columns)
    rows = ""
    for i, r in df.iterrows():
        cls = ' class="best"' if i == best else ""
        cells = "".join(
            f"<td>{v:.2f}%</td>" if c == "Response Rate (%)" else f"<td>{v:,}</td>" if isinstance(v, (int,)) or str(v).isdigit() else f"<td>{v}</td>"
            for c, v in r.items()
        )
        rows += f"<tr{cls}>{cells}</tr>"
    return f"<table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>"


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/campaign-analysis")


@app.get("/campaign-analysis", response_class=HTMLResponse)
def campaign_analysis():
    """Campaign response rate tables by gender, age group, last quarter purchase and product usage."""
    sections = ""
    for i, (name, df) in enumerate(((k, v) for k, v in RESULTS.items() if not k.startswith("_")), 1):
        sections += f"<h2>{i}. {name}</h2>{table_html(df)}"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Skin Clinic Campaign Analysis</title><style>{CSS}</style></head><body>
<h1>Skin Clinic Campaign Analysis</h1>
<p class="sub">{RESULTS['_total']:,} customers targeted. Overall response rate: <b>{RESULTS['_overall']:.2f}%</b>. Bold row = highest response in each table.</p>
{sections}
<h2>Key insights</h2>
<ul>
<li>Recent buyers are the strongest signal: customers who purchased last quarter responded at more than double the rate of those who did not.</li>
<li>Product breadth matters: customers using more than 8 products respond at roughly three times the rate of those using 1 to 4.</li>
<li>The 30 to 50 age group is the most responsive; under 30s and over 50s are similar and lower.</li>
<li>Female customers respond better than male customers.</li>
<li>Best future target: female, aged 30 to 50, purchased last quarter, more than 8 products.</li>
</ul>
<footer>JSON version: <a href="/campaign-analysis/json">/campaign-analysis/json</a> · API docs: <a href="/docs">/docs</a></footer>
</body></html>"""


@app.get("/campaign-analysis/json")
def campaign_analysis_json():
    """Same results as JSON."""
    out = {k: v.astype({c: str for c in v.columns[:1]}).to_dict(orient="records")
           for k, v in RESULTS.items() if not k.startswith("_")}
    return {"total_customers": RESULTS["_total"], "overall_response_rate_pct": RESULTS["_overall"], "tables": out}


@app.get("/health", include_in_schema=False)
def health():
    return {"status": "ok"}
