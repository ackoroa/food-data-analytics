import requests
import xml.etree.ElementTree as ET
import pymongo

SERVICE_TOKEN = ''

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
    count = db.products.count({'packaging_tags.0': {'$exists': True}})
    cur = db.products.find(
        {'packaging_tags.0': {'$exists': True}}, 
        {'_id': 1, 'packaging_tags': 1})

    token = getToken()
    translations = {}
    i = 0
    for data in cur:
        # translate
        packaging_tags_en = []
        for tag in data['packaging_tags']:
            if not tag in translations:
                translations[tag], token = translate(tag, token)
            packaging_tags_en.append(translations[tag])
        
        # insert translation to document by id
        db.products.update_one(
            {'_id':data['_id']}, 
            {'$set': {'packaging_tags_en': packaging_tags_en}}, 
            upsert=False)

        i += 1
        if i % 50 == 0:
            print i, "/", count
    print i, "/", count
    print "Completed"
