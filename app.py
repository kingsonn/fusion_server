from flask import Flask, redirect, request, jsonify
from flask_cors import cross_origin
import stripe
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)
app.config["DEBUG"] = True

# app = Flask(__name__)
YOUR_DOMAIN = 'http://quickteen-v1.vercel.app'
@app.route('/')
@cross_origin()
def index():
    return "<h1>hello</h1>"


if __name__ == '__main__':
    app.run(port=4242)
