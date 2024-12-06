from time_entries_db_tools import get_time_entries
import chat_bot_tools

import datetime
from datetime import date
from isoweek import Week


def get_week_dates(week_number, year=datetime.datetime.now().year):
    '''
    Returns the start and end dates of the week.
    '''
    monday = Week(year, week_number).monday()
    sunday = Week(year, week_number).sunday()

    return monday, sunday

def hours_to_string(hours):
    full_hours  = int(hours)
    minutes     = (hours - full_hours) * 60
    return '{:2}h {:2.0f}min'.format(full_hours, minutes)


def breakdown_for_user(user_email, week_number, space_name):
    '''
    Sends a card to the space with a breakdown of time entries for the user.
    '''
    print('sending breakdown for user {} for week {}'.format(user_email, week_number))
    monday, sunday  = get_week_dates(week_number)
    title_text = 'week {} (Monday {} - Sunday {}) for {}\n\n'.format(week_number, monday.strftime('%d.%b'), sunday.strftime('%d.%b'), user_email)

    intro_text = 'Hi there! Here is a breakdown of time entries for week {}.'.format(week_number)

    # get time entries
    time_entries = get_time_entries(
        user_email = user_email,
        before= sunday,
        after = monday,
    )[[
        'activity_id',
        'project',
        'type',
        'start_time',
        'end_time',
        'duration'
    ]]


    # get and print stats
    total_time_logged = time_entries['duration'].sum()
    total_seconds_logged = total_time_logged.total_seconds()
    total_hours_logged = total_seconds_logged / (60 * 60)
    total_hours_logged_string = hours_to_string(total_hours_logged)

    overview_text = ''
    overview_text += 'You logged <b>{}</b> '.format(total_hours_logged_string)

    time_spent_in_meetings = time_entries[time_entries['type'] == 'Meeting']['duration'].sum()
    if time_spent_in_meetings == 0:
        hours_spent_in_meetings_string = 'no time'
    else:
        seconds_spent_in_meetings = time_spent_in_meetings.total_seconds()
        hours_spent_in_meetings = seconds_spent_in_meetings / (60 * 60)
        hours_spent_in_meetings_string = hours_to_string(hours_spent_in_meetings)
    overview_text += 'of which you spent <b>{}</b> in meetings. \n'.format(hours_spent_in_meetings_string)

    projects_worked_on = time_entries['project'].unique()
    # overview_text += 'Projects worked on: {}\n'.format(projects_worked_on)
    # overview_text += 'Total number of time entries logged: {}\n\n'.format(len(time_entries))

    subsection_texts = []
    for project in projects_worked_on:
        subsection_text = ['', '']
        if project is None:
            project_seconds_logged = time_entries[time_entries['project'].isnull()]['duration'].sum().total_seconds()
        else:
            project_seconds_logged = time_entries[time_entries['project'] == project]['duration'].sum().total_seconds()

        fraction_of_total = project_seconds_logged / total_seconds_logged
        project_hours_logged = project_seconds_logged / (60 * 60)
        project_hours_logged_string = hours_to_string(project_hours_logged)
        subsection_text[0] = '{}'.format(project)
        subsection_text[1] = ''
        subsection_text[1] += '  Time logged : {}\n'.format(project_hours_logged_string)
        subsection_text[1] += '  Fraction    : {:.2f}%\n'.format(fraction_of_total * 100)

        subsection_texts.append(subsection_text)


    # send message
    chat_bot_tools.send_card(
        space_name = space_name,
        title_text = title_text,
        intro_text = intro_text,
        overview_text = overview_text,
        subsection_texts = subsection_texts
    )

