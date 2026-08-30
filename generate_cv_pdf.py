#!/usr/bin/env python3
"""Generate Herman Suykerbuyk CV as PDF - single source of truth is index.html"""
from fpdf import FPDF
import re
import html
from pathlib import Path

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
    return t.replace("\u2014", "-").replace("\u2013", "-").replace("\u2011", "-").replace("\u2192", "->").replace("\u00a0", " ").replace("\u202f", " ").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"')

# Colors
PRIMARY = (45, 55, 72)      # #2d3748
SECONDARY = (74, 85, 104)   # #4a5568
ACCENT = (56, 178, 93)      # #38b25d
LIGHT_BG = (237, 242, 247)  # #edf2f7
BORDER = (203, 213, 224)    # #cbd5e0
TEXT_LIGHT = (113, 128, 150)

# === Single source of truth: parse index.html ===
HTML_PATH = Path(__file__).parent / "index.html"
HTML = HTML_PATH.read_text(encoding="utf-8")

def strip_tags(s: str) -> str:
    # remove tags, unescape HTML entities, normalize whitespace
    t = re.sub(r"<[^>]+>", "", s)
    t = html.unescape(t)
    return t

def norm_space(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def clean_block(block: str) -> str:
    return norm_space(strip_tags(block))

def load_about_me():
    """Parse About Me from index.html .about-section -> list of (prefix, text) where prefix may be None"""
    try:
        start = HTML.find('class="about-section"')
        end = HTML.find('class="personal-details"')
        if start == -1 or end == -1:
            return None
        block = HTML[start:end]
        paras = re.findall(r"<p>(.*?)</p>", block, re.DOTALL)
        result = []
        for p in paras:
            m = re.search(r"<b>(.*?)</b>\s*(.*)", p, re.DOTALL)
            if m:
                prefix = norm_space(strip_tags(m.group(1)))
                rest = norm_space(strip_tags(m.group(2)))
                # ensure prefix ends with colon for PDF styling
                if prefix and not prefix.endswith(":"):
                    prefix += ":"
                if rest:
                    result.append((prefix, rest))
            else:
                txt = norm_space(strip_tags(p))
                if txt:
                    result.append((None, txt))
        return result if result else None
    except Exception as e:
        print(f"warn: about_me parse failed: {e}")
        return None

def load_personal_cards():
    """Parse personal cards grid -> list of (title, text)"""
    try:
        cards = re.findall(r'<div class="personal-card">.*?<h4>(.*?)</h4>.*?<p>(.*?)</p>.*?</div>', HTML, re.DOTALL)
        out = []
        for h4, p in cards:
            title = norm_space(strip_tags(h4).replace("\U0001f4cd","").replace("\U0001f3e0","").replace("\U0001f5e3\ufe0f","").replace("\u2696\ufe0f","")).strip()
            # clean emoji prefix: original titles contain emoji, strip leading non-alpha
            title = re.sub(r'^[^\w]+', '', title).strip()
            text = norm_space(strip_tags(p))
            if title and text:
                out.append((title, text))
        return out if out else None
    except Exception as e:
        print(f"warn: personal cards parse failed: {e}")
        return None

def load_toolstack():
    """Parse toolstack -> list of (group, [tags]) preserving order"""
    try:
        groups = re.findall(r'<div class="stack-group">.*?<h4>(.*?)</h4>.*?<div class="stack-tags">(.*?)</div>', HTML, re.DOTALL)
        out = []
        for g_title, tags_block in groups:
            group = norm_space(strip_tags(g_title))
            tags = re.findall(r'<span class="stack-tag">(.*?)</span>', tags_block, re.DOTALL)
            tags = [norm_space(strip_tags(t)) for t in tags if norm_space(strip_tags(t))]
            if group and tags:
                out.append((group, tags))
        return out if out else None
    except Exception as e:
        print(f"warn: toolstack parse failed: {e}")
        return None

def load_h4_paras(h4_title: str):
    """Generic loader for any timeline <h4>title</h4> followed by <p> paragraphs until closing timeline-content.
    Handles HTML entities (&amp;) and is case-insensitive for robustness."""
    try:
        target = norm_space(h4_title).lower()
        # find all h4 blocks with their following content up to </div></div>
        for m in re.finditer(r'<h4>(.*?)</h4>(.*?)</div>\s*</div>', HTML, re.DOTALL):
            raw_h4 = m.group(1)
            block = m.group(2)
            cleaned_h4 = norm_space(strip_tags(raw_h4)).lower()
            if cleaned_h4 == target:
                paras = re.findall(r"<p>(.*?)</p>", block, re.DOTALL)
                cleaned = []
                for p in paras:
                    t = norm_space(strip_tags(p))
                    if t:
                        cleaned.append(t)
                if cleaned:
                    return " ".join(cleaned)
        # also handle headings like "Airflow & AKS" vs "Airflow" – try prefix match?
        # fallback: try escaped exact match (old logic)
        pat = re.compile(r'<h4>' + re.escape(h4_title) + r'</h4>(.*?)</div>\s*</div>', re.DOTALL)
        m = pat.search(HTML)
        if m:
            block = m.group(1)
            paras = re.findall(r"<p>(.*?)</p>", block, re.DOTALL)
            cleaned = [norm_space(strip_tags(p)) for p in paras if norm_space(strip_tags(p))]
            if cleaned:
                return " ".join(cleaned)
    except Exception as e:
        print(f"warn: h4 parse {h4_title} failed: {e}")
    return None

def load_cicd_text():
    try:
        m = re.search(r'id="subtab-pe-cicd"(.*?)(?:</div>\s*){3}', HTML, re.DOTALL)
        if m:
            block = m.group(1)
            paras = re.findall(r"<p>(.*?)</p>", block, re.DOTALL)
            cleaned = [norm_space(strip_tags(p)) for p in paras if norm_space(strip_tags(p))]
            if cleaned:
                return " ".join(cleaned)
    except Exception as e:
        print(f"warn: CI/CD parse failed: {e}")
    return None

def load_mentoring_text():
    try:
        m = re.search(r'id="subtab-lead-mentoring"(.*?)(?:</div>\s*){3}', HTML, re.DOTALL)
        if m:
            block = m.group(1)
            paras = re.findall(r"<p>(.*?)</p>", block, re.DOTALL)
            cleaned = [norm_space(strip_tags(p)) for p in paras if norm_space(strip_tags(p))]
            if cleaned:
                return " ".join(cleaned)
    except Exception as e:
        print(f"warn: mentoring parse failed: {e}")
    return None

def load_employment():
    """Parse employment timeline -> list of (period, role, desc)"""
    try:
        # isolate employment section
        sec_match = re.search(r'<section id="employment".*?>(.*?)</section>', HTML, re.DOTALL)
        if not sec_match:
            return None
        sec = sec_match.group(1)
        items = re.findall(r'<div class="timeline-item">.*?<h4>(.*?)</h4>\s*<p>(.*?)</p>', sec, re.DOTALL)
        out = []
        for h4, p in items:
            h4_clean = norm_space(strip_tags(h4))
            # h4 format: "2018 – 2022 · Stock Trader — Self-employed" or "Sep 2022 – Nov 2024 · Data Engineer — Argenta, Antwerpen"
            # split on "·"
            if "·" in h4_clean:
                period, role = [norm_space(s) for s in h4_clean.split("·", 1)]
            elif "•" in h4_clean:
                period, role = [norm_space(s) for s in h4_clean.split("•", 1)]
            else:
                # fallback: try " - " split?
                parts = h4_clean.split(" ", 2)
                period = ""
                role = h4_clean
            desc = norm_space(strip_tags(p))
            out.append((period, role, desc))
        return out if out else None
    except Exception as e:
        print(f"warn: employment parse failed: {e}")
        return None

def load_education_formal():
    try:
        # Find Formal Education grid until Certifications header
        parts = HTML.split("Formal Education")
        if len(parts) < 2:
            return None
        after = parts[1].split("Certifications")[0] if "Certifications" in parts[1] else parts[1]
        cards = re.findall(r'<div class="education-card">.*?<h3>(.*?)</h3>.*?<p>(.*?)</p>.*?<p><small>(.*?)</small></p>', after, re.DOTALL)
        out = []
        for h3,p1,p2 in cards:
            title = norm_space(strip_tags(h3))
            loc = norm_space(strip_tags(p1))
            date = norm_space(strip_tags(p2))
            if title and date:
                out.append((date, f"{title} — {loc}"))
        return out if out else None
    except Exception as e:
        print(f"warn: formal education parse failed: {e}")
        return None

def load_hero():
    """Parse hero title/subtitle/badge from index.html"""
    try:
        title_m = re.search(r'<h1 class="hero-title">(.*?)</h1>', HTML, re.DOTALL)
        subtitle_m = re.search(r'<p class="hero-subtitle">(.*?)</p>', HTML, re.DOTALL)
        badge_m = re.search(r'<div class="hero-badge">(.*?)</div>', HTML, re.DOTALL)
        title = norm_space(strip_tags(title_m.group(1))) if title_m else None
        subtitle = norm_space(strip_tags(subtitle_m.group(1))) if subtitle_m else None
        badge = norm_space(strip_tags(badge_m.group(1))) if badge_m else None
        return title, subtitle, badge
    except Exception as e:
        print(f"warn: hero parse failed: {e}")
        return None, None, None

def load_contact_lines():
    """Parse contact-info <p> lines and extract hrefs"""
    try:
        m = re.search(r'<div class="contact-info">(.*?)</div>', HTML, re.DOTALL)
        if not m:
            return None
        block = m.group(1)
        # find all <p>...</p>
        p_blocks = re.findall(r"<p>(.*?)</p>", block, re.DOTALL)
        out = []
        for pb in p_blocks:
            link_m = re.search(r'<a\s+href="([^"]+)"', pb)
            link = link_m.group(1).strip() if link_m else None
            text = norm_space(strip_tags(pb))
            if text:
                # text like "Phone: +32 491 12 54 20" or "Email: suykerbuykh@gmail.com"
                # ensure link handling: for Email/Phone we want mailto/tel, for LinkedIn/GitHub full https
                if text.lower().startswith("email") and not link:
                    # fallback
                    em = re.search(r"[\w\.-]+@[\w\.-]+", text)
                    if em:
                        link = f"mailto:{em.group(0)}"
                elif text.lower().startswith("phone") and not link:
                    # link already captured as tel:
                    pass
                elif "linkedin" in text.lower() and link and not link.startswith("http"):
                    link = "https://" + link if not link.startswith("//") else "https:" + link
                    if not link.startswith("https://"):
                        link = "https://" + link
                elif "github" in text.lower() and link and not link.startswith("http"):
                    # original is https://github.com/...
                    if "github.com" in pb.lower() and link:
                        if link.startswith("https://"):
                            pass
                        else:
                            link = "https://" + link.lstrip("/")
                out.append((text, link))
        return out if out else None
    except Exception as e:
        print(f"warn: contact parse failed: {e}")
        return None

def load_certs_from_html():
    try:
        parts = HTML.split("Certifications")
        if len(parts) < 2:
            return None
        cert_section = parts[1].split("</section>")[0]
        card_blocks = re.findall(r'<div class="education-card">(.*?)</div>', cert_section, re.DOTALL)
        certs_parsed = []
        for block in card_blocks:
            m_title = re.search(r"<h3>(.*?)</h3>", block, re.DOTALL)
            m_date = re.search(r"<p>(.*?)</p>", block, re.DOTALL)
            m_link = re.search(r'<a\s+href="([^"]+)"', block)
            if not m_title or not m_date:
                continue
            title = norm_space(strip_tags(m_title.group(1)))
            date = norm_space(strip_tags(m_date.group(1)))
            link = m_link.group(1).strip() if m_link else None
            certs_parsed.append((date, title, link))
        if certs_parsed:
            return certs_parsed
    except Exception as e:
        print(f"warn: HTML cert parse failed: {e}")
    return None

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
# Name + Title/Badge - try to derive from HTML, fallback to hardcoded
_hero_title, _hero_subtitle, _hero_badge = load_hero()
pdf.set_font("Helvetica", "B", 22)
pdf.set_text_color(*PRIMARY)
pdf.cell(0, 9, sanitize("Herman Suykerbuyk"), ln=True, align="C")
pdf.set_font("Helvetica", "B", 9)
pdf.set_text_color(*SECONDARY)
_hero_subtitle_fallback = "Business Data Engineer  |  Platform Engineer  |  Data Infrastructure  |  ETL & Pipelines"
# use subtitle from HTML if found, else fallback
_subtitle_text = _hero_subtitle if _hero_subtitle else _hero_subtitle_fallback
# subtitle in HTML is "Platform Engineer | Data Infrastructure | ETL & Pipelines" – we prepend Business...
if _hero_subtitle and "Business Data Engineer" not in _hero_subtitle:
    _subtitle_text = "Business Data Engineer  |  " + _hero_subtitle
pdf.cell(0, 5, sanitize(_subtitle_text), ln=True, align="C")
pdf.ln(1)
# Badge
pdf.set_font("Helvetica", "B", 7)
pdf.set_fill_color(*ACCENT)
pdf.set_text_color(255,255,255)
_badge_text = _hero_badge if _hero_badge else "3-5 years experience"
badge = f"  {_badge_text}  "
w = pdf.get_string_width(badge) + 6
pdf.set_x((210 - w)/2)
pdf.cell(w, 5, badge, ln=True, align="C", fill=True)
pdf.ln(2)
# Contact line - derive from HTML contact-info + header
_pdf_contact_fallback = "Mechelen, Belgium  |  +32 491 12 54 20  |  suykerbuykh@gmail.com  |  linkedin.com/in/herman-suykerbuyk-16299323b  |  github.com/Hermannnnnnnn"
_contact_lines = load_contact_lines()
if _contact_lines:
    # Build single line from contact lines: extract phone/email/linkedin/github + location from personal cards
    # Find location from personal cards for "Mechelen, Belgium"
    _cards_for_header = load_personal_cards()
    _loc = "Mechelen, Belgium"
    if _cards_for_header:
        for ct, ct_txt in _cards_for_header:
            if ct.lower() == "location":
                # extract first part before dash
                _loc = ct_txt.split("-")[0].strip().rstrip(",")
                # clean
                _loc = _loc.split(",")[0].strip() + ", Belgium" if "Mechelen" in _loc else norm_space(_loc.split("-")[0])
                # fallback to Mechelen if parse weird
                if "Mechelen" not in _loc:
                    _loc = "Mechelen, Belgium"
                else:
                    _loc = "Mechelen, Belgium"
                break
    # Build parts in fixed order: location | phone | email | linkedin | github
    _phone = _email = _linkedin = _github = None
    for txt, link in _contact_lines:
        if "phone" in txt.lower():
            _phone = txt.split(":", 1)[-1].strip()
        elif "email" in txt.lower():
            _email = txt.split(":", 1)[-1].strip()
        elif "linkedin" in txt.lower():
            li = txt.split(":", 1)[-1].strip() if ":" in txt else txt
            li = li.replace("https://", "").replace("http://","")
            _linkedin = li
        elif "github" in txt.lower():
            gh = txt.split(":", 1)[-1].strip() if ":" in txt else txt
            gh = gh.replace("https://", "").replace("http://","")
            _github = gh
    header_parts = [_loc]
    if _phone: header_parts.append(_phone)
    if _email: header_parts.append(_email)
    if _linkedin: header_parts.append(_linkedin)
    if _github: header_parts.append(_github)
    _header_line = "  |  ".join(header_parts)
else:
    _header_line = _pdf_contact_fallback
pdf.set_font("Helvetica", "", 7)
pdf.set_text_color(*TEXT_LIGHT)
pdf.cell(0, 4, sanitize(_header_line), ln=True, align="C")
# Divider
pdf.ln(2)
pdf.set_draw_color(*BORDER)
pdf.set_line_width(0.3)
pdf.line(14, pdf.get_y(), 196, pdf.get_y())
pdf.ln(4)

# ===== ABOUT ME =====
section_title("About Me")
_about = load_about_me()
if _about:
    for prefix, txt in _about:
        if prefix:
            body_with_bold_prefix(prefix, txt)
        else:
            body(txt)
else:
    # fallback (should not happen) - keep minimal
    body("Business Data Engineer with 3-5 years of experience across data engineering and platform engineering.")
    body_with_bold_prefix("Data Engineering:", "Two years building end-to-end data transformations - from ingestion pipelines to Data Vault and dimensional modelling.")
    body_with_bold_prefix("Platform Engineering:", "Two years building a new platform on Airflow, dbt and Databricks - enabling faster delivery through reliable pipelines, reusable tooling, test automation and CI/CD.")
    body_with_bold_prefix("Leadership:", "Improved how teams work: reducing unnecessary meetings, consolidating documentation, strengthening refinement sessions, challenging unsuitable frameworks, introducing future-proof solutions and Communities of Practice (COP).")

# Personal grid - 2x2
pdf.set_font("Helvetica", "B", 7)
pdf.set_text_color(*PRIMARY)
col_w = (pdf.w - 28 - 4)/2
y_start = pdf.get_y()
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

_cards = load_personal_cards()
if not _cards:
    _cards = [
        ("Location", "Based in Mechelen, Belgium - open to hybrid/remote. Willing to commute within region."),
        ("Current Circumstances", "Business Data Engineer, currently working as Platform Engineer. Open to new opportunities."),
        ("Languages", "Dutch (native), English (professional), French (basic)"),
        ("Work Preferences", "Interested in both technical depth and people leadership."),
    ]
y = pdf.get_y()
pdf.set_xy(14, y)
for i in range(0, len(_cards), 2):
    x1 = 14
    x2 = 14 + col_w + 4
    h = 14
    if pdf.get_y() + h*1.2 > 285:
        pdf.add_page()
        y = pdf.get_y()
    # ensure we have pair
    personal_card(x1, y, col_w, h, _cards[i][0], _cards[i][1] if len(_cards[i])>1 else "")
    if i+1 < len(_cards):
        personal_card(x2, y, col_w, h, _cards[i+1][0], _cards[i+1][1])
    y += h + 2
    pdf.set_y(y)
pdf.ln(2)

# ===== TOOLSTACK =====
section_title("Toolstack")
_toolstack = load_toolstack()
if _toolstack:
    for grp, tags in _toolstack:
        sub_sub(grp)
        tag_row(tags)
else:
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

# Helper to get bullet with fallback and warn if fallback used
def _bullet_h4(title_display):
    # title_display like "Pipeline Development:" -> h4 title is without colon
    h4 = title_display.rstrip(":")
    txt = load_h4_paras(h4)
    if txt:
        bullet(title_display, txt)
        return True
    return False

# Track which h4s succeeded to warn
_fallbacks_used = []

# Pipeline Development
if not _bullet_h4("Pipeline Development:"):
    _fallback = "I built and maintained end-to-end ETL pipelines: ODI (Oracle) and dbt for transformations, and IWS and Apache Airflow for orchestration. Made ways to speed up the development phase (PL/SQl scripts that generate production release script, groovy for generating ODI mappings)."
    bullet("Pipeline Development:", _fallback)
    _fallbacks_used.append("Pipeline Development")

if not _bullet_h4("Ops:"):
    _fallback = "Weekly Ops rotations. Deepened product knowledge, troubleshot production issues (e.g., mining metadata tables for root causes) and proposed several improvements to the Ops process."
    bullet("Ops:", _fallback)
    _fallbacks_used.append("Ops")

if not _bullet_h4("Transformation Logic:"):
    _fallback = 'Co-authored "Big Book of dbt": the organization\'s manual of best practices for type casting, deduplication, business-logic encapsulation, test tagging, naming conventions.'
    bullet("Transformation Logic:", _fallback)
    _fallbacks_used.append("Transformation Logic")

sub_sub("Testing")
if not _bullet_h4("Load testing:"):
    bullet("Load testing:", "Revived an underused PL/SQL testing framework: added test templates, expanded coverage beyond file ingestion, and prevented integrity issues before they reached the Data Vault and dimensional model.")
    _fallbacks_used.append("Load testing")
if not _bullet_h4("Unit & regression testing:"):
    bullet("Unit & regression testing:", "Built an automated testing tool in Python with GitHub, CI/CD and Python. The framework runs a comprehensive suite of tests on source ingestion (source to Data Vault) or presentation (Data Vault to dimensional model) and is still used today, replacing the tedious manual testing cycle. Found many data issues, sped up testing and increased business trust in the data.")
    _fallbacks_used.append("Unit & regression testing")

sub_sub("Modeling")
if not _bullet_h4("Data Vault & Dimensional:"):
    bullet("Data Vault & Dimensional:", "Delivered end-to-end solutions from ingestion through Data Vault to dimensional modelling (dimensions/facts, star schema).")
    _fallbacks_used.append("Data Vault & Dimensional")

sub_sub("Documenting")
if not _bullet_h4("Revamping:"):
    bullet("Revamping:", "Found documentation scattered and often outdated. Consolidated in Confluence, rewrote what I could and delegated the rest.")
    _fallbacks_used.append("Revamping")
if not _bullet_h4("Expanding:"):
    bullet("Expanding:", "Authored numerous pages to standardise way of working and help future newcomers onboard faster.")
    _fallbacks_used.append("Expanding")

# Platform Engineering
sub_heading("Platform Engineering")
sub_sub("Testing")
if not _bullet_h4("Infra Regression Testing:"):
    # try alternate case "Infra regression Testing" if first fails (handled by exact match, but HTML has "Infra Regression Testing")
    if not _bullet_h4("Infra regression Testing:"):
        bullet("Infra Regression Testing:", "Took ownership of a pytest regression testing framework for platform components during infra releases. Added tests and refactored codebase with fixtures, modules and markers.")
        _fallbacks_used.append("Infra Regression Testing")
if not _bullet_h4("Codebase Testing:"):
    if not _bullet_h4("Code-base Testing:"):
        bullet("Codebase Testing:", "Implemented and owned dbt-bouncer and SQLFluff for defining and enforcing coding standards in CI/CD.")
        _fallbacks_used.append("Codebase Testing")
if not _bullet_h4("Data quality:"):
    bullet("Data quality:", "Helped build a framework that pulls test definitions from Collibra, saves them as dbt tests, deploys to production, runs the tests and reports results.")
    _fallbacks_used.append("Data quality")

sub_sub("Tooling")
if not _bullet_h4("dbt:"):
    _fallback = "Wrote macros and materialisation overrides for organisation-wide use. Performed package upgrades, worked out the kinks and supported data colleagues. Found ways to improve, like reduced parsing time and reduced API calls to Databricks. Advocated and lobbied for dbt-bouncer and SQLFluff. Brought it to maturity from beginning to end: worked with data team colleagues to determine the standards, implemented these standards and enforced them through CI/CD, documented how the tools work and how to configure VS Code for local use."
    bullet("dbt:", _fallback)
    _fallbacks_used.append("dbt")

if not _bullet_h4("Airflow & AKS:"):
    if not _bullet_h4("Airflow:"):
        bullet("Airflow & AKS:", "Wrote Airflow operators and helped build the orchestration framework: a semantic layer on top of Airflow. Data colleagues write YAML with templated tasks instead of raw Airflow code. Improved stability by tuning pod resources, queue setup, and Cosmos WATCHER mode for heavy dbt DAGs. Implemented PVCs, PVC mounts in Airflow Helm, secret scopes and service connections.")
        _fallbacks_used.append("Airflow & AKS")

if not _bullet_h4("Databricks:"):
    _fallback = "Developed a Lakeflow Pipelines framework for SQL Server ingestion. Built an ingestion framework for on-prem Oracle databases to databricks using Spark JDBC. Co-built a trial environment: before release to production, we shallow-clone production data to trial, deploy the release there and run our DAGs. This catches issues before causing incidents on production. Investigated cost spikes and failing SQL queries caused by excessive Unity Catalog API calls."
    bullet("Databricks:", _fallback)
    _fallbacks_used.append("Databricks")

sub_sub("CI/CD")
_cicd_html = load_cicd_text()
if _cicd_html:
    bullet("GitHub Actions & release management:", _cicd_html)
else:
    _fallback = "Implemented PR validations (SQLFluff, dbt-bouncer, YAML schema) and branch protection. Suggested and built a deploy-branch strategy for concurrent deployments to the same test environment. Brought release management to maturity: built a pipeline to generate releases and release notes, implemented automatic labeling of pull requests with dataproduct tags, offering stakeholders an insight into what changed by the overview in release notes which was grouped per data product."
    bullet("GitHub Actions & release management:", _fallback)
    _fallbacks_used.append("CI/CD")

# Lead Team
sub_heading("Lead / Team")
sub_sub("Way of Working")
if not _bullet_h4("Team Efficiency:"):
    bullet("Team Efficiency:", "Drove organisational change. In first team: reduced unnecessary meetings, introduced Communities of Practice, challenged push for unsuitable framework. In second team: advocated better feature refinement (named stakeholders, consultation, demos) and more demos due to poorly T-shaped team.")
    _fallbacks_used.append("Team Efficiency")

sub_sub("Future-proofing")
if not _bullet_h4("Sustainable Solutions:"):
    bullet("Sustainable Solutions:", "Reversed a management-preferred Gherkin/Java decision by delivering a superior Python/GitHub testing framework that was adopted.")
    _fallbacks_used.append("Sustainable Solutions")
if not _bullet_h4("Process discipline:"):
    bullet("Process discipline:", 'Enforced disciplined change processes, stopping unplanned "cowboy" changes and ensuring proper consultation and analysis.')
    _fallbacks_used.append("Process discipline")

sub_sub("Mentoring")
_mentoring_html = load_mentoring_text()
if _mentoring_html:
    bullet("Guiding juniors & newcomers:", _mentoring_html)
else:
    _fallback = "Guided two juniors through their onboarding with in-depth weekly demos. Became the go-to person for things related to testing, performance, data vault and release."
    bullet("Guiding juniors & newcomers:", _fallback)
    _fallbacks_used.append("Mentoring")

if _fallbacks_used:
    print(f"warn: used fallbacks for {', '.join(_fallbacks_used)} - consider updating index.html or parser")

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

_emp = load_employment()
if _emp:
    for period, role, desc in _emp:
        employment_entry(period, role, desc)
else:
    employment_entry("2018 - 2022", "Stock Trader — Self-employed", "Independent trading before transition to data engineering. Built analytical discipline and self-directed learning.")
    employment_entry("Sep 2022 - Nov 2024", "Data Engineer — Argenta, Antwerpen", "Oracle tool stack. Built ETL/ELT pipelines, Data Vault & star-schema models, automated testing (Python/GitHub Actions) and Confluence documentation overhaul.")
    employment_entry("Nov 2024 - Present", "Platform Engineer — Argenta, Antwerpen", "Azure Databricks stack. Airflow/AKS, Databricks Lakeflow/JDBC ingestion, dbt & governance, pytest regression testing, GitHub Actions CI/CD & release management. Little bit of Terraform.")

# ===== EDUCATION =====
section_title("Education")
sub_sub("Formal Education")
_formal = load_education_formal()
if _formal:
    for date, title in _formal:
        employment_entry(date, title, "")
else:
    employment_entry("Sep 2008 - Jul 2012", "Bachelor of Science in Chemistry — University of Antwerp, Belgium", "")
    employment_entry("Sep 2014 - Jul 2018", "Bachelor of Science in Mathematics — University of Antwerp, Belgium", "")
    employment_entry("Apr 2022 - Sep 2022", "Data Science Training Program — Cevora, Belgium", "")

sub_sub("Certifications")
_certs_html = load_certs_from_html()
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
        title_s = sanitize(title)
        title_w = pdf.get_string_width(title_s)
        x = pdf.get_x()
        y = pdf.get_y()
        pdf.cell(title_w, 4, title_s, link=link)
        # draw underline
        pdf.set_draw_color(*LINK_BLUE)
        pdf.set_line_width(0.2)
        pdf.line(x, y+3.8, x+title_w, y+3.8)
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_x(x+title_w+2)
        pdf.cell(0, 4, " [credential]", link=link, new_x="LMARGIN", new_y="NEXT")
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
_contact_for_pdf = load_contact_lines()
if _contact_for_pdf:
    # Build list preserving order as in HTML
    for line_text, link in _contact_for_pdf:
        x = pdf.get_x()
        y = pdf.get_y()
        w = pdf.get_string_width(line_text)
        pdf.cell(w, 5, sanitize(line_text), link=link)
        if link:
            pdf.set_draw_color(*LINK_BLUE)
            pdf.set_line_width(0.15)
            pdf.line(x, y+4.5, x+w, y+4.5)
            pdf.set_draw_color(*BORDER)
            pdf.set_text_color(*LINK_BLUE)
        pdf.ln(5)
        pdf.set_text_color(*TEXT_LIGHT)
else:
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
if _fallbacks_used:
    print(f"WARNING: fallbacks used for {', '.join(_fallbacks_used)}")
