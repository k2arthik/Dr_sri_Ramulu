from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from django_ratelimit.decorators import ratelimit

from .models import Inquiry
from .forms import InquiryForm


@require_http_methods(['GET', 'POST'])
def inquiry_view(request):  

    if request.method == 'GET':
        return render(request, 'inquiry/inquiry-create.html')
    
    elif request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            form.save()
            # Integration logic
            from utils.dynamodb import process_inquiry
            process_inquiry(form.cleaned_data)
            return redirect("contact-success")

        return render(request, 'inquiry/inquiry-create.html', {
                'errors': form.errors,
                'data': request.POST,
        })
    

@require_http_methods(['POST'])
@ratelimit(key='ip', rate='10/min', method=ratelimit.ALL, block=True)
def inquiry_api_view(request):
    
    form = InquiryForm(request.POST)

    if form.is_valid():
        form.save(commit=False)
        
        # Integration logic
        from utils.dynamodb import process_inquiry
        process_inquiry(form.cleaned_data)

        return JsonResponse({'success': 'inquiry submitted'}, status=200)

    else:
        return JsonResponse({'error': 'invalid data error'}, status=400)


@require_http_methods(['GET'])
def inquiry_success(request):

    return render(request, "components/pages/success.html", {
        'title': 'Inquiry Submitted', 
        'description': 'Thank you for taking time to submit an inquiry, our team will be in touch shortly.'
    })