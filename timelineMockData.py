#
# mock data generation for Timeline project
# Honghan
# @KCL 2016
#

import httplib
import urllib
import random
import math
import time
import json
import datetime

# elastic server (using redhat cloud server or local ones)
es_server = "timeline-silverash.rhcloud.com:80"

# number of patients to be generated
num_patients = 100

# number of minimal docs for one patient
num_min_docs = 5

# maximum number of extra docs
num_more_docs = 3

# sentences for randomly generating text
sentences = ["Alzheimer's disease is a progressive condition, which means the symptoms develop gradually and become more severe over the course of several years.",
"It affects multiple brain functions.",
"The first sign of Alzheimer's disease is usually minor memory problems.",
"For example, this could be forgetting about recent conversations or events, and forgetting the names of places and objects.",
"People with dementia can become apathetic or uninterested in their usual activities, and have problems controlling their emotions.",
"They may also find social situations challenging, lose interest in socialising, and aspects of their personality may change.",
"A person with dementia may lose empathy (understanding and compassion), they may see or hear things that other people do not (hallucinations), or they may make false claims or statements.",
"As dementia affects a person's mental abilities, they may find planning and organising difficult.",
"Maintaining their independence may also become a problem.",
"A person with dementia will therefore usually need help from friends or relatives, including help with decision making.",
"Your GP will discuss the possible causes of memory loss with you, including dementia.",
"If you are worried about your memory or think you may have dementia, it's a good idea to see your GP.",
"If you're worried about someone else, who you think has dementia, encourage them to make an appointment and perhaps suggest that you go along with them.",
"If you are forgetful, it doesn't mean you have dementia.",
"Memory problems can also be caused by depression, stress, drug side effects, or other health problems.",
"It can be just as important to rule out these other problems or find ways to treat them.",
"Your GP will be able to run through some simple checks and either reassure you, give you a diagnosis, or refer you to a specialist for further tests.",
"An early diagnosis gives you both the best chance to prepare and plan for the future, and receive any treatment.",
"With treatment and support from healthcare professionals, family and friends, many people are able to lead active, fulfilling lives.",
"Dementia can be difficult to diagnose, especially if your symptoms are mild.",
"If your GP is unsure about your diagnosis, they will refer you to a specialist such as a neurologist (an expert in treating conditions that affect the brain and nervous system), an elderly care physician, or a psychiatrist with experience of treating dementia.",
"The specialist may be based in a memory clinic alongside other professionals who are experts in diagnosing, caring for and advising people with dementia and their families.",
"It's important to make good use of your consultation with the specialist.",
"Write down questions you want to ask, make a note of any medical terms the doctor might use, and ask if you can come back if you think of any more questions.",
"Taking the opportunity to go back can be very helpful.",
"The specialist may want to organise further tests, which may include brain scans such as a computerised tomography (CT) scan, or preferably a magnetic resonance imaging (MRI) scan.",
"If they are still not certain about the diagnosis, you may need to have further, more complex, tests."]

# random a string or a number for given length
def rndstring(len, digitonly=None):
    s = ''
    for i in range(1, len + 1):
        if (None != digitonly):
            s += str((int)(random.random()*10))
        else:
            s += unichr( (int)(random.random() * 26 ) + 65)
    return s


# generate a random date
def rnddate(min=1930):
    y = (int)(random.random() * 80) + min
    m = (int)(random.random() * 12) + 1
    d = (int)(random.random() * 28) + 1
    return datetime.datetime(y, m, d)


# randomly generate a text by randomly choosing sentences from
# an arry
def rndtext():
    global sentences
    num = (int)(random.random() * 6) + 8
    t = ""
    for i in range(1, num):
        t += sentences[(int)(random.random() * len(sentences) )] + " "
    return t


# generate one patient data
def genpatientdata():
    patient = {}
    patient["brcid"] = rndstring(10, True)
    patient["firstname"] = rndstring(5)
    patient["lastname"] = rndstring(6)
    patient["dob"] = rnddate().strftime("%Y-%m-%d")
    if random.random() > 0.5 :
        patient["gender"] = "male"
    else:
        patient["gender"] = "female"
    return patient


# generate documents for a given patient id
def gendoc(brcid):
    doc = {"brcid": brcid}
    if random.random() > 0.3:
        doc["type"] = "text"
    else:
        doc["type"] = "binary"
        doc["thumbnail"] = "/thumb/" + rndstring(6) + ".png"
    doc["text"] = rndtext()
    doc["created"] = (rnddate(2006) - datetime.datetime(1970, 1, 1)).total_seconds() * 1000
    return doc

# post data (dictionary) to the elastic server
def postdata(dic):
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection(es_server)
    for indexstr in dic:
        params = json.dumps(dic[indexstr]) #urllib.urlencode(dic[indexstr])
        print(params)
        conn.request("POST", indexstr, params, headers)
        response = conn.getresponse()
        data = response.read()
        print (data)
    conn.close()


# delete indice from the elastic server
# arr - the string array containing all indice to be delete
def cleanIndex(arr, conn=None):
    if conn is None:
        conn = httplib.HTTPConnection(es_server)
    for idexstr in arr:
        conn.request('DELETE', idexstr, '')
        resp = conn.getresponse()
        print( resp.read() )


cleanIndex(['/mock'])
print('index cleaned, generating data...')

data = {}
numdocs = 1
for i in range(1, num_patients + 1):
    p = genpatientdata()
    data["/mock/patient/" + str(i)] = p
    numdoc = (int)(random.random() * num_more_docs) + num_min_docs
    for j in range(1, numdoc + 1):
        data["/mock/doc/" + str(numdocs)] = gendoc(p["brcid"])
        numdocs += 1
print('data generated, saving to Elastic Index...')

postdata(data)
print('all done')
