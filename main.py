from flask import Flask, render_template, request
import requests
import dash
import dash_core_components as dcc
import dash_html_components as html

from dash.dependencies import Input, Output

import pandas as pd
from datetime import datetime as dt
import json

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

external_stylesheets = [
    'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/css/bootstrap.min.css',
    {
        'href': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.2/css/bootstrap.min.css',
        'rel': 'stylesheet',
    }
]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
  html.Div(
    className="navbar navbar-inverse",
    children = [
    html.H1(children = "Digital Device Shopping Trend", style = {'color':'white'}),
    dcc.DatePickerSingle(
      #Start_date
      className="dropdown col-md-1",
      id='startDate', 
        min_date_allowed=dt(2010, 1, 1),
        max_date_allowed=dt(2099, 12, 31),
        initial_visible_month=dt(2020, 1, 1),
        date=str(dt(2020, 1, 1))[0:10]
    ), 
    dcc.DatePickerSingle(
      #End_date
      className="dropdown col-md-1",
      id='endDate',
        min_date_allowed=dt(2010, 1, 1),
        max_date_allowed=dt(2099, 12, 31),
        initial_visible_month=dt(2020, 5, 1),
        date=str(dt(2020, 5, 1))[0:10]
    )
    ]
  ),
  html.Div(
    className="navbar",
    children = [
    dcc.Dropdown(
      #Time_Unit
      className="dropdown col-md-3",
      id='timeUnit',
      options=[
        {'label': 'Date', 'value': 'date'},
        {'label': 'Week', 'value': 'week'},
        {'label': 'Month', 'value': 'month'}
      ],
      value = 'week'
    ), 
    dcc.Dropdown(
      #Device
      className="dropdown col-md-3",
      id='device',
      options=[
        {'label': 'PC', 'value': 'pc'},
        {'label': 'Mobile', 'value': 'mo'},
      ],
      value = 'pc'
    ), 
    dcc.Dropdown(
      #Gender
      className="dropdown col-md-3",
      id='gender',
      options=[
        {'label': 'male', 'value': 'm'},
        {'label': 'female', 'value': 'f'}
      ],
      value = 'f'
    ), 
    dcc.Dropdown(
      #ages
      className="dropdown col-md-3",
      id='ages',
      options=[
        {'label': '10', 'value': '10'},
        {'label': '20', 'value': '20'},
        {'label': '30', 'value': '30'},
        {'label': '40', 'value': '40'},
        {'label': '50', 'value': '50'},
        {'label': '60', 'value': '60'},      
      ],
      value = '10',
    ), 
  ]),

  # clicktrend_linechart
  html.Div(
    children=[
    html.H2(children='Click Trend'),
    dcc.Graph(
      id='clicktrend_linechart'
    )]
  ),
  # Pie_Charts
  html.Div([
    # deviceshare_piechart
    html.Div(
      children=[
      html.H2(children='Share by Device'),
      dcc.Graph(
        id='deviceshare_piechart'
      )],
      className="col-md-5"
    ),
    # gendershare_piechart
    html.Div(
      children=[
      html.H2(children='Share by Gender'),
      dcc.Graph(
        id='gendershare_piechart'
      )],
      className="col-md-5"
    )
  ]),
])

@app.callback(Output('clicktrend_linechart', 'figure'),[
  Input('startDate', 'date'),
  Input('endDate', 'date'),
  Input('timeUnit', 'value'),
  Input('device', 'value'),
  Input('gender', 'value'),
  Input('ages', 'value'),
])

def update_linechart(startDate, endDate, timeUnit, device, gender, ages):
  params = {'startDate':startDate,'endDate':endDate,'timeUnit':timeUnit,'device':device,'gender':gender,'ages':ages}
  URL = "http://3.34.2.70:5000/saveclicktrend"
  # Response 된 값을 response 로 받아라
  response = requests.get(URL, params=params) #params= params
  result = json.loads(response.text)
  response = result['results'][0]['data']
  x = []
  for i in response:
    x.append(i['period'])
  y = []
  for i in response:
    y.append(i['ratio'])
  return {
    'data': [{
      'x':x,
      'y':y,
    }],
    'layout': dict(
      xaxis = {'type' : 'date', 'title': 'period'},
      yaxis = {'title' : 'clicktrend'},
      legend = {'x':'period', 'y':'clicktrend'}
    )
  }
  
@app.callback(Output('deviceshare_piechart', 'figure'),[
  Input('startDate', 'date'),
  Input('endDate', 'date'),
  Input('timeUnit', 'value'),
  Input('gender', 'value'),
  Input('ages', 'value'),
])
def deviceshare_piechart(startDate, endDate, timeUnit, gender, ages):
  params = {'startDate':startDate,'endDate':endDate,'timeUnit':timeUnit,'gender':gender,'ages':ages}
  URL = "http://3.34.2.70:5000/savedeviceshare"
  # Response 된 값을 response 로 받아라
  response = requests.get(URL, params=params) #params= params
  result = json.loads(response.text)
  response = result['results'][0]['data']
  #mobile 과 pc 의 클릭 추이 합산
  mobile_total = 0
  pc_total = 0
  for i in response:
    if i['group'] == 'mo':
      mobile_total = mobile_total + i['ratio']
    else:
      pc_total = pc_total + i['ratio']
  data = [
    {
      'values' : [mobile_total,pc_total],
      'labels' : ['mobile','pc'],
      'type' : 'pie'
    },
    
  ]
  return {
    'data':data,
    'layout':{
      'margin': {
        'l':0,
        'r':0,
        'b':15,
        't':15}
        }
      }

@app.callback(Output('gendershare_piechart', 'figure'),[
  Input('startDate', 'date'),
  Input('endDate', 'date'),
  Input('timeUnit', 'value'),
  Input('device', 'value'),
  Input('ages', 'value'),
])
def gendershare_piechart(startDate, endDate, timeUnit, device, ages):
  params = {'startDate':startDate,'endDate':endDate,'timeUnit':timeUnit,'device':device,'ages':ages}
  URL = "http://3.34.2.70:5000/savegendershare"
  # Response 된 값을 response 로 받아라
  response = requests.get(URL, params=params) #params= params
  result = json.loads(response.text)
  response = result['results'][0]['data']
  #female 과 male 의 클릭 추이 합산
  female_total = 0
  male_total = 0
  for i in response:
    if i['group'] == 'f':
      female_total = female_total + i['ratio']
    else:
      male_total = male_total + i['ratio']
  data = [
    {
      'values' : [female_total,male_total],
      'labels' :['Female', 'Male'],
      'type' : 'pie',
    }
  ]
  return {
    'data':data,
    'layout':{
      'margin': {
        'l':0,
        'r':0,
        'b':15,
        't':15}
      }
    }

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=True)
