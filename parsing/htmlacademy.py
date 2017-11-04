
# coding: utf-8

# In[1]:

from functools import partial
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import sqlite3
import re


# In[16]:

courses = set()


# In[2]:

mozilla_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


# In[27]:

def parse_course(course_index):
    url = "https://htmlacademy.ru/courses/{0}".format(course_index)
    html = requests.get(url, headers=mozilla_headers)
    soup = BeautifulSoup(html.content.decode(), "html.parser")
    title = soup.findAll('h1')[0].text
    text = title + ". "
    needed_span = soup.findAll('span', {'class': 'course-task__title'})
    for i in range(len(needed_span)):
        text += needed_span[i].text + ". "
    cnn = sqlite3.connect("data")
    cur = cnn.cursor()
    if title == 'Страница не\xa0найдена':
        return 0
    cur.execute("insert into courses (title, text, type, url) values ('{0}', '{1}', '{2}', '{3}')"
                .format(title, text, "htmlacademy", url))
    cnn.commit()
    return (title, text, "htmlacademy", url)


# In[32]:

def update_all():
    for i in tqdm(range(1500)):
        parse_course(i)


# In[34]:

update_all()


# In[ ]:



