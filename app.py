from flask import Flask, redirect, request, jsonify
from flask_cors import cross_origin
import stripe
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pickle
import numpy as np
import pandas as pd

stripe.api_key = 'sk_test_51MWG4bSIlus8ySuKQKbDh3nGdHjtqaW5zylFXa1fy8Y3jp2L86JBuzBJJTAprVBedgd0Z5IXzBIgOEVfyQCljDGK00lgq89Mje'
popular_df= pickle.load(open('server\popular.pkl','rb'))
pt= pickle.load(open('server\pt.pkl','rb'))
similarity_scores= pickle.load(open('server\similarity_scores.pkl','rb'))
items= pickle.load(open('server\items.pkl','rb'))
cf= pickle.load(open('server\cf.pkl','rb'))
similarity= pickle.load(open('server\similarity.pkl','rb'))
app = Flask(__name__)
app.config["DEBUG"] = True
endpoint_secret = 'whsec_BK84hvaiziq2x7l7IqaLStkppcGYsV3z'
cred = credentials.Certificate("C://Users//hanso//Projects//FUSION-//server//canteen.json")
fstore = firebase_admin.initialize_app(cred)
db = firestore.client()

# app = Flask(__name__)
YOUR_DOMAIN = 'http://quickteen-v1.vercel.app'
YOUR_DOMAIN = 'http://quickteen-v1.vercel.app'
@app.route('/')
@cross_origin()
def index():
    return "<h1>hello</h1>"
@app.route('/getpopular', methods=['POST'])
@cross_origin()
def get_popular():
    return list(popular_df['Item_name'].values)



def recommend(Items):
    # index fetch
    index = np.where(pt.index==Items)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])),key=lambda x:x[1],reverse=True)[1:6]
    
    data = []
    for i in similar_items:
        item = []
        temp_df = items[items['Items'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Items')['Items'].values))

        
        data.append(item[0])
    
    return data

def recommend1(food):
    l=[]
    index = cf[cf['Item_name'] == food].index[0]
    distances = sorted(list(enumerate(similarity[index])),reverse=True,key = lambda x: x[1])
    for i in distances[1:6]:
        l.append(cf.iloc[i[0]].Item_name)
        
    return l
   
def hybrid(item):
    a=recommend1(item)
    b=list(map(recommend,a))
    return b

@app.route('/recommend', methods=['POST'])
@cross_origin()
def get_recommendations():
    data=request.json['yo']
    print(data)
    return list(np.unique(list(np.unique(hybrid(data)))+list(recommend1(data))))


if __name__ == '__main__':
    app.run(port=4242)
