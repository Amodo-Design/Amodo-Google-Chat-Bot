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


def wrapped2024(user_email, space_name):
    # chat_bot_tools.send_message(
    #     space_name = space_name,
    #     message = 'Shhhh, this is a secret.'
    # )
    # return

    title_text = 'Your Amodo Task Wrapped 2024'

    intro_text = 'It\'s that time of the year. Wrapped is ready. Are you?'

    overview_text = '🌠 Life moves fast. Luckily, we took notes.\n\n'


    # get time entries
    time_entries = get_time_entries(
        user_email = user_email,
        after = date(2024, 1, 1),
    )[[
        'activity_id',
        'activity_name',
        'project',
        'type',
        'start_time',
        'end_time',
        'duration'
    ]]

    if len(time_entries) == 0:
        chat_bot_tools.send_message(
            space_name = space_name,
            message = 'I could not find any time entries for you this year.'
        )
        return


    subsection_texts = []

    # general
    total_time_logged = time_entries['duration'].sum()
    total_seconds_logged = total_time_logged.total_seconds()
    total_hours_logged = total_seconds_logged / (60 * 60)
    total_hours_logged_string = hours_to_string(total_hours_logged)

    overview_text += '⌛ You logged <b>{}</b> this year.'.format(total_hours_logged_string)



    # activities overview
    subsection = ['', '\n']
    activities = time_entries['activity_id'].unique()
    top_activity = time_entries['activity_id'].value_counts().idxmax()
    top_activity_name = time_entries[time_entries['activity_id'] == top_activity]['activity_name'].values[0]

    top_activity_time_logged = time_entries[time_entries['activity_id'] == top_activity]['duration'].sum()
    top_activity_seconds_logged = top_activity_time_logged.total_seconds()
    top_activity_hours = top_activity_seconds_logged / (60 * 60)
    top_activity_hours_string = hours_to_string(top_activity_hours)

    subsection[0] += '🌃 You logged time for <b>{}</b> activities.'.format(len(activities))
    subsection[1] += '⭐ But one stood out. Your top activity was <b>{}</b> with <b>{}</b> logged.\n\n'.format(top_activity_name, top_activity_hours_string)
    subsection[1] += '🔧 You logged it <b>{}</b> times.'.format(time_entries[time_entries['activity_id'] == top_activity].shape[0])

    subsection_texts.append(subsection)

    # top activities
    subsection = ['', '\n']
    subsection[0] += '🪜 While it\'s not a competition... '
    subsection[0] += 'There is a leaderboard.\n\n'
    subsection[0] += '🏆 Your top activities by time were:'


    # top_activities = time_entries['activity_id'].value_counts().head(5)[1:]
    top_activities = time_entries.groupby('activity_id')['duration'].sum().sort_values(ascending=False)[1:5]
    for activity in top_activities.index:
        activity_hours = time_entries[time_entries['activity_id'] == activity]['duration'].sum().total_seconds() / (60 * 60)
        activity_hours_string = hours_to_string(activity_hours)
        activity_name = time_entries[time_entries['activity_id'] == activity]['activity_name'].values[0]
        subsection[1] += '<b>{}</b> for <b>{}</b>. '.format(activity_hours_string, activity_name)
        subsection[1] += 'You logged this <b>{}</b> times.\n\n'.format(time_entries[time_entries['activity_id'] == activity].shape[0])

    subsection[1] += '👀 Any surprises?'

    subsection_texts.append(subsection)


    # top projects
    subsection = ['', '\n']

    number_of_projects = len(time_entries['project'].unique())

    if number_of_projects > 1 and number_of_projects < 5:
        max_projects = number_of_projects
    else:
        max_projects = 5
    subsection[0] += '🔨 Your top projects by time were:'
    top_projects = time_entries.groupby('project')['duration'].sum().sort_values(ascending=False).head(max_projects)
    for project in top_projects.index:
        project_hours = time_entries[time_entries['project'] == project]['duration'].sum().total_seconds() / (60 * 60)
        project_hours_string = hours_to_string(project_hours)
        subsection[1] += '<b>{}</b> for <b>{}</b>. '.format(project_hours_string, project)
        subsection[1] += 'You logged this <b>{}</b> times.\n\n'.format(time_entries[time_entries['project'] == project].shape[0])

    subsection[1] += '🏗️ You worked on <b>{}</b> projects this year.'.format(number_of_projects)


    subsection_texts.append(subsection)

    # meetings
    subsection = ['', '\n']
    time_spent_in_meetings = time_entries[time_entries['type'] == 'Meeting']['duration'].sum()
    seconds_spent_in_meetings = time_spent_in_meetings.total_seconds()
    if seconds_spent_in_meetings > 0:
        hours_spent_in_meetings = seconds_spent_in_meetings / (60 * 60)
        hours_spent_in_meetings_string = hours_to_string(hours_spent_in_meetings)

        longest_meeting = time_entries[time_entries['type'] == 'Meeting']['duration'].max()

        longest_meeting_seconds = longest_meeting.total_seconds()
        longest_meeting_hours = longest_meeting_seconds / (60 * 60)
        longest_meeting_hours_string = hours_to_string(longest_meeting_hours)
        longest_meeting_name = time_entries[time_entries['duration'] == longest_meeting]['activity_name'].values[0]

        subsection[0] += '🤝 You went to <b>{}</b> meetings.'.format(len(time_entries[time_entries['type'] == 'Meeting']))
        subsection[1] += '🕐 They added up to <b>{}</b>.\n\n'.format(hours_spent_in_meetings_string)
        subsection[1] += '💤 Your longest meeting was <b>{}</b> with <b>{}</b> logged.\n\n'.format(longest_meeting_name, longest_meeting_hours_string)

        meeting_fraction = time_spent_in_meetings / total_time_logged
        subsection[1] += '📊 Overall, you spent {:.2f}% of your time in meetings.'.format(meeting_fraction * 100)

        if meeting_fraction > 0.5:
            subsection[1] += '\n\n💼 You are in your meeting babe era!'

        subsection_texts.append(subsection)

    # final comments

    subsection = ['', '\n']
    subsection[0] += '📝 And that\'s a wrap.'
    subsection[1] += '🎉 Congratulations on a productive year and keep up the great work!'


    subsection_texts.append(subsection)


    # send message
    chat_bot_tools.send_card(
        space_name = space_name,
        title_text = title_text,
        intro_text = intro_text,
        overview_text = overview_text,
        subsection_texts = subsection_texts
    )

