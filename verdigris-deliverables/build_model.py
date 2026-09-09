"""Build Verdigris_Economics_Model.xlsx — traditional lender vs AI-native lender, same loan book."""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter

FONT = "Arial"
BLUE = Font(name=FONT, color="0000FF", size=10)
BLACK = Font(name=FONT, color="000000", size=10)
GREEN = Font(name=FONT, color="008000", size=10)
BOLD = Font(name=FONT, bold=True, size=10)
H1 = Font(name=FONT, bold=True, size=14, color="1F4E48")
H2 = Font(name=FONT, bold=True, size=11, color="FFFFFF")
NOTE = Font(name=FONT, italic=True, size=9, color="555555")
HDR_FILL = PatternFill("solid", fgColor="1F4E48")
SUB_FILL = PatternFill("solid", fgColor="D9E8E4")
YELLOW = PatternFill("solid", fgColor="FFFF00")
TOTAL_FILL = PatternFill("solid", fgColor="EAF2EF")
thin = Side(style="thin", color="BBBBBB")
BOX = Border(top=thin, bottom=thin, left=thin, right=thin)

GBP = '£#,##0;(£#,##0);-'
GBPk = '£#,##0.0,"k";(£#,##0.0,"k");-'
GBPm = '£#,##0.00,,"m";(£#,##0.00,,"m");-'
PCT = '0.0%;(0.0%);-'
PCT2 = '0.00%;(0.00%);-'
NUM = '#,##0;(#,##0);-'
NUM1 = '#,##0.0;(#,##0.0);-'
X = '0.0"x"'

wb = Workbook()

