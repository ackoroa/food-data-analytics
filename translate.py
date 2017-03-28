import requests
import xml.etree.ElementTree as ET
import pymongo

SERVICE_TOKEN = '6ae5a2dea8c44720908de69d04a5ba23'

def getToken():
    issueTokenUrl = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken'
    issueTokenHeader = {'Ocp-Apim-Subscription-Key': SERVICE_TOKEN}
    issueToken = requests.post(issueTokenUrl, headers=issueTokenHeader)
    return issueToken.text

def translate(word, token):
    translateUrl = 'https://api.microsofttranslator.com/v2/http.svc/Translate?appid=Bearer%20'
    translateQuery = '&text=' + word + '&to=en'
    
    translate = requests.get(translateUrl + token + translateQuery)
    if not translate.ok:
        # token expires every 10 minutes
        token = getToken()
        translate = requests.get(translateUrl + token + translateQuery)

    translatedWord = ''
    try:
        translatedWord = ET.fromstring(translate.text).text
    except UnicodeEncodeError:
        print "Cannot parse, skipping..."
    return translatedWord, token

if __name__ == "__main__":
    db = pymongo.MongoClient().off

    # query input documents
    count = db.products.count({'product_name': {'$exists': True}})
    cur = db.products.find(
        {'product_name': {'$exists': True}}, 
        {'_id': 1, 'product_name': 1})

    token = getToken()
    translations = {}
    i = 0
    for data in cur:
        # translate
        name = data['product_name']
        if not name in translations:
            translations[name], token = translate(name, token)
        name_en = translations[name]
        
        # insert translation to document by id
        db.products.update_one(
            {'_id':data['_id']}, 
            {'$set': {'product_name_en': name_en}}, 
            upsert=False)

        i += 1
        if i % 50 == 0:
            print i, "/", count
    print i, "/", count
    print "Completed"
