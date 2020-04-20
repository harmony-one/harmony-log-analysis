#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
import requests
import pandas as pd
from pytz import timezone
import pytz
from datetime import datetime


# In[2]:


html_url = "https://jenkins.harmony.one/job/harmony-release/api/json"
res = requests.get(html_url)
job_lst = json.loads(res.content)


# In[3]:


network = []
branch = []
binary = []
date = []
commit_hash = []
github_link = []
name = []
id_num = []
url_lst = []
for j in job_lst['builds']:
    # get the url
    url = j['url'] + "api/json"
    url_lst.append(j['url'])
    res = requests.get(url)
    content = json.loads(res.content)
    
    # data processing
    for p in content['actions'][0]['parameters']:
        if p['name'] == 'NETWORK':
            network.append(p['value'])
        elif p['name'] == 'BRANCH':
            branch.append(p['value'])
        elif p['name'] == 'STATIC_BINARY':
            binary.append(p['value'])
    pst = datetime.fromtimestamp(content['timestamp']/1000.0).astimezone(timezone('US/Pacific'))
    date.append(pst.strftime("%Y/%m/%d %H:%M:%S"))

    for i in content['actions']:
        if '_class' in i and i['_class'] == 'hudson.plugins.git.util.BuildData' and i['remoteUrls'][0] == 'https://github.com/harmony-one/harmony':
            commit = i['lastBuiltRevision']['SHA1']
            commit_hash.append(commit)
            github_link.append("https://github.com/harmony-one/harmony/commit/" + commit )
        if '_class' in i and i['_class'] == 'hudson.model.CauseAction':
            name.append(i['causes'][0]['userName'])
    id_num.append(content['id'])


# In[4]:


df = pd.DataFrame(list(zip(id_num, date, network, branch, binary, name, commit_hash, url_lst, github_link)), columns = ['job-id','date','network','branch','binary','username', 'commit_hash', "jenkins-link",'github-link'])
df            
             


# In[5]:


df.to_csv('./csv/jenkins.csv')

