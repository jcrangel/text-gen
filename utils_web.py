from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
import pickle
from lxml.html import fromstring
import requests
from itertools import cycle
import traceback



def simple_get(url,proxy=None):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0'}
    proxy_par = {"http":proxy,"https":proxy} if proxy is not None else proxy
    try:
        with closing(get(url, stream=True,\
         headers = headers,proxies=proxy_par)) as resp:
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


def get_sentences_from_url(url,proxy=None):
    """
    Return a list of sentences from the url linguee
    with specify query
    """
    if proxy is not None:
            raw_html = simple_get(url,proxy=proxy)
            #proxy failed 
            if raw_html is None:
                return None
    else: 
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

def save_map(file,mapping):
    with open(file,'wb') as f:
        pickle.dump(mapping,f,0)

def load_map(file):
    #load the data 
    with open(file,'rb') as f:
        mapping = pickle.load(f)

    return mapping

def scrap_for_radicals(words_map, words_file,time=5):
    """
    save the words from words_file into the dictionary
    words_map
    mode = radicals, kanji,or vocab
    """

    data_df = pd.read_csv(words_file)

    column = 'radical-name'
    total = data_df.shape[0]
    for index,row in data_df.iterrows():

        radical = row[column].lower()
        if radical in words_map:
            print('Word already scraped:', radical )
            continue
        print('(',index,"/",total,") Searching sentences for: ", radical)
        
        #'https://www.linguee.pe/espanol-ingles/search?source=auto&query=axe'
        query = 'https://www.linguee.pe/espanol-ingles/search?source=auto&query=' + radical
        
        try:
            words_map[radical] = get_sentences_from_url(query)
        except :
            print('Something happen, we got blocked probably')
            break
            print('waiting '+str(time)+' secs')
            time.sleep(time)

def scrap_for_kanji_radicals(words_map, words_file,list_proxies=None,time_w=5):

    data_df = pd.read_csv(words_file)

    column = 'kanji-meaning'
    total = data_df.shape[0]
    num_proxy = 0
    proxy = list_proxies[num_proxy]
    num_saved_words = 0
    file_words_temp = 'temp_radical_to_sentences.pkl'  
    for index,row in data_df.iterrows():

        for radical in row[column].split(','):

            radical = radical.lower().lstrip()
            if radical in words_map:
                print('Word already scraped:', radical )
                continue

            print('(',index,"/",total,") Searching sentences for: ", radical)
            
            #'https://www.linguee.pe/espanol-ingles/search?source=auto&query=axe'
            query = 'https://www.linguee.pe/espanol-ingles/search?source=auto&query=' + radical
            
            while 1:
                res_sentences = get_sentences_from_url(query,proxy)
                #If got something
                if res_sentences is not None:
                    words_map[radical] = res_sentences
                    num_saved_words += 1
                    #save each the words
#                     if num_saved_words % 5 == 0 :
#                         print('Saving words in ', file_words_temp)
                    save_map(file_words_temp,words_map)
                    break
                # if fail...
                if num_proxy >= len(list_proxies):
                    print('Proxies exhasuted, need new ones')
                    return

                num_proxy += 1
                proxy = list_proxies[num_proxy] 
                print('Something happen, we got blocked probably. Try next proxy')

            print('waiting '+str(time_w)+' secs')
            time.sleep(time_w)



    
def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies


def get_proxies2():
    url = 'https://free-proxy-list.net/'

    raw_html = simple_get(url)

    html = BeautifulSoup(raw_html,'html.parser')
    table_body = html.find('tbody')
    rows = html.find_all('tr')
    # import pdb; pdb.set_trace()
    proxies = []
    for row in rows:
        # removes
        # print(td.text)
        td_list = row.find_all('td')
        # print(row)
        try:
            proxies.append(td_list[0].text+':'+td_list[1].text)
        except:
            continue

    return proxies


def get_proxies4():

    proxies = []
    with open('data/proxy_list2.txt') as fp:
        line = fp.readline()
        c = 1
        line = line.split('\n')[0]
        proxies.append(line)
        while line:
            line = fp.readline()
            line = line.split('\n')[0]
            c += 1
            proxies.append(line)



    return proxies