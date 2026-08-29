#!/usr/bin/env python3
"""Generate Herman Suykerbuyk CV as PDF - matches website content/style"""
from fpdf import FPDF

class CVPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(113, 128, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}  |  Herman Suykerbuyk - Business Data Engineer  |  suykerbuykh@gmail.com", align="C")

pdf = CVPDF(format="A4")
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=18)
pdf.set_margins(14, 14, 14)

def sanitize(t: str) -> str:
    return t.replace("\u2014", "-").replace("\u2013", "-").replace("\u2192", "->").replace("\u00a0", " ").replace("\u202f", " ").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')

# Colors
PRIMARY = (45, 55, 72)      # #2d3748
SECONDARY = (74, 85, 104)   # #4a5568
ACCENT = (56, 178, 93)      # #38b25d
LIGHT_BG = (237, 242, 247)  # #edf2f7
BORDER = (203, 213, 224)    # #cbd5e0
TEXT_LIGHT = (113, 128, 150)

def section_title(title):
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*PRIMARY)
    pdf.set_fill_color(*LIGHT_BG)
    pdf.set_draw_color(*BORDER)
    # check space: need ~10mm for title + content
    if pdf.get_y() > 265:
        pdf.add_page()
    pdf.cell(0, 8, sanitize(f"  {title.upper()}"), ln=True, fill=True, border=1)
    pdf.ln(3)

def sub_heading(text):
    if pdf.get_y() > 270:
        pdf.add_page()
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*PRIMARY)
    pdf.cell(0, 5, sanitize(text), ln=True)
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.5)
    x = pdf.get_x()
    y = pdf.get_y()
    pdf.line(x, y, x+30, y)
    pdf.ln(2)

def sub_sub(text):
    if pdf.get_y() > 272:
        pdf.add_page()
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*SECONDARY)
    pdf.cell(0, 4.5, sanitize(text), ln=True)
    pdf.ln(0.5)

def body(text):
    pdf.set_font("Helvetica", "", 7.8)
    pdf.set_text_color(*TEXT_LIGHT)
    pdf.multi_cell(0, 4, sanitize(text))
    pdf.ln(1.2)

def body_with_bold_prefix(prefix, text):
    """Render 'Prefix: text' where prefix is bold (for ABOUT ME) - mirrors HTML <b>Prefix:</b>"""
    prefix = sanitize(prefix)
    text = sanitize(text)
    x = pdf.get_x()
    w = pdf.w - pdf.r_margin - x
    chars_per_line = max(1, w / 1.7)
    lines = (len(prefix) + len(text)) / chars_per_line + 1
    if pdf.get_y() + lines*4 + 4 > 285:
        pdf.add_page()
    pdf.set_font("Helvetica", "B", 7.8)
    pdf.set_text_color(*PRIMARY)
    pdf.write(4, prefix + " ")
    pdf.set_font("Helvetica", "", 7.8)
    pdf.set_text_color(*TEXT_LIGHT)
    pdf.write(4, text)
    pdf.ln(6)

def bullet(title, text):
    # estimate height to keep bullet together if possible
    text_s = sanitize(text)
    title_s = sanitize(title)
    x0 = 14  # left margin
    indent = 6
    w = pdf.w - pdf.r_margin - (x0+indent)
    # rough lines: avg char width ~1.7mm at 7.8pt
    chars_per_line = max(1, w / 1.7)
    lines = max(1, (len(text_s) / chars_per_line) + 0.9)
    est_h = 4 + lines*4 + 2  # title + text
    if pdf.get_y() + est_h > 285:
        pdf.add_page()
    x = pdf.get_x()
    y0 = pdf.get_y()
    # bullet dot
    pdf.set_fill_color(*ACCENT)
    pdf.ellipse(x+1, y0+1.5, 2, 2, style="F")
    # title on its own line (bold)
    pdf.set_xy(x+indent, y0)
    pdf.set_font("Helvetica", "B", 7.8)
    pdf.set_text_color(*PRIMARY)
    pdf.cell(0, 4, title_s, new_x="LMARGIN", new_y="NEXT")
    # text block indented, wrapping correctly
    pdf.set_x(x+indent)
    pdf.set_font("Helvetica", "", 7.8)
    pdf.set_text_color(*TEXT_LIGHT)
    pdf.multi_cell(w, 4, text_s)
    pdf.ln(1.5)

