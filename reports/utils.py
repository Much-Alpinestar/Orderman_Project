from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from orders.models import Order
from datetime import date, timedelta
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from decimal import Decimal


def get_daily_report_data():
    today = date.today()
    orders = Order.objects.filter(created_at__date=today)
    return orders

def get_monthly_report_data():
    today = date.today()
    first_day_of_month = today.replace(day=1)
    orders = Order.objects.filter(created_at__date__gte=first_day_of_month)
    return orders

def get_yearly_report_data():
    today = date.today()
    first_day_of_year = today.replace(month=1, day=1)
    orders = Order.objects.filter(created_at__date__gte=first_day_of_year)
    return orders

def get_custom_report_data(start_date, end_date):
    orders = Order.objects.filter(
        created_at__date__gte=start_date, created_at__date__lte=end_date
    )
    return orders


def generate_pdf(response, orders, report_title):
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Firmenname und Berichtstitel
    elements.append(Paragraph("Fritzhütte", styles['Title']))
    elements.append(Paragraph(report_title, styles['Title']))
    elements.append(Spacer(1, 12))

    # Datum
    elements.append(Paragraph(f"Datum: {timezone.localtime(timezone.now()).strftime('%d.%m.%Y')}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Tabelle der Bestellungen
    data = [['Bestellnr.', 'Tisch/Kunde', 'Artikel', 'Menge', 'Preis (€)', 'Erstellt am', 'Preis ohne MwSt', 'Preis mit MwSt']]
    for order in orders:
        total_price = Decimal('0.00')
        table_or_customer = f'Tisch {order.table.number_of_table}' if order.table else f'Kunde {order.customer.name}'
        data.append([order.id, table_or_customer, '', '', '', timezone.localtime(order.created_at).strftime('%d.%m.%Y %H:%M'), '', ''])
        for item in order.items.all():
            item_total_price = item.quantity * item.price
            total_price += item_total_price
            if item.food:
                tax_rate = Decimal('1.10')  # 10% MwSt für Speisen
            else:
                tax_rate = Decimal('1.20')  # 20% MwSt für Getränke
            price_without_tax = item_total_price / tax_rate
            price_with_tax = item_total_price
            data.append(['', '', item.food.name if item.food else item.beverage.name, item.quantity, f'{item_total_price:.2f}', '', f'{price_without_tax:.2f}', f'{price_with_tax:.2f}'])
        total_price_without_tax = total_price / Decimal('1.20')  # Beispiel für gemischte Steuer
        total_price_with_tax = total_price
        data.append(['', '', 'Gesamt', '', f'{total_price:.2f}', '', f'{total_price_without_tax:.2f}', f'{total_price_with_tax:.2f}'])
        data.append(['', '', '', '', '', '', '', ''])  # Leerzeile zur Trennung der Bestellungen

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F81BD')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#DCE6F1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),  # Dickere Linie unter dem Header
        ('LINEBELOW', (0, 1), (-1, -1), 1, colors.grey),  # Dünne Linien zwischen den Zeilen
        ('LINEABOVE', (0, -2), (-1, -2), 1.5, colors.black),  # Dickere Linie zwischen Bestellungen
    ]))

    elements.append(table)
    doc.build(elements)