def setw(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

def header(ws, row, cols, texts):
    for c, t in zip(cols, texts):
        cell = ws.cell(row=row, column=c, value=t)
        cell.font = H2; cell.fill = HDR_FILL; cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

def label(ws, r, c, text, bold=False):
    cell = ws.cell(row=r, column=c, value=text); cell.font = BOLD if bold else BLACK; return cell

def inp(ws, r, c, val, fmt=None, note=None, key=False):
    cell = ws.cell(row=r, column=c, value=val); cell.font = BLUE
    if fmt: cell.number_format = fmt
    if key: cell.fill = YELLOW
    if note: cell.comment = Comment(note, "Verdigris model")
    return cell

def fx(ws, r, c, formula, fmt=None, bold=False, link=False):
    cell = ws.cell(row=r, column=c, value=formula)
    cell.font = Font(name=FONT, bold=bold, size=10, color=("008000" if link else "000000"))
    if fmt: cell.number_format = fmt
    return cell

# =====================================================================
# Sheet 1: README
# =====================================================================
ws = wb.active; ws.title = "Read me"
setw(ws, [3, 110])
ws["B2"] = "Verdigris — Economics Model: traditional bridging lender vs AI-native lender"; ws["B2"].font = H1
lines = [
    "Purpose: compare the cost structure of a typical mid-size UK bridging lender ('Northgate Bridging', a fictional composite) with an AI-native lender ('Verdigris') running the SAME loan book, then show how each scales.",
    "",
    "How to use",
    "• Blue text = input you can change. Yellow fill = the key assumptions that drive the answer. Black = formula. Green = link from another sheet.",
    "• Change inputs only on the 'Assumptions' sheet and the two Headcount sheets. Everything else recalculates.",
    "• Every input has a cell comment saying where it came from (public source, founder estimate, or research benchmark). Hover to read it.",
    "",
    "Sheets",
    "1. Assumptions — loan book, pricing, fees, funding cost, losses, on-costs, AI cost per case.",
    "2. Headcount — Traditional — 36-person team by function, salary, bonus, fully loaded cost.",
    "3. Headcount — AI-native — 8-person team doing the same book with AI agents.",
    "4. Revenue — revenue build for the loan book (identical for both models).",
    "5. Comparison — P&L side by side, cost per loan, margin, and the scaling table (£150m → £600m book).",
    "6. Per-case cost — what it costs to underwrite ONE case, human vs AI-assisted.",
    "7. Sources — where every number came from, with URLs.",
    "",
    "Status of the numbers",
    "• Salary bands: 2025–26 London job ads and salary guides (see Sources). C-suite bands are estimates.",
    "• Loan book, loan size, completions: founder estimate calibrated to public market data (BDLA avg loan £540k; ~25 loans per analyst per year).",
    "• Pricing: market rates (0.81–0.84%/month average, Bridging Trends 2025–26). Arrangement fee and broker fee are market-typical assumptions.",
    "• AI cost per case: computed from Anthropic list prices (June 2026) and typical document volumes; a 10x safety factor is applied.",
    "• Nothing in this model is a claim about any specific company. 'Northgate Bridging' is a composite.",
    "",
    "Built 9 September 2026.",
]
for i, t in enumerate(lines, 4):
    c = ws.cell(row=i, column=2, value=t)
    c.font = BOLD if t in ("How to use", "Sheets", "Status of the numbers") else BLACK
    c.alignment = Alignment(wrap_text=True, vertical="top")

# =====================================================================
# Sheet 2: Assumptions
# =====================================================================
A = wb.create_sheet("Assumptions")
setw(A, [3, 46, 16, 12, 70])
A["B2"] = "Assumptions — all inputs in blue; yellow = key drivers"; A["B2"].font = H1
header(A, 4, [2, 3, 4, 5], ["Item", "Value", "Unit", "Basis / source"])

rows = [
    # (label, value, fmt, unit, note, key)
    ("LOAN BOOK", None, None, None, None, False),
    ("Live loan book (average)", 150_000_000, GBP, "£", "Founder estimate for a ~35-person lender; consistent with £3–10m book per employee benchmark (Octane, Hope, Tuscan) and est. £120–320m for the comparator.", True),
    ("Average loan size", 650_000, GBP, "£", "Founder data: pipeline tracker Jan 2026 shows facilities £205k–£1.59m, median ≈ £440k; development loans larger; CV: typically £500k–£1m. BDLA market average £540k.", True),
    ("Average term", 12, NUM, "months", "Bridging Trends 2025 average term 12 months; founder calculator example 18 months (refurb).", False),
    ("Loans completed per year", "=ROUND(C6/C7*12/C8,0)", NUM, "loans", "Book ÷ avg loan × 12 ÷ term. ~240 → ~24 per underwriter with 10 in credit, matching ~25 loans/yr per analyst.", False),
    ("Annual originations (£)", "=C9*C7", GBP, "£", "Loans × average loan size.", False),
    ("Applications assessed per completed loan", 4, NUM1, "x", "Founder estimate: pipeline of 15–23 live cases vs ~2 completions/month per analyst → roughly 1 in 4 assessed cases completes.", False),
    ("Cases assessed per year", "=C9*C11", NUM, "cases", "Every assessed case costs underwriting effort whether or not it completes.", False),
    ("PRICING & REVENUE", None, None, None, None, False),
    ("Borrower interest rate (monthly)", 0.0090, PCT2, "% / month", "Founder calculator: 0.95%/month fixed on a medium refurb (variable option BoE 4.25% + 0.51%/mo = 10.37% pa). Market average 0.81–0.84% (Bridging Trends). 0.90% blended used.", True),
    ("Borrower interest rate (annualised, simple)", "=C14*12", PCT, "% pa", "Simple ×12. Founder calculator effective rate 11.98% pa on 0.95%/mo.", False),
    ("Arrangement fee charged to borrower", 0.02, PCT, "% of loan", "Founder calculator: 2% of gross loan ('Lender & Broker Fee').", True),
    ("Arrangement fee retained by lender (after introducer share)", 0.005, PCT, "% of loan", "Founder calculator: on the example deal 0% retained, 2% paid as 'introducer share'. Founder: broker payout 1–2%. 0.5% retained assumed — change if your typical split differs.", True),
    ("Admin fee per loan (retained)", 1500, GBP, "£", "Founder calculator: £1,995 (<£100k), £1,500 (£100–250k), £1,250 (>£250k) automatic admin fee. £1,500 blended.", False),
    ("Redemption + drawdown fees per loan", 1500, GBP, "£", "Founder calculator: redemption fee £495; drawdown fee £295/month on refurb/development. ~£1,500 per loan blended.", False),
    ("Exit fee", 0.0, PCT, "% of loan", "Founder calculator: 0%. Some lenders charge 0–1%.", False),
    ("Other fees (extension, variation, non-redemption)", 0.002, PCT, "% of originations", "Founder estimate; extension/variation fees exist but are not systematic.", False),
    ("Share of loans introduced by brokers", 0.85, PCT, "%", "BDLA/Interpath 2026 survey: 61% of lenders name brokers as primary channel, 15% direct → ~85% broker-introduced. Broker fee is already netted in 'retained' above.", False),
    ("FUNDING & RISK", None, None, None, None, False),
    ("Funding partner buy rate (cost of funds, annual)", 0.0875, PCT2, "% pa", "Founder calculator rate card: institutional partner 8.25–9.75% depending on product and advance rate (8.75% on the example); bank line = BoE + 4.3–4.8%. 8.75% used.", True),
    ("Share of book funded by partners", 0.95, PCT, "%", "Founder calculator: partner advance rate 95%, lender first-loss 5%.", False),
    ("Funder fee per loan", 500, GBP, "£", "Founder calculator: £500 partner fee per deal.", False),
    ("Expected credit loss (annual, % of book)", 0.005, PCT2, "% pa", "Founder estimate; comparator claims 0 capital losses over 7 years; BDLA default rates typically <1%. 0.5% is prudent.", True),
    ("EMPLOYMENT ON-COSTS (2026/27)", None, None, None, None, False),
    ("Employer National Insurance rate", 0.15, PCT, "%", "15% above secondary threshold (unchanged from April 2025).", False),
    ("NI secondary threshold", 5000, GBP, "£ pa", "£5,000 per employee per year, frozen to 2030–31.", False),
    ("Employer pension contribution", 0.05, PCT, "% of salary", "Auto-enrolment minimum 3%; 5% typical for a financial-services employer.", False),
    ("Other on-costs (benefits, kit, recruitment, software seats)", 0.08, PCT, "% of salary", "All-in multiplier 1.25–1.4x is typical (Grove HR); NI 15% + pension 5% + 8% other ≈ 1.28x.", False),
    ("Office cost per desk per year", 9600, GBP, "£ pa", "London serviced office £700–900/desk/month City; £800 used.", False),
    ("Software & data per employee per year", 3000, GBP, "£ pa", "CRM/LOS seat £1–3k plus general tooling.", False),
    ("AI-NATIVE OPERATING COSTS", None, None, None, None, False),
    ("Model (LLM) cost per assessed case", 16, GBP, "£", "Anthropic list prices Jun 2026: Opus 5 $5/$25 per M tokens; ~300k input + 20k output tokens per case ≈ $2. ×10 safety factor for retries, tools, re-underwrites, evals = $20 ≈ £16 at $1.30/£.", True),
    ("Data & verification per assessed case", 50, GBP, "£", "Land Registry £7/doc (£14–28), KYC £2–6, company credit £5–15, AVM £10–25, consumer credit £1–5 → £40–80.", False),
    ("Platform, hosting, monitoring per year", 60000, GBP, "£ pa", "Founder estimate: cloud, observability, model evals, security tooling for a regulated lender.", False),
    ("Human review time per assessed case (AI-native)", 1.5, NUM1, "hours", "Underwriter reviews the AI-drafted pack and decides. Founder estimate.", False),
    ("Underwriter time per assessed case (traditional)", 12, NUM1, "hours", "Founder estimate: 15–23 live cases, ~2 completions/month, ~50% of week on document work. Includes reading, reconciling, chasing, credit paper.", True),
    ("Working hours per FTE per year", 1650, NUM, "hours", "37.5 h/week × 44 productive weeks.", False),
]
r = 5
addr = {}
for lab, val, fmt, unit, note, key in rows:
    if val is None:
        c = A.cell(row=r, column=2, value=lab); c.font = BOLD; c.fill = SUB_FILL
        for col in (3, 4, 5): A.cell(row=r, column=col).fill = SUB_FILL
    else:
        label(A, r, 2, lab)
        if isinstance(val, str) and val.startswith("="):
            fx(A, r, 3, val, fmt)
        else:
            inp(A, r, 3, val, fmt, None, key)
        A.cell(row=r, column=4, value=unit).font = NOTE
        n = A.cell(row=r, column=5, value=note); n.font = NOTE; n.alignment = Alignment(wrap_text=True, vertical="top")
        addr[lab] = f"Assumptions!$C${r}"
    r += 1
for rr in range(5, r):
    A.row_dimensions[rr].height = 30 if A.cell(row=rr, column=5).value else 16

# Convenience names
BOOK = addr["Live loan book (average)"]
LOANS = addr["Loans completed per year"]
ORIG = addr["Annual originations (£)"]
CASES = addr["Cases assessed per year"]
RATE_M = addr["Borrower interest rate (monthly)"]
RATE_A = addr["Borrower interest rate (annualised, simple)"]
ARR = addr["Arrangement fee charged to borrower"]
ARR_RET = addr["Arrangement fee retained by lender (after introducer share)"]
ADMIN_FEE = addr["Admin fee per loan (retained)"]
REDEMP_FEE = addr["Redemption + drawdown fees per loan"]
EXIT = addr["Exit fee"]
OTHER = addr["Other fees (extension, variation, non-redemption)"]
BROKER_SHARE = addr["Share of loans introduced by brokers"]
COF = addr["Funding partner buy rate (cost of funds, annual)"]
FUND_SHARE = addr["Share of book funded by partners"]
FUNDER_FEE = addr["Funder fee per loan"]
ECL = addr["Expected credit loss (annual, % of book)"]
NI = addr["Employer National Insurance rate"]
NI_T = addr["NI secondary threshold"]
PENS = addr["Employer pension contribution"]
OTH = addr["Other on-costs (benefits, kit, recruitment, software seats)"]
DESK = addr["Office cost per desk per year"]
SOFT = addr["Software & data per employee per year"]
AI_CASE = addr["Model (LLM) cost per assessed case"]
DATA_CASE = addr["Data & verification per assessed case"]
PLATFORM = addr["Platform, hosting, monitoring per year"]
REV_HRS = addr["Human review time per assessed case (AI-native)"]
UW_HRS = addr["Underwriter time per assessed case (traditional)"]
FTE_HRS = addr["Working hours per FTE per year"]

# =====================================================================
# Headcount sheets (shared builder)
# =====================================================================
def headcount_sheet(name, title, team, intro):
    H = wb.create_sheet(name)
    setw(H, [3, 22, 34, 8, 14, 10, 14, 14, 14, 14, 16, 40])
    H["B2"] = title; H["B2"].font = H1
    H["B3"] = intro; H["B3"].font = NOTE
    header(H, 5, range(2, 13), ["Function", "Role", "FTE", "Base salary (each)", "Bonus %", "Base total", "Bonus total", "Employer NI", "Pension + other", "Fully loaded cost", "Basis"])
    r = 6
    first = r
    for func, role, fte, base, bonus, basis in team:
        label(H, r, 2, func)
        label(H, r, 3, role)
        inp(H, r, 4, fte, NUM1)
        inp(H, r, 5, base, GBP, basis)
        inp(H, r, 6, bonus, PCT)
        fx(H, r, 7, f"=D{r}*E{r}", GBP)
        fx(H, r, 8, f"=G{r}*F{r}", GBP)
        fx(H, r, 9, f"=MAX(0,(E{r}+E{r}*F{r})-{NI_T})*{NI}*D{r}", GBP)
        fx(H, r, 10, f"=(G{r}+H{r})*({PENS}+{OTH})", GBP)
        fx(H, r, 11, f"=G{r}+H{r}+I{r}+J{r}", GBP)
        n = H.cell(row=r, column=12, value=basis); n.font = NOTE
        r += 1
    last = r - 1
    # totals
    label(H, r, 2, "TOTAL PEOPLE COST", True)
    for col, letter in ((4, "D"), (7, "G"), (8, "H"), (9, "I"), (10, "J"), (11, "K")):
        c = fx(H, r, col, f"=SUM({letter}{first}:{letter}{last})", NUM1 if col == 4 else GBP, bold=True); c.fill = TOTAL_FILL
    tot_row = r
    r += 2
    label(H, r, 2, "Office (desks × cost per desk)"); fx(H, r, 11, f"=D{tot_row}*{DESK}", GBP, link=True); off_row = r; r += 1
    label(H, r, 2, "Software & data seats"); fx(H, r, 11, f"=D{tot_row}*{SOFT}", GBP, link=True); soft_row = r; r += 1
    return H, tot_row, off_row, soft_row, first, last

trad_team = [
    ("Credit", "Head of Credit", 1, 115000, 0.25, "Head of Credit, bridging/dev lender London £100–130k (jobsite; Morgan McKinley). EST."),
    ("Credit", "Senior underwriter (bridging + development)", 2, 75000, 0.15, "Senior bridging UW £70–80k + 10–20% (exec-appointments; Fintelligent)."),
    ("Credit", "Credit analyst / underwriter (mid)", 4, 55000, 0.15, "Mid UW £45–65k + 10–20% (Tandem; Fintelligent job ads)."),
    ("Credit", "Junior credit analyst", 3, 37500, 0.05, "Junior bridging UW £30–45k (Fame Recruitment ad; talent.com)."),
    ("Portfolio", "Portfolio manager", 1, 57500, 0.125, "Portfolio Manager bridging up to £60–65k + bonus (Reed; Fintelligent)."),
    ("Portfolio", "Completions / case manager", 3, 42500, 0.05, "Completions specialist up to £40k (+London uplift); case manager £30–35k (NRG)."),
    ("Portfolio", "Loan administrator / servicing", 4, 32000, 0.025, "Loan admin £26–38k London (Indeed; PayScale)."),
    ("Sales", "Head of Sales", 1, 110000, 0.35, "Head of Sales London avg £104k, 30–40% variable (Glassdoor; sales-director norm). EST."),
    ("Sales", "Senior BDM / originator", 2, 85000, 0.60, "Originator £75–85k + bonus up to 100% (Fintelligent); £90k + uncapped (jobsite)."),
    ("Sales", "BDM", 3, 65000, 0.40, "BDM bridging up to £65k + 20% bonus; £60–80k + OTE 1.3–1.8x (Fintelligent; Totaljobs)."),
    ("Marketing", "Marketing manager", 1, 48000, 0.075, "Marketing manager London avg £48k (Glassdoor)."),
    ("Marketing", "Marketing executive", 3, 36000, 0.025, "Marketing executive London avg £36k (Glassdoor)."),
    ("Management", "CEO / Managing Director", 1, 200000, 0.40, "CEO <£50m revenue £150–250k, 30–50% bonus (Exec Capital). EST."),
    ("Management", "CFO / Finance Director", 1, 140000, 0.225, "SME CFO £110–170k with FS premium (FD Capital). EST."),
    ("Management", "COO / Operations Director", 1, 100000, 0.225, "Ops Director £80–120k + 15–30% (Exec Capital). EST."),
    ("Management", "CTO / Head of Technology", 1, 115000, 0.15, "Head of Technology London avg £114k (Glassdoor). EST."),
    ("Management", "Compliance officer (SMF16/17)", 1, 67500, 0.125, "Compliance Officer London £60–75k (Morgan McKinley 2026)."),
    ("Technology", "Software engineer / IT", 4, 65000, 0.05, "Software engineer London mid £50–80k (Glassdoor)."),
]
T, T_tot, T_off, T_soft, T_first, T_last = headcount_sheet(
    "Headcount - Traditional",
    "Northgate Bridging (composite) — 36-person traditional lender",
    trad_team,
    "Team shape from founder's knowledge of a typical mid-size lender: 10 credit, 8 portfolio, 6 sales, 4 marketing, 5 management, 4 tech. Salaries = London 2025–26 benchmarks (see Sources).")

ai_team = [
    ("Leadership", "CEO / Head of Credit (founder, underwrites)", 1, 100000, 0.0, "Founder salary — below market by design at seed stage."),
    ("Leadership", "CTO (technical co-founder)", 1, 100000, 0.0, "Founder salary — below market by design at seed stage."),
    ("Credit", "Senior underwriter (human-in-the-loop)", 2, 75000, 0.15, "Same band as traditional senior UW. Reviews AI-drafted packs, owns the decision."),
    ("Operations", "Completions & servicing lead", 1, 42500, 0.05, "One person runs completions and servicing with automated workflow."),
    ("Compliance", "Compliance officer (SMF16/17)", 1, 67500, 0.125, "Regulated lender needs one regardless of size."),
    ("Sales", "BDM / broker relationships", 1, 65000, 0.40, "One BDM; brokers still introduce ~85% of flow."),
    ("Technology", "Software / ML engineer", 1, 65000, 0.05, "Maintains pipelines, evals, integrations."),
]
V, V_tot, V_off, V_soft, V_first, V_last = headcount_sheet(
    "Headcount - AI-native",
    "Verdigris — 8-person AI-native lender running the same book",
    ai_team,
    "AI agents do document reading, extraction, reconciliation, drafting, chasing and monitoring. Humans decide, sign off, and own relationships and compliance.")

# AI operating costs block on AI sheet
r = V_soft + 1
label(V, r, 2, "AI model cost (cases × £ per case)"); fx(V, r, 11, f"={CASES}*{AI_CASE}", GBP, link=True); V_ai = r; r += 1
label(V, r, 2, "Data & verification (cases × £ per case)"); fx(V, r, 11, f"={CASES}*{DATA_CASE}", GBP, link=True); V_data = r; r += 1
label(V, r, 2, "Platform, hosting, monitoring"); fx(V, r, 11, f"={PLATFORM}", GBP, link=True); V_plat = r; r += 1

# Traditional also incurs data costs per case (they buy the same searches)
r = T_soft + 1
label(T, r, 2, "Data & verification (cases × £ per case)"); fx(T, r, 11, f"={CASES}*{DATA_CASE}", GBP, link=True); T_data = r; r += 1

# =====================================================================
# Revenue sheet
# =====================================================================
R = wb.create_sheet("Revenue")
setw(R, [3, 52, 18, 60])
R["B2"] = "Revenue build — identical for both models (same book, same pricing)"; R["B2"].font = H1
header(R, 4, [2, 3, 4], ["Line", "£ per year", "Formula / note"])
rev_rows = [
    ("Annual originations", f"={ORIG}", "Loans × average loan size", GBP),
    ("Average live loan book", f"={BOOK}", "", GBP),
    ("", None, "", None),
    ("Arrangement fee charged (gross)", f"=C5*{ARR}", "Originations × arrangement fee %", GBP),
    ("Less: introducer / broker share of arrangement fee", f"=-C5*({ARR}-{ARR_RET})*{BROKER_SHARE}", "Paid away to brokers on broker-introduced loans", GBP),
    ("Gross interest income", f"=C6*{RATE_A}", "Book × annualised borrower rate", GBP),
    ("Admin, drawdown and redemption fees", f"={LOANS}*({ADMIN_FEE}+{REDEMP_FEE})", "Loans × (admin fee + redemption/drawdown fees)", GBP),
    ("Exit fee income", f"=C5*{EXIT}", "Originations × exit fee %", GBP),
    ("Other fee income", f"=C5*{OTHER}", "Extensions, variations, non-redemption", GBP),
    ("GROSS REVENUE (after broker share)", "=SUM(C8:C13)", "", GBP),
    ("", None, "", None),
    ("Less: cost of funds (funding partner buy rate)", f"=-C6*{FUND_SHARE}*{COF}", "Book × partner-funded share × buy rate", GBP),
    ("Less: funder fees", f"=-{LOANS}*{FUNDER_FEE}", "Loans × partner fee per deal", GBP),
    ("Less: expected credit losses", f"=-C6*{ECL}", "Book × annual loss rate", GBP),
    ("NET REVENUE (after funding, brokers, losses)", "=C14+SUM(C16:C18)", "This is what has to pay for people, premises and technology", GBP),
    ("", None, "", None),
    ("Net revenue as % of book", "=C19/C6", "", PCT),
    ("Net revenue per completed loan", f"=C19/{LOANS}", "", GBP),
    ("Net interest margin (% of book)", f"=(C10+C16)/C6", "Gross interest less cost of funds. Founder calculator example: 3.4% of facility over 18 months.", PCT),
]
r = 5
for lab, f, note, fmt in rev_rows:
    if lab:
        bold = lab.isupper()
        label(R, r, 2, lab, bold)
        c = fx(R, r, 3, f, fmt, bold=bold, link=f.startswith("=Assumptions") if f else False)
        if bold: c.fill = TOTAL_FILL; R.cell(row=r, column=2).fill = TOTAL_FILL
        R.cell(row=r, column=4, value=note).font = NOTE
    r += 1

# =====================================================================
# Comparison sheet
# =====================================================================
C = wb.create_sheet("Comparison")
setw(C, [3, 46, 18, 18, 16, 50])
C["B2"] = "Same loan book, two operating models"; C["B2"].font = H1
header(C, 4, [2, 3, 4, 5, 6], ["", "Northgate Bridging (traditional)", "Verdigris (AI-native)", "Difference", "Note"])
cmp_rows = [
    ("Headcount (FTE)", f"='Headcount - Traditional'!D{T_tot}", f"='Headcount - AI-native'!D{V_tot}", NUM1),
    ("People cost (fully loaded)", f"='Headcount - Traditional'!K{T_tot}", f"='Headcount - AI-native'!K{V_tot}", GBP),
    ("Office", f"='Headcount - Traditional'!K{T_off}", f"='Headcount - AI-native'!K{V_off}", GBP),
    ("Software & data seats", f"='Headcount - Traditional'!K{T_soft}", f"='Headcount - AI-native'!K{V_soft}", GBP),
    ("Data & verification per case", f"='Headcount - Traditional'!K{T_data}", f"='Headcount - AI-native'!K{V_data}", GBP),
    ("AI model cost", "=0", f"='Headcount - AI-native'!K{V_ai}", GBP),
    ("Platform, hosting, monitoring", "=0", f"='Headcount - AI-native'!K{V_plat}", GBP),
    ("TOTAL OPERATING COST", "=SUM(C6:C11)", "=SUM(D6:D11)", GBP),
    ("", None, None, None),
    ("Net revenue (from Revenue sheet)", "=Revenue!C19", "=Revenue!C19", GBP),
    ("OPERATING PROFIT (before tax)", "=C14-C12", "=D14-D12", GBP),
    ("Operating margin (% of net revenue)", "=C15/C14", "=D15/D14", PCT),
    ("", None, None, None),
    ("Loans completed per year", f"={LOANS}", f"={LOANS}", NUM),
    ("Operating cost per completed loan", f"=C12/{LOANS}", f"=D12/{LOANS}", GBP),
    ("Operating cost as % of originations", f"=C12/{ORIG}", f"=D12/{ORIG}", PCT2),
    ("Loan book per employee", f"={BOOK}/C5", f"={BOOK}/D5", GBP),
    ("Loans completed per employee per year", f"={LOANS}/C5", f"={LOANS}/D5", NUM1),
]
r = 5
for lab, f1, f2, fmt in cmp_rows:
    if lab:
        bold = lab.isupper()
        label(C, r, 2, lab, bold)
        c1 = fx(C, r, 3, f1, fmt, bold=bold, link=True)
        c2 = fx(C, r, 4, f2, fmt, bold=bold, link=True)
        if fmt in (GBP, NUM1, NUM, PCT, PCT2) and lab not in ("Loans completed per year",):
            d = fx(C, r, 5, f"=D{r}-C{r}", fmt, bold=bold)
        if bold:
            for col in (2, 3, 4, 5): C.cell(row=r, column=col).fill = TOTAL_FILL
    r += 1
C.cell(row=6, column=6, value="Traditional: 36 people. AI-native: 8 people, AI does reading/reconciling/drafting.").font = NOTE
C.cell(row=11, column=6, value="Model cost ≈ £16/case ×10 safety factor already included; see Assumptions.").font = NOTE
C.cell(row=19, column=6, value="Same loans, same revenue: the difference is entirely operating cost.").font = NOTE
C.cell(row=20, column=6, value="Cost to originate. Traditional lenders typically 1.5–3% of volume.").font = NOTE

# ---- Scaling table
r = 25
C.cell(row=r, column=2, value="Scaling: what happens as the book grows (same pricing, same loss rate)").font = H1
r += 1
C.cell(row=r, column=2, value="Traditional: management fixed, every other function grows in proportion to the book. AI-native: fixed core team + 1 underwriter per £75m of book + 1 BDM per £150m; AI cost grows with cases.").font = NOTE
r += 1
header(C, r, [2, 3, 4, 5, 6], ["Metric", "Book £150m", "Book £300m", "Book £600m", "Note"])
r += 1
books = [150_000_000, 300_000_000, 600_000_000]
# helper rows on the comparison sheet: base book, fixed/variable staff
mgmt_fte = f"SUMIF('Headcount - Traditional'!B{T_first}:B{T_last},\"Management\",'Headcount - Traditional'!D{T_first}:D{T_last})"
mgmt_cost = f"SUMIF('Headcount - Traditional'!B{T_first}:B{T_last},\"Management\",'Headcount - Traditional'!K{T_first}:K{T_last})"
ai_core_rows = f"'Headcount - AI-native'!K{V_first}:K{V_last}"
ai_core_fte = f"'Headcount - AI-native'!D{V_first}:D{V_last}"
# AI-native fixed = everyone except UW (row V_first+2) and BDM (row V_first+5)
UW_ROW = V_first + 2; BDM_ROW = V_first + 5
ai_uw_unit = f"('Headcount - AI-native'!K{UW_ROW}/'Headcount - AI-native'!D{UW_ROW})"
ai_bdm_unit = f"('Headcount - AI-native'!K{BDM_ROW}/'Headcount - AI-native'!D{BDM_ROW})"
ai_fixed_cost = f"(SUM({ai_core_rows})-'Headcount - AI-native'!K{UW_ROW}-'Headcount - AI-native'!K{BDM_ROW})"
ai_fixed_fte = f"(SUM({ai_core_fte})-'Headcount - AI-native'!D{UW_ROW}-'Headcount - AI-native'!D{BDM_ROW})"

scale_start = r
label(C, r, 2, "Loan book");
for i, b in enumerate(books): inp(C, r, 3 + i, b, GBP)
C.cell(row=r, column=6, value="Scale factor vs base = book ÷ Assumptions book").font = NOTE
r += 1
label(C, r, 2, "Scale factor vs base case")
for i in range(3): fx(C, r, 3 + i, f"={get_column_letter(3+i)}{scale_start}/{BOOK}", X)
sf = r; r += 1
label(C, r, 2, "Loans completed per year")
for i in range(3): fx(C, r, 3 + i, f"=ROUND({LOANS}*{get_column_letter(3+i)}{sf},0)", NUM)
ln = r; r += 1
label(C, r, 2, "Net revenue")
for i in range(3): fx(C, r, 3 + i, f"=Revenue!$C$19*{get_column_letter(3+i)}{sf}", GBP)
nr = r; r += 2

label(C, r, 2, "TRADITIONAL", True); C.cell(row=r, column=2).fill = SUB_FILL; r += 1
label(C, r, 2, "Headcount")
for i in range(3):
    col = get_column_letter(3+i)
    fx(C, r, 3 + i, f"={mgmt_fte}+('Headcount - Traditional'!$D${T_tot}-{mgmt_fte})*{col}{sf}", NUM1)
t_hc = r; r += 1
label(C, r, 2, "Operating cost")
for i in range(3):
    col = get_column_letter(3+i)
    fx(C, r, 3 + i, f"={mgmt_cost}+('Headcount - Traditional'!$K${T_tot}-{mgmt_cost})*{col}{sf}+{col}{t_hc}*({DESK}+{SOFT})+{CASES}*{col}{sf}*{DATA_CASE}", GBP)
t_oc = r; r += 1
label(C, r, 2, "Operating profit")
for i in range(3):
    col = get_column_letter(3+i)
    fx(C, r, 3 + i, f"={col}{nr}-{col}{t_oc}", GBP)
t_op = r; r += 1
label(C, r, 2, "Operating margin")
for i in range(3):
    col = get_column_letter(3+i)
    fx(C, r, 3 + i, f"={col}{t_op}/{col}{nr}", PCT)
r += 1
label(C, r, 2, "Cost per completed loan")
for i in range(3):
    col = get_column_letter(3+i)
    fx(C, r, 3 + i, f"={col}{t_oc}/{col}{ln}", GBP)
r += 2

label(C, r, 2, "AI-NATIVE", True); C.cell(row=r, column=2).fill = SUB_FILL; r += 1
label(C, r, 2, "Headcount")
for i in range(3):
    col = get_column_letter(3+i)
    fx(C, r, 3 + i, f"={ai_fixed_fte}+ROUNDUP({col}{scale_start}/75000000,0)+ROUNDUP({col}{scale_start}/150000000,0)", NUM1)
a_hc = r; r += 1
label(C, r, 2, "Operating cost")
for i in range(3):
    col = get_column_letter(3+i)
    fx(C, r, 3 + i, f"={ai_fixed_cost}+ROUNDUP({col}{scale_start}/75000000,0)*{ai_uw_unit}+ROUNDUP({col}{scale_start}/150000000,0)*{ai_bdm_unit}+{col}{a_hc}*({DESK}+{SOFT})+{CASES}*{col}{sf}*({AI_CASE}+{DATA_CASE})+{PLATFORM}*(1+0.5*({col}{sf}-1))", GBP)
a_oc = r; r += 1
C.cell(row=a_oc, column=6, value="Platform cost grows at half the rate of the book.").font = NOTE
label(C, r, 2, "Operating profit")
for i in range(3):
    col = get_column_letter(3+i)
    fx(C, r, 3 + i, f"={col}{nr}-{col}{a_oc}", GBP)
a_op = r; r += 1
label(C, r, 2, "Operating margin")
for i in range(3):
    col = get_column_letter(3+i)
    fx(C, r, 3 + i, f"={col}{a_op}/{col}{nr}", PCT)
r += 1
label(C, r, 2, "Cost per completed loan")
for i in range(3):
    col = get_column_letter(3+i)
    fx(C, r, 3 + i, f"={col}{a_oc}/{col}{ln}", GBP)
r += 2
label(C, r, 2, "AI-native cost advantage (traditional ÷ AI-native)", True)
for i in range(3):
    col = get_column_letter(3+i)
    fx(C, r, 3 + i, f"={col}{t_oc}/{col}{a_oc}", X, bold=True)
r += 1
label(C, r, 2, "Extra operating profit from AI-native model", True)
for i in range(3):
    col = get_column_letter(3+i)
    fx(C, r, 3 + i, f"={col}{a_op}-{col}{t_op}", GBP, bold=True)

# =====================================================================
# Per-case sheet
# =====================================================================
P = wb.create_sheet("Per-case cost")
setw(P, [3, 50, 18, 18, 50])
P["B2"] = "What it costs to underwrite one case"; P["B2"].font = H1
header(P, 4, [2, 3, 4, 5], ["Item", "Traditional", "AI-native", "Note"])
# fully loaded underwriter hourly rate: senior+mid blended from Traditional sheet rows 2-3 (T_first+1, T_first+2)
uw_rows = f"'Headcount - Traditional'!K{T_first+1}:K{T_first+2}"
uw_fte = f"'Headcount - Traditional'!D{T_first+1}:D{T_first+2}"
pc = [
    ("Fully loaded underwriter cost per hour", f"=SUM({uw_rows})/SUM({uw_fte})/{FTE_HRS}", f"=SUM({uw_rows})/SUM({uw_fte})/{FTE_HRS}", GBP, "Blended senior + mid underwriter, fully loaded, ÷ productive hours."),
    ("Underwriter hours per assessed case", f"={UW_HRS}", f"={REV_HRS}", NUM1, "Traditional: reading, reconciling, chasing, drafting. AI-native: review and decide."),
    ("Human cost per case", "=C5*C6", "=D5*D6", GBP, ""),
    ("AI model cost per case", "=0", f"={AI_CASE}", GBP, "Includes 10x safety factor."),
    ("Data & verification per case", f"={DATA_CASE}", f"={DATA_CASE}", GBP, "Same searches either way."),
    ("TOTAL COST PER ASSESSED CASE", "=SUM(C7:C9)", "=SUM(D7:D9)", GBP, ""),
    ("", None, None, None, ""),
    ("Cases one underwriter can assess per year", f"={FTE_HRS}/C6", f"={FTE_HRS}/D6", NUM, "Productive hours ÷ hours per case."),
    ("Elapsed time to first credit view", 5, 0.25, NUM1, "Working days. Traditional: founder experience 3–7 days to a credit view. AI-native: hours. Input cells."),
    ("Cost reduction per case", None, "=1-D10/C10", PCT, ""),
]
r = 5
for lab, f1, f2, fmt, note in pc:
    if lab:
        bold = lab.isupper()
        label(P, r, 2, lab, bold)
        if f1 is not None:
            (inp if isinstance(f1, (int, float)) else fx)(P, r, 3, f1, fmt) if not isinstance(f1, str) else fx(P, r, 3, f1, fmt, bold=bold, link=True)
        if f2 is not None:
            (inp if isinstance(f2, (int, float)) else fx)(P, r, 4, f2, fmt) if not isinstance(f2, str) else fx(P, r, 4, f2, fmt, bold=bold, link=True)
        P.cell(row=r, column=5, value=note).font = NOTE
        if bold:
            for col in (2, 3, 4): P.cell(row=r, column=col).fill = TOTAL_FILL
    r += 1

# =====================================================================
# Sources
# =====================================================================
S = wb.create_sheet("Sources")
setw(S, [3, 40, 90])
S["B2"] = "Sources"; S["B2"].font = H1
header(S, 4, [2, 3], ["Topic", "Source"])
src = [
    ("Bridging market: BDLA loan books & completions", "Mortgage Solutions, 12 Jun 2026 — https://www.mortgagesolutions.co.uk/specialist-lending/bridging/2026/06/12/bridging-market-softens-as-growth-tapers-off-bdla-finds/"),
    ("Bridging market: BDLA Q4 2025", "https://thebdla.org/news/bridging-market-maintains-momentum-in-2025/"),
    ("Bridging market: average loan £540k", "MPA Mag — https://www.mpamag.com/uk/mortgage-types/bridging/bdla-reports-strong-start-for-bridging-finance-in-2025/539187"),
    ("Bridging Trends 2025 (rate 0.84%, LTV 55%, 43 days, term 12m)", "MT Finance — https://www.mt-finance.com/speed-and-stability-bridging-loan-completion-times-hit-eight-year-low-in-2025/"),
    ("Bridging Trends Q2 2026 (rate 0.81%)", "https://www.mt-finance.com/bridging-trends-savvy-borrowers-focus-on-speed-and-equity-release-in-q2/"),
    ("Broker channel share (61% primary, 15% direct)", "Mortgage Solutions, 9 Jun 2026 — https://www.mortgagesolutions.co.uk/specialist-lending/bridging/2026/06/09/bridging-lenders-say-the-market-is-still-growing-survey-finds/"),
    ("Broker fees / arrangement fee norms", "Bridging Loan Directory fee guide — https://bridgingloandirectory.co.uk/guides/bridging-loan-fees-explained-full-cost-breakdown-2025-guide/"),
    ("Broker commission benchmark (1.5% avg)", "Bridging & Commercial, Octane £2bn milestone — https://bridgingandcommercial.co.uk/article/21707/octane-surpasses-%C2%A32bn-lending-milestone"),
    ("Loan book per employee benchmarks", "Octane (~30 staff), Hope Capital (32–41), Tuscan (19) — see company press; Tracxn/LinkedIn headcounts"),
    ("Salaries: underwriters", "Fintelligent, Tandem, exec-appointments job ads 2025–26; talent.com; Reed"),
    ("Salaries: portfolio, completions, admin", "Reed, Fintelligent, NRG, Stellar Select ads; Indeed; PayScale"),
    ("Salaries: BDM / Head of Sales", "Fintelligent, Totaljobs, jobsite ads; Glassdoor Head of Sales London"),
    ("Salaries: marketing, engineering, CTO", "Glassdoor London 2026"),
    ("Salaries: CEO / CFO / COO (estimates)", "Exec Capital, FD Capital, Stone Executive salary guides 2026"),
    ("Salaries: compliance", "Morgan McKinley 2026 salary guide"),
    ("Employer NI 15%, threshold £5,000", "https://employerscalculator.co.uk/guides/employer-ni-rates-2026-27"),
    ("Pension auto-enrolment 3% minimum", "https://www.moorepay.co.uk/payroll-hr-rates/automatic-enrolment/"),
    ("All-in on-cost multiplier 1.25–1.4x", "https://grove.hr/blog/true-cost-hiring-employee-uk"),
    ("London serviced office £700–900/desk/month", "https://www.flexioffices.co.uk/blog/serviced-office-cost-london"),
    ("Land Registry fees £7", "https://gov.uk/guidance/changes-to-fees-for-hm-land-registrys-information-services"),
    ("KYC / credit / AVM per-check costs", "SmartSearch, Creditsafe/Experian comparison, Hometrack retail pricing"),
    ("AI model pricing (Opus 5 $5/$25 per M tokens)", "Anthropic pricing, June 2026 — https://docs.anthropic.com/en/docs/about-claude/pricing"),
    ("Founder inputs", "Lisa Huang — underwriting experience: ~25 loans/yr, 15–23 live cases, £500k–£1m facilities, 15–28 day completions, broker fee 1–2%"),
    ("Founder data: deal pricing calculator (anonymised)", "Rate 0.95%/mo fixed; partner advance 95% at 8.25–9.75%; bank line BoE+4.3–4.8% at 75% advance; lender first-loss 5%; arrangement fee 2% with introducer share; admin £1,250–1,995; drawdown £295/mo; redemption £495; partner fee £500; example deal GPM 4.6% of facility over 18 months"),
    ("Founder data: pipeline tracker (Jan 2026, anonymised)", "~20 live cases; facilities £205k–£1.59m, median ≈ £440k; weekly status dominated by chasing valuers, monitoring surveyors and solicitors"),
]
r = 5
for t, s in src:
    label(S, r, 2, t); c = S.cell(row=r, column=3, value=s); c.font = BLACK; c.alignment = Alignment(wrap_text=True)
    r += 1

for sh in wb.worksheets:
    sh.sheet_view.showGridLines = False
    sh.freeze_panes = None

out = "/tmp/claude-0/-home-user-Jun15/2a55ae62-2767-59db-8c11-ea7415702ab5/scratchpad/verdigris/Verdigris_Economics_Model.xlsx"
wb.save(out)
print("saved", out)
