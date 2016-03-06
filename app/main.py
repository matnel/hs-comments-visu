from flask import *

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory( 'static' , 'index.html' )

@app.route('/api/topicmodel', methods=['POST'] )
def analyze():
    return None

if __name__ == "__main__":
    app.run()