def tag_row(tags):
    pdf.set_font("Helvetica", "", 6.5)
    x_start = pdf.get_x()
    y = pdf.get_y()
    for tag in tags:
        tag = sanitize(tag)
        w = pdf.get_string_width(tag) + 6
        # check wrap
        if pdf.get_x() + w > pdf.w - pdf.r_margin:
            pdf.ln(5)
        # draw tag pill
        cx = pdf.get_x()
        cy = pdf.get_y()
        pdf.set_fill_color(*LIGHT_BG)
        pdf.set_draw_color(*BORDER)
        pdf.set_xy(cx, cy)
        pdf.cell(w, 4.5, tag, border=1, align="C", fill=True)
        pdf.set_xy(cx + w + 1.2, cy)
    pdf.ln(6)

# ===== PAGE 1 HEADER =====
pdf.add_page()

# Top accent bar
pdf.set_fill_color(*ACCENT)
pdf.rect(0, 0, 210, 4, style="F")

pdf.ln(6)
# PDF metadata (matches <title> in index.html:7)
pdf.set_title(sanitize("Herman Suykerbuyk - Business Data Engineer"))
pdf.set_author("Herman Suykerbuyk")
# Name
pdf.set_font("Helvetica", "B", 22)
pdf.set_text_color(*PRIMARY)
pdf.cell(0, 9, sanitize("Herman Suykerbuyk"), ln=True, align="C")
# Title — now bold to match HTML <title> styling request
pdf.set_font("Helvetica", "B", 9)
pdf.set_text_color(*SECONDARY)
pdf.cell(0, 5, sanitize("Business Data Engineer  |  Platform Engineer  |  Data Infrastructure  |  ETL & Pipelines"), ln=True, align="C")
pdf.ln(1)
# Badge
pdf.set_font("Helvetica", "B", 7)
pdf.set_fill_color(*ACCENT)
pdf.set_text_color(255,255,255)
badge = "  3-5 years experience  "
w = pdf.get_string_width(badge) + 6
pdf.set_x((210 - w)/2)
pdf.cell(w, 5, badge, ln=True, align="C", fill=True)
pdf.ln(2)
# Contact line — now includes phone (Contact + PDF header request)
pdf.set_font("Helvetica", "", 7)
pdf.set_text_color(*TEXT_LIGHT)
pdf.cell(0, 4, sanitize("Mechelen, Belgium  |  +32 491 12 54 20  |  suykerbuykh@gmail.com  |  linkedin.com/in/herman-suykerbuyk-16299323b  |  github.com/Hermannnnnnnn"), ln=True, align="C")
# Divider
pdf.ln(2)
pdf.set_draw_color(*BORDER)
pdf.set_line_width(0.3)
pdf.line(14, pdf.get_y(), 196, pdf.get_y())
pdf.ln(4)

# ===== ABOUT ME =====
section_title("About Me")
body("Business Data Engineer with 3-5 years of experience across data engineering and platform engineering.")
body_with_bold_prefix("Data Engineering:", "Two years building end-to-end data transformations - from ingestion pipelines to Data Vault and dimensional modelling.")
body_with_bold_prefix("Platform Engineering:", "Helped build a new platform on Airflow, dbt and Databricks - enabling faster delivery through reliable pipelines, reusable tooling, test automation and CI/CD.")
body_with_bold_prefix("Leadership:", "Improved how teams work: reducing unnecessary meetings, consolidating documentation, strengthening refinement sessions, challenging unsuitable frameworks, introducing future-proof solutions and Communities of Practice (COP).")

# Personal grid - 2x2
pdf.set_font("Helvetica", "B", 7)
pdf.set_text_color(*PRIMARY)
# We'll do 2 columns
col_w = (pdf.w - 28 - 4)/2
y_start = pdf.get_y()
# Helper to draw card
def personal_card(x, y, w, h, title, text):
    pdf.set_xy(x, y)
    pdf.set_fill_color(*LIGHT_BG)
    pdf.set_draw_color(*BORDER)
    pdf.rect(x, y, w, h, style="DF")
    pdf.set_xy(x+3, y+2)
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_text_color(*PRIMARY)
    pdf.cell(w-6, 3.5, sanitize(title), ln=True)
    pdf.set_x(x+3)
    pdf.set_font("Helvetica", "", 6.8)
    pdf.set_text_color(*TEXT_LIGHT)
    pdf.multi_cell(w-6, 3.2, sanitize(text))

