from itertools import product
from unittest.util import safe_repr
from django.contrib import messages 
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect
from .models import *
from django.db.models import Q
from .forms import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json




# Create your views here.

def home(request):


    return render(request, 'base/home.html', {})

def market(request):

    items = Item.objects.all()

    if request.GET.get('q') != None:
        return redirect('search')

    context = {'items':items}

    return render(request, 'base/marketplace.html', context)

def search(request):

    if request.GET.get('q') != None:
        query = request.GET.get('q')
    else:
        query = ''

    items = Item.objects.filter(Q(item_name__icontains = query))
    items_count = items.count
    context = {
        'items' : items,
        'items_count' : items_count,
    }
    return render(request, 'base/searchResults.html', context)

@login_required(login_url='login')
def cart(request):

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer = customer, complete = False)
        items = order.orderitems_set.all()
    else: 
        items = [] 
        order = {'get_cart_total' : 0, 'get_cart_items': 0}
    
    return render(request, 'base/cart.html', {'items':items, 'order':order})

def product_info(request,pk):

    item = Item.objects.get(id=pk)
    item_tags = item.tags.similar_objects()

    context = {
        'item' : item,
        'item_tags' : item_tags
    }
    return render(request, 'base/info.html', context)

def register_view(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'{user.first_name}, your account has been created succesfully')
            return redirect('home')
        else:
            messages.error(request, 'An error has occured')
    return render(request, 'base/register.html', {'form' : form, 'page':page })

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = UserModel.objects.get(email=email)
        except:
            # messages.error(request, 'User does not exist')
            pass

        user = authenticate(request, email=email , password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'{user.first_name} logged in succesfully')
            return redirect('home')
        else: 
            messages.error(request, 'Email and password do not match')
             
    return render(request, 'base/login.html', {})

def logout_view(request):

    logout(request)
    messages.info(request, f'You have been logged out')
    return redirect('home')


def update_item(request):

    data = json.loads(request.body)
    itemId = data['itemId']
    action = data['action']

    customer = request.user
    item = Item.objects.get(id=itemId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItems, created = OrderItems.objects.get_or_create(order = order, item = item)

    if action == 'add':
        orderItems.item_quantity = (orderItems.item_quantity + 1 )
    elif action == 'remove':
        orderItems.item_quantity = (orderItems.item_quantity - 1 )


    orderItems.save()
    
    if orderItems.item_quantity <= 0:
        orderItems.delete()


    return JsonResponse('Item was added', safe=False)