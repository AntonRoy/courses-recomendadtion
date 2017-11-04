
# coding: utf-8

# In[7]:

from functools import partial
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import sqlite3
import re
import json
import requests


# In[64]:

cnn = sqlite3.connect("data")
cur = cnn.cursor()


# In[9]:

def get_token() -> str:
    client_id = 'UV9HpDB6lTdJXa35ayxxCX9Iw47rptSMHHRB4Qx9'
    client_secret = '0c1kWfRCRJp5GWswqLbNZU8OzP9id9MlWS5PH2Ycg16FfHscK7Oqiquf7uikggp8MY1vfinhyCZQt9QwXsjSOqK9lhmYkXCe9jNRTqDsUoSmgPMblgKgq1NEMPvyHsXN'

    auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    resp = requests.post('https://stepik.org/oauth2/token/',
                         data={'grant_type': 'client_credentials'},
                         auth=auth)

    return json.loads(resp.text)['access_token']


# In[41]:

already_in_db_ids = cur.execute("select * from courses where type == '{0}'".format("stepic")).fetchall()


# In[11]:

get_course_url = lambda x: "https://stepik.org/course/%s/" % x


# In[34]:

def get_data(page: int) -> list:
    api_url = 'https://stepik.org/api/courses?page=%s' % page
    html = requests.get(api_url, headers={'Authorization': 'Bearer ' + get_token()}).text
    course = json.loads(html)
    return [course['courses'], course['meta']['has_next']]


# In[35]:

def parse_new_state_for_stepic_course(_id):
    html = requests.get("https://stepik.org/api/courses/%s/" % _id, headers=mozilla_headers).text
    html = json.loads(html)
    return html['courses'][0]['is_active']


# In[54]:

def parse_course(course: dict):
    text = course['course_format'] + " "
    text += course['description'] + " "
    text += course['certificate'] + " "
    text += course['requirements'] + " "
    text += course['summary'] + " "
    text += course['target_audience'] + " "
    text += course['title'] + " "

    #text = clear_text(text)

    if course['cover']:
        image = 'https://stepik.org{}'.format(course['cover'])
    else:
        image = None

    if len(course['title']) < 3 or len(text) < 5:
        return None
    cnn = sqlite3.connect("data")
    cur = cnn.cursor()
    try:
        cur.execute(
            "insert into courses (title, text, type, url) values ('{0}', '{1}', '{2}', '{3}')"
                    .format(course['title'], 
                            text, 
                            "stepic", 
                            get_course_url(course['id']))
        )
    except:
        pass
    cnn.commit()
    cnn.close()
    return (course['title'], text, "stepic", get_course_url(course['id']))


# In[55]:

def download_from_page(page_number: int):
    flag = True
    whole_data = []
    pbar = tqdm(desc="Download stepic dataset")

    while flag:
        current_data = get_data(page_number)
        data = current_data[0]
        data = list(filter(lambda x: x['id'] not in already_in_db_ids, data))
        whole_data += list(map(parse_course, data))
        pbar.update(1)
        page_number += 1
        flag = current_data[1]

    whole_data = list(filter(lambda x: x, whole_data))
    #added_courses = save_courses(whole_data)
    #print("Saved %s stepic courses" % added_courses)


# In[56]:

def update_courses_states():
    open_courses = get_open_stepic_courses()
    new_states = list(map(parse_new_state_for_stepic_course, tqdm(open_courses, desc="Update stepic states")))
    update_stepic_states({x: y for x, y in zip(open_courses, new_states)})


# In[57]:

def update_all():
    page_number = 1#get_last_stepic_page()
    download_from_page(page_number)


# In[58]:

update_all()


# In[65]:

cur.execute("delete from courses where LENGTH(text) < 250")
cnn.commit()


# In[ ]:



