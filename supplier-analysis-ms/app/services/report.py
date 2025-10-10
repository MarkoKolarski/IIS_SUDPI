from typing import List, Dict, Any, Optional
from datetime import date, datetime
import logging
import tempfile
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import LineChart
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import requests

from app import crud

class ReportGenerator:
    def __init__(self, django_service_url: Optional[str] = None):
        """
        Initialize the report generator
        django_service_url: URL of the Django service to fetch relational data
        """
        self.styles = getSampleStyleSheet()
        self.django_service_url = django_service_url or os.environ.get("DJANGO_SERVICE_URL", "http://localhost:8000")
        
    def _get_django_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Get data from Django service
        """
        try:
            url = f"{self.django_service_url}/api/{endpoint}"
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error fetching data from Django: {e}")
            return {}
    
    def generate_supplier_report(self, supplier_id: int) -> bytes:
        """
        Generate a comprehensive report for a specific supplier
        """
        # Get supplier data from Neo4j
        supplier_analytics = crud.get_supplier(supplier_id)
        supplier_complaints = crud.get_supplier_complaints(supplier_id)
        supplier_certificates = crud.get_supplier_certificates(supplier_id)
        alternative_suppliers = crud.find_better_suppliers(supplier_id)
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Collect the story (content)
        story = []
        
        # Title
        title_style = self.styles["Heading1"]
        story.append(Paragraph(f"Supplier Analysis Report", title_style))
        story.append(Spacer(1, 0.25 * inch))
        
        # Supplier Information
        if supplier_analytics:
            story.append(Paragraph(f"Supplier: {supplier_analytics.get('name', 'N/A')}", self.styles["Heading2"]))
            story.append(Spacer(1, 0.1 * inch))
            
            # Create a table for supplier details
            supplier_data = [
                ["ID", str(supplier_analytics.get('supplier_id', 'N/A'))],
                ["Email", supplier_analytics.get('email', 'N/A')],
                ["PIB", supplier_analytics.get('pib', 'N/A')],
                ["Material", supplier_analytics.get('material_name', 'N/A')],
                ["Price", f"{supplier_analytics.get('price', 'N/A')} RSD"],
                ["Delivery Time", f"{supplier_analytics.get('delivery_time', 'N/A')} days"],
                ["Rating", f"{supplier_analytics.get('rating', 'N/A')}/10"],
                ["Rating Date", supplier_analytics.get('rating_date', 'N/A')],
            ]
            
            supplier_table = Table(supplier_data, colWidths=[2*inch, 3*inch])
            supplier_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(supplier_table)
            story.append(Spacer(1, 0.25 * inch))
            
        # Complaints Section
        story.append(Paragraph("Complaint History", self.styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))
        
        if supplier_complaints:
            # Create a chart for complaints severity
            complaint_data = []
            complaint_labels = []
            
            # Sort complaints by date
            sorted_complaints = sorted(supplier_complaints, 
                                      key=lambda x: x.get('reception_date', '2000-01-01'))
            
            for complaint in sorted_complaints:
                complaint_data.append(complaint.get('severity', 0))
                complaint_date = complaint.get('reception_date', 'N/A')
                if isinstance(complaint_date, str) and len(complaint_date) >= 10:
                    complaint_date = complaint_date[:10]  # Format as YYYY-MM-DD
                complaint_labels.append(complaint_date)
            
            # Create matplotlib chart
            plt.figure(figsize=(8, 4))
            plt.bar(complaint_labels, complaint_data, color='coral')
            plt.xlabel('Complaint Date')
            plt.ylabel('Severity (1-10)')
            plt.title('Complaint Severity History')
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Save chart to a temporary buffer
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)
            
            # Add the chart to the PDF
            img = Image(img_buffer, width=6*inch, height=3*inch)
            story.append(img)
            story.append(Spacer(1, 0.1 * inch))
            plt.close()
            
            # Complaints table
            complaint_table_data = [["Date", "Severity", "Duration", "Status", "Description"]]
            for complaint in sorted_complaints:
                complaint_date = complaint.get('reception_date', 'N/A')
                if isinstance(complaint_date, str) and len(complaint_date) >= 10:
                    complaint_date = complaint_date[:10]
                    
                complaint_table_data.append([
                    complaint_date,
                    complaint.get('severity', 'N/A'),
                    f"{complaint.get('duration', 'N/A')} days",
                    complaint.get('status', 'N/A'),
                    complaint.get('problem_description', 'N/A')[:50] + '...' 
                    if len(complaint.get('problem_description', '')) > 50 else complaint.get('problem_description', 'N/A')
                ])
            
            complaint_table = Table(complaint_table_data, colWidths=[1*inch, 0.8*inch, 0.8*inch, 1*inch, 2.4*inch])
            complaint_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(complaint_table)
        else:
            story.append(Paragraph("No complaints recorded for this supplier.", self.styles["Normal"]))
        
        story.append(Spacer(1, 0.25 * inch))
        
        # Certificates Section
        story.append(Paragraph("Certificates", self.styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))
        
        if supplier_certificates:
            cert_table_data = [["Certificate", "Type", "Issue Date", "Expiry Date"]]
            for cert in supplier_certificates:
                issue_date = cert.get('issue_date', 'N/A')
                if isinstance(issue_date, str) and len(issue_date) >= 10:
                    issue_date = issue_date[:10]
                
                expiry_date = cert.get('expiry_date', 'N/A')
                if isinstance(expiry_date, str) and len(expiry_date) >= 10:
                    expiry_date = expiry_date[:10]
                    
                cert_table_data.append([
                    cert.get('name', 'N/A'),
                    cert.get('type', 'N/A'),
                    issue_date,
                    expiry_date
                ])
            
            cert_table = Table(cert_table_data, colWidths=[2*inch, 1*inch, 1.5*inch, 1.5*inch])
            cert_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(cert_table)
        else:
            story.append(Paragraph("No certificates recorded for this supplier.", self.styles["Normal"]))
        
        story.append(Spacer(1, 0.25 * inch))
        
        # Alternative Suppliers Section
        story.append(Paragraph("Alternative Suppliers", self.styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))
        
        if alternative_suppliers:
            alt_table_data = [["Supplier", "Rating", "Price", "Comparison"]]
            for alt in alternative_suppliers:
                alt_table_data.append([
                    alt.get('name', 'N/A'),
                    f"{alt.get('rating', 'N/A')}/10",
                    f"{alt.get('price', 'N/A')} RSD",
                    alt.get('price_comparison', 'N/A').replace('_', ' ').title()
                ])
            
            alt_table = Table(alt_table_data, colWidths=[2*inch, 1*inch, 1.5*inch, 1.5*inch])
            alt_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(alt_table)
        else:
            story.append(Paragraph("No alternative suppliers found.", self.styles["Normal"]))
        
        # Build the PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_supplier_comparison_report(self, supplier_ids: List[int]) -> bytes:
        """
        Generate a report comparing multiple suppliers
        """
        if not supplier_ids or len(supplier_ids) < 2:
            raise ValueError("At least two supplier IDs must be provided for comparison")
        
        # Get suppliers data
        suppliers = []
        for supplier_id in supplier_ids:
            supplier = crud.get_supplier(supplier_id)
            if supplier:
                supplier_complaints = crud.get_supplier_complaints(supplier_id)
                supplier_certificates = crud.get_supplier_certificates(supplier_id)
                supplier['complaint_count'] = len(supplier_complaints)
                supplier['certificate_count'] = len(supplier_certificates)
                suppliers.append(supplier)
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Collect the story
        story = []
        
        # Title
        title_style = self.styles["Heading1"]
        story.append(Paragraph(f"Supplier Comparison Report", title_style))
        story.append(Spacer(1, 0.25 * inch))
        
        # Summary table
        story.append(Paragraph("Supplier Comparison Summary", self.styles["Heading2"]))
        story.append(Spacer(1, 0.1 * inch))
        
        if suppliers:
            # Create comparison table
            comparison_data = [["Metric"] + [s.get('name', f"Supplier {i+1}") for i, s in enumerate(suppliers)]]
            
            # Add metrics rows
            metrics = [
                ("Material", "material_name"),
                ("Price", "price"),
                ("Rating", "rating"),
                ("Delivery Time (days)", "delivery_time"),
                ("Complaints", "complaint_count"),
                ("Certificates", "certificate_count")
            ]
            
            for metric_name, metric_key in metrics:
                row = [metric_name]
                for supplier in suppliers:
                    value = supplier.get(metric_key, "N/A")
                    if metric_key == "price":
                        value = f"{value} RSD" if value != "N/A" else "N/A"
                    row.append(value)
                comparison_data.append(row)
            
            # Create the table
            col_widths = [1.5*inch] + [4.5*inch / len(suppliers) for _ in suppliers]
            comparison_table = Table(comparison_data, colWidths=col_widths)
            
            # Style the table
            comparison_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(comparison_table)
            story.append(Spacer(1, 0.25 * inch))
            
            # Create comparison charts
            # Rating comparison
            story.append(Paragraph("Rating Comparison", self.styles["Heading3"]))
            
            labels = [s.get('name', f"Supplier {i+1}")[:10] for i, s in enumerate(suppliers)]
            ratings = [float(s.get('rating', 0)) for s in suppliers]
            
            plt.figure(figsize=(8, 4))
            bars = plt.bar(labels, ratings, color='steelblue')
            plt.xlabel('Supplier')
            plt.ylabel('Rating (0-10)')
            plt.title('Supplier Rating Comparison')
            plt.ylim(0, 10)
            
            # Add rating values on top of bars
            for bar, rating in zip(bars, ratings):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                         f"{rating:.1f}", ha='center')
            
            # Save chart to buffer
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)
            
            # Add the chart to PDF
            img = Image(img_buffer, width=6*inch, height=3*inch)
            story.append(img)
            story.append(Spacer(1, 0.2 * inch))
            plt.close()
            
            # Price comparison
            story.append(Paragraph("Price Comparison", self.styles["Heading3"]))
            
            prices = [float(s.get('price', 0)) for s in suppliers]
            
            plt.figure(figsize=(8, 4))
            bars = plt.bar(labels, prices, color='coral')
            plt.xlabel('Supplier')
            plt.ylabel('Price (RSD)')
            plt.title('Price Comparison for ' + suppliers[0].get('material_name', 'Material'))
            
            # Add price values on top of bars
            for bar, price in zip(bars, prices):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                         f"{price:.2f}", ha='center')
            
            # Save chart to buffer
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)
            
            # Add the chart to PDF
            img = Image(img_buffer, width=6*inch, height=3*inch)
            story.append(img)
            plt.close()
            
            # Recommendation section
            story.append(Spacer(1, 0.25 * inch))
            story.append(Paragraph("Recommendation", self.styles["Heading2"]))
            story.append(Spacer(1, 0.1 * inch))
            
            # Simple recommendation algorithm based on rating and price
            best_supplier = None
            best_score = -1
            
            for supplier in suppliers:
                # Normalize rating and price
                try:
                    rating = float(supplier.get('rating', 0))
                    price = float(supplier.get('price', float('inf')))
                    delivery_time = float(supplier.get('delivery_time', float('inf')))
                    
                    # Calculate score - higher is better
                    # 60% rating, 30% price, 10% delivery time
                    # For price and delivery time, lower is better
                    max_price = max(float(s.get('price', 0)) for s in suppliers)
                    max_delivery = max(float(s.get('delivery_time', 0)) for s in suppliers)
                    
                    price_score = 1 - (price / max_price) if max_price > 0 else 0
                    delivery_score = 1 - (delivery_time / max_delivery) if max_delivery > 0 else 0
                    
                    score = (rating / 10) * 0.6 + price_score * 0.3 + delivery_score * 0.1
                    
                    if score > best_score:
                        best_score = score
                        best_supplier = supplier
                except (ValueError, TypeError):
                    continue
            
            if best_supplier:
                story.append(Paragraph(
                    f"Based on our analysis, <b>{best_supplier.get('name', 'N/A')}</b> appears to be the best choice " +
                    f"with a rating of {best_supplier.get('rating', 'N/A')}/10 and competitive pricing of " +
                    f"{best_supplier.get('price', 'N/A')} RSD.",
                    self.styles["Normal"]
                ))
            else:
                story.append(Paragraph(
                    "Unable to determine the best supplier from the provided data.",
                    self.styles["Normal"]
                ))
        else:
            story.append(Paragraph("No supplier data available for comparison.", self.styles["Normal"]))
        
        # Build the PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def generate_material_suppliers_report(self, material_name: str) -> bytes:
        """
        Generate a report of all suppliers for a specific material
        """
        # Get suppliers for this material
        suppliers = crud.find_alternative_suppliers(material_name)
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Collect the story
        story = []
        
        # Title
        title_style = self.styles["Heading1"]
        story.append(Paragraph(f"Material Suppliers Report", title_style))
        story.append(Paragraph(f"Material: {material_name}", self.styles["Heading2"]))
        story.append(Spacer(1, 0.25 * inch))
        
        if suppliers:
            # Summary statistics
            avg_price = sum(float(s.get('price', 0)) for s in suppliers) / len(suppliers)
            avg_rating = sum(float(s.get('rating', 0)) for s in suppliers) / len(suppliers)
            min_price = min(float(s.get('price', float('inf'))) for s in suppliers)
            max_rating = max(float(s.get('rating', 0)) for s in suppliers)
            
            story.append(Paragraph("Market Summary", self.styles["Heading3"]))
            summary_data = [
                ["Metric", "Value"],
                ["Number of Suppliers", str(len(suppliers))],
                ["Average Price", f"{avg_price:.2f} RSD"],
                ["Average Rating", f"{avg_rating:.2f}/10"],
                ["Lowest Price", f"{min_price:.2f} RSD"],
                ["Highest Rating", f"{max_rating:.2f}/10"],
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('BACKGROUND', (0, 1), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(summary_table)
            story.append(Spacer(1, 0.25 * inch))
            
            # List all suppliers
            story.append(Paragraph("All Suppliers", self.styles["Heading3"]))
            
            # Sort suppliers by rating (highest first)
            sorted_suppliers = sorted(suppliers, key=lambda s: float(s.get('rating', 0)), reverse=True)
            
            supplier_data = [["Supplier", "Rating", "Price", "Delivery Time"]]
            for supplier in sorted_suppliers:
                supplier_data.append([
                    supplier.get('name', 'N/A'),
                    f"{supplier.get('rating', 'N/A')}/10",
                    f"{supplier.get('price', 'N/A')} RSD",
                    f"{supplier.get('delivery_time', 'N/A')} days"
                ])
            
            supplier_table = Table(supplier_data, colWidths=[2*inch, 1*inch, 1.5*inch, 1.5*inch])
            supplier_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(supplier_table)
            story.append(Spacer(1, 0.25 * inch))
            
            # Price vs. Rating chart
            story.append(Paragraph("Price vs. Rating Analysis", self.styles["Heading3"]))
            
            prices = [float(s.get('price', 0)) for s in sorted_suppliers]
            ratings = [float(s.get('rating', 0)) for s in sorted_suppliers]
            names = [s.get('name', f"Supplier {i}") for i, s in enumerate(sorted_suppliers)]
            
            plt.figure(figsize=(8, 6))
            plt.scatter(ratings, prices, alpha=0.7, s=100)
            
            # Add supplier names as labels
            for i, name in enumerate(names):
                plt.annotate(name[:10] + ('...' if len(name) > 10 else ''), 
                            (ratings[i], prices[i]),
                            xytext=(5, 5),
                            textcoords='offset points')
            
            plt.xlabel('Rating (0-10)')
            plt.ylabel('Price (RSD)')
            plt.title(f'Price vs. Rating for {material_name} Suppliers')
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # Save chart to buffer
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)
            
            # Add the chart to PDF
            img = Image(img_buffer, width=6*inch, height=4.5*inch)
            story.append(img)
            story.append(Spacer(1, 0.2 * inch))
            plt.close()
            
            # Recommendations section
            story.append(Paragraph("Recommendations", self.styles["Heading3"]))
            
            # Find best value suppliers (good balance of price and rating)
            value_scores = []
            for supplier in suppliers:
                try:
                    rating = float(supplier.get('rating', 0))
                    price = float(supplier.get('price', float('inf')))
                    
                    # Normalize price (0-1 where 1 is the cheapest)
                    max_price = max(float(s.get('price', 0)) for s in suppliers)
                    normalized_price = 1 - (price / max_price) if max_price > 0 else 0
                    
                    # Calculate value score (60% rating, 40% price)
                    value_score = (rating / 10) * 0.6 + normalized_price * 0.4
                    
                    value_scores.append({
                        'name': supplier.get('name', 'N/A'),
                        'rating': rating,
                        'price': price,
                        'value_score': value_score
                    })
                except (ValueError, TypeError):
                    continue
            
            # Sort by value score
            value_scores.sort(key=lambda x: x['value_score'], reverse=True)
            
            # Add recommendations
            if value_scores:
                story.append(Paragraph("Best Value Suppliers:", self.styles["Heading4"]))
                for i, supplier in enumerate(value_scores[:3], 1):
                    story.append(Paragraph(
                        f"{i}. <b>{supplier['name']}</b> - Rating: {supplier['rating']}/10, " +
                        f"Price: {supplier['price']} RSD",
                        self.styles["Normal"]
                    ))
                story.append(Spacer(1, 0.1 * inch))
            
            # Find cheapest supplier with acceptable rating
            acceptable_suppliers = [s for s in suppliers if float(s.get('rating', 0)) >= 6.0]
            if acceptable_suppliers:
                cheapest = min(acceptable_suppliers, key=lambda s: float(s.get('price', float('inf'))))
                story.append(Paragraph("Best Budget Option:", self.styles["Heading4"]))
                story.append(Paragraph(
                    f"<b>{cheapest.get('name', 'N/A')}</b> - Rating: {cheapest.get('rating', 'N/A')}/10, " +
                    f"Price: {cheapest.get('price', 'N/A')} RSD",
                    self.styles["Normal"]
                ))
                story.append(Spacer(1, 0.1 * inch))
                
            # Find highest rated supplier
            highest_rated = max(suppliers, key=lambda s: float(s.get('rating', 0)))
            story.append(Paragraph("Highest Quality Option:", self.styles["Heading4"]))
            story.append(Paragraph(
                f"<b>{highest_rated.get('name', 'N/A')}</b> - Rating: {highest_rated.get('rating', 'N/A')}/10, " +
                f"Price: {highest_rated.get('price', 'N/A')} RSD",
                self.styles["Normal"]
            ))
            
        else:
            story.append(Paragraph(f"No suppliers found for {material_name}.", self.styles["Normal"]))
        
        # Build the PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
