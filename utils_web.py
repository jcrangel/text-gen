from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import re

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)


def get_sentences_from_url(url):
    """
    Return a list of sentences from the url linguee
    with specify query
    """
    raw_html = simple_get(url)

    html = BeautifulSoup(raw_html,'html.parser')



    #clean The data 
    #Delete the text that are url
    for td in html.select('div[class="source_url"]'):
        td.extract()
    for td in html.select('div[class="source_url_spacer"]'):
        td.extract()

    #delete [...]
    puntos_raros = re.compile(r'placeholder.*')
    for td in html.find_all('span', {'class': puntos_raros}):
        td.extract()


    list_sentences = []
    for td in html.select('td[class*="sentence left"]'):
        # removes
        list_text = td.text.split()
        text = ' '.join(list_text)
        list_sentences.append(text)

    return list_sentences

# #10,11,12,13,14,15,16,19,25

def delete_items_list_bydindex(list_to_delete,indices):
    """
    Delete items given by aa list of indices

    indices : index to delete from list?to?delete

    """

    for i in sorted(indices, reverse=True):
        del list_to_delete[i]

def printli(the_list):

    for i,sentence in enumerate(the_list):
        print(i,sentence)


def insert_words_list(words,list_sentences):
    """
    Take a list of sentences(strings).
    for each sentence, find if the sentence includes
    all the words. It not insert all the words:
    exameple :
    words = ['god','ra']
    'God was about to show him the holy temple in heaven in vision'
    --->>
    'God ra was about to show him the holy temple in heaven in vision'
    """
    # import pdb; pdb.set_trace()
    for i,sentence in enumerate(list_sentences):
        list_sentences[i] = insert_words(words,replace_nonalphanum(sentence).lower())
           
    return list_sentences


def insert_words(words,sentence):
    """
        words = ['god','ra']
    'God was about to show him the holy temple in heaven in vision'
    --->>
    'God ra was about to show him the holy temple in heaven in vision'
    """
    #find for all words, delete found words from words

    w  = list(words)
    iw = -1
    for i,word in enumerate(words):
        index = sentence.find(word + ' ')
        #if found delete word from w
        if index != -1:
            w.remove(word)
            iw = index
    # print(iw)
    # print(w)
    #all found return the same sentence        
    if len(w) == 0:
        return sentence
    else:
        sentence = sentence[:iw] + ' ' +' '.join(w) + ' ' + sentence[iw:]
        return sentence


def replace_nonalphanum(sentence):
    return re.sub('[^0-9a-zA-z]+', ' ',sentence)
