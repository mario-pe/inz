import copy

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
import datetime as dt
from datetime import timedelta

from account.decorators import manager_required
from care_point.forms import WorksheetForm
from care_point.models import Worksheet, Decision
from care_point.utils import _prepare_duties_for_decisoin


@manager_required
def worksheet(request):
    worksheet = Worksheet.objects.all()
    return render(request, 'care_point/worksheet/worksheet.html', {'worksheet': worksheet})


@manager_required
def worksheet_add(request):
    if request.method == 'POST':
        form = WorksheetForm(data=request.POST)
        if form.is_valid():
            new_worksheet = form.save(commit=False)
            quantity = form.cleaned_data.get('quantity')
            if quantity and quantity > 1:
                return _add_multiple_worksheets(request, form, quantity)
            return create_worksheet(request, new_worksheet, path='care_point/worksheet/worksheet_add.html')
    else:
        form = WorksheetForm()
        return render(request, 'care_point/worksheet/worksheet_add.html', {'form': form})

@login_required
def worksheet_details(request, worksheet_id):
    worksheet = get_object_or_404(Worksheet, pk=worksheet_id)
    decision = Decision.objects.filter(pk=worksheet.decision_id).first()
    illnesses, activities = _prepare_duties_for_decisoin(decision)
    return render(request, 'care_point/worksheet/worksheet_details.html', {'worksheet': worksheet,
                                                                           'illnesses': illnesses,
                                                                           'decision': decision,
                                                                           'activities': activities})


@manager_required
def worksheet_update(request, worksheet_id):
    worksheet = get_object_or_404(Worksheet, pk=worksheet_id)
    form = WorksheetForm(data=request.POST or None, instance=worksheet)
    if request.method == 'POST':
        if form.is_valid():
            new_worksheet = form.save(commit=False)
            return create_worksheet(request, new_worksheet, path='care_point/worksheet/worksheet_update.html')
        return redirect('care_point:worksheet')
    return render(request, 'care_point/worksheet/worksheet_update.html', {'form': form})


@manager_required
def worksheet_delete(request, worksheet_id):
    worksheet = get_object_or_404(Worksheet, pk=worksheet_id)
    worksheet.delete()
    return redirect('care_point:worksheet')


@manager_required
def create_worksheet(request, new_worksheet, path):
    caregiver_worksheet_at_date, ward_worksheet_at_date = get_caregiver_and_ward_worksheets_for_date(new_worksheet)
    is_caregiver_free = check_available(caregiver_worksheet_at_date, new_worksheet)
    is_ward_free = check_available(ward_worksheet_at_date, new_worksheet)
    if not is_new_worksheet_time_valid(new_worksheet):
        info = "Nieprawidłowe godziny"
        form = WorksheetForm(data=request.POST, instance=new_worksheet)
        return render(request, path, {'form': form, "info": info})
    elif is_caregiver_free and is_ward_free:
        new_worksheet.save()
        return redirect('care_point:worksheet')
    elif not is_caregiver_free:
        info = "W godzinach " + new_worksheet.hour_from.__str__() + " - " + new_worksheet.hour_to.__str__() + " pracownik " + new_worksheet.caregiver.__str__() + " wykonuje inne obowiazki"
        form = WorksheetForm(data=request.POST, instance=new_worksheet)
        return render(request, path, {'form': form, "info": info})
    elif not is_ward_free:
        info = "W godzinach " + new_worksheet.hour_from.__str__() + " - " + new_worksheet.hour_to.__str__() + " podopieczny " + new_worksheet.ward.__str__() + " ma inna wizyte"
        form = WorksheetForm(data=request.POST, instance=new_worksheet)
        return render(request, path, {'form': form, "info": info})


