from django.shortcuts import render
from django.http import HttpResponse
from .utils import get_daily_report_data, get_monthly_report_data, get_custom_report_data, generate_pdf, get_yearly_report_data

def generate_daily_report(request):
    data = get_daily_report_data()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="daily_report.pdf"'
    generate_pdf(response, data, "Tagesbericht")
    return response

def generate_monthly_report(request):
    data = get_monthly_report_data()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="monthly_report.pdf"'
    generate_pdf(response, data, "Monatsbericht")
    return response

def generate_yearly_report(request):
    data = get_yearly_report_data()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition']= 'attachment; filename="Jahresbericht.pdf"'
    generate_pdf(response, data, "Jahresbericht")
    return response

def list_reports(request):
    return render(request, 'reports/index.html')

def generate_custom_report(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        data = get_custom_report_data(start_date, end_date)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="custom_report_{start_date}_to_{end_date}.pdf"'
        generate_pdf(response, data, f"Benutzerdefinierter Bericht: {start_date} bis {end_date}")
        return response
    return render(request, 'reports/custom_report_form.html')