cards = [
    ("Location", "Based in Mechelen, Belgium - open to hybrid/remote. Willing to commute within region."),
    ("Current Circumstances", "Business Data Engineer, currently working as Platform Engineer. Open to new opportunities."),
    ("Languages", "Dutch (native), English (professional), French (basic)"),
    ("Work Preferences", "Interested in both technical depth and people leadership."),
]
# Calculate heights
y = pdf.get_y()
pdf.set_xy(14, y)
# draw 2 per row
for i in range(0, 4, 2):
    x1 = 14
    x2 = 14 + col_w + 4
    # estimate height 14
    h = 14
    if pdf.get_y() + h*1.2 > 285:
        pdf.add_page()
        y = pdf.get_y()
    personal_card(x1, y, col_w, h, cards[i][0], cards[i][1])
    personal_card(x2, y, col_w, h, cards[i+1][0], cards[i+1][1])
    y += h + 2
    pdf.set_y(y)
pdf.ln(2)

# ===== TOOLSTACK =====
section_title("Toolstack")
sub_sub("Languages")
tag_row(["Python", "SQL", "PL/SQL", "Groovy", "Shell", "Terraform"])
sub_sub("Data & Transformation")
tag_row(["ODI", "dbt", "Data Vault 2.0", "Dimensional Modelling", "Vaultspeed"])
sub_sub("Orchestration & Platform")
tag_row(["Apache Airflow", "IWS", "Databricks", "Oracle", "Lakeflow Connect", "AKS", "Azure"])
sub_sub("Engineering Practices")
tag_row(["pytest", "GitHub Actions", "CI/CD", "Confluence", "JDBC"])

# ===== EXPERIENCE =====
section_title("Experience")

# Data Engineering
sub_heading("Data Engineering")
sub_sub("ETL / ELT")
def _load_h4_paras(h4_title):
    try:
        import re
        from pathlib import Path
        html = Path("index.html").read_text(encoding="utf-8")
        # find h4 with exact title then capture following <p>...</p> until closing timeline-content
        pat = re.compile(r'<h4>' + re.escape(h4_title) + r'</h4>(.*?)</div>\s*</div>', re.DOTALL)
        m = pat.search(html)
        if m:
            block = m.group(1)
            paras = re.findall(r"<p>(.*?)</p>", block, re.DOTALL)
            cleaned = []
            for p in paras:
                t = re.sub(r"<[^>]+>", "", p).strip()
                t = re.sub(r"\s+", " ", t)
                if t:
                    cleaned.append(t)
            if cleaned:
                return " ".join(cleaned)
    except Exception as e:
        print(f"warn: h4 parse {h4_title} failed: {e}")
    return None

_pipeline_html = _load_h4_paras("Pipeline Development")
_pipeline_fallback = "I built and maintained end-to-end ETL pipelines: ODI (Oracle) and dbt for transformations, and IWS and Apache Airflow for orchestration. Made ways to speed up the development phase (PL/SQl scripts that generate production release script, groovy for generating ODI mappings)."
bullet("Pipeline Development:", _pipeline_html if _pipeline_html else _pipeline_fallback)
bullet("Ops:", "Weekly Ops rotations. Deepened product knowledge, troubleshot production issues (e.g., mining metadata tables for root causes) and proposed several improvements to the Ops process.")
bullet("Transformation Logic:", 'Co-authored "Big Book of dbt": the organization\'s manual of best practices for type casting, deduplication, business-logic encapsulation, test tagging, naming conventions.')

sub_sub("Testing")
bullet("Load testing:", "Revived an underused PL/SQL testing framework: added test templates, expanded coverage beyond file ingestion, and prevented integrity issues before they reached the Data Vault and dimensional model.")
bullet("Unit & regression testing:", "Built an automated testing tool in Python with GitHub, CI/CD and Python. The framework runs a comprehensive suite of tests on source ingestion (source to Data Vault) or presentation (Data Vault to dimensional model) and is still used today, replacing the tedious manual testing cycle. Found many data issues, sped up testing and increased business trust in the data.")

