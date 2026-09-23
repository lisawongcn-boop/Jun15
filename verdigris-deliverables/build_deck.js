// Verdigris — Antler pitch deck (pptxgenjs)
const path = require("path");
const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.author = "Lisa Huang";
pres.title = "Verdigris";

// Palette — verdigris + copper
const DEEP = "1F4E48";   // deep verdigris (dark bg)
const VERD = "2E8B7A";   // verdigris
const COPPER = "B87333"; // accent
const INK = "2B2B2B";    // body text
const MUTED = "6B7674";
const PALE = "E6F0ED";   // tint for cards
const WHITE = "FFFFFF";
const OFF = "F4F6F5";

const HFONT = "Cambria";
const BFONT = "Calibri";

// ---- helpers
function darkSlide(title, sub) {
  const s = pres.addSlide();
  s.background = { color: DEEP };
  if (title) s.addText(title, { x: 0.6, y: 1.9, w: 8.8, h: 1.2, fontFace: HFONT, fontSize: 40, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  if (sub) s.addText(sub, { x: 0.6, y: 3.1, w: 8.8, h: 0.8, fontFace: BFONT, fontSize: 18, color: "CFE3DE", isTextBox: true, margin: 0 });
  return s;
}
function lightSlide(title) {
  const s = pres.addSlide();
  s.background = { color: WHITE };
  s.addText(title, { x: 0.5, y: 0.3, w: 9.0, h: 0.85, fontFace: HFONT, fontSize: 24, bold: true, color: DEEP, isTextBox: true, margin: 0, valign: "top" });
  return s;
}
function footer(s, n) {
  s.addText("Verdigris — confidential", { x: 0.5, y: 5.25, w: 4, h: 0.25, fontFace: BFONT, fontSize: 8, color: MUTED, isTextBox: true, margin: 0 });
  s.addText(String(n), { x: 9.0, y: 5.25, w: 0.5, h: 0.25, fontFace: BFONT, fontSize: 8, color: MUTED, align: "right", isTextBox: true, margin: 0 });
}
function card(s, x, y, w, h, fill) {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill || PALE }, line: { color: fill || PALE }, rectRadius: 0.08 });
}
function stat(s, x, y, w, big, label, color) {
  s.addText(big, { x, y, w, h: 0.75, fontFace: HFONT, fontSize: 36, bold: true, color: color || VERD, isTextBox: true, margin: 0, valign: "bottom" });
  s.addText(label, { x, y: y + 0.78, w, h: 0.55, fontFace: BFONT, fontSize: 11, color: INK, isTextBox: true, margin: 0, valign: "top" });
}
function numCircle(s, x, y, n, color, textColor) {
  s.addShape(pres.ShapeType.ellipse, { x, y, w: 0.42, h: 0.42, fill: { color: color || VERD }, line: { color: color || VERD } });
  s.addText(String(n), { x, y, w: 0.42, h: 0.42, fontFace: BFONT, fontSize: 13, bold: true, color: textColor || WHITE, align: "center", valign: "middle", isTextBox: true, margin: 0 });
}
function body(s, x, y, w, h, text, opts) {
  s.addText(text, Object.assign({ x, y, w, h, fontFace: BFONT, fontSize: 13, color: INK, isTextBox: true, margin: 0, valign: "top" }, opts || {}));
}
function bullets(s, x, y, w, h, items, size) {
  const arr = items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1, paraSpaceAfter: 6 } }));
  s.addText(arr, { x, y, w, h, fontFace: BFONT, fontSize: size || 12, color: INK, isTextBox: true, margin: 0, valign: "top" });
}

