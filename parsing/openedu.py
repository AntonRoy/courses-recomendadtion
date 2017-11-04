
# coding: utf-8

# In[76]:

from functools import partial
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import sqlite3
import re


# In[77]:

mozilla_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


# In[78]:

def text_sum(text: list) -> str:
    tmp_text = ""
    for i in text:
        tmp_text += i
        tmp_text += " "
    return tmp_text


# In[79]:

def parse_openedu(data: list):
    answer = {}
    answer['title'] = data[0]

    # Get half of url
    url = data[1]
    answer['specific_id'] = url

    # Made normal url
    url = 'https://openedu.ru%s' % url
    # Save it
    answer['url'] = url

    # Parse course by url
    html = requests.get(url, headers=mozilla_headers)

    # BS it
    root = BeautifulSoup(html.content.decode(), "html.parser")

    # Get div with text
    needed_div = root.findAll('div', {'class': 'col-sm-8 issue'})

    if len(needed_div) > 0:
        needed_div = needed_div[0]

        # Append text to data
        answer['text'] = text_sum([i.text for i in needed_div.findAll('p')])

        # Find photo
        photo = root.findAll('meta', {'property': 'og:image'})

        if len(photo) > 0:
            photo = photo[0]['content']
            answer['image_link'] = photo
        else:
            answer['image_link'] = None

        answer['type'] = 'openedu'
        answer['is_active'] = True
        cnn = sqlite3.connect("data")
        cur = cnn.cursor()
        cur.execute("insert into courses (title, text, type, url) values ('{0}', '{1}', '{2}', '{3}')"
                    .format(answer['title'], answer['text'], 'openedu', url))
        cnn.commit()
        return (answer['title'], answer['text'], 'openedu', url)
    else:
        return None


# In[80]:

def update_all():
    courses = open('courses.json').read()
    courses = eval(courses[:-1].replace('false', 'False').replace('true', 'True'))
    titles = []
    urls = []

    for i in courses:
        titles.append(courses[i]['title'])
        urls.append(courses[i]['url'])
    data = []

    for title, url in zip(titles, urls):
        data.append([title, url])
    data = list(map(parse_openedu, tqdm(data, desc="Openedu parse")))
    data = list(filter(lambda x: x, data))


# In[83]:

update_all()


# In[94]:

cur.execute("delete from courses where type == '{0}'".format("htmlacademy"))
cnn.commit()


# In[95]:

cur.execute("select * from courses where type == '{0}'".format("htmlacademy")).fetchall()


# In[ ]:



