import calendar

from django.http import JsonResponse
from django.shortcuts import render
from .models import Feedback, Giver, ENTRUSTABILITY_SCORES, ACTIVITIES


# primary view, calls the html script
def bootstrap_view(request):
    # no filtering done on initial request
    qs_inputs = filter_request(request, 'None')
    # store the filter input from the form so users will not have to reenter data upon each filter request
    url_filter = request.META['QUERY_STRING']
    context = {
        'queryset': qs_inputs['qs'],
        'activities': qs_inputs['activities'],
        'givers': qs_inputs['givers'],
        'url_filter': url_filter,
        'selected_inputs': qs_inputs['selected_inputs'],
        'entrustability_dict': qs_inputs['entrustability_dict'],
        'activities_dict': qs_inputs['activities_dict']
    }
    return render(request, "bootstrap_form.html", context)


# primary filtering method used by views
# request is the html request
# config is to disable certain filtering for specific chart types, can be empty, 'GiverPie', or 'ActivityType'
def filter_request(request, config):
    # order by date and store all queries
    qs = Feedback.objects.order_by('feedbackDate').all()
    start_date_query = request.GET.get('startDate')
    end_date_query = request.GET.get('endDate')
    giver_name_query = request.GET.get('giverName')
    complicated_query = request.GET.get('complicated')
    complex_query = request.GET.get('complex')
    not_complicated_query = request.GET.get('notComplicated')
    not_complex_query = request.GET.get('notComplex')
    activity_query = request.GET.get('activity')
    sorting_query = request.GET.get('byTime')

    # save initial inputs
    selected_start_date = start_date_query
    selected_end_date = end_date_query
    selected_giver = giver_name_query
    selected_complicated = complicated_query
    selected_complex = complex_query
    selected_not_complicated = not_complicated_query
    selected_not_complex = not_complex_query
    selected_activity = activity_query
    selected_sorting = sorting_query

    # filtering
    if is_valid_queryparam(giver_name_query) and giver_name_query != 'All' and config != 'GiverPie':
        qs = qs.filter(giver__name__icontains=giver_name_query)
    else:
        selected_giver = 'All'
    if is_valid_queryparam(start_date_query):
        qs = qs.filter(feedbackDate__gte=start_date_query)
    else:
        selected_start_date = "2017-01-01"  # preset date for filling
    if is_valid_queryparam(end_date_query):
        qs = qs.filter(feedbackDate__lt=end_date_query)
    else:
        selected_end_date = "2019-12-31"  # preset date for filling
    # if complicated is on, set complicated to true (regardless of if not_complicated is also on)
    if complicated_query == 'on':
        qs = qs.filter(complicated=True)
    elif not_complicated_query == 'on':
        qs = qs.filter(complicated=False)
    else:
        selected_complicated = 'off'
        selected_not_complicated = 'off'
    if complex_query == 'on':
        qs = qs.filter(complex=True)
    elif not_complex_query == 'on':
        qs = qs.filter(complex=False)
    else:
        selected_complex = 'off'
        selected_not_complex = 'off'
    if is_valid_queryparam(activity_query) and activity_query != 'All' and config != 'ActivityRadar':
        qs = qs.filter(activity=activity_query)
    else:
        selected_activity = 'All'

    activities = Feedback.objects.order_by('activity').values('activity').distinct()
    givers = Feedback.objects.order_by('giver__name').values('giver__name').distinct()

    # store selected inputs
    selected_inputs = {
        'selected_start_date': selected_start_date,
        'selected_end_date': selected_end_date,
        'selected_giver': selected_giver,
        'selected_complicated': selected_complicated,
        'selected_complex': selected_complex,
        'selected_not_complicated': selected_not_complicated,
        'selected_not_complex': selected_not_complex,
        'selected_activity': selected_activity,
        'selected_sorting': selected_sorting
    }
    qs_inputs = {
        'qs': qs,
        'selected_inputs': selected_inputs,
        'entrustability_dict': dict(ENTRUSTABILITY_SCORES),
        'activities_dict': dict(ACTIVITIES),
        'givers': givers,
        'activities': activities
    }
    return qs_inputs


# primary method for generating the appropriate data for the feedback chart
def feedback_chart(request):
    # run all filters
    qs_inputs = filter_request(request, 'None')
    qs = qs_inputs['qs']
    selected_inputs = qs_inputs['selected_inputs']
    data = []
    labels = []
    # averages the entrustability score by year and month
    data_month, data_year, labels_month, labels_year = averaging_helper(qs, selected_inputs['selected_start_date'],
                                                                        selected_inputs['selected_end_date'])

    # display appropriate output based on user input, default to month
    if selected_inputs['selected_sorting'] == 'byYear':
        data = data_year
        labels = labels_year
    elif selected_inputs['selected_sorting'] == 'byIndividual':
        for entry in qs:
            data.append(entry.entrustability)
            labels.append(entry.to_month_day_year())
    else:
        data = data_month
        labels = labels_month

    return JsonResponse(data={
        'labels': labels,
        'data': data,
        'selected_inputs': selected_inputs,
        'entrustability_dict': qs_inputs['entrustability_dict'],
        'activities_dict': qs_inputs['activities_dict']
    })