sub_sub("Modeling")
bullet("Data Vault & Dimensional:", "Delivered end-to-end solutions from ingestion through Data Vault to dimensional modelling (dimensions/facts, star schema).")

sub_sub("Documenting")
bullet("Revamping:", "Found documentation scattered and often outdated. Consolidated in Confluence, rewrote what I could and delegated the rest.")
bullet("Expanding:", "Authored numerous pages to standardise way of working and help future newcomers onboard faster.")

# Platform Engineering
sub_heading("Platform Engineering")
sub_sub("Testing")
bullet("Infra Regression Testing:", "Took ownership of a pytest regression testing framework for platform components during infra releases. Added tests and refactored codebase with fixtures, modules and markers.")
bullet("Codebase Testing:", "Implemented and owned dbt-bouncer and SQLFluff for defining and enforcing coding standards in CI/CD.")
bullet("Data quality:", "Helped build a framework that pulls test definitions from Collibra, saves them as dbt tests, deploys to production, runs the tests and reports results.")

sub_sub("Tooling")
_dbt_html = _load_h4_paras("dbt")
_dbt_fallback = "Wrote macros and materialisation overrides for organisation-wide use. Performed package upgrades, worked out the kinks and supported data colleagues. Found ways to improve, like reduced parsing time and reduced API calls to Databricks. Advocated and lobbied for dbt-bouncer and SQLFluff. Brought it to maturity from beginning to end: worked with data team colleagues to determine the standards, implemented these standards and enforced them through CI/CD, documented how the tools work and how to configure VS Code for local use."
bullet("dbt:", _dbt_html if _dbt_html else _dbt_fallback)

bullet("Airflow & AKS:", "Wrote Airflow operators and helped build the orchestration framework: a semantic layer on top of Airflow. Data colleagues write YAML with templated tasks instead of raw Airflow code. Improved stability by tuning pod resources, queue setup, and Cosmos WATCHER mode for heavy dbt DAGs. Implemented PVCs, PVC mounts in Airflow Helm, secret scopes and service connections.")

_databricks_html = _load_h4_paras("Databricks")
_databricks_fallback = "Developed a Lakeflow Pipelines framework for SQL Server ingestion. Built an ingestion framework for on-prem Oracle databases to databricks using Spark JDBC. Co-built a trial environment: before release to production, we shallow-clone production data to trial, deploy the release there and run our DAGs. This catches issues before causing incidents on production. Investigated cost spikes and failing SQL queries caused by excessive Unity Catalog API calls."
bullet("Databricks:", _databricks_html if _databricks_html else _databricks_fallback)

sub_sub("CI/CD")
def _load_cicd_text():
    try:
        import re
        from pathlib import Path
        html = Path("index.html").read_text(encoding="utf-8")
        m = re.search(r'id="subtab-pe-cicd"(.*?)(?:</div>\s*){3}', html, re.DOTALL)
        if m:
            block = m.group(1)
            paras = re.findall(r"<p>(.*?)</p>", block, re.DOTALL)
            cleaned = []
            for p in paras:
                t = re.sub(r"<[^>]+>", "", p).strip()
                t = re.sub(r"\s+", " ", t)
                if t:
                    cleaned.append(t)
            if cleaned:
                return " ".join(cleaned)
    except Exception as e:
        print(f"warn: CI/CD parse failed: {e}")
    return None

_cicd_html = _load_cicd_text()
_cicd_fallback = "Implemented PR validations (SQLFluff, dbt-bouncer, YAML schema) and branch protection. Suggested and built a deploy-branch strategy for concurrent deployments to the same test environment. Brought release management to maturity: built a pipeline to generate releases and release notes, implemented automatic labeling of pull requests with dataproduct tags, offering stakeholders an insight into what changed by the overview in release notes which was grouped per data product."
bullet("GitHub Actions & release management:", _cicd_html if _cicd_html else _cicd_fallback)

# Lead Team
sub_heading("Lead / Team")
sub_sub("Way of Working")
bullet("Team Efficiency:", "Drove organisational change. In first team: reduced unnecessary meetings, introduced Communities of Practice, challenged push for unsuitable framework. In second team: advocated better feature refinement (named stakeholders, consultation, demos) and more demos due to poorly T-shaped team.")

