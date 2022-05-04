import pandas as pd
import yfinance as yf
import talib
from flask import Flask, render_template, request  #for render HTML code
from pattern import patterns
from datetime import date
import os, csv

app = Flask(__name__)
#export FLASK_ENV=development: turn on dev/ debug mode, switch to production when deploy

STOCK_NAME_PATH = 'datasets/companies.csv'
STOCK_PRICE_FD_PATH = 'datasets/daily/'

@app.route('/')
def index():
  current_pattern = request.args.get('pattern', None)
  stock = {}
  with open(STOCK_NAME_PATH) as f:
    for row in csv.reader(f):
      stock[row[0]] = {'company name':row[1]}
  if current_pattern:
    datafiles = os.listdir(STOCK_PRICE_FD_PATH)
    for datafile in datafiles:
      df = pd.read_csv('datasets/daily/{}'.format(datafile))
      pattern_func = getattr(talib, current_pattern) #very useful
      symbol = datafile.split('.')[0]
      try:
        result = pattern_func(df['Open'], df['High'], df['Low'], df['Close'])
        last = result.tail(1).values[0]
        if last > 0:
          stock[symbol][current_pattern] = "bullish"
        elif last < 0:
          stock[symbol][current_pattern] = "bearish"
        else:
          stock[symbol][current_pattern] = None
      except:
        pass
  return render_template("index.html", patterns= patterns, stock = stock, current_pattern = current_pattern) #set patterns = patterns import from pattern.py

@app.route('/update')
def update():
  with open (STOCK_NAME_PATH) as f:
    stocks = f.read().splitlines()
    for stock in stocks :
      symbol = stock.split(',')[0]
      df = yf.download(symbol, start = "2022-01-01", end = date.today().strftime("%Y-%m-%d") )
      df.to_csv('datasets/daily/{}.csv'.format(symbol))
  return "gg"

@app.route('/overview')
def overview():
  stock = {}
  show_pattern = {}
  with open(STOCK_NAME_PATH) as f:
    for row in csv.reader(f):
      stock[row[0]] = {'company name':row[1]}
  current_stock = request.args.get('stock', None)
  if current_stock:
    df = pd.read_csv('datasets/daily/{}.csv'.format(current_stock))
    for pattern in patterns:
      pattern_func = getattr(talib,pattern)
      try:
        result = pattern_func(df['Open'], df['High'], df['Low'], df['Close'])
        last = result.tail(1).values[0]

        if last > 0:
          show_pattern[patterns[pattern]]= "bullish"
        elif last < 0:
          show_pattern[patterns[pattern]]= "bearish"
        else:
          show_pattern[patterns[pattern]]= None
      except:
        pass
  print(show_pattern)
  return render_template("tab.html", stock = stock, show_pattern = show_pattern, current_stock = current_stock)

@app.route('/abb')
def hello_wor():
  return "-.-"

#<img src ="https://stockcharts.com/c-sc/sc?s={{ symbol }}&p=D&b=5&g=0&i=0&r=1651231120597" />
