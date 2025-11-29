from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q, Sum, F
from .models import Product, Transaction, Category, Warehouse
from .forms import ProductForm, TransactionForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'inventory/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(quantity__lte=F('min_stock_level'))
    total_inventory_value = Product.objects.aggregate(
        total=Sum(F('quantity') * F('price'))
    )['total'] or 0
    recent_transactions = Transaction.objects.all()[:5]
    
    context = {
        'total_products': total_products,
        'low_stock_count': low_stock_products.count(),
        'low_stock_products': low_stock_products,
        'total_inventory_value': total_inventory_value,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'inventory/dashboard.html', context)

@login_required
def product_list(request):
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    
    products = Product.objects.all()
    
    if search_query:
        products = products.filter(
            Q(sku__icontains=search_query) | 
            Q(name__icontains=search_query)
        )
    
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    categories = Category.objects.all()
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,
    }
    return render(request, 'inventory/product_list.html', context)

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()
    
    return render(request, 'inventory/product_form.html', {'form': form, 'action': 'Create'})

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'inventory/product_form.html', {'form': form, 'action': 'Edit', 'product': product})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully!')
        return redirect('product_list')
    
    return render(request, 'inventory/product_confirm_delete.html', {'product': product})

@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            try:
                transaction = form.save(commit=False)
                transaction.user = request.user
                transaction.save()
                messages.success(request, f'Transaction recorded successfully! Product quantity updated.')
                return redirect('dashboard')
            except ValueError as e:
                messages.error(request, str(e))
    else:
        form = TransactionForm()
    
    return render(request, 'inventory/transaction_form.html', {'form': form})

@login_required
def reports(request):
    products = Product.objects.all()
    total_value = products.aggregate(total=Sum(F('quantity') * F('price')))['total'] or 0
    low_stock = products.filter(quantity__lte=F('min_stock_level'))
    
    # Category-wise summary
    categories = Category.objects.annotate(
        total_products=Sum('product__quantity'),
        total_value=Sum(F('product__quantity') * F('product__price'))
    )
    
    context = {
        'products': products,
        'total_value': total_value,
        'low_stock': low_stock,
        'categories': categories,
    }
    return render(request, 'inventory/reports.html', context)