# primary method for generating the appropriate data for the giver pie chart
def giver_pie_chart(request):
    # run all filters using config: 'GiverPie'
    qs_inputs = filter_request(request, 'GiverPie')
    qs = qs_inputs['qs']
    selected_inputs = qs_inputs['selected_inputs']

    # primary helper function that counts the amount of feedback given be each giver
    labels, data_count = count_by_giver(qs, qs_inputs['givers'])

    return JsonResponse(data={
        'labels': labels,
        'data': data_count,
        'selected_inputs': selected_inputs,
        'entrustability_dict': qs_inputs['entrustability_dict'],
        'activities_dict': qs_inputs['activities_dict']
    })


# primary method for generating the appropriate data for the activity radar chart
def activity_radar_chart(request):
    # run all filters using config: 'ActivityRadar'
    qs_inputs = filter_request(request, 'ActivityRadar')
    qs = qs_inputs['qs']
    selected_inputs = qs_inputs['selected_inputs']

    # primary helper function that averages entrustability scores by activities
    labels, data = average_by_activity(qs, qs_inputs['activities'])

    return JsonResponse(data={
        'labels': labels,
        'data': data,
        'selected_inputs': selected_inputs,
        'entrustability_dict': qs_inputs['entrustability_dict'],
        'activities_dict': qs_inputs['activities_dict']
    })


# primary helper function for generating the average entrustability score by year and month
def averaging_helper(qs, start_date, end_date):
    # this only works for the given data model
    start_year = int(start_date[0:4])
    end_year = int(end_date[0:4])
    start_month = int(start_date[5:7])
    end_month = int(end_date[5:7])
    labels_month = []
    labels_year = []
    data_month = []
    data_year = []

    # exception handling
    if start_year == end_year and start_month > end_month:
        return data_month, data_year, labels_month, labels_year
    if start_year > end_year:
        return data_month, data_year, labels_month, labels_year

    # creating labels
    cur_year = start_year
    cur_month = start_month
    labels_year_temp = []
    while cur_year != end_year or cur_month != end_month:
        labels_month.append(calendar.month_abbr[cur_month] + ' ' + str(cur_year))
        labels_year_temp.append(str(cur_year))
        if cur_month == 12:
            cur_month = 1
            cur_year = cur_year + 1
        else:
            cur_month = cur_month + 1
    labels_month.append(calendar.month_abbr[cur_month] + ' ' + str(cur_year))
    labels_year_temp.append(str(cur_year))
    for i in labels_year_temp:
        if i not in labels_year:
            labels_year.append(i)

    data_sum_year = [0] * len(labels_year)
    data_sum_month = [0] * len(labels_month)
    data_count_year = [0] * len(labels_year)
    data_count_month = [0] * len(labels_month)

    # iterating through queryset to sum entrustability scores
    for entry in qs:
        index_year = labels_year.index(entry.to_year())
        data_sum_year[index_year] = data_sum_year[index_year] + entry.entrustability
        data_count_year[index_year] = data_count_year[index_year] + 1
        index_month = labels_month.index(entry.to_month_year())
        data_sum_month[index_month] = data_sum_month[index_month] + entry.entrustability
        data_count_month[index_month] = data_count_month[index_month] + 1

    # average the values ofr month and year
    for index in range(0, len(labels_year)):
        if data_count_year[index] == 0:
            data_year.append(None)
        else:
            data_year.append(data_sum_year[index] / data_count_year[index])
    for index in range(0, len(labels_month)):
        if data_count_month[index] == 0:
            data_month.append(None)
        else:
            data_month.append(data_sum_month[index] / data_count_month[index])

    return data_month, data_year, labels_month, labels_year


# primary helper function for the giver pie chart, counts the amount of feedback given by each giver
def count_by_giver(qs, givers):
    labels = []
    for giver in givers:
        labels.append(giver['giver__name'])
    data_count = [0] * len(givers)

    for entry in qs:
        index = labels.index(entry.giver.name)
        data_count[index] = data_count[index] + 1

    return labels, data_count


# primary helper function for the activity radar chart, calculates the average entrustability score by activity
def average_by_activity(qs, activities):
    # creating initial variables
    labels = []
    labels_temp = []
    for activity in activities:
        labels.append(dict(ACTIVITIES)[activity['activity']])
        labels_temp.append(activity['activity'])
    data_sum = [0] * len(activities)
    data_count = [0] * len(activities)
    data = []

    # iterating through all entries and queryset and summing the entrustability
    for entry in qs:
        index = labels_temp.index(entry.activity)
        data_sum[index] = data_sum[index] + entry.entrustability
        data_count[index] = data_count[index] + 1

    # averaging the scores
    for index in range(0, len(labels)):
        if data_count[index] == 0:
            data.append(None)
        else:
            data.append(data_sum[index] / data_count[index])

    return labels, data


# checks if the given query parameter is valid
def is_valid_queryparam(param):
    return param != '' and param is not None
