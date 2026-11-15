from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
S = getSampleStyleSheet()
H = ParagraphStyle("h", parent=S["Heading2"], textColor=colors.HexColor("#1f3b73"), spaceBefore=8, spaceAfter=3)
B = ParagraphStyle("b", parent=S["BodyText"], fontSize=9.3, leading=12.5)
doc = SimpleDocTemplate("insights.pdf", pagesize=A4, leftMargin=16*mm, rightMargin=16*mm, topMargin=13*mm, bottomMargin=12*mm)
kp = [["Delivered revenue", "Delivered orders", "Avg order value", "Repeat customers", "Avg delivery"],
      ["Rs 312.1M", "12,906", "Rs 24.2k (median 12.1k)", "85.4%", "8.0 days"]]
t = Table(kp, colWidths=[36*mm]*5)
t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1f3b73")), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTSIZE", (0,0), (-1,-1), 8), ("ALIGN", (0,0), (-1,-1), "CENTER"), ("FONTNAME", (0,1), (-1,1), "Helvetica-Bold"),
    ("GRID", (0,0), (-1,-1), .4, colors.grey), ("BOTTOMPADDING", (0,0), (-1,-1), 4), ("TOPPADDING", (0,0), (-1,-1), 4)]))
el = [Paragraph("E-commerce Sales Analysis - Insights Summary", S["Title"]),
      Paragraph("Period: Jan 2023 - Dec 2024. Revenue = quantity x unit price x (1 - discount), Delivered orders only.", B),
      Spacer(1, 4), t, Paragraph("3 key findings", H)]
for x in [
 "<b>1. Revenue depends on one category.</b> Electronics earns 64.7% of revenue and all of the top 10 products are Electronics. Books is just 1.3%. Maharashtra, Karnataka and Delhi together contribute 56% of revenue.",
 "<b>2. The business is flat and leaks about 11% of orders.</b> Revenue was Rs 157.0M in 2023 and Rs 155.1M in 2024 (-1.2%), at roughly Rs 26M a month. 6% of orders are cancelled and 5% returned. COD has the highest cancellation rate (6.3% vs 5.6% for debit card). The 85.4% repeat-customer rate is strong, so retention is not the problem: acquisition and basket mix are.",
 "<b>3. Discounts do not buy volume, and delivery is inconsistent.</b> Average quantity is about 2.0 at every discount level (correlation -0.004). Delivery ranges from 2 to 14 days with a flat spread; a quarter of orders take 11+ days. State averages are almost identical (7.88 to 8.14 days; slowest are WB, RJ, UP), so the problem is variability everywhere, not a few bad states."]:
    el.append(Paragraph(x, B)); el.append(Spacer(1, 2))
el.append(Paragraph("3 actionable recommendations", H))
for x in [
 "<b>1. Diversify beyond Electronics.</b> Cross-sell Home &amp; Kitchen (12.7%) and Sports (10.3%) with Electronics bundles, and grow Rajasthan (5.5%) and West Bengal (7.5%), the least-penetrated states, with targeted campaigns.",
 "<b>2. Test lower discounts.</b> Run an A/B test replacing 15-20% discounts with 5-10%. Since quantity does not respond to discount, the expected result is higher margin at the same volume. Measure the effect on orders, not just revenue.",
 "<b>3. Fix delivery reliability and order leakage.</b> Set a delivery SLA (for example 6 days) and review the carriers behind the 11+ day tail, starting with WB, RJ and UP. Nudge COD buyers to prepaid (UPI) with a small incentive to reduce cancellations, and investigate Electronics returns first because they carry the most revenue."]:
    el.append(Paragraph(x, B)); el.append(Spacer(1, 2))
el.append(Spacer(1, 4)); el.append(Image("charts/02_category_share.png", width=88*mm, height=44*mm))
doc.build(el)
