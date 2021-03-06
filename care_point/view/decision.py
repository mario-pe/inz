from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from account.decorators import manager_required
from care_point.forms import DecisionFormWard, IllnessFormCheckboxes, ActivityFormCheckboxes
from care_point.models import Decision, WardIllness, WardActivity, Illness
from care_point.utils import _update_or_create_duties, _prepare_duties_for_decisoin


@manager_required
def decision(request):
    decision = Decision.objects.all().order_by('id').reverse()
    return render(request, 'care_point/decision/decision.html', {'decision': decision})


@manager_required
def decision_add(request):
    if request.method == 'POST':
        decision_form = DecisionFormWard(data=request.POST)
        illness_form = IllnessFormCheckboxes(data=request.POST)
        activity_form = ActivityFormCheckboxes(data=request.POST)
        if decision_form.is_valid() and illness_form.is_valid() and activity_form.is_valid():
            decisoin = decision_form.save(commit=False)
            decisoin.save()
            new_decision = decision_form.instance
            illnesses = illness_form.cleaned_data['illness']
            activities = activity_form.cleaned_data['activity']
            _update_or_create_duties(decision=new_decision, new_illnesses=illnesses, new_activites=activities)
            return redirect('care_point:decision')
        else:
            return render(request, 'care_point/decision/decision_add.html', {'form': decision_form,
                                                                             'illness_form': illness_form,
                                                                             'activity_form': activity_form})

    else:
        decision_form = DecisionFormWard()
        illness_form = IllnessFormCheckboxes()
        activity_form = ActivityFormCheckboxes()
        return render(request, 'care_point/decision/decision_add.html', {'form': decision_form,
                                                                         'illness_form': illness_form,
                                                                         'activity_form': activity_form})


@manager_required
def decision_details(request, decision_id):
    decision = get_object_or_404(Decision, pk=decision_id)
    illnesses, activities = _prepare_duties_for_decisoin(decision)
    return render(request, 'care_point/decision/decision_details.html', {'decision': decision,
                                                                         'illness': illnesses,
                                                                         'activity': activities, })


@manager_required
def decision_update(request, decision_id):
    decision = get_object_or_404(Decision, pk=decision_id)  # wyciagnac dane
    ward_illness_for_decision, ward_activity_for_decision = _prepare_duties_for_decisoin(decision=decision)
    if request.method == 'POST':
        decision_form = DecisionFormWard(data=request.POST, instance=decision)
        illness_form = IllnessFormCheckboxes(data=request.POST)
        activity_form = ActivityFormCheckboxes(data=request.POST)
        if request.method == 'POST':
            if decision_form.is_valid() and illness_form.is_valid() and activity_form.is_valid():
                new_illnesses_for_update = illness_form.cleaned_data['illness']
                new_activites_for_update = activity_form.cleaned_data['activity']
                decision = decision_form.save(commit=False)
                _update_or_create_duties(decision, new_illnesses_for_update, new_activites_for_update, ward_illness_for_decision, ward_activity_for_decision)
                decision.save()
            return redirect('care_point:decision')
    else:
        decision_form = DecisionFormWard(instance=decision)
        illness_form = IllnessFormCheckboxes()
        activity_form = ActivityFormCheckboxes()
        return render(request, 'care_point/decision/decision_update.html', {'form': decision_form,
                                                                            'illness_form': illness_form,
                                                                            'activity_form': activity_form,
                                                                            'ward_illness_for_decision': _generate_duties_ids(ward_illness_for_decision),
                                                                            'ward_activity_for_decision': _generate_duties_ids(ward_activity_for_decision),
                                                                            })


@manager_required
def decision_delete(request, decision_id):
    decision = get_object_or_404(Decision, pk=decision_id)
    decision.delete()
    return redirect('care_point:decision')


def _generate_duties_ids(duties):
    ids =[]
    for d in duties:
        ids.append(d.id)
    return ids