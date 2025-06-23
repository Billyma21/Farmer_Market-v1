from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from products.models.models import Order, AvailabilityTimeSlot, PickupAppointment
from products.services import PickupService, NotificationService
from products.forms import TimeSlotForm, PickupAppointmentForm


@login_required
def manage_time_slots(request):
    """Vue pour gérer les créneaux horaires (pour les fermiers)"""
    if not request.user.is_farmer:
        messages.error(request, "Vous devez être un fermier pour accéder à cette page.")
        return redirect('home')
    
    slots = PickupService.get_available_slots_for_farmer(request.user)
    
    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            try:
                slot = form.save(commit=False)
                slot.farmer = request.user
                slot.save()
                messages.success(request, "Le créneau horaire a été créé avec succès.")
                return redirect('manage_time_slots')
            except Exception as e:
                messages.error(request, f"Erreur lors de la création du créneau: {str(e)}")
    else:
        form = TimeSlotForm(initial={'farmer': request.user})
    
    return render(request, 'products/time_slots/manage.html', {
        'form': form,
        'slots': slots
    })

@login_required
def edit_time_slot(request, slot_id):
    """Vue pour éditer un créneau horaire"""
    if not request.user.is_farmer:
        messages.error(request, "Vous devez être un fermier pour accéder à cette page.")
        return redirect('home')
    
    slot = get_object_or_404(AvailabilityTimeSlot, id=slot_id, farmer=request.user)
    
    if request.method == 'POST':
        form = TimeSlotForm(request.POST, instance=slot)
        if form.is_valid():
            form.save()
            messages.success(request, "Le créneau horaire a été mis à jour avec succès.")
            return redirect('manage_time_slots')
    else:
        form = TimeSlotForm(instance=slot, initial={'farmer': request.user})
    
    return render(request, 'products/time_slots/edit.html', {
        'form': form,
        'slot': slot
    })

@login_required
def delete_time_slot(request, slot_id):
    """Vue pour supprimer un créneau horaire"""
    if not request.user.is_farmer:
        messages.error(request, "Vous devez être un fermier pour accéder à cette page.")
        return redirect('home')
    
    slot = get_object_or_404(AvailabilityTimeSlot, id=slot_id, farmer=request.user)
    
    # Vérifier s'il y a des rendez-vous future liés à ce créneau
    future_appointments = PickupAppointment.objects.filter(
        availability_slot=slot,
        pickup_date__gte=timezone.now().date()
    )
    
    if future_appointments.exists():
        messages.error(request, "Ce créneau ne peut pas être supprimé car des rendez-vous sont planifiés.")
        return redirect('manage_time_slots')
    
    if request.method == 'POST':
        slot.delete()
        messages.success(request, "Le créneau horaire a été supprimé avec succès.")
        return redirect('manage_time_slots')
    
    return render(request, 'products/time_slots/delete_confirm.html', {
        'slot': slot
    })

@login_required
def schedule_pickup(request, order_id):
    """Vue pour planifier un rendez-vous de retrait"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    # Vérifier que la commande est bien confirmée
    if order.status not in ['confirmed']:
        messages.error(request, "Vous ne pouvez planifier un retrait que pour une commande confirmée.")
        return redirect('order_detail', order_id=order.id)
    
    # Vérifier si un rendez-vous existe déjà
    existing_appointment = PickupAppointment.objects.filter(order=order).first()
    
    if request.method == 'POST':
        form = PickupAppointmentForm(order, request.POST, instance=existing_appointment)
        if form.is_valid():
            with transaction.atomic():
                appointment = form.save(commit=False)
                appointment.order = order
                appointment.save()
                
                # Mettre à jour le statut de la commande
                order.status = 'ready'
                order.save()
                
                # Envoyer une notification
                NotificationService.notify_order_status_change(order, 'confirmed')
                
            messages.success(request, "Votre rendez-vous de retrait a été planifié avec succès.")
            return redirect('order_detail', order_id=order.id)
    else:
        form = PickupAppointmentForm(order, instance=existing_appointment)
    
    return render(request, 'products/orders/schedule_pickup.html', {
        'form': form,
        'order': order
    })

@login_required
def view_pickup_calendar(request):
    """Vue pour afficher le calendrier des retraits (pour les fermiers)"""
    if not request.user.is_farmer:
        messages.error(request, "Vous devez être un fermier pour accéder à cette page.")
        return redirect('home')
    
    # Gestion de la navigation par mois
    today = timezone.now().date()
    
    try:
        month_param = request.GET.get('month', '')
        if month_param:
            year, month = map(int, month_param.split('-'))
            start_date = timezone.datetime(year, month, 1).date()
        else:
            start_date = today.replace(day=1)
    except (ValueError, TypeError):
        start_date = today.replace(day=1)
    
    # Calculer le mois précédent et le mois suivant
    if start_date.month == 1:
        prev_month = f"{start_date.year - 1}-12"
    else:
        prev_month = f"{start_date.year}-{start_date.month - 1}"
    
    if start_date.month == 12:
        next_month = f"{start_date.year + 1}-1"
    else:
        next_month = f"{start_date.year}-{start_date.month + 1}"
    
    # Calculer la date de fin (30 jours après la date de début)
    end_date = start_date + timedelta(days=35)  # Afficher 5 semaines
    
    # Récupérer tous les rendez-vous pour la période
    appointments = PickupAppointment.objects.filter(
        availability_slot__farmer=request.user,
        pickup_date__range=[start_date, end_date]
    ).select_related('order', 'order__customer', 'availability_slot')
    
    # Organiser les rendez-vous par date
    appointments_by_date = {}
    for appointment in appointments:
        date_str = appointment.pickup_date.strftime('%Y-%m-%d')
        if date_str not in appointments_by_date:
            appointments_by_date[date_str] = []
        appointments_by_date[date_str].append(appointment)

    return render(request, 'products/time_slots/calendar.html', {
        'appointments_by_date': appointments_by_date,
        'start_date': start_date,
        'end_date': end_date,
        'today': today,
        'prev_month': prev_month,
        'next_month': next_month
    })