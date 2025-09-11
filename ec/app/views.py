from django.db.models import Count
from django.shortcuts import render, redirect 
from django.views import View
from django.db import models
from .models import Cart, Product, Customer
from .forms import CustomerProfileForm, CustomerRegistrationForm 
from django.contrib import messages 
from django.contrib.auth.decorators import login_required 
from django.utils.decorators import method_decorator 
from django.http import JsonResponse 
from django.db.models import Q
from django.contrib.auth.models import User



# Create your views here.
def home(request):
    return render(request, "app/home.html")

def about(request):
    return render(request, "app/about.html")

def contact(request):
    return render(request, "app/contact.html")

class CategoryView(View):
    def get(self, request, val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request, "app/category.html", locals())

class CategoryTitle(View):
    def get(self, request, val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        return render(request, "app/category.html", locals())

class ProductDetail(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        return render(request, "app/productdetail.html", locals())

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', locals())

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Congratulations! User Registered Successfully")
            return redirect('home')
        else:
            messages.warning(request, "Invalid Input Data")
            return render(request, 'app/customerregistration.html', locals())

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', locals())

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            boulevard = form.cleaned_data['boulevard']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=user, name=name, locality=locality, city=city, mobile=mobile, boulevard=boulevard, zipcode=zipcode)
            reg.save()
            messages.success(request, "Congratulations! Profile Saved Successfully")
            return redirect('profile')
        else:
            messages.warning(request, "Invalid Input Data")
            return render(request, 'app/profile.html', locals())

def address(request):  
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', locals())

# ... keep everything above as-is ...

class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)
        return render(request, 'app/updateAddress.html', locals())

    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.boulevard = form.cleaned_data['boulevard']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request, "Congratulations! Profile Saved Successfully")
        else:
            messages.warning(request, "Invalid Input Data")
        return redirect("address")

# ↓↓↓ DEDENT THIS so it’s not inside the class ↓↓↓


@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')  # or product_id, just be consistent
    try:
        product = Product.objects.get(id=product_id)
        Cart.objects.create(user=user, product=product)
    except Product.DoesNotExist:
        messages.error(request, "This product does not exist.")
        return redirect("home")
    return redirect("showcart")



@login_required
def show_cart(request):
    cart = Cart.objects.filter(user=request.user).select_related('product')

    amount = sum(item.total_cost for item in cart)   # now selling_price × quantity
    shipping = 10 if cart else 0
    totalamount = amount + shipping

    return render(
        request,
        'app/addtocart.html',
        {
            'cart': cart,
            'amount': amount,
            'shipping': shipping,
            'totalamount': totalamount
        }
    )



@method_decorator(login_required, name='dispatch')
class checkout(View):
    def get(self, request):
        # Why: be explicit and resilient; avoid locals()
        user = request.user

        cart_items = (
            Cart.objects.filter(user=user)
            .select_related('product')
        )
        amount = sum(item.quantity * item.product.selling_price for item in cart_items)
        shipping = 10 if cart_items else 0
        totalamount = amount + shipping

        add = Customer.objects.filter(user=user)

        return render(
            request,
            'app/checkout.html',
            {
                'cart_items': cart_items,
                'totalamount': totalamount,
                'add': add,
            },
        )
    
    

   

    

   
        








from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Cart, Product
from django.db.models import Q

@csrf_exempt
@login_required
def plus_cart(request):
    if request.method == 'GET':
        try:
            prod_id = request.GET.get('prod_id')
            if not prod_id:
                return JsonResponse({'error': 'Missing prod_id'}, status=400)

            cart_item = Cart.objects.filter(product_id=prod_id, user=request.user).first()
            if not cart_item:
                return JsonResponse({'error': 'Cart item not found'}, status=404)

            cart_item.quantity += 1
            cart_item.save()

            cart = Cart.objects.filter(user=request.user).select_related('product')
            amount = sum(item.quantity * item.product.selling_price for item in cart)
            shipping = 10 if cart else 0
            totalamount = amount + shipping

            return JsonResponse({
                'quantity': cart_item.quantity,
                'amount': amount,
                'totalamount': totalamount
            })

        except Exception as e:
            return JsonResponse({'error': 'Server error', 'details': str(e)}, status=500)

    


@csrf_exempt
@login_required
def remove_cart(request):
    if request.method == 'GET':
        try:
            prod_id = request.GET.get('prod_id')
            if not prod_id:
                return JsonResponse({'error': 'Missing prod_id'}, status=400)

            cart_items = Cart.objects.filter(product_id=prod_id, user=request.user)
            if not cart_items.exists():
                return JsonResponse({'error': 'Cart item not found'}, status=404)

            cart_items.delete()

            cart = Cart.objects.filter(user=request.user).select_related('product')
            amount = sum(item.quantity * item.product.selling_price for item in cart)
            shipping = 10 if cart else 0
            totalamount = amount + shipping

            return JsonResponse({
                'amount': amount,
                'totalamount': totalamount,
                'empty': cart.count() == 0
            })

        except Exception as e:
            return JsonResponse({'error': 'Server error', 'details': str(e)}, status=500)

      

      
@csrf_exempt
@login_required
def minus_cart(request):
    if request.method == 'GET':
        try:
            prod_id = request.GET.get('prod_id')
            if not prod_id:
                return JsonResponse({'error': 'Missing prod_id'}, status=400)

            cart_item = Cart.objects.filter(product_id=prod_id, user=request.user).first()
            if not cart_item:
                return JsonResponse({'error': 'Cart item not found'}, status=404)

            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()

            cart = Cart.objects.filter(user=request.user).select_related('product')
            amount = sum(item.quantity * item.product.selling_price for item in cart)
            shipping = 10 if cart else 0
            totalamount = amount + shipping

            return JsonResponse({
                'quantity': cart_item.quantity if cart_item.id else 0,
                'amount': amount,
                'totalamount': totalamount,
                'empty': cart.count() == 0
            })

        except Exception as e:
            return JsonResponse({'error': 'Server error', 'details': str(e)}, status=500)


       
       

