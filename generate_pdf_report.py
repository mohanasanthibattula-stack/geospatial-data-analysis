"""
Executive PDF Report Generator: Geospatial Market Analysis
Generates 'Geospatial_Market_Analysis_Report.pdf' and 'Spatial_Analysis_Report.pdf'
"""

import os
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "india_regional_market_v2.csv")
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
PDF_PATH_1 = os.path.join(BASE_DIR, "Geospatial_Market_Analysis_Report.pdf")
PDF_PATH_2 = os.path.join(BASE_DIR, "Spatial_Analysis_Report.pdf")

# Load and compute metrics
df = pd.read_csv(DATA_PATH)
df['OpportunityScore'] = (df['MonthlySearchDemand'] * df['LeadConversionRate']) / (df['ExistingCompetitors'] + 1)
df['EstimatedRevenuePotential'] = df['MonthlySearchDemand'] * df['LeadConversionRate'] * df['MedianAnnualIncomeINR']
top_3 = df.sort_values(by='OpportunityScore', ascending=False).head(3).copy()

# Numbered Canvas for professional header/footer
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (on pages 2 and later)
        if self._pageNumber > 1:
            self.drawString(54, 11 * 72 - 36, "GEOSPATIAL MARKET ANALYSIS & REGIONAL EXPANSION REPORT")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)
        
        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 32, footer_text)
        self.drawString(54, 32, "CONFIDENTIAL & PROPRIETARY — WORKORA GEOSPATIAL INTELLIGENCE")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 44, 8.5 * 72 - 54, 44)
        
        self.restoreState()

