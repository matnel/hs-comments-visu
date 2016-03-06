import requests
import bs4
import json
import re

def _comment( story , index = 0):

    path = "http://www.hs.fi/ajax/keskustelut/" + story + "?startIndex=" + str(index) + "&order=a"

    r = requests.get( path )
    text = r.text.strip()

    ## no more comments left
    if text == '':
        return False

    html = bs4.BeautifulSoup( text )

    ret = []

    comments = html.find_all('div', class_='comment-text')
    comments_meta = html.find_all('div', class_= 'meta')

    for i, c in enumerate( comments ):
        comment = {}

        comment['story'] = story

        meta = comments_meta[ i ]

        ## comment id
        comment['id'] = meta['id'].replace('comment-meta', '')

        ## author name
        comment['author'] = meta.find('a' , class_='author' ).text

        ## samaa mielta score
        scores = c.find_all('div', class_='comment-btn-container')[0]
        scores = scores.find_all('span', class_='rating-value')
        comment['agreement_yes'] = int( scores[0].text[1:-1] )
        comment['agreement_no'] = int( scores[1].text[1:-1] )

        ## hyvin argumentoitu score
        scores = c.find_all('div', class_='comment-btn-container')[1]
        scores = scores.find_all('span', class_='rating-value')
        comment['argument_yes'] = int( scores[0].text[1:-1] )
        comment['argument_no'] = int( scores[1].text[1:-1] )

        ## comment text
        c.find( class_ = 'comment-text-links').decompose() ## remove non-comment stuff
        comments = c.find_all('p')
        comment['text'] = '\n'.join( map( lambda x: x.text , comments ) )

        ret.append( comment )

    return ret

def comment( story ):

    comments = []

    current = _comment( story )

    while current:

        comments += current

        current = _comment( story , len( comments ) + 1 )

    return comments

## http://www.hs.fi/ajax/keskustelut/1296808743968/a1305922917503?startIndex=3&order=a
## http://www.hs.fi/ajax/keskustelut/1296808474403/a1305922917503?startIndex=0&order=a

def collect_for_stories():

    collected = []

    data = []

    r = requests.get( 'http://www.hs.fi/uutiset/?ref=hs-navi-osastot' )
    html = bs4.BeautifulSoup( r.text )

    for link in html.find_all( 'a' , class_='article-link'):

        path1 = '1296808743968' ## link['data-department-id']
        path2 = link['data-article-id']

        if path2 not in collected:

            data += comment( path1 + '/a' + path2 )

            collected.append( path2 )

    print data

    return data



if __name__ == '__main__':

    collect_for_stories()