// =====================================================================
// 1. Title
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: DEEP };
  s.addShape(pres.ShapeType.ellipse, { x: 7.7, y: 0.25, w: 3.4, h: 3.4, fill: { color: VERD }, line: { color: VERD } });
  s.addShape(pres.ShapeType.ellipse, { x: 8.7, y: 3.9, w: 2.2, h: 2.2, fill: { color: COPPER }, line: { color: COPPER } });
  s.addText("Verdigris", { x: 0.6, y: 1.5, w: 6.5, h: 1.1, fontFace: HFONT, fontSize: 54, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  s.addText("The AI-native lender for UK bridging and development finance", { x: 0.6, y: 2.6, w: 6.9, h: 0.55, valign: "top", fontFace: BFONT, fontSize: 18, color: "CFE3DE", isTextBox: true, margin: 0 });
  s.addText("One underwriter. 200 live deals. A lender that scales by compute, not headcount.", { x: 0.6, y: 3.2, w: 6.9, h: 0.5, valign: "top", fontFace: BFONT, fontSize: 14, italic: true, color: "CFE3DE", isTextBox: true, margin: 0 });
  s.addText("Lisa Huang  ·  Antler UK residency application  ·  September 2026", { x: 0.6, y: 4.7, w: 7, h: 0.4, fontFace: BFONT, fontSize: 11, color: "9FBFB8", isTextBox: true, margin: 0 });
  s.addNotes("Verdigris is an AI-native lender. I underwrite bridging loans for a living and carry 15–25 live deals at a time. Agents hold the file; the underwriter decides. That is how a small team runs a large book, and grows it without hiring.");
}

// =====================================================================
// 2. Problem
// =====================================================================
{
  const s = lightSlide("A bridging lender can only grow as fast as it can hire underwriters.");
  stat(s, 0.5, 1.3, 2.8, "15–25", "live deals one underwriter can carry at once. That is the ceiling on growth.");
  stat(s, 3.6, 1.3, 2.8, "~12 hrs", "of underwriter time per assessed case, most of it reading and chasing");
  stat(s, 6.7, 1.3, 2.8, "37 people", "to run a £150m book: every £4m of growth means another hire");
  card(s, 0.5, 2.95, 4.4, 2.1);
  body(s, 0.7, 3.07, 4.0, 0.3, "What the 37 people actually do", { bold: true, fontSize: 12, color: DEEP });
  bullets(s, 0.7, 3.42, 4.0, 1.6, [
    "10 in credit read valuations, monitoring-surveyor reports and bank statements, then reconcile the parties who disagree.",
    "8 in portfolio chase solicitors, valuers and surveyors, then service the loan to redemption.",
    "The credit decision itself is a fraction of anyone's week.",
  ], 10.5);
  card(s, 5.1, 2.95, 4.4, 2.1, DEEP);
  s.addText("This is not a speed problem", { x: 5.3, y: 3.07, w: 4.0, h: 0.3, fontFace: BFONT, fontSize: 12, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  s.addText("A bridging loan takes 43–53 days on average, and that pace is set by the valuation, the monitoring surveyor's report and the solicitor's title work. The lender controls none of them. What it does control is how many files each person can hold while they wait. Today that is 15–25.", { x: 5.3, y: 3.42, w: 4.0, h: 1.55, fontFace: BFONT, fontSize: 10.5, color: "E6F0ED", isTextBox: true, margin: 0, valign: "top" });
  footer(s, 2);
  s.addNotes("Composite of a typical mid-size London lender. Headcount shape from my own experience; completion times from Bridging Trends 2025–26. I deliberately don't pitch speed: third parties set the timeline. The pitch is capacity: how many deals one underwriter can carry.");
}

// =====================================================================
// 3. What an underwriter's day is (native chart)
// =====================================================================
{
  const s = lightSlide("Where an underwriter's capacity goes");
  s.addChart(pres.ChartType.bar, [{
    name: "Share of underwriter time",
    labels: ["Reading documents", "Chasing valuers, surveyors, solicitors", "Reconciling valuer vs surveyor vs borrower", "Writing the credit paper", "Deciding"],
    values: [35, 25, 20, 10, 10],
  }], {
    x: 0.5, y: 1.3, w: 5.6, h: 3.55, barDir: "bar",
    chartColors: [VERD, VERD, VERD, COPPER, COPPER],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '0"%"', dataLabelFontSize: 10, dataLabelColor: INK,
    catAxisLabelFontSize: 10, catAxisLabelColor: INK, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showLegend: false, showTitle: false, valAxisMaxVal: 45,
  });
  card(s, 6.4, 1.25, 3.1, 3.6, DEEP);
  s.addText("The judgement is 10–20%.", { x: 6.6, y: 1.45, w: 2.7, h: 0.9, fontFace: HFONT, fontSize: 18, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  s.addText("Everything else is document work and chasing: extracting, cross-checking, summarising, following up. An agent can do that for 200 files at once while they wait on third parties. A person can do it for 20.", { x: 6.6, y: 2.4, w: 2.7, h: 1.6, fontFace: BFONT, fontSize: 11, color: "CFE3DE", isTextBox: true, margin: 0 });
  s.addText("Copper = where a human must stay.", { x: 6.6, y: 4.1, w: 2.7, h: 0.5, fontFace: BFONT, fontSize: 10, italic: true, color: "E8C9AE", isTextBox: true, margin: 0 });
  body(s, 0.5, 4.95, 5.6, 0.3, "Founder estimate from ~25 completed loans a year and a 15–25 case pipeline; to be measured with design partners.", { fontSize: 9, color: MUTED });
  footer(s, 3);
}

// =====================================================================
// 4. Insight / thesis
// =====================================================================
{
  const s = darkSlide(null, null);
  s.addText("Capacity, not speed. One underwriter, 200 live deals.", { x: 0.6, y: 0.55, w: 8.8, h: 1.1, fontFace: HFONT, fontSize: 30, bold: true, color: WHITE, isTextBox: true, margin: 0, valign: "middle" });
  // two columns
  card(s, 0.6, 1.8, 4.2, 3.0, "2A5F58");
  card(s, 5.2, 1.8, 4.2, 3.0, VERD);
  s.addText("Traditional lender", { x: 0.85, y: 1.95, w: 3.7, h: 0.4, fontFace: HFONT, fontSize: 16, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  s.addText([
    { text: "People read, reconcile, chase and draft.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "One underwriter carries 15–25 live deals.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Every £4m of book needs another employee.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Operating cost ≈ 2.8% of what is lent each year.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Grows by hiring.", options: { bullet: true } },
  ], { x: 0.85, y: 2.4, w: 3.7, h: 2.35, fontFace: BFONT, fontSize: 12, color: "E6F0ED", isTextBox: true, margin: 0, valign: "top" });
  s.addText("AI-native lender", { x: 5.45, y: 1.95, w: 3.7, h: 0.4, fontFace: HFONT, fontSize: 16, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  s.addText([
    { text: "Agents read, reconcile, chase and draft. People decide.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "8× the capacity: 120–200 live deals per underwriter.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Every £19m of book needs another employee.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Operating cost ≈ 0.7% of what is lent each year.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Grows by compute.", options: { bullet: true } },
  ], { x: 5.45, y: 2.4, w: 3.7, h: 2.35, fontFace: BFONT, fontSize: 12, color: WHITE, isTextBox: true, margin: 0, valign: "top" });
  s.addNotes("Capacity multiple = 12 underwriter hours per case today ÷ 1.5 hours of review when agents draft the pack = 8×. On a 15–25 caseload that is 120–200 live deals. Going beyond 200 needs review time below 1.5 hours; the model does not assume it.");
  s.addText("Figures from the Verdigris economics model — a £150m book, 181 loans a year, identical pricing and funding on both sides. 8× = 12 hours per case today ÷ 1.5 hours of review.", { x: 0.6, y: 4.95, w: 8.8, h: 0.35, fontFace: BFONT, fontSize: 9.5, color: "9FBFB8", isTextBox: true, margin: 0 });
}

// =====================================================================
// 5. Worked example — traditional P&L
// =====================================================================
{
  const s = lightSlide("The worked example: 'Northgate Bridging', a composite £150m lender");
  body(s, 0.5, 1.18, 9, 0.42, "Fictional but built from real numbers: 37 staff at 2025–26 London salaries, market pricing, institutional funding at 95% advance.", { fontSize: 11, color: MUTED });
  const rows = [
    [{ text: "£ per year", options: { bold: true, color: WHITE, fill: { color: DEEP } } }, { text: "Northgate", options: { bold: true, color: WHITE, fill: { color: DEEP }, align: "right" } }, { text: "How", options: { bold: true, color: WHITE, fill: { color: DEEP } } }],
    ["Gross interest income", "£16.2m", "£150m book × 0.90%/month"],
    ["Less cost of funds", "(£12.5m)", "95% partner-funded at 8.75% pa"],
    ["Fees retained (arrangement, admin, drawdown, redemption)", "£1.9m", "2% fee mostly paid away to introducers; ~£3k of fees per loan"],
    ["Less partner fees and expected losses", "(£0.8m)", "£500 per deal; 0.5% of book"],
    [{ text: "Net revenue", options: { bold: true, fill: { color: PALE } } }, { text: "£4.8m", options: { bold: true, fill: { color: PALE }, align: "right" } }, { text: "3.3% of book — what has to pay for the business", options: { fill: { color: PALE } } }],
    ["People, fully loaded (37 FTE)", "(£3.6m)", "Salaries + 15% NI + pension + on-costs"],
    ["Office, software, data searches", "(£0.5m)", "£9.6k per desk; £50 of searches per case"],
    [{ text: "Operating profit", options: { bold: true, fill: { color: PALE } } }, { text: "£0.7m", options: { bold: true, fill: { color: PALE }, align: "right" } }, { text: "14% margin. £22,900 to originate each loan.", options: { fill: { color: PALE } } }],
  ];
  s.addTable(rows, { x: 0.5, y: 1.62, w: 9.0, colW: [3.7, 1.1, 4.2], fontFace: BFONT, fontSize: 10, color: INK, border: { type: "solid", color: "DDDDDD", pt: 0.5 }, rowH: 0.34, valign: "middle", autoPage: false, margin: 0.04 });
  body(s, 0.5, 4.75, 9, 0.45, "The example deal in a lender's own calculator returns 4.6% gross margin on facility over 18 months. Almost all of it goes on the people who process the file.", { fontSize: 10, italic: true, color: MUTED });
  footer(s, 5);
  s.addNotes("All inputs are in the accompanying spreadsheet, each with its source. Northgate is a composite, not a real company.");
}

// =====================================================================
// 6. Same book, AI-native — chart comparison
// =====================================================================
{
  const s = lightSlide("The same £150m book, run by 8 people instead of 37");
  s.addChart(pres.ChartType.bar, [
    { name: "Northgate (traditional)", labels: ["Headcount", "Operating cost £m", "Operating profit £m"], values: [37, 4.14, 0.68] },
    { name: "Verdigris (AI-native)", labels: ["Headcount", "Operating cost £m", "Operating profit £m"], values: [8, 1.01, 3.82] },
  ], {
    x: 0.5, y: 1.3, w: 5.4, h: 3.6, barDir: "col", barGrouping: "clustered",
    chartColors: ["9FBFB8", VERD], showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 10, dataLabelColor: INK, dataLabelFormatCode: "#,##0.0#",
    catAxisLabelFontSize: 10, catAxisLabelColor: INK, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "b", legendFontSize: 10, legendColor: INK, showTitle: false,
  });
  stat(s, 6.3, 1.25, 3.2, "4.1×", "lower operating cost for the same loans", COPPER);
  stat(s, 6.3, 2.65, 3.2, "£5,600", "to originate each loan, versus £22,900");
  stat(s, 6.3, 4.05, 3.2, "79%", "operating margin, versus 14%");
  footer(s, 6);
  s.addNotes("Eight people: two founders, two senior underwriters who review and decide, one ops, one compliance, one BDM, one engineer. AI cost is £16 per case with a 10x safety factor, plus £50 of data searches. Traditional profit £0.68m, AI-native £3.82m on £4.8m net revenue.");
}

// =====================================================================
// 7. Scaling
// =====================================================================
{
  const s = lightSlide("Traditional lenders scale by hiring. Verdigris scales by compute.");
  s.addChart(pres.ChartType.line, [
    { name: "Northgate headcount", labels: ["£150m book", "£300m book", "£600m book"], values: [37, 69, 133] },
    { name: "Verdigris headcount", labels: ["£150m book", "£300m book", "£600m book"], values: [8, 11, 17] },
  ], {
    x: 0.5, y: 1.3, w: 4.4, h: 3.4, chartColors: ["9FBFB8", VERD], lineSize: 3, lineDataSymbolSize: 8,
    showValue: true, dataLabelFontSize: 10, dataLabelColor: INK, dataLabelPosition: "t",
    catAxisLabelFontSize: 10, catAxisLabelColor: INK, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "b", legendFontSize: 10, legendColor: INK, showTitle: true, title: "People needed", titleFontSize: 12, titleColor: INK,
  });
  s.addChart(pres.ChartType.line, [
    { name: "Northgate profit £m", labels: ["£150m book", "£300m book", "£600m book"], values: [0.7, 2.4, 5.9] },
    { name: "Verdigris profit £m", labels: ["£150m book", "£300m book", "£600m book"], values: [3.8, 8.2, 17.0] },
  ], {
    x: 5.1, y: 1.3, w: 4.4, h: 3.4, chartColors: ["9FBFB8", COPPER], lineSize: 3, lineDataSymbolSize: 8,
    showValue: true, dataLabelFontSize: 10, dataLabelColor: INK, dataLabelPosition: "t", dataLabelFormatCode: "#,##0.0",
    catAxisLabelFontSize: 10, catAxisLabelColor: INK, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showLegend: true, legendPos: "b", legendFontSize: 10, legendColor: INK, showTitle: true, title: "Operating profit, £m a year", titleFontSize: 12, titleColor: INK,
  });
  body(s, 0.5, 4.8, 9, 0.4, "At £600m of book the gap is 116 people and £11m of profit a year. The AI-native model adds one underwriter per £75m and one BDM per £150m; everything else is compute.", { fontSize: 10.5, color: INK });
  footer(s, 7);
}

// =====================================================================
// 8. Product
// =====================================================================
{
  const s = lightSlide("The product: agents hold every file, the underwriter decides");
  const steps = [
    ["Ingest", "Application, valuation, surveyor report, title, ID, bank statements"],
    ["Extract", "Every number and claim, with its page reference"],
    ["Reconcile", "Valuer vs surveyor vs borrower: where they disagree; stale comps, weak exits"],
    ["Chase", "Agents chase valuers, surveyors and solicitors, and keep every file moving"],
    ["Draft", "Credit paper in the lender's own format: metrics, SWOT, risks, mitigants"],
    ["Decide", "A human underwriter reviews, challenges and signs. Always."],
  ];
  const x0 = 0.5, w = 1.45, gap = 0.06;
  steps.forEach((st, i) => {
    const x = x0 + i * (w + gap);
    const last = i === steps.length - 1;
    card(s, x, 1.3, w, 2.05, last ? COPPER : PALE);
    numCircle(s, x + 0.12, 1.42, i + 1, last ? WHITE : VERD, last ? COPPER : WHITE);
    s.addText(st[0], { x: x + 0.12, y: 1.9, w: w - 0.24, h: 0.35, fontFace: HFONT, fontSize: 14, bold: true, color: last ? WHITE : DEEP, isTextBox: true, margin: 0 });
    s.addText(st[1], { x: x + 0.12, y: 2.25, w: w - 0.24, h: 1.05, fontFace: BFONT, fontSize: 9.5, color: last ? WHITE : INK, isTextBox: true, margin: 0, valign: "top" });
  });
  card(s, 0.5, 3.6, 4.4, 1.45);
  body(s, 0.7, 3.7, 4.0, 0.3, "What stays deterministic, never a model output", { bold: true, fontSize: 12, color: DEEP });
  bullets(s, 0.7, 4.02, 4.0, 1.0, ["LTV, LTGDV and LTC caps; eligibility gates; rate cards", "Every calculation in the term sheet and the pricing approval", "Who can approve what: credit manager, senior, committee"], 10);
  card(s, 5.1, 3.6, 4.4, 1.45);
  body(s, 5.3, 3.7, 4.0, 0.3, "What the model is for", { bold: true, fontSize: 12, color: DEEP });
  bullets(s, 5.3, 4.02, 4.0, 1.0, ["Reading 200 pages and citing where each fact came from", "Holding 200 live files at once without losing track of one", "Spotting the inconsistency a tired analyst misses on case 19 of 23"], 10);
  footer(s, 8);
  s.addNotes("Live demo available: a real deal's documents in, a cited credit pack out. Built with Cursor and Claude Code. Underwriting logic encoded from my own completed loans; tested against cases where I already know the answer.");
}

// =====================================================================
// 9. Why now
// =====================================================================
{
  const s = lightSlide("Why now");
  const tiles = [
    ["Models can read the documents", "Frontier models now handle long valuation and monitoring reports with page-level citations. Two years ago they could not be trusted with a Red Book report. The cost is about £2 per case at list price."],
    ["The rest of the chain is going digital", "Land Registry, Companies House, Open Banking, AVMs and KYC all have APIs. Legal AI already supports a quarter of a million property transactions across the UK and US (Orbital). The third parties are speeding up."],
    ["Lender margins are under pressure", "Average bridging rates fell from 0.88% to 0.81% a month; member loan books are down 16% from the 2025 peak. A 14% operating margin does not survive that. Growing without hiring is the way out."],
  ];
  tiles.forEach((t, i) => {
    const x = 0.5 + i * 3.05;
    card(s, x, 1.25, 2.9, 3.4);
    numCircle(s, x + 0.2, 1.45, i + 1);
    s.addText(t[0], { x: x + 0.2, y: 1.98, w: 2.5, h: 0.6, fontFace: HFONT, fontSize: 14, bold: true, color: DEEP, isTextBox: true, margin: 0 });
    s.addText(t[1], { x: x + 0.2, y: 2.6, w: 2.5, h: 1.95, fontFace: BFONT, fontSize: 10.5, color: INK, isTextBox: true, margin: 0, valign: "top" });
  });
  body(s, 0.5, 4.85, 9, 0.35, "Sources: Bridging Trends 2024–Q2 2026; BDLA quarterly data Q3 2025–Q1 2026; Anthropic list pricing June 2026; Will Pearce (Orbital), interview.", { fontSize: 9, color: MUTED });
  footer(s, 9);
}

// =====================================================================
// 10. Market and wedge
// =====================================================================
{
  const s = lightSlide("Market and wedge");
  stat(s, 0.5, 1.2, 2.2, "£11.5bn", "UK bridging loan books (BDLA members, Q1 2026)");
  stat(s, 2.9, 1.2, 2.2, "£8–10bn", "new bridging completions a year");
  stat(s, 5.3, 1.2, 2.2, "~100", "active lenders, most with 15–60 staff");
  stat(s, 7.7, 1.2, 1.9, "61%", "of lenders name brokers as their primary channel");
  card(s, 0.5, 2.85, 4.4, 2.2);
  body(s, 0.7, 2.95, 4.0, 0.3, "Wedge: sell the engine before lending with it", { bold: true, fontSize: 12.5, color: DEEP });
  bullets(s, 0.7, 3.3, 4.0, 1.7, [
    "Per-case pricing to small and mid-size lenders at £250, against ~£600 of in-house cost per assessed case.",
    "~65,000 cases assessed a year across the market (17,000 loans × 4 cases each): a £16m annual pool at that price, and a direct line into every lender's credit team.",
    "Design partners give the training data and the credibility to originate."
  ], 10);
  card(s, 5.1, 2.85, 4.4, 2.2, DEEP);
  s.addText("Then: originate on the AI-native cost base", { x: 5.3, y: 2.95, w: 4.0, h: 0.3, fontFace: BFONT, fontSize: 12.5, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  s.addText([
    { text: "Funding partners already lend 95% of each loan at 8.25–9.75%; the lender puts in 5% first-loss. The funding model exists — the cost base is the innovation.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "A £150m book on the Verdigris cost base makes £3.8m a year, not £0.7m.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Target: £50m book in year 2, £150m in year 3, funded deal-by-deal then on a facility.", options: { bullet: true } },
  ], { x: 5.3, y: 3.3, w: 4.0, h: 1.7, fontFace: BFONT, fontSize: 10, color: "E6F0ED", isTextBox: true, margin: 0, valign: "top" });
  footer(s, 10);
}

// =====================================================================
// 11. Competition and moat
// =====================================================================
{
  const s = lightSlide("The alternatives move the file around. None of them carries it.");
  const hdr = (t) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: DEEP } } });
  const rows = [
    [hdr("Alternative"), hdr("What it does well"), hdr("Why capacity stays at 15–25")],
    [{ text: "In-house credit team", options: { bold: true } }, "Judgement, broker relationships, knows the lender's policy", "Every file is read, chased and written up by hand"],
    [{ text: "Loan origination and case-management software", options: { bold: true } }, "Tracks the pipeline, stores documents, runs the workflow", "It moves the file; a person still has to read it"],
    [{ text: "General-purpose AI chat and document tools", options: { bold: true } }, "Summarises one document on request", "No cross-checking, no citations, no lender format, no audit trail. One file at a time"],
    [{ text: "Other lenders with online front ends", options: { bold: true } }, "Fast indicative terms for brokers", "Behind the portal, credit is still done by people. Cost still scales with headcount"],
  ];
  s.addTable(rows, { x: 0.5, y: 1.25, w: 5.5, colW: [1.55, 1.85, 2.1], fontFace: BFONT, fontSize: 9, color: INK, border: { type: "solid", color: "DDDDDD", pt: 0.5 }, rowH: [0.32, 0.7, 0.7, 0.7, 0.7], valign: "middle", autoPage: false, margin: 0.05 });
  card(s, 6.2, 1.25, 3.3, 3.75, DEEP);
  s.addText("Why it holds", { x: 6.4, y: 1.38, w: 2.9, h: 0.4, fontFace: HFONT, fontSize: 16, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  s.addText([
    { text: "Built by an underwriter. ", options: { bold: true, color: WHITE } },
    { text: "Encoded from real closed cases: which valuer caveats and surveyor comments actually move the credit.", options: { breakLine: true, paraSpaceAfter: 6 } },
    { text: "Every review is data. ", options: { bold: true, color: WHITE } },
    { text: "Each edit an underwriter makes to a pack is a labelled example no generic tool has.", options: { breakLine: true, paraSpaceAfter: 6 } },
    { text: "Incumbents can't copy it. ", options: { bold: true, color: WHITE } },
    { text: "Matching the cost base means cutting 29 of 37 roles and rebuilding the process.", options: { breakLine: true, paraSpaceAfter: 6 } },
    { text: "Ready for the instant transaction. ", options: { bold: true, color: WHITE } },
    { text: "When valuers and solicitors go AI, a people-run lender becomes the bottleneck.", options: {} },
  ], { x: 6.4, y: 1.85, w: 2.9, h: 3.05, fontFace: BFONT, fontSize: 9.5, color: "E6F0ED", isTextBox: true, margin: 0, valign: "top" });
  body(s, 0.5, 4.7, 5.5, 0.4, "Categories, not named firms: a founder's view of the market, to be tested with design partners.", { fontSize: 9, color: MUTED });
  footer(s, 11);
  s.addNotes("29 of 37 roles: Northgate's 37 people vs Verdigris's 8 on the same book (economics model). The moat is not the model — anyone can call an LLM. It is the underwriting judgement encoded in the workflow, the labelled review data, and the cost base once lending.");
}

// =====================================================================
// 12. Roadmap / business model
// =====================================================================
{
  const s = lightSlide("Roadmap to the first loan");
  const phases = [
    ["Now → Dec 2026", "Prove the engine", ["Working demo: one deal in, credit pack out", "3 lender design partners on real, closed cases", "Measure live deals per underwriter and errors caught", "SEIS advance assurance; tech company structured separately from any lending entity"]],
    ["H1 2027", "Sell it", ["Per-case pricing live with 3–5 lenders", "Broker submissions handled end to end", "Compliance and audit trail designed in: every decision reconstructable", "Angel round under SEIS; technical co-founder in place"]],
    ["H2 2027 →", "Lend with it", ["First loans on a partner funding line, deal by deal", "Human underwriters decide; the engine does the rest", "£50m book target by end of year 2", "Facility funding once track record exists"]],
  ];
  phases.forEach((p, i) => {
    const x = 0.5 + i * 3.05;
    card(s, x, 1.25, 2.9, 3.55, i === 2 ? DEEP : PALE);
    const tc = i === 2 ? WHITE : DEEP;
    const bc = i === 2 ? "E6F0ED" : INK;
    s.addText(p[0], { x: x + 0.2, y: 1.38, w: 2.5, h: 0.3, fontFace: BFONT, fontSize: 10, bold: true, color: i === 2 ? "E8C9AE" : COPPER, isTextBox: true, margin: 0 });
    s.addText(p[1], { x: x + 0.2, y: 1.7, w: 2.5, h: 0.45, fontFace: HFONT, fontSize: 18, bold: true, color: tc, isTextBox: true, margin: 0 });
    s.addText(p[2].map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < p[2].length - 1, paraSpaceAfter: 5 } })), { x: x + 0.2, y: 2.2, w: 2.5, h: 2.5, fontFace: BFONT, fontSize: 10, color: bc, isTextBox: true, margin: 0, valign: "top" });
  });
  body(s, 0.5, 4.9, 9, 0.3, "Regulatory note: consumer bridging is FCA-regulated; the initial focus is unregulated commercial and investment lending. Counsel engaged before loan one.", { fontSize: 9, color: MUTED });
  footer(s, 12);
}

// =====================================================================
// 13. Vision — the one-person lending company
// =====================================================================
{
  const s = darkSlide(null, null);
  s.addText("WHERE THIS GOES", { x: 0.6, y: 0.4, w: 8.8, h: 0.3, fontFace: BFONT, fontSize: 11, bold: true, color: "9FBFB8", isTextBox: true, margin: 0 });
  s.addText("The one-person lending company", { x: 0.6, y: 0.68, w: 8.8, h: 0.6, fontFace: HFONT, fontSize: 28, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  const stages = [
    ["Now", "Capacity", "Valuers, monitoring surveyors and solicitors set the pace. Agents hold every file while it waits, so one underwriter carries 120–200 live deals instead of 15–25. The lender grows without hiring.", "2A5F58", "E8C9AE"],
    ["Next", "The instant transaction", "The third parties go AI too: automated valuations, AI-assisted monitoring reports, near-instant legal and title work. When they speed up, a lender run by people becomes the bottleneck. An AI-native lender keeps pace.", "2A5F58", "E8C9AE"],
    ["Vision", "Lending that runs itself", "Agents originate, underwrite, complete, monitor and redeem. One person sets the credit appetite, signs the decisions and owns the funder relationships. The lending business becomes a platform.", COPPER, WHITE],
  ];
  stages.forEach((st, i) => {
    const x = 0.6 + i * 3.0;
    card(s, x, 1.45, 2.8, 2.4, st[3]);
    s.addText(st[0].toUpperCase(), { x: x + 0.2, y: 1.6, w: 2.4, h: 0.3, fontFace: BFONT, fontSize: 10, bold: true, color: st[4], isTextBox: true, margin: 0 });
    s.addText(st[1], { x: x + 0.2, y: 1.88, w: 2.4, h: 0.4, fontFace: HFONT, fontSize: 15, bold: true, color: WHITE, isTextBox: true, margin: 0, valign: "top" });
    s.addText(st[2], { x: x + 0.2, y: 2.35, w: 2.4, h: 1.42, fontFace: BFONT, fontSize: 10, color: "E6F0ED", isTextBox: true, margin: 0, valign: "top" });
  });
  s.addText([
    { text: "“The logical outcome of this trend is a near-instant real estate transaction… From a technical perspective, I would imagine less than five years.”", options: { italic: true, breakLine: true } },
    { text: "Will Pearce, Orbital (AI for real estate legal work)", options: { fontSize: 9.5, color: "9FBFB8" } },
  ], { x: 0.6, y: 4.1, w: 8.8, h: 0.9, fontFace: BFONT, fontSize: 12, color: WHITE, isTextBox: true, margin: 0, valign: "top" });
  footer(s, 13);
  s.addNotes("Speed is not the pitch today: third parties set the timeline. But the transcript view from Orbital is that legal reasoning becomes near-instant and the bottleneck becomes humans. When that happens, the lender is the slowest link, unless it is already AI-native. Verdigris is built for that world; the end state is a lender one person can run.");
}

// =====================================================================
// 14. Founder and ask
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: DEEP };
  s.addText("Founder", { x: 0.6, y: 0.5, w: 4, h: 0.4, fontFace: BFONT, fontSize: 11, bold: true, color: "9FBFB8", isTextBox: true, margin: 0 });
  s.addText("Lisa Huang", { x: 0.6, y: 0.85, w: 4.4, h: 0.6, fontFace: HFONT, fontSize: 28, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  s.addText([
    { text: "Credit analyst at a London specialist lender: ~25 bridging and development loans completed in a year, 15–25 live cases at a time, completions in 15–28 days.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Five years managing a ~£400m commercial portfolio in Shanghai; supported a £300m industrial park sale.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "Capital markets and advisory at Cushman & Wakefield and CBRE.", options: { bullet: true, breakLine: true, paraSpaceAfter: 6 } },
    { text: "MSc Real Estate Finance, Distinction (Henley). Builds with Cursor and Claude Code.", options: { bullet: true } },
  ], { x: 0.6, y: 1.5, w: 4.4, h: 3.0, fontFace: BFONT, fontSize: 11.5, color: "E6F0ED", isTextBox: true, margin: 0, valign: "top" });

  card(s, 5.4, 0.6, 4.0, 4.4, VERD);
  s.addText("The ask", { x: 5.65, y: 0.75, w: 3.5, h: 0.45, fontFace: HFONT, fontSize: 22, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  s.addText([
    { text: "A technical co-founder", options: { bold: true, breakLine: true } },
    { text: "who can turn a working underwriting demo into a product a regulated lender will trust.", options: { breakLine: true, paraSpaceAfter: 8 } },
    { text: "Antler's £210k buys", options: { bold: true, breakLine: true } },
    { text: "six months of two founders full-time, v1 of the engine, three design partners on live cases, and SEIS advance assurance in hand for the angel round.", options: { breakLine: true, paraSpaceAfter: 8 } },
    { text: "What you get", options: { bold: true, breakLine: true } },
    { text: "a domain founder who has done the job by hand, one underwriter carrying 200 live deals instead of 15–25, and a model that makes £3.8m where the incumbent makes £0.7m.", options: {} },
  ], { x: 5.65, y: 1.3, w: 3.5, h: 3.5, fontFace: BFONT, fontSize: 11, color: WHITE, isTextBox: true, margin: 0, valign: "top" });
  s.addText("lisawongcn@gmail.com  ·  linkedin.com/in/lisa-h-53139529a", { x: 0.6, y: 4.9, w: 6, h: 0.3, fontFace: BFONT, fontSize: 10, color: "9FBFB8", isTextBox: true, margin: 0 });
}

// =====================================================================
// 15. Appendix — assumptions
// =====================================================================
{
  const s = lightSlide("Appendix: model assumptions");
  const hdr = (t, a) => ({ text: t, options: { bold: true, color: WHITE, fill: { color: DEEP }, align: a || "left" } });
  const rows = [
    [hdr("Assumption"), hdr("Value", "right"), hdr("Basis")],
    ["Loan book / blended loan / term", "£150m / £830k / 12 mo", "Founder: bridging £500–800k (institutional partner), development £1–1.5m (bank partner), 30% dev"],
    ["Loans completed / cases assessed per year", "181 / 724", "~1 in 4 assessed cases completes"],
    ["Borrower rate", "0.90% per month", "Lender calculator 0.95%; market average 0.81–0.84%"],
    ["Cost of funds / partner share", "8.75% pa / 95%", "Lender rate card: 8.25–9.75% at 95% advance; 5% first loss"],
    ["Arrangement fee charged / retained", "2.0% / 0.5%", "Introducer share paid away; £3k of admin and redemption fees per loan"],
    ["Expected credit loss", "0.5% of book pa", "Prudent; comparator reports zero capital losses"],
    ["Salaries and on-costs", "London 2025–26 bands", "Founder: analysts under £55k; other roles from job ads and guides; NI 15%, pension 5%, 8% other"],
    ["AI cost per case", "£16 + £50 data", "~320k tokens ≈ $2, ×10 safety factor; Land Registry, KYC, AVM, credit searches"],
    ["Underwriter hours per case", "12 / 1.5", "Traditional / AI-native. Founder estimate; to be measured with design partners"],
    ["Live deals per underwriter", "15–25 / 120–200", "Founder caseload today × capacity multiple (12 h ÷ 1.5 h = 8×)"],
  ];
  s.addTable(rows, { x: 0.5, y: 1.2, w: 9.0, colW: [2.9, 1.9, 4.2], fontFace: BFONT, fontSize: 9, color: INK, border: { type: "solid", color: "DDDDDD", pt: 0.5 }, rowH: 0.3, valign: "middle", autoPage: false, margin: 0.03 });
  body(s, 0.5, 4.9, 9, 0.33, "Full model with sources: Verdigris_Economics_Model.xlsx. 'Northgate Bridging' is a fictional composite; no figure is a claim about a specific company.", { fontSize: 9, color: MUTED });
  footer(s, 15);
}

pres.writeFile({ fileName: path.join(__dirname, "Verdigris_Pitch_Deck.pptx") }).then(f => console.log("wrote", f));
