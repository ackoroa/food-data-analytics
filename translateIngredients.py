# -*- coding: utf-8 -*- 

from time import sleep
import requests

api_key = ''
target_language='en'
end_point='https://translation.googleapis.com/language/translate/v2'



def assemble_url(query, target=target_language):
    return end_point + '?key=' + api_key + '&target=' + target + '&q=' + query.replace(" ", "%20")


def translate_text(text):
    r = requests.get(assemble_url(text))
    if (r.ok):
        try:
            # print text, "==", r.json()['data']['translations'][0]['translatedText'].decode("utf8")
            return r.json()['data']['translations'][0]['translatedText'].decode("utf8")
        except:
            return "ERROR_VAL"

    else:
        return "ERROR_STATUS"


if __name__=='__main__':
    f = open('ingredients_translated.txt', 'w')
    f.close()
    counter = 0
    with open('ingredients_processed.txt', 'r') as f_in:
        with open('ingredients_translated.txt', 'a+') as f_out:
            try:
                for line in f_in:
                    # print line
                    f_out.write(line.strip() + "\t") 
                    f_out.write(translate_text(line.strip()) + "\n")
                    counter += 1
                if counter % 1000 == 0:
                    print "Translated", counter, "ingredients."
            except:
                print "Failed at:", counter

            print "Done."
