# Import general libraries
import os
import re
import json
import heapq
import onnxruntime

# Import NLP libraries
import spacy
import nltk
import pytextrank

# Import TF libraries
import tensorflow as tf

# Import webdriver
from selenium import webdriver
from pyvirtualdisplay import Display

# Import flask
from flask import Flask
from flask_cors import CORS
from flask import request, jsonify, send_from_directory

# Import core functions
from .summarizer import get_summary, get_title, get_bullets
from .media import parse_tree, get_image_subject, needs_image, needs_plot, needs_table, get_plot_name



class App(Flask):
    def __init__(self, name):
        super(App, self).__init__(name)

        # Load models
        print("[INFO] Loading spacy model")
        self.nlp = spacy.load('en_core_web_md')

        # Adding pipe
        print("[INFO] Adding pipe")
        tr = pytextrank.TextRank()
        self.nlp.add_pipe(tr.PipelineComponent, name="textrank", last=True)

        # Load classifier
        self.classifier = onnxruntime.InferenceSession("./models/classifier.onnx")


        


app = App(__name__)
CORS(app)


@app.route("/getTitle", methods=["POST"])
def title_gen():

    data = request.get_json()
    text = data['text']
    doc = app.nlp(text)
    title = get_title(doc)

    return jsonify({'title':title})

@app.route("/parsetext", methods=["POST"])
def driver():
    
    data = request.get_json()
    text = data['text']

    doc = app.nlp(text)

    # Check if image needed
    vec = doc.vector.reshape(1,-1)
    ort_inputs = {app.classifier.get_inputs()[0].name: vec}
    result = app.classifier.run(None, ort_inputs)


    data = {}

    if needs_image(result, doc) is True:
        subject = get_image_subject(doc)
        
        data['type'] = 'image'
        data['image'] = {'subject':subject}
    
    elif needs_plot(doc):
        plot_name = get_plot_name(doc)

        data['type'] = 'plot'
        data['plot'] = {'type':plot_name}

    elif needs_table(doc):
       
        data['type'] = 'table'
        data['table'] = {}

    else:
        bulleted_points = get_bullets(doc)
        if len(bulleted_points) == 0:
            bulleted_points = [sent.text for sent in doc.sents] 
        
        data['type'] = 'bullet'
        data['bullet'] = {'bullets': '|'.join(bulleted_points)}
      

    return jsonify(data)


@app.route("/get-image/<image_name>")
def get_image(image_name):
        return send_from_directory("C:/Users/Muskan Rastogi/Documnets", filename=image_name, as_attachment=True)