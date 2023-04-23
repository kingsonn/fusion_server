from flask import Flask, redirect, request, jsonify
from flask_cors import cross_origin
import stripe
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pickle
import numpy as np

stripe.api_key = 'sk_test_51MWG4bSIlus8ySuKQKbDh3nGdHjtqaW5zylFXa1fy8Y3jp2L86JBuzBJJTAprVBedgd0Z5IXzBIgOEVfyQCljDGK00lgq89Mje'

app = Flask(__name__)
app.config["DEBUG"] = True
endpoint_secret = 'whsec_BK84hvaiziq2x7l7IqaLStkppcGYsV3z'
cred = credentials.Certificate("canteen.json")
fstore = firebase_admin.initialize_app(cred)
db = firestore.client()
popular_df= pickle.load(open('server\popular.pkl','rb'))

# app = Flask(__name__)
YOUR_DOMAIN = 'http://quickteen-v1.vercel.app'
@app.route('/')
@cross_origin()
def index():
    return "<h1>Hello</h1>"
@app.route('/create-checkout-session', methods=['POST'])
@cross_origin()
def create_checkout_session():
    items=request.json['items']
    user= request.json['email']
    time= request.json['time']
    d = {
    u'email': user,
    u'items': items,
    u'time': time,
    u'timestamp': firestore.SERVER_TIMESTAMP,

}
    update_time, temp_ref = db.collection(u'temp').add(d)
    print(f'Added document with id {temp_ref.id}')
    transformed_items = [{    
    'price_data': {
        'currency': 'inr',
        'product_data': {
            'name': item["Item_name"],
            },
        'unit_amount': int(item["Price"]) * 100,
    },
    'quantity': item["qty"],
    } for item in items]
    try:
        checkout_session = stripe.checkout.Session.create(
        line_items=transformed_items,
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/',
        metadata={
        "id": temp_ref.id,
    }
        )
    except Exception as e:
        return str(e)

    return (checkout_session)

@app.route('/webhook', methods=['POST'])
def webhook():

    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        raise e
    except stripe.error.SignatureVerificationError as e:
        raise e

    # Handle the event
    if event['type'] == 'checkout.session.completed':
      session = event['data']['object']
    #   print(session)
      doc_ref = db.collection(u'temp').document(session.metadata.id)
      doc = doc_ref.get()
      order_status={
        u'status': u'Order Placed',
        u'timestamp': firestore.SERVER_TIMESTAMP,
      }
      data={
        u'email': doc.to_dict()['email'],
        u'items': doc.to_dict()['items'],
        u'time': doc.to_dict()['time'],
        u'order_status': order_status,
        u'order_ID': session.id,
        u'total': session.amount_subtotal,
      }
      db.collection(u'orders').add(data)

    else:
      print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)


@app.route('/getpopular', methods=['POST'])
@cross_origin()
def get_popular():
    return list(popular_df['Item_name'].values)

if __name__ == '__main__':
    app.run(port=4242)
