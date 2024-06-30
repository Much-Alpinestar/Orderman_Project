""" from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from orders.models import Order
from datetime import date, timedelta

def get_daily_report_data():
    today = date.today()
    orders = Order.objects.filter(created_at__date=today)
    return orders

def get_monthly_report_data():
    today = date.today()
    first_day_of_month = today.replace(day=1)
    orders = Order.objects.filter(created_at__date__gte=first_day_of_month)
    return orders

def get_custom_report_data(start_date, end_date):
    orders = Order.objects.filter(created_at__date__gte=start_date, created_at__date__lte=end_date)
    return orders

def generate_pdf(response, orders):
    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    c.drawString(100, height - 100, "Bestellbericht")
    y = height - 150
    for order in orders:
        c.drawString(100, y, f"Bestellung {order.id}: {order.total_price} €")
        y -= 20
    c.showPage()
    c.save()
 """