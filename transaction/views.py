from django.shortcuts import render
from transaction.models import transactions
from order.models import AlOrder
import pandas as pd
from django.utils.timezone import make_naive
from django.http import HttpResponse
from datetime import datetime,timedelta
from django.template.loader import render_to_string
from xhtml2pdf import pisa



# Create your views here.
def transaction_list(request):

    alpha = transactions.objects.all()

    
    return render(request,'admin/transaction.html',{'items':alpha})

def download_sales_excel(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    range_option = request.GET.get('range', 'daily')
    print(range_option,start_date,end_date)
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    if range_option == 'daily':
        end_date = datetime.now().date()
        start_date = end_date  
    elif range_option == 'weekly':
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7) 
    elif range_option == 'yearly':
        end_date = datetime.now().date()
        start_date = datetime(end_date.year, 1, 1).date()
    
    orders = AlOrder.objects.all()
    if start_date:
        orders = orders.filter(created_at__gte=start_date)
    if end_date:
        orders = orders.filter(created_at__lte=end_date)


    orders = AlOrder.objects.all()
    data = orders.values('id','user__username','payment_method','total_price','status','coupon__code','created_at')
    
    sample = pd.DataFrame(data)
    if 'created_at' in sample.columns:
        sample['created_at'] = sample['created_at'].apply(lambda x: make_naive(x) if x else x)
    sample.rename(columns={
        'id':'Order ID',
        'user__username':'Client',
        'total_price':'Total',
        'coupon__name':'Coupon',
        'payment_method':'Payment',
        'status':'Status',
        'created_at':'Order Date'

    },inplace=True)
    print('========================================')
    response=HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)

    response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'

    # Write the DataFrame to Excel
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        sample.to_excel(writer, index=False, sheet_name='Sales Report')
    return response

def download_sales_pdf(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    range_option = request.GET.get('range', 'daily')

    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    print(range_option,start_date,end_date)
    if range_option == 'daily':
        end_date = datetime.now().date()
        start_date = end_date  
    elif range_option == 'weekly':
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7) 
    elif range_option == 'yearly':
        end_date = datetime.now().date()
        start_date = datetime(end_date.year, 1, 1).date()
    
    orders = AlOrder.objects.all()
    if start_date:
        orders = orders.filter(created_at__gte=start_date)
    if end_date:
        orders = orders.filter(created_at__lte=end_date)
    orders = AlOrder.objects.all()
    context = {
        "orders":orders,
        "current_year": datetime.now().year

    }

    content = render_to_string('admin/salesreport_port.html',context)
    response = HttpResponse(content_type='application/pdf')
    response['content-disposition'] = 'attachment; filename="sales_report.pdf" '
    pisa_status = pisa.CreatePDF(content,dest=response)
    if pisa_status.err:
        return HttpResponse('An error occured while makeing PDF',status=500)

    return response

def reviews(request):
    return render(request,)