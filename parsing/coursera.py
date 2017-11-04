
# coding: utf-8

# In[3]:

from functools import partial
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import sqlite3
import re


# In[112]:

cnn = sqlite3.connect("data")
cur = cnn.cursor()


# In[47]:

already_in_db_ids = len(cur.execute("select * from courses where type == '{0}'".format("coursera")).fetchall())


# In[4]:

mozilla_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


# In[5]:

def download_pack(start):
    url = 'https://ru.coursera.org/courses?_facet_changed_=true&domains=computer-science%2Cdata-science&start={0}'.format(start)
    html = requests.get(url, headers=mozilla_headers).text
    root = BeautifulSoup(html, "html.parser")
    items = root.findAll('div', {'class': 'rc-SearchResults'})[0]
    return [x['href'] for x in items.findAll('a')]


# In[6]:

def download_coursera_links() -> list:
    
    all_links = []
    old_len = len(already_in_db_ids) if len(already_in_db_ids) != 0 else -1
    pbar = tqdm(desc="Download links of coursera courses")
    
    while old_len != len(all_links):
        old_len = len(all_links)
        all_links += download_pack(len(all_links))
        pbar.update(1)
    all_links = download_pack(0)
    return all_links


# In[7]:

def parse_coursera_link(link):
    try:
        try:
            connection = sqlite3.connect("data")
        except:
            print("!!!Couldn't connect!!!")
        cur = connection.cursor()
        url = 'https://www.coursera.org%s' % link

        html = requests.get(url, headers=mozilla_headers)
        root = BeautifulSoup(html.content.decode(), "html.parser")

        title = root.findAll('h1', {'class': 'title'})
        image = root.findAll('meta', {'property': 'og:image'})[0]['content']

        if len(title) == 0:
            title = root.findAll('h2')[0]
        else:
            title = title[0]

        descriptions = root.findAll('p', {'class': 'course-description'})

        if len(descriptions) == 0:
            descriptions = root.findAll('div', {'class': 'description'})
        courses = root.findAll('div', {'class': 'course-cont'})

        if len(courses) == 0:
            courses = root.findAll('div', {'class': 'module-desc'})

        text = " ".join(
            [description.text + course.text for description, course in zip(descriptions, courses)])

        if len(title.text) < 3 or len(text) < 5:
            return None
        try:
            cur.execute("INSERT INTO courses (title, text, type, url)" +
                         "VALUES ('{0}', '{1}', '{2}', '{3}')".format(title.text, text, "coursera", url))
        except:
            pass
        connection.commit()
        connection.close()
        return (title.text, text, "coursera", url)
    except IndexError:
        pass


# In[8]:

def update_all():
    links = []
    for i in range(0, 741, 20):
        dp = download_pack(i)
        links.extend(dp)
    courses = list(map(parse_coursera_link, tqdm(links, desc="Parse coursera links into courses")))
    courses = list(filter(lambda x: x, courses))
    return courses


# In[127]:

update_all()


# In[9]:

cnn = sqlite3.connect("data")
cur = cnn.cursor()


# In[10]:

#cur.execute("DELETE FROM courses")
cnn.commit()


# In[11]:

import numpy as np


# In[98]:

cur.execute("select text from courses").fetchall()


# In[106]:

tags = ["C++", "C", "SQL", "Javascript", "Software Programming", "Java Language", "HTML code programming,", "Object-Oriented Programming", "Web Application Programming","PHP","CSS","Database Programming", "Java Programming"]


# In[107]:

tags = list(map(lambda x: x.split()[0], tags))[:-1]


# In[108]:

tags += "Text Mining, Predictive Analytics, Machine Learning, Pattern Recognition, Classification, Supervised Learning, Advanced Machine Learning, Unsupervised Learning, Neural Networks and Artificial Intelligence, Statistical Learning, Feature Selection, Feature Extraction, Prediction, Applied Artificial Intelligence, KNN, Statistical Pattern Recognition, Fuzzy Clustering, Pattern Matching, Object Recognition, Semi-Supervised Learning, Backpropagation, Soft Computing, Predictive Modeling, Statistical Data Analysis, Genetic Programming, Nonlinear Regression, Automated Pattern Recognition, Large Scale Data Analysis, Reinforcement Learning, High-Dimensional Data Analysis, Machine Intelligence, Computational Intelligence, Data Clustering, Pattern Classification, Information Extraction, Web Mining, Data Science, Knowledge Discovery, Natural Language Processing, Text Classification, Social Network Analysis, Sentiment Analysis, Association Rule Mining, Hierarchical Cluster Analysis, Data preparation, Data Processing and Computer Science, Frequent Pattern Mining, SVD".split(", ")


# In[109]:

tags.extend(['Neural Networks', 'Artificial Intelligence'])


# In[4]:

cnn = sqlite3.connect("data")
cur = cnn.cursor()
cur.execute("create table tags (text nvarchar(200))")
cnn.commit()


# In[6]:

cnn = sqlite3.connect("data")
cur = cnn.cursor()


# In[126]:

for tag in tags:
    cur.execute("insert into tags (text) values ('{0}')".format(tag))
    cnn.commit()


# In[14]:

cur.execute("insert into tags (text) values ('{0}')".format("web DevOps"))
cnn.commit()


# In[ ]:



