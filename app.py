import requests, os, json
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, json, request

app = Flask(__name__)

# get data lists
with open('assets/common_words.json', 'r') as myfile:
    data=myfile.read()
common_word_list = json.loads(data)
with open('assets/common_tags.json', 'r') as myfile:
    data=myfile.read()
common_tag_list = json.loads(data)
with open('assets/common_genres.json', 'r') as myfile:
    data=myfile.read()
common_genre_list = json.loads(data)
with open('assets/developer_dict.json', 'r') as myfile:
    data=myfile.read()
developer_dict = json.loads(data)
with open('assets/publisher_dict.json', 'r') as myfile:
    data=myfile.read()
publisher_dict = json.loads(data)

# get top 20 appear-the-most dev & pub
cutdevlist = list(developer_dict.keys())
cutdevlist = [a for a in cutdevlist if developer_dict[a] > 50]
cutpublist = list(publisher_dict.keys())
cutpublist = [a for a in cutpublist if publisher_dict[a] > 50]
developerList = json.dumps( cutdevlist )
publisherList = json.dumps( cutpublist )

# helper funcs
def check_chars(value):
    if value == " ":
        return True
    else:
        return value.isalpha()

def remove_special_chars(value):
    return ''.join(filter(check_chars, str(value)))

def replace_with_list_count(value, cList, delim=','):
    words = str(value).split(delim)
    gcount = 0
    for word in words:
        if word in cList:
            gcount += 1
    return gcount

def get_appearance_value(key, value):
    if key == 'dev' and value in developer_dict:
        return developer_dict[value]
    elif key == 'pub' and value in publisher_dict:
        return publisher_dict[value]
    return 0

# routing
@app.route('/', methods=['POST'])
def index_post():
    error = ""
    # Read raw values from the form
    try:
        multR = request.form['mult']
    except Exception as e:
        multR = "off"
    try:
        gamenameR = request.form['gamename']
        genresR = request.form['genres']
        tagsR = request.form['tags']
        platcount = request.form['platcount']
        if request.form['devInputType'] == 1:
            developerR = request.form['developer1']
        else:
            developerR = request.form['developer2']
        if request.form['pubInputType'] == 1:
            publisherR = request.form['publisher1']
        else:
            publisherR = request.form['publisher2']

        # Load the values from .env
        endpoint = os.environ['ENDPOINT']

        # convert to numerical features
        gamename = replace_with_list_count(remove_special_chars(gamenameR), common_word_list, " ")
        genres = replace_with_list_count(genresR, common_genre_list)
        tags = replace_with_list_count(tagsR, common_tag_list)
        if multR == 'on':
            mult = 1
        else:
            mult = 0
        developer = get_appearance_value('dev', developerR)
        publisher = get_appearance_value('pub', publisherR)

        # send request to model endpoint
        headers = {"Content-Type": "application/json"}
        alldata = {
            'data': [
                gamename, publisher, developer, tags, mult, genres, platcount
            ]
        }
        data = json.dumps(alldata)
        response = requests.post(endpoint, data=data, headers=headers)

    except Exception as e:
        error = str(e)

    if error != "":
        showAlert = json.dumps( True )
        errMsg = json.dumps( error )
        return render_template('index.html', developerList=developerList, publisherList=publisherList, showAlert=showAlert, errMsg=errMsg)

    # show alert if request failed
    if response.status_code != 200:
        showAlert = json.dumps( True )
        errMsg = json.dumps( response.status_code )
        return render_template('index.html', developerList=developerList, publisherList=publisherList, showAlert=showAlert, errMsg=errMsg)

    # process result if request passes
    try:
        number = int(float(response.json()['data'][0]))
        gameData = [gamenameR, publisherR, developerR, tagsR, mult, genresR, platcount]
    except Exception as e:
        showAlert = json.dumps( True )
        errMsg = json.dumps( response.json()['data'][0] )
        return render_template('index.html', developerList=developerList, publisherList=publisherList, showAlert=showAlert, errMsg=errMsg)

    # show result page
    return render_template(
        'results.html',
        number=number,
        gameData=gameData
    )

@app.route('/', methods=['GET'])
def index():
    showAlert = json.dumps( False )
    errMsg = json.dumps( "" )
    return render_template('index.html', developerList=developerList, publisherList=publisherList, showAlert=showAlert, errMsg=errMsg)