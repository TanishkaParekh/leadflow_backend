from django.shortcuts import render

# Create your views here.
# invoices/views.py
from django.http import JsonResponse
from .selectors import get_invoice_dashboard_stats

def invoice_stats_api(request):
    data = get_invoice_dashboard_stats()
    return JsonResponse(data)

from datetime import datetime
from django.http import HttpResponse
from django.template.loader import get_template
from rest_framework.views import APIView
from rest_framework.response import Response
from xhtml2pdf import pisa
from .reports import get_monthly_financial_report

class MonthlyReportAPIView(APIView):
    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        export_format = request.query_params.get('format')

        data = get_monthly_financial_report(month=month, year=year)

        # If user asks for ?format=pdf, trigger the PDF generator
        if export_format == 'pdf':
            return self.generate_pdf_response(data, month, year)
        
        return Response(data)

    def generate_pdf_response(self, data, month, year):
        template = get_template('invoices/report_pdf_template.html')
        context = {'report': data, 'today': datetime.now()}
        html = template.render(context)
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="LeadFlow_Report_{month}_{year}.pdf"'
        
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error generating PDF', status=500)
        return response