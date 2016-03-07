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
stopwords = map( lambda x: x.strip().decode('utf8'), open('stopword.txt').readlines() )

def topicmodel( comments ):

    _texts = []
    texts = []

    for c in comments:

        c = c['text']
        _texts.append( c )
        texts.append( c )



    tf_vectorizer = CountVectorizer(
                max_df=.20,
                min_df=10,
                stop_words = stopwords )
    texts = tf_vectorizer.fit_transform( texts )

    ## test between 2 and 20 topics
    topics = {}

    for k in range(2, 10):

        print "Testing", k

        model = LatentDirichletAllocation(
                    n_topics= k ,
                    max_iter=5,
                    learning_method='batch',
                    learning_offset=50.,
                    random_state=0
                )
        model.fit( texts )
        ll = model.score( texts )
        topics[ ll ] = model

    topic = max( topics.keys() )

    ret = collections.defaultdict( list )

    ## ugly, rewrite some day
    model = topics[ topic ]

    ## for debug pront chosen models' names
    feature_names = tf_vectorizer.get_feature_names()
    for topic_idx, topic in enumerate(model.components_):
        print "Topic #%d:" % topic_idx
        print " ".join( [feature_names[i].encode('utf8') for i in topic.argsort()[:-5 - 1:-1]])
        print

    for i, topic in enumerate( model.transform( texts ) ):

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
