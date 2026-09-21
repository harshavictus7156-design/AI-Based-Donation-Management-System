from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from donor.models import Donor, Donation
from django.db.models import Sum

def home(request):
    return render(request, 'home.html')
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {
                'error': 'Invalid username or password'
            })

    return render(request, 'login.html')
def dashboard(request):
    total_donors = Donor.objects.count()
    total_donations = Donation.objects.count()

    total_quantity = (
        Donation.objects.aggregate(
            total=Sum("quantity")
        )["total"] or 0
    )

    pending_donations = Donation.objects.filter(
        status="Pending"
    ).count()

    accepted_donations = Donation.objects.filter(
        status="Accepted"
    ).count()

    collected_donations = Donation.objects.filter(
        status="Collected"
    ).count()

    return JsonResponse({
        "total_donors": total_donors,
        "total_donations": total_donations,
        "total_quantity": total_quantity,
        "pending_donations": pending_donations,
        "accepted_donations": accepted_donations,
        "collected_donations": collected_donations,
    })