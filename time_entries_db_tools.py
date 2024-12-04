import sqlite3
import pandas as pd
from datetime import date, datetime

# helper functions
def get_time_entries(
        user_email = None,
        project = None,
        before  = date.today(),
        after   = date(2020, 1, 1)
    ):
    '''
    Queries the time_entries table and returns the results.
    Args:
        user_id (int): The user ID to filter by.
        project_code (str): The project code to filter by.
        before (datetime): The latest start date to include.
        after (datetime): The earliest start date to include.
    '''

    # set up the connection to the database
    connection = sqlite3.connect('time_entries.db')
    cursor = connection.cursor()

    # query
    def getDateString(date):
        return date.strftime('%Y-%m-%dT00:00:00.000Z')

    query = "SELECT * FROM time_entries WHERE start_time <= ? AND start_time >= ?"
    params = (getDateString(before), getDateString(after))

    if user_email is not None:
        query += " AND person_email= ?"
        params += (user_email,)

    if project is not None:
        query += " AND project = ?"
        params += (project,)

    result = cursor.execute(query, params)


    all_results =  result.fetchall()

    # close the connection
    connection.close()


    # turn into data frame
    columns = ['person_id', 'person_email', 'activity_id', 'activity_name', 'project', 'type', 'start_time', 'end_time']
    time_entries = pd.DataFrame(all_results, columns = columns)

    # turn start time and end time into datetime objects
    time_entries['start_time']  = pd.to_datetime(time_entries['start_time'])
    time_entries['end_time']    = pd.to_datetime(time_entries['end_time'])

    # add column for duration for each entry
    time_entries['duration'] = time_entries['end_time'] - time_entries['start_time']


    return time_entries