def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=50,
        rightMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()
    
    # Custom typography styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#0f172a")
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#475569")
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=14,
        spaceAfter=6
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0284c7"),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6
    )
    callout_style = ParagraphStyle(
        'Callout_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#065f46")
    )
    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1e293b")
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#0f172a")
    )

    story = []

    # Title & Metadata Banner
    story.append(Paragraph("GEOSPATIAL DATA ANALYSIS & MARKET EXPANSION", title_style))
    story.append(Paragraph("Strategic Regional Intelligence, Demand Hotspots & Competitor Whitespace Identification", subtitle_style))
    story.append(Spacer(1, 10))

    meta_table_data = [
        [
            Paragraph("<b>Project:</b> Geospatial Market Analysis", table_cell),
            Paragraph("<b>Dataset:</b> india_regional_market_v2.csv", table_cell),
            Paragraph("<b>Records:</b> 400 Micro-Regions", table_cell)
        ],
        [
            Paragraph("<b>Lead Analyst:</b> Geospatial & MLOps Team", table_cell),
            Paragraph("<b>Coverage:</b> 10 Major Indian Metros", table_cell),
            Paragraph("<b>Status:</b> Production Verified", table_cell)
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[170, 170, 170])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # Executive Summary
    story.append(Paragraph("1. Executive Summary & Strategic Objectives", h1_style))
    story.append(Paragraph(
        "This geospatial data investigation evaluates location-based commercial metrics across <b>400 micro-regional markets</b> "
        "spanning 10 major metropolitan clusters in India (Delhi, Mumbai, Bengaluru, Hyderabad, Chennai, Kolkata, Pune, Ahmedabad, "
        "Jaipur, and Kochi). The core objective is to uncover <b>high-demand, high-conversion geographic clusters</b> where incumbent "
        "competitor density remains exceptionally low ('underserved markets'), offering maximum return on customer acquisition spend.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Core Strategic Breakthrough:</b> While top-tier metros like Delhi, Ahmedabad, and Chennai aggregate the highest gross search volumes, "
        "they suffer from intense competitor crowding (averaging 7 to 9 competitors per zone) and heightened customer acquisition costs. "
        "Conversely, select coastal and secondary hubs—specifically <b>Kochi (Kerala)</b> and <b>Kolkata (West Bengal)</b>—harbor "
        "exceptional micro-markets demonstrating search demand exceeding 1,780/month and conversion rates above 13%, but contested by only "
        "<b>a single incumbent competitor</b>. These areas represent prime expansion targets with instant market-leadership potential.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # Methodology & Mathematical Formulation
    story.append(Paragraph("2. Mathematical Formulation & Scoring Methodology", h1_style))
    story.append(Paragraph(
        "To objectively rank regional attractiveness, an <b>Opportunity Index</b> was engineered to balance market pull against competitive resistance:",
        body_style
    ))
    
    formula_data = [
        [
            Paragraph("<b>Metric</b>", table_header),
            Paragraph("<b>Mathematical Definition</b>", table_header),
            Paragraph("<b>Business Interpretation</b>", table_header)
        ],
        [
            Paragraph("<b>Opportunity Score</b>", table_cell_bold),
            Paragraph("<code>(MonthlySearchDemand × LeadConversionRate) / (ExistingCompetitors + 1)</code>", table_cell),
            Paragraph("Yields expected customer acquisitions per competitor unit; +1 prevents division-by-zero for greenfield zones.", table_cell)
        ],
        [
            Paragraph("<b>Revenue Potential</b>", table_cell_bold),
            Paragraph("<code>MonthlySearchDemand × LeadConversionRate × MedianAnnualIncomeINR</code>", table_cell),
            Paragraph("Quantifies gross monetizable annual earning power flowing through the immediate lead funnel.", table_cell)
        ],
        [
            Paragraph("<b>Market Saturation</b>", table_cell_bold),
            Paragraph("<code>ExistingCompetitors / (MonthlySearchDemand / 1000)</code>", table_cell),
            Paragraph("Ratio of competitor density relative to organic consumer interest volume.", table_cell)
        ]
    ]
    formula_table = Table(formula_data, colWidths=[110, 210, 190])
    formula_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(formula_table)
    story.append(Spacer(1, 12))

    # Top 3 High-Potential Underserved Regions
    story.append(Paragraph("3. Target Profile: Top 3 High-Potential Underserved Regions", h1_style))
    story.append(Paragraph(
        "Rigorous algorithmic screening across all 400 micro-regions isolated the top three geographic targets boasting "
        "the highest Opportunity Scores in India:",
        body_style
    ))

    top3_table_data = [
        [
            Paragraph("<b>Rank</b>", table_header),
            Paragraph("<b>Region & City</b>", table_header),
            Paragraph("<b>Segment</b>", table_header),
            Paragraph("<b>Demand</b>", table_header),
            Paragraph("<b>Competitors</b>", table_header),
            Paragraph("<b>Conv %</b>", table_header),
            Paragraph("<b>CAC (INR)</b>", table_header),
            Paragraph("<b>Opportunity</b>", table_header)
        ]
    ]
    for rank, (_, row) in enumerate(top_3.iterrows(), 1):
        top3_table_data.append([
            Paragraph(f"<b>#{rank}</b>", table_cell_bold),
            Paragraph(f"<b>{row['RegionID']}</b><br/>{row['City']}, {row['State']}", table_cell),
            Paragraph(row['PopulationSegment'], table_cell),
            Paragraph(f"{row['MonthlySearchDemand']:,}", table_cell),
            Paragraph(f"<font color='#16a34a'><b>{row['ExistingCompetitors']}</b></font>", table_cell),
            Paragraph(f"{row['LeadConversionRate']:.2%}", table_cell),
            Paragraph(f"INR {row['EstimatedAcquisitionCostINR']}", table_cell),
            Paragraph(f"<font color='#d90429'><b>{row['OpportunityScore']:.2f}</b></font>", table_cell_bold),
        ])
    top3_table = Table(top3_table_data, colWidths=[35, 115, 65, 55, 55, 50, 65, 70])
    top3_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (3,1), (-1,-1), 'CENTER')
    ]))
    story.append(top3_table)
    story.append(Spacer(1, 10))

    # Detailed Micro-Market Highlights
    summary_box_data = [
        [Paragraph(
            "<b>Key Expansion Takeaways for Identified Target Hubs:</b><br/>"
            "• <b>Priority #1 — REG-0027 (Kochi, Kerala):</b> Exceptional student demand of 1,816 queries/mo with an outstanding "
            "13.81% lead conversion rate. Held by only 1 competitor with CAC at INR 613, offering rapid market capture.<br/>"
            "• <b>Priority #2 — REG-0353 (Kolkata, West Bengal):</b> Premium professional hub generating 1,799 queries/mo with high "
            "purchasing power (INR 7.95L median income). With only 1 competitor, expected monthly revenue reaches INR 19.38 Cr.<br/>"
            "• <b>Priority #3 — REG-0206 (Kochi, Kerala):</b> Early Career demographic displaying 1,787 queries/mo, 13.05% conversion, "
            "and industry-lowest CAC of INR 407 against only 1 competitor, maximizing ROI efficiency.",
            callout_style
        )]
    ]
    summary_box = Table(summary_box_data, colWidths=[510])
    summary_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#ecfdf5")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#10b981")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_box)

    # Page 2: Visualizations
    story.append(PageBreak())
    story.append(Paragraph("4. Geospatial Analytics & Visual Intelligence Gallery", h1_style))
    story.append(Paragraph(
        "The following empirical plots illustrate market clustering, competitor saturation curves, and demographic economics:",
        body_style
    ))
    story.append(Spacer(1, 4))

    img1_path = os.path.join(CHARTS_DIR, "01_demand_vs_competitors.png")
    img2_path = os.path.join(CHARTS_DIR, "02_top_underserved_regions.png")
    img3_path = os.path.join(CHARTS_DIR, "03_city_opportunity_and_demand.png")
    img4_path = os.path.join(CHARTS_DIR, "04_revenue_potential_distribution.png")
    img5_path = os.path.join(CHARTS_DIR, "05_population_segment_breakdown.png")
    img6_path = os.path.join(CHARTS_DIR, "06_correlation_matrix.png")

    if os.path.exists(img1_path) and os.path.exists(img2_path):
        img_table = Table([
            [Image(img1_path, width=250, height=145), Image(img2_path, width=250, height=145)],
            [
                Paragraph("<b>Figure 1:</b> Demand vs. Competitor Density (Top 3 Highlighted)", subtitle_style),
                Paragraph("<b>Figure 2:</b> Top 10 Underserved Regional Expansion Targets", subtitle_style)
            ]
        ], colWidths=[255, 255])
        img_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(img_table)
        story.append(Spacer(1, 8))

    if os.path.exists(img3_path) and os.path.exists(img4_path):
        img_table_2 = Table([
            [Image(img3_path, width=250, height=140), Image(img4_path, width=250, height=140)],
            [
                Paragraph("<b>Figure 3:</b> Aggregated City-Level Opportunity vs. Total Demand", subtitle_style),
                Paragraph("<b>Figure 4:</b> Revenue Potential Distribution Across Metros", subtitle_style)
            ]
        ], colWidths=[255, 255])
        img_table_2.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(img_table_2)
        story.append(Spacer(1, 8))

    if os.path.exists(img5_path) and os.path.exists(img6_path):
        img_table_3 = Table([
            [Image(img5_path, width=250, height=135), Image(img6_path, width=250, height=135)],
            [
                Paragraph("<b>Figure 5:</b> Demographic Segment Performance (CAC & Conv)", subtitle_style),
                Paragraph("<b>Figure 6:</b> Correlation Matrix of Geospatial & Financial Metrics", subtitle_style)
            ]
        ], colWidths=[255, 255])
        img_table_3.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(img_table_3)

    # Page 3: City Aggregate Landscape & Phased Rollout
    story.append(PageBreak())
    story.append(Paragraph("5. Metropolitan Macro Landscape & Cluster Benchmarks", h1_style))
    story.append(Paragraph(
        "Aggregating all 400 micro-regions into their respective metropolitan clusters provides clarity on overarching regional characteristics:",
        body_style
    ))

    city_summary = df.groupby('City').agg(
        Count=('RegionID', 'count'),
        AvgDemand=('MonthlySearchDemand', 'mean'),
        TotalDemand=('MonthlySearchDemand', 'sum'),
        AvgComp=('ExistingCompetitors', 'mean'),
        AvgConv=('LeadConversionRate', 'mean'),
        MeanScore=('OpportunityScore', 'mean'),
        MaxScore=('OpportunityScore', 'max')
    ).sort_values(by='MeanScore', ascending=False).reset_index()

    city_table_data = [
        [
            Paragraph("<b>City</b>", table_header),
            Paragraph("<b>Zones</b>", table_header),
            Paragraph("<b>Avg Demand</b>", table_header),
            Paragraph("<b>Total Demand</b>", table_header),
            Paragraph("<b>Avg Comp</b>", table_header),
            Paragraph("<b>Avg Conv %</b>", table_header),
            Paragraph("<b>Mean Score</b>", table_header),
            Paragraph("<b>Max Score</b>", table_header),
        ]
    ]
    for _, r in city_summary.iterrows():
        city_table_data.append([
            Paragraph(f"<b>{r['City']}</b>", table_cell_bold),
            Paragraph(str(r['Count']), table_cell),
            Paragraph(f"{r['AvgDemand']:.0f}", table_cell),
            Paragraph(f"{r['TotalDemand']:,}", table_cell),
            Paragraph(f"{r['AvgComp']:.1f}", table_cell),
            Paragraph(f"{r['AvgConv']:.2%}", table_cell),
            Paragraph(f"<b>{r['MeanScore']:.2f}</b>", table_cell),
            Paragraph(f"{r['MaxScore']:.2f}", table_cell),
        ])
    city_table = Table(city_table_data, colWidths=[75, 45, 65, 75, 55, 65, 65, 65])
    city_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(city_table)
    story.append(Spacer(1, 14))

    # Strategic Expansion Roadmap
    story.append(Paragraph("6. Strategic Expansion Roadmap & Rollout Phases", h1_style))
    roadmap_data = [
        [
            Paragraph("<b>Phase & Timeline</b>", table_header),
            Paragraph("<b>Target Markets</b>", table_header),
            Paragraph("<b>Strategic Rationale & Playbook</b>", table_header)
        ],
        [
            Paragraph("<b>Phase 1</b><br/>Months 1 – 3", table_cell_bold),
            Paragraph("<b>Kochi (REG-0027, REG-0206)</b> & <b>Kolkata (REG-0353)</b>", table_cell),
            Paragraph("Immediate Blitzkrieg acquisition. Capture dominant first-mover share in high-intent student & professional corridors while competitor count is 1. Low CAC delivers sub-3-month payback.", table_cell)
        ],
        [
            Paragraph("<b>Phase 2</b><br/>Months 4 – 6", table_cell_bold),
            Paragraph("<b>Pune (REG-0361)</b> & <b>Bengaluru (REG-0050)</b>", table_cell),
            Paragraph("Expand into Western/Deccan tech corridors. Scale digital marketing channels focusing on Early Career & Student segments with proven willingness to convert.", table_cell)
        ],
        [
            Paragraph("<b>Phase 3</b><br/>Months 7 – 12", table_cell_bold),
            Paragraph("<b>Delhi, Mumbai, Chennai, Ahmedabad</b>", table_cell),
            Paragraph("Mature Metro penetration. Adopt hyper-targeted niche campaigns to bypass entrenched competitors. Focus on high-income micro-pockets with premium pricing models.", table_cell)
        ]
    ]
    roadmap_table = Table(roadmap_data, colWidths=[90, 160, 260])
    roadmap_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(roadmap_table)
    story.append(Spacer(1, 14))

    # Verification and Deliverables
    story.append(Paragraph("7. Interactive Deliverable Links & Repository Artifacts", h1_style))
    story.append(Paragraph(
        "• <b>Interactive Folium Map:</b> <code>geospatial_market_analysis.html</code> (Complete map with cluster zooming, demand heatmap, and glowing pin markers).<br/>"
        "• <b>Reproducible Analysis Notebook:</b> <code>geospatial_analysis.ipynb</code> (Data ingestion, metric modeling, spatial visualizations, and markdown commentary).<br/>"
        "• <b>Static Chart Asset Suite:</b> <code>charts/*.png</code> (High-resolution publication figures at 300 DPI).<br/>"
        "• <b>GitHub Repository:</b> <code>https://github.com/mohanasanthibattula-stack/geospatial-data-analysis</code>",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Compiled executive PDF: {filename}")

if __name__ == "__main__":
    build_pdf(PDF_PATH_1)
    build_pdf(PDF_PATH_2)