def check_available(worksheets, new_worksheet):
    new_worksheet_time_from = dt.datetime.combine(dt.date(1, 1, 1), new_worksheet.hour_from)
    new_worksheet_time_to = dt.datetime.combine(dt.date(1, 1, 1), new_worksheet.hour_to)
    compare_time = dt.timedelta(0, 0, 0)
    is_free = True
    if len(worksheets) > 0:
        for i in worksheets:
            worksheet_time_from = dt.datetime.combine(dt.date(1, 1, 1), i.hour_from)
            worksheet_time_to = dt.datetime.combine(dt.date(1, 1, 1), i.hour_to)
            if worksheet_time_from - new_worksheet_time_from < compare_time:
                if worksheet_time_to - new_worksheet_time_from > compare_time or worksheet_time_to - new_worksheet_time_to > compare_time:
                    is_free = False
            elif worksheet_time_from - new_worksheet_time_from > compare_time:
                if worksheet_time_from - new_worksheet_time_to < compare_time or worksheet_time_to - new_worksheet_time_to < compare_time:
                    is_free = False
            else:
                is_free = False
    return is_free


def get_caregiver_and_ward_worksheets_for_date(worksheet):
    caregiver_worksheets = Worksheet.objects.filter(caregiver=worksheet.caregiver).filter(date=worksheet.date)
    ward_worksheets = Worksheet.objects.filter(ward=worksheet.ward).filter(date=worksheet.date)
    return caregiver_worksheets, ward_worksheets


def is_new_worksheet_time_valid(new_worksheet):
    new_time_from = dt.datetime.combine(dt.date(1, 1, 1), new_worksheet.hour_from)
    new_time_to = dt.datetime.combine(dt.date(1, 1, 1), new_worksheet.hour_to)
    compare_time = dt.timedelta(0, 0, 0)
    if new_time_from - new_time_to < compare_time:
        return True
    return False


def _add_multiple_worksheets(request, form, quantity):
    new_worksheet = form.save(commit=False)
    interval = form.cleaned_data.get('interval')
    date = form.cleaned_data.get('date')
    worksheets = prepare_worksheet_list(new_worksheet, interval, date, quantity - 1)
    info = save_correct_worksheets(worksheets)
    worksheet_all = Worksheet.objects.all()
    return render(request, 'care_point/worksheet/worksheet.html', {'info': info, 'worksheet': worksheet_all})


def prepare_worksheet_list(worksheet, interval, date, quantity):
    worksheets = []
    worksheets.append(worksheet)
    for i in range(quantity):
        delta = timedelta(days=+interval)
        date = date + delta
        next_worksheet = copy.deepcopy(worksheet)
        next_worksheet.date = date
        worksheets.append(next_worksheet)
    return worksheets


def save_correct_worksheets(worksheets):
    info = ''
    worksheet_to_save = []
    for w in worksheets:
        message, worksheet = create_worksheet_for_multiple_creator(w)
        if worksheet:
            worksheet_to_save.append(worksheet)
        info += message
    Worksheet.objects.bulk_create(worksheet_to_save)
    return info


def create_worksheet_for_multiple_creator(new_worksheet):
    caregiver_worksheet_at_date, ward_worksheet_at_date = get_caregiver_and_ward_worksheets_for_date(new_worksheet)
    is_caregiver_free = check_available(caregiver_worksheet_at_date, new_worksheet)
    is_ward_free = check_available(ward_worksheet_at_date, new_worksheet)
    if not is_new_worksheet_time_valid(new_worksheet):
        info = "Karta pracy z dnia " + new_worksheet.date.__str__() + " ma błedne godziny początek:" + new_worksheet.hour_from.__str__() + " ,koniec: " + new_worksheet.hour_to.__str__() + '.' + ' \n'
        return info, None
    elif is_caregiver_free and is_ward_free:
        info = "Pomyslnie dodano karte pracy na dzień " + new_worksheet.date.__str__() + " w  godzinach " + new_worksheet.hour_from.__str__() + " - " + new_worksheet.hour_to.__str__() + '.' + '\n'
        return info, new_worksheet
    elif not is_caregiver_free:
        info = "Dnia " + new_worksheet.date.__str__() + " w  godzinach " + new_worksheet.hour_from.__str__() + " - " + new_worksheet.hour_to.__str__() + " pracownik " + new_worksheet.caregiver.__str__() + " wykonuje inne obowiazki." + '\n'
        return info, None
    elif not is_ward_free:
        info = "Dnia " + new_worksheet.date.__str__() + " w godzinach " + new_worksheet.hour_from.__str__() + " - " + new_worksheet.hour_to.__str__() + " podopieczny " + new_worksheet.ward.__str__() + " ma inna wizyte." + '\n'
        return info, None
