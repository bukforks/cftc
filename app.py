from flask import Flask, request, render_template
import json
import requests
import os
from datetime import datetime, timedelta
import pandas as pd

from notas import texto

app = Flask(__name__)

@app.route("/")
def menu():
  conteudo = texto()
  return conteudo
