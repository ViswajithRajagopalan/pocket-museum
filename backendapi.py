import io, os
from google.cloud import vision
from google.cloud.vision import ImageAnnotatorClient
from firebase_admin import db
from firebase_admin import credentials
from firebase_admin import storage
import firebase_admin
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import re
import wikipedia
import wikipediaapi
from urllib.request import urlopen
import flask
from flask import Flask, jsonify
# import the libraries below
#from firebase_admin import db
from firebase_admin import credentials
import firebase_admin
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import re
import wikipedia
import wikipediaapi
from urllib.request import urlopen
from firebase_admin import storage
from aiohttp import web
import json
import falcon

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r"C:\Users\viswa\Documents\Google Cloud\cloudkey.json"
client = vision.ImageAnnotatorClient()


# define the image_url here so it can be accessed outside of the function
image_url = ''
# This function will print out the url of the latest image(which is the last object) stored in firebase cloud storage
def get_url():
    # import storage
    from google.cloud import storage

    # Explicitly use service account credentials by specifying the private key
    # file.
    storage_client = storage.Client.from_service_account_json(
        'auth.json')

    # get all the buckets in the account
    buckets = list(storage_client.list_buckets())

    # get the first bucket, which is the first element of the list
    firstBucket = buckets[0]
     # https://console.cloud.google.com/storage/browser/[bucket-id]/
    bucket = storage_client.get_bucket(firstBucket)
    # Then do other things...
    #blob = bucket.get_blob('napolean.JPG')
    #print(blob.public_url)

# Set blobs to all the objects in the bucket and loop through all the objects in the bucket, and store the file name of the last object(most recent)
# to the lastFileName variable
    blobs = storage_client.list_blobs(bucket)

    for blob in blobs:
        # set the file name to the last file since it is the one that is the most recent
        lastFileName = blob.name

    # get that last file object and set image_url variable to the url of that object and print the url
    blob = bucket.get_blob(lastFileName)
    image_url = str(blob.public_url)
    return image_url


# call the function to execute the code and get the image url

image_uri = get_url()

# pylint: disable=no-member
image = vision.types.Image()
image.source.image_uri = image_uri
response = client.web_detection(image=image)


web_detection = response.web_detection
web_detection.best_guess_labels
web_detection.full_matching_images
web_detection.visually_similar_images
web_detection.pages_with_matching_images
web_detection.partial_matching_images

maximum = 0
# recommend tags for the image based on data collected from the web
for entity in web_detection.web_entities:
    if entity.score > maximum:
        title = entity.description
        maximum = entity.score

wiki = wikipediaapi.Wikipedia('en')


wiki_page = wiki.page(title.lower())

#####################################################################################################
# The Last Supper is an exception because it has the artist name, Leonardo, in the url:

# Another example is of the painting Magpie by Monet
# https://en.wikipedia.org/wiki/The_Magpie_(Monet)
#####################################################################################################

# get the page's url
my_url = wiki_page.fullurl
#my_url =  'https://en.wikipedia.org/wiki/The_Last_Supper_(Leonardo)'

# tested if we can get the image of the paintings with additional parameters needed in the url such as an artist name
# my_url = 'https://en.wikipedia.org/wiki/Woman_with_a_Parasol_-_Madame_Monet_and_Her_Son'

# yes this can be done!

# opening connection and getting the page
uClient = uReq(my_url)

# put the content in page_html variable
page_html = uClient.read()

# close the client
uClient.close()

# call the soup function to parse the HTML
page_soup = soup(page_html, "html.parser")

# get the container that has the picture and other information including artist and the year
# the container is the manual of style of the wikipedia page
container = page_soup.find("table", {"class": "infobox vevent"})

# if the wikipedia page's url does not take us to the right page then output this message to the user
if container is None:
    print("Not enough information is known")

# set artist, year, and medium to empty string for now
artist = ''
year = ''
medium = ''


# find all the th html tags in only the container specified above
ths = container.find_all('th')