sub_sub("Future-proofing")
bullet("Sustainable Solutions:", "Reversed a management-preferred Gherkin/Java decision by delivering a superior Python/GitHub testing framework that was adopted.")
bullet("Process discipline:", 'Enforced disciplined change processes, stopping unplanned "cowboy" changes and ensuring proper consultation and analysis.')

sub_sub("Mentoring")
def _load_mentoring_text():
    try:
        import re
        from pathlib import Path
        html = Path("index.html").read_text(encoding="utf-8")
        m = re.search(r'id="subtab-lead-mentoring"(.*?)(?:</div>\s*){3}', html, re.DOTALL)
        if m:
            block = m.group(1)
            paras = re.findall(r"<p>(.*?)</p>", block, re.DOTALL)
            cleaned = []
            for p in paras:
                t = re.sub(r"<[^>]+>", "", p).strip()
                t = re.sub(r"\s+", " ", t)
                if t:
                    cleaned.append(t)
            if cleaned:
                return " ".join(cleaned)
    except Exception as e:
        print(f"warn: mentoring parse failed: {e}")
    return None

_mentoring_html = _load_mentoring_text()
_mentoring_fallback = "Guided two juniors through their onboarding with in-depth weekly demos. Became the go-to person for things related to testing, performance, data vault and release."
bullet("Guiding juniors & newcomers:", _mentoring_html if _mentoring_html else _mentoring_fallback)

# ===== EMPLOYMENT =====
section_title("Employment")
def employment_entry(period, role, desc):
    if pdf.get_y() > 275:
        pdf.add_page()
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(*PRIMARY)
    pdf.cell(0, 4.5, sanitize(f"{period}  -  {role}"), ln=True)
    if desc:
        body(desc)

employment_entry("2018 - 2022", "Stock Trader — Self-employed", "Independent trading before transition to data engineering. Built analytical discipline and self-directed learning.")
employment_entry("Sep 2022 - Nov 2024", "Data Engineer — Argenta, Antwerpen", "Oracle tool stack. Built ETL/ELT pipelines, Data Vault & star-schema models, automated testing (Python/GitHub Actions) and Confluence documentation overhaul.")
employment_entry("Nov 2024 - Present", "Platform Engineer — Argenta, Antwerpen", "Azure Databricks stack. Airflow/AKS, Databricks Lakeflow/JDBC ingestion, dbt & governance, pytest regression testing, GitHub Actions CI/CD & release management. Little bit of Terraform.")

# ===== EDUCATION =====
section_title("Education")
sub_sub("Formal Education")
employment_entry("Sep 2008 - Jul 2012", "Bachelor of Science in Chemistry — University of Antwerp, Belgium", "")
employment_entry("Sep 2014 - Jul 2018", "Bachelor of Science in Mathematics — University of Antwerp, Belgium", "")
employment_entry("Apr 2022 - Sep 2022", "Data Science Training Program — Cevora, Belgium", "")

sub_sub("Certifications")
# --- sync cert order from index.html to avoid drift ---
def _load_certs_from_html():
    try:
        import re
        from pathlib import Path
        html = Path("index.html").read_text(encoding="utf-8")
        parts = html.split("Certifications")
        if len(parts) < 2:
            return None
        cert_section = parts[1].split("</section>")[0]
        # capture full card to extract title, date, and credential link
        card_blocks = re.findall(r'<div class="education-card">(.*?)</div>', cert_section, re.DOTALL)
        certs_parsed = []
        for block in card_blocks:
            m_title = re.search(r"<h3>(.*?)</h3>", block, re.DOTALL)
            m_date = re.search(r"<p>(.*?)</p>", block, re.DOTALL)
            m_link = re.search(r'<a\s+href="([^"]+)"', block)
            if not m_title or not m_date:
                continue
            title = re.sub(r"<[^>]+>", "", m_title.group(1)).strip()
            date = re.sub(r"<[^>]+>", "", m_date.group(1)).strip()
            title = title.replace("\u2013", "-").replace("\u2014", "-")
            link = m_link.group(1).strip() if m_link else None
            certs_parsed.append((date, title, link))
        if certs_parsed:
            return certs_parsed
    except Exception as e:
        print(f"warn: HTML cert parse failed: {e}")
    return None

