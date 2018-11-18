from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from care_point.forms import AddressForm, Ward
from care_point.models import Address


@login_required
def address(request):
    address = Address.objects.all()
    return render(request, 'care_point/address/address.html', {'address': address})


@login_required
def address_add(request):
    if request.method == 'POST':
        form = AddressForm(data=request.POST)
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
            # ward_id = new.id
        # return render(request, 'care_point/ward/address_add.html', {'ward_id': ward_id})
        return redirect('care_point:address')
    else:
        form = AddressForm()
        return render(request, 'care_point/address/address_add.html', {'form': form})


@login_required
def address_details(request, address_id):
    address = get_object_or_404(Address, pk=address_id)
    ward = Ward.objects.filter(address=address).all
    return render(request, 'care_point/address/address_details.html', {'address': address, 'ward': ward})


@login_required
def address_update(request, address_id):

    a = get_object_or_404(Address, pk=address_id)
    form = AddressForm(data=request.POST or None, instance=a)
    if request.method == 'POST':
        if form.is_valid():
            new = form.save(commit=False)
            new.save()
        return redirect('care_point:address')
    return render(request, 'care_point/address/address_update.html', {'form': form})


@login_required
def address_delete(request, address_id):
    address = get_object_or_404(Address, pk=address_id)
    address.delete()
    return redirect('care_point:address')