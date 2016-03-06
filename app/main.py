from flask import *

import collect_hs

import collections

import nltk

import numpy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

app = Flask(__name__)


## common constructs
stem = nltk.stem.snowball.SnowballStemmer('finnish')

def topicmodel( comments ):

    _texts = []
    texts = []

    for c in comments:

        _texts.append( c['text'] )

        text = nltk.word_tokenize( c['text'] )
        text = map( lambda x: stem.stem( x ) , text )
        texts.append( ' '.join( text ) )

    tf_vectorizer = CountVectorizer(
                max_df=.95,
                min_df=2,
                max_features= 10000 )
    texts = tf_vectorizer.fit_transform( texts )

    ## test between 2 and 50 topics
    topics = {}

    for k in range(2, 51):
        model = LatentDirichletAllocation(
                    n_topics= k ,
                    max_iter=5,
                    learning_method='online',
                    learning_offset=50.,
                    random_state=0
                )
        fit = model.fit( texts )
        ll = model.score( texts )
        topics[ ll ] = fit

    topic = max( topics.keys() )

    ret = collections.defaultdict( list )

    ## ugly, rewrite some day
    new_topics = topics[ topic ].transform( texts )
    for i, topic in enumerate( new_topics ):

        topic = numpy.argmax( topic )
        text = _texts[ i ].encode('utf8')

        ret[ topic ].append( text )

    return ret


@app.route("/")
def index():
    return send_from_directory( 'static' , 'index.html' )

@app.route('/all', methods=['POST'] )
def all():

    comments = collect_hs.collect_for_stories()
    ret = topicmodel( comments )

    return jsonify( ret )

@app.route('/topicmodel', methods=['POST'] )
def analyze():

    path1 = request.form['url'].split('/')[-1]
    path = '1296808743968/' + path1

    comments = collect_hs.comment( path )
    ret = topicmodel( comments )

    return jsonify( ret )

if __name__ == "__main__":
    app.run( debug = True)