_certs_html = _load_certs_from_html()
certs = _certs_html if _certs_html else [
    ("Jul 2023", "Certified Data Vault 2.0 Practitioner", "https://www.credential.net/d3e744a4-3605-43ae-bff3-290800b8cb29#acc.ihcWado1"),
    ("Dec 2023", "dbt Fundamentals", "https://credentials.getdbt.com/b6d0492c-8c7f-4d3b-8be2-840a8ed39fc0#acc.7dSCGywh"),
    ("Dec 2023", "Databricks Lakehouse Fundamentals", "https://credentials.databricks.com/bb657983-ae44-4aa7-882b-da4859f99716#acc.WP3f42QU"),
    ("Mar 2024", "Astronomer Certification - Apache Airflow Fundamentals", "https://www.credly.com/badges/4c4747cb-e8c3-44ac-9631-faebb1b53257/linked_in_profile"),
    ("2026", "Cert Prep: Scrum Master (LinkedIn Learning)", "https://www.linkedin.com/learning/certificates/4e977e33249ab9dfdcfc1badd04461b190d524196f58c1f28ae3c31fa5c2264d/"),
    ("2026", "Scrum: Advanced (LinkedIn Learning)", "https://www.linkedin.com/learning/certificates/d1aded3c4723e477229142035c1bdf3c545fcce97c038761a92196755a59e534/"),
]
# LINK color for certs
LINK_BLUE = (49, 130, 206)
for item in certs:
    if len(item) == 3:
        date, title, link = item
    else:
        date, title = item
        link = None
    if pdf.get_y() > 275:
        pdf.add_page()
    # date
    pdf.set_font("Helvetica", "B", 7.8)
    pdf.set_text_color(*PRIMARY)
    w_date = pdf.get_string_width(date + "  ")
    pdf.cell(w_date, 4, sanitize(date))
    # title (bold + blue + clickable if link present)
    if link:
        pdf.set_font("Helvetica", "B", 7.8)
        pdf.set_text_color(*LINK_BLUE)
        # underline title for affordance - need bold width
        title_s = sanitize(title)
        title_w = pdf.get_string_width(title_s)
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.cell(title_w, 4, title_s, link=link)
        # draw underline
        pdf.set_draw_color(*LINK_BLUE)
        pdf.set_line_width(0.2)
        pdf.line(x, y+3.8, x+title_w, y+3.8)
        # credential tag as small link text (keep regular for contrast)
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_x(x+title_w+2)
        pdf.cell(0, 4, " [credential]", link=link, new_x="LMARGIN", new_y="NEXT")
        # reset draw color
        pdf.set_draw_color(*BORDER)
    else:
        pdf.set_font("Helvetica", "B", 7.8)
        pdf.set_text_color(*PRIMARY)
        pdf.cell(0, 4, sanitize(title), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(0.5)

# ===== CONTACT =====
section_title("Contact")
pdf.set_font("Helvetica", "", 8)
pdf.set_text_color(*TEXT_LIGHT)
for line, link in [
    ("Phone: +32 491 12 54 20", "tel:+32491125420"),
    ("Email: suykerbuykh@gmail.com", "mailto:suykerbuykh@gmail.com"),
    ("LinkedIn: linkedin.com/in/herman-suykerbuyk-16299323b", "https://linkedin.com/in/herman-suykerbuyk-16299323b"),
    ("GitHub: github.com/Hermannnnnnnn", "https://github.com/Hermannnnnnnn"),
]:
    x = pdf.get_x()
    y = pdf.get_y()
    w = pdf.get_string_width(line)
    pdf.cell(w, 5, sanitize(line), link=link)
    # underline for link affordance
    if link:
        pdf.set_draw_color(*LINK_BLUE)
        pdf.set_line_width(0.15)
        pdf.line(x, y+4.5, x+w, y+4.5)
        pdf.set_draw_color(*BORDER)
        pdf.set_text_color(*LINK_BLUE)
    pdf.ln(5)
    pdf.set_text_color(*TEXT_LIGHT)

out_path = "assets/Herman_Suykerbuyk_CV.pdf"
pdf.output(out_path)
print(f"PDF generated: {out_path} - {pdf.pages_count} pages")
