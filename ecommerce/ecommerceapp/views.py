from django.shortcuts import render
from ecommerceapp.models import Contact,Product,Orders,OrderUpdate,Order,Order3
from django.contrib import messages
from math import ceil
from ecommerceapp import keys
from django.conf import settings
MERCHANT_KEY=keys.MK
import json
from django.views.decorators.csrf import  csrf_exempt
import razorpay
from django.http import JsonResponse
import logging

# Create your views here.
def index(request):
    allProds = []
    catprods = Product.objects.values('category','id')
    print(catprods)
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params= {'allProds':allProds}

    return render(request,"index.html",params)
    

def contact(request):
     if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        desc=request.POST.get("desc")
        pnumber=request.POST.get("pnumber")
        myquery=Contact(name=name,email=email,desc=desc,phonenumber=pnumber)
        myquery.save()
        messages.info(request,"we will get back to you soon..")
     return render(request,"contact.html")


    
# Initialize Razorpay client
# client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

# def checkout(request):
#     if request.method == "POST":
#         items_json = request.POST.get('itemsJson', '')
#         name = request.POST.get('name', '')
#         amount = float(request.POST.get('amt', 0))  # Convert amount to float
#         email = request.POST.get('email', '')
#         address1 = request.POST.get('address1', '')
#         address2 = request.POST.get('address2', '')
#         city = request.POST.get('city', '')
#         state = request.POST.get('state', '')
#         zip_code = request.POST.get('zip_code', '')
#         phone = request.POST.get('phone', '')

#         # Create a new order in your database
#         order = Orders(
#             items_json=items_json,
#             name=name,
#             amount=amount,
#             email=email,
#             address1=address1,
#             address2=address2,
#             city=city,
#             state=state,
#             zip_code=zip_code,
#             phone=phone
#         )
#         order.save()

#         # Create a Razorpay Order
#         razorpay_order = client.order.create({
#             "amount": int(amount * 100),  # Convert to paisa
#             "currency": "INR",
#             "payment_capture": "1"
#         })

#         # Update the order with the Razorpay order ID
#         order.razorpay_order_id = razorpay_order['id']
#         order.save()

#         # Prepare the context for the template
#         context = {
#             'order_id': razorpay_order['id'],
#             'amount': amount,
#             'currency': 'INR',
#             'key': settings.RAZORPAY_API_KEY,
#             'name': name,
#             'email': email,
#             'phone': phone,
#             'address1': address1,
#             'address2': address2,
#             'city': city,
#             'state': state,
#             'zip_code': zip_code
#         }

#         return render(request, 'checkout.html', context)

#     return render(request, 'checkout.html')

def checkout(request):
    if request.method == "POST":
        # Get form data
        items_json = request.POST.get('itemsJson', '')
        amount = request.POST.get('amt', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        # Save order in the database
        order = Order(items_json=items_json, amount=amount, name=name, email=email,
                      address1=address1, address2=address2, city=city, state=state,
                      zip_code=zip_code, phone=phone)
        order.save()

        # Generate the payment ID with Razorpay
        client = razorpay.Client(auth=("rzp_test_X6uVA1Ff0ddxCQ", ""))
        payment = client.order.create({'amount': int(amount) * 100, 'currency': 'INR', 'payment_capture': '1'})

        order.razorpay_order_id = payment['id']
        order.save()

        return render(request, 'checkout.html', {'payment': payment})

    return render(request, 'checkout.html')

# @csrf_exempt
# def handlerequest(request):
#     # paytm will send you post request here
#     form = request.POST
#     response_dict = {}
#     for i in form.keys():
#         response_dict[i] = form[i]
#         if i == 'CHECKSUMHASH':
#             checksum = form[i]

#     verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
#     if verify:
#         if response_dict['RESPCODE'] == '01':
#             print('order successful')
#             a=response_dict['ORDERID']
#             b=response_dict['TXNAMOUNT']
#             rid=a.replace("ShopyCart","")
           
#             print(rid)
#             filter2= Orders.objects.filter(order_id=rid)
#             print(filter2)
#             print(a,b)
#             for post1 in filter2:

#                 post1.oid=a
#                 post1.amountpaid=b
#                 post1.paymentstatus="PAID"
#                 post1.save()
#             print("run agede function")
#         else:
#             print('order was not successful because' + response_dict['RESPMSG'])
#     return render(request, 'paymentstatus.html', {'response': response_dict})



@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        payment_id = data.get('razorpay_payment_id')
        order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')

        try:
            # Verify the payment signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })

            # Update the order status to paid
            order = Orders.objects.get(razorpay_order_id=order_id)
            order.is_paid = True
            order.save()

            # Add an order update
            update = OrderUpdate(order_id=order.order_id, update_desc="The order has been paid")
            update.save()

            return JsonResponse({'status': 'success'})
        except:
            return JsonResponse({'status': 'failed'})

    return JsonResponse({'status': 'failed'})









def profile(request):
    # if not request.user.is_authenticated:
    #     messages.warning(request,"Login & Try Again")
    #     return redirect('/auth/login')
    # currentuser=request.user.username
    # items=Orders.objects.filter(email=currentuser)
    # rid=""
    # for i in items:
    #     print(i.oid)
    #     # print(i.order_id)
    #     myid=i.oid
    #     rid=myid.replace("ShopyCart","")
    #     print(rid)
    # status=OrderUpdate.objects.filter(order_id=int(rid))
    # for j in status:
    #     print(j.update_desc)

   
    # context ={"items":items,"status":status}
    # print(currentuser)
    return render(request,"profile.html")


def order_confirmation(request):
    return render(request, 'order_confirmation.html')