# loop through all the th tags
for th in ths:

    # if the text of th tag is 'Artist' then use the find_next_sibling function to get the td tag
    # and assign its text which contains the artist's name to the variable, artist_name
    if th.text == 'Artist':
        artist_name = th.find_next_sibling("td").text

    # if the text of th tag is 'Year' then use the find_next_sibling function to get the td tag
    # and assign its text which contains the date to the variable, date
    elif th.text == 'Year':
        date = th.find_next_sibling("td").text

    # if the text of th tag is 'Medium' then use the find_next_sibling function to get the td tag
    # and assign its text which contains the medium to the variable, medium
    elif th.text == 'Medium' or th.text == "Type":
        medium = th.find_next_sibling("td").text

# convert date to string and use the re.sub function to remove the strings and spaces(we only want numbers)

# convert the date to a string and
# use the replace function instead of re.sub function to get rid of the characters "c." only and preserve the character "c"

date = str(date)
date = date.replace("c. ", "")

# get the url of the first image and exit to the printing steps
html = urlopen(my_url)
bs = soup(html, 'html.parser')
images = bs.find_all('img', {'src': re.compile('.jpg')})
for image in images:
    image = image['src']
    break

# label and print the title,imageUrl, artist, time period, and medium in that order
artist = "Artist:" + " " + artist_name
time_period = "Time Period:" + " " + date
art_medium = "Medium:" + " " + medium

# make sure the image does not have double quotes
image = image.replace("\"", "")



print(title)
print(image)
print(artist)
print(time_period)
print(art_medium)

# print the summary from wikipedia page and put a default sentence length of 3

summary = "Summary: " + str(wikipedia.summary(title, sentences=3))

# remove the content inside the parenthesis from the summary
summary = re.sub(r'\([^()]*\)', '', summary)
print(summary)

# Tested the code for the following paintings and correct output received
# Mona Lisa, Starry Night, The Scream, The Girl with pearl Earring, The Last Supper

# Note: getting this error while trying out different titles:    ths = container.find_all('th')
# AttributeError: 'NoneType' object has no attribute 'find_all'
# But works with Mona Lisa and The Scream


###################################################################################################################################
# Install firebase admin

# install libraries needed

'''

mycredentials = credentials.Certificate('service-account.json')

# initialize firebase app
firebase_admin.initialize_app(mycredentials, {
    # provide the url of the real time database
    'databaseURL': 'https://pmuploadtofirebase.firebaseio.com/',

})



# add the data to database

# get the database reference
ref = db.reference('/')

# set the reference to contain an array of paintings
ref.set({

    # The array of paintings will store information about
    # all the paintings, It is an array of paintings
    'Paintings':
    {
        # This is the first painting in the array
        # When connected to google-cloud vision API, we can create an array of paintings (or a class) and retrieve information about each painting
        # instead of just getting 1 painting like this here, we can access the painting with an array such as titles[0] if titles was the array we created
        title: {
            'artist': artist_name,
            'wikiImageUrl': image,
            ################################################################################################################
            # The image url is stored as a string in the real time database so we will need to remove the quotes
            # for the url to work

            # Example: "//upload.wikimedia.org/wikipedia/commons/thumb/f/fd/David_-_Napoleon_crossing_the_Alps_-_Malmaison2.jpg/300px-David_-_Napoleon_crossing_the_Alps_-_Malmaison2.jpg"

            # We need to remove the quotes
            ################################################################################################################
            'date': date,
            'medium': medium

        }

    }
})
'''

'''
companies = [{"id": artist_name, "name": image}, {"id": 2, "name": "Company Two"}]

api = Flask(__name__)

@api.route('/companies', methods=['GET'])
def get_companies():
  return json.dumps(companies)

if __name__ == '__main__':
    api.run()
    '''



'''
class CompaniesResource(object):
  companies = [{"id": 1, "name": artist_name}, {"id": 2, "name": "Company Two"}]
  def on_get(self, req, resp):
    resp.body = json.dumps(self.companies)

api = falcon.API()
companies_endpoint = CompaniesResource()
api.add_route('/companies', companies_endpoint)
'''

app = Flask(__name__)

# now the app automatically routes to the url, you don't have to append '/test'

# also output the title and summary along with other information
@app.route('/')
def sendOutput():
  return jsonify([ {'summary': summary, 'artist': artist_name, 'date': date, 'medium': medium, 'title': title }])
# the title is not returned first because the output is automatically returned in alphabetical order

# the port can be changed to any port does not have to be 9090
if __name__ == '__main__':
  app.run(debug = True, port=9090)
