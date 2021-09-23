import dash
import dash_core_components as dcc
import dash_table as dt
import dash_html_components as html
from dash.dependencies import Output, Input
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go

import pandas as pd
import pymongo
import datetime
import numpy as np
import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
from _plotly_future_ import v4_subplots
import plotly
from plotly.graph_objs import Scatter, Layout
import plotly.offline as pyo
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px
import dash_daq as daq
#from sklearn.linear_model import LinearRegression

import datetime as dt
from datetime import datetime, timedelta #delta time

from timeit import default_timer as timer #tic toc
from flask import Flask
from flask_caching import Cache  #time update
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

##### DB Server connection ############################################################################
# myclient =  pymongo.MongoClient('161.122.121.44', 27111, username='CAMs', password='best', authSource='DB_CAMs')
myclient =  pymongo.MongoClient('192.168.0.46', 27111, username='CAMs', password='best', authSource='DB_CAMs')
print(myclient.list_database_names()) #check DB list 
#######################################################################################################

##### Sub collection list in DB_CAMs ###############################################################
mydb = myclient["DB_CAMs"]
print(mydb.list_collection_names()) #check collection list 
#######################################################################################################

##### Data Column ##########################################################################
mycol = mydb["sensors"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
def query_data():
    now_Y = datetime.today().strftime("%Y")
    now_m = datetime.today().strftime("%m")
    now_d = datetime.today().strftime("%d")
    today = dt.date.today()
    week_ago = today - dt.timedelta(days=7)
    week_ago_Y=week_ago.strftime("%Y")
    week_ago_m=week_ago.strftime("%m")
    week_ago_d=week_ago.strftime("%d")
    ref_time=[now_Y,now_m,now_d,week_ago_Y,week_ago_m,week_ago_d]
    return ref_time

data_name = ['Light','Air_Temp','Leaf_Temp','Humidity','CO2','Dewpoint','EvapoTranspiration','HD','VPD']
SN_List = ['B2F_CAMs_1000000000001', 'B2F_CAMs_1000000000002']
def basic_info_val():
    Date = query_data()[0]+query_data()[1]+query_data()[2]
    data1 = pd.DataFrame(mycol.find({'Date':Date, 'SN':SN_List[0]}))
    val1 = val2 = val3 = val4 = 0
    if data1.shape[0]:
        val1 = float(data1['Air_Temp'][-1:])
        val2 = float(data1['Leaf_Temp'][-1:])
        val3 = float(data1['Humidity'][-1:])
        val4 = float(data1['CO2'][-1:])    
    return val1, val2, val3, val4

app.title = 'B2F CAMs Viewer - Expert'

def layout():
    val1, val2, val3, val4=basic_info_val()
    tmp_val=val1
    leaf_tmp_val=val2
    humidity_tmp_val=val3
    co2_tmp_val=val4
    return html.Div([
        html.H1('B2F CAMs Viewer - Expert'),
        html.Div('Monitoring Time: '+datetime.now().strftime("%H:%M:%S")),

        html.Div([
            html.Div([
                daq.Gauge(
                    id='air_temp_gauge',
                    color={"gradient":True,"ranges":{"lightblue":[-10,0],"lightgreen":[0,20],"green":[20,30],"yellow":[30,40],"red":[40,50]}},
                    scale={'start': -10, 'interval': 2, 'labelInterval': 5},
                    label='Air Temperature',
                    max=50,
                    min=-10,
                    showCurrentValue=True,
                    value=tmp_val,
                    units="Deg.",
            )],
            style={
                "display": "inline-block",
                "width": "20%"
            }),
            html.Div([
                daq.Gauge(
                    id='leaf_temp_gauge',
                    color={"gradient":True,"ranges":{"lightgreen":[0,20],"green":[20,30],"yellow":[30,40]}},
                    scale={'start': 0, 'interval': 2, 'labelInterval': 5},
                    label='Leaf Temperature',
                    max=40,
                    min=0,
                    showCurrentValue=True,
                    value=leaf_tmp_val,
                    units="Deg.",
            )],
            style={
                "display": "inline-block",
                "width": "20%",
                "margin-left": "20px",
                "verticalAlign": "top"
            }),
            html.Div([
                daq.Tank(
                    id='humidity_gauge',
                    min=0,
                    max=100,
                    value=humidity_tmp_val,
                    showCurrentValue=True,
                    units='%',
                    label='Humidity',
                    labelPosition='top',
                    #style={'margin-top': '20px'}
            )],
            style={
                "display": "inline-block",
                "width": "20%",
                "margin-left": "20px",
                "verticalAlign": "top"
            }),
            html.Div([
                daq.Gauge(
                    id='co2_gauge',
                    #color={"gradient":True,"ranges":{"lightblue":[10,20],"green":[20,30],"yellow":[30,40]}},
                    scale={'start': 0, 'interval': 20, 'labelInterval': 10},
                    label='CO2',
                    max=800,
                    min=0,
                    showCurrentValue=True,
                    value=co2_tmp_val,
                    units="ppm",
            )],
            style={
                "display": "inline-block",
                "width": "20%",
                #"margin-left": "20px",
                "verticalAlign": "top"
            }),
        ]),

        dcc.Dropdown(id='Year', options=[
            {'label': 'Year: 2020', 'value': '2020'},
            {'label': 'Year: 2021', 'value': '2021'},
            {'label': 'Year: 2021', 'value': '2022'},
            {'label': 'Year: 2021', 'value': '2023'},
            {'label': 'Year: 2021', 'value': '2024'},
            {'label': 'Year: 2021', 'value': '2025'},
            {'label': 'Year: 2021', 'value': '2026'},
            {'label': 'Year: 2021', 'value': '2027'},
            {'label': 'Year: 2021', 'value': '2028'},
            {'label': 'Year: 2021', 'value': '2029'},
            {'label': 'Year: 2021', 'value': '2030'}
        ], value=query_data()[0]),

        dcc.Dropdown(id='Month', options=[
            {'label': 'Month: January 1', 'value': '01'},
            {'label': 'Month: Febrary 2', 'value': '02'},
            {'label': 'Month: March 3', 'value': '03'},
            {'label': 'Month: April 4', 'value': '04'},
            {'label': 'Month: May 5', 'value': '05'},
            {'label': 'Month: June 6', 'value': '06'},
            {'label': 'Month: July 7', 'value': '07'},
            {'label': 'Month: August 8', 'value': '08'},
            {'label': 'Month: September 9', 'value': '09'},
            {'label': 'Month: October 10', 'value': '10'},
            {'label': 'Month: November 11', 'value': '11'},
            {'label': 'Month: December 12', 'value': '12'}
        ], value=query_data()[1]),

        dcc.Dropdown(id='Day', options=[
            {'label': 'Day: 1', 'value': '01'},
            {'label': 'Day: 2', 'value': '02'},
            {'label': 'Day: 3', 'value': '03'},
            {'label': 'Day: 4', 'value': '04'},
            {'label': 'Day: 5', 'value': '05'},
            {'label': 'Day: 6', 'value': '06'},
            {'label': 'Day: 7', 'value': '07'},
            {'label': 'Day: 8', 'value': '08'},
            {'label': 'Day: 9', 'value': '09'},
            {'label': 'Day: 10', 'value': '10'},
            {'label': 'Day: 11', 'value': '11'},
            {'label': 'Day: 12', 'value': '12'},
            {'label': 'Day: 13', 'value': '13'},
            {'label': 'Day: 14', 'value': '14'},
            {'label': 'Day: 15', 'value': '15'},
            {'label': 'Day: 16', 'value': '16'},
            {'label': 'Day: 17', 'value': '17'},
            {'label': 'Day: 18', 'value': '18'},
            {'label': 'Day: 19', 'value': '19'},
            {'label': 'Day: 20', 'value': '20'},
            {'label': 'Day: 21', 'value': '21'},
            {'label': 'Day: 22', 'value': '22'},
            {'label': 'Day: 23', 'value': '23'},
            {'label': 'Day: 24', 'value': '24'},
            {'label': 'Day: 25', 'value': '25'},
            {'label': 'Day: 26', 'value': '26'},
            {'label': 'Day: 27', 'value': '27'},
            {'label': 'Day: 28', 'value': '28'},
            {'label': 'Day: 29', 'value': '29'},
            {'label': 'Day: 30', 'value': '30'},
            {'label': 'Day: 31', 'value': '31'}
        ], value=query_data()[2]),

        # dcc.DatePickerRange(
        #     id='my-date-picker-range',
        #     min_date_allowed=dt.date(2020, 1, 1),
        #     max_date_allowed=dt.date(2120, 12, 31),
        #     initial_visible_month=dt.date(int(query_data()[3]),int(query_data()[4]),int(query_data()[5])),
        #     start_date = dt.date(int(query_data()[3]),int(query_data()[4]),int(query_data()[5])),
        #     end_date=dt.date(int(query_data()[0]),int(query_data()[1]),int(query_data()[2]))
        # ),
        # html.Div(id='output-container-date-picker-range'),

        dcc.Graph(id='graph1'),
        #dcc.Graph(id='graph2'),
        dcc.Graph(id='graph3'),
        #dcc.Graph(id='graph4'),
        dcc.Graph(id='graph5')
    ])

app.layout = layout

####### find extraction #####################################
def DB_Data_Extraction(Date):
    data = pd.DataFrame(mycol.find({'Date':Date, 'Time':{'$gte':'00:00:30','$lte':'23:59:30'}}))
    data1 = data[data['SN']==SN_List[0]]
    data2 = data[data['SN']==SN_List[1]]
    return data1, data2

# def DB_Data_Extraction_Week(Start_Date,End_Date):
#     week_data1 = pd.DataFrame(mycol.find({'Date':{'$gte':Start_Date, '$lte':End_Date}, 'SN':SN_List[0], 'Time':{'$gte':'00:00:30','$lte':'23:59:30'}}))
#     week_data2 = pd.DataFrame(mycol.find({'Date':{'$gte':Start_Date, '$lte':End_Date}, 'SN':SN_List[1], 'Time':{'$gte':'00:00:30','$lte':'23:59:30'}}))
#     #for RTR Graph
#     date_list=week_data1['Date'].unique()
#     radiation_list=[]
#     air_temp_list=[]
#     for ii in range(0,len(date_list)):
#         tmp_val1=pd.to_numeric(week_data1[week_data1['Date']==date_list[ii]]['Light']).sum()
#         radiation_list=np.append(radiation_list,tmp_val1)
#         tmp_val2=pd.to_numeric(week_data1[week_data1['Date']==date_list[ii]]['Air_Temp']).mean()
#         air_temp_list=np.append(air_temp_list,tmp_val2)
#         print(air_temp_list)
    
#     return week_data1, week_data2, date_list, radiation_list, air_temp_list
#############################################################

@app.callback(
    [
    Output(component_id='graph1', component_property='figure'),
    #Output(component_id='graph2', component_property='figure'),
    Output(component_id='graph3', component_property='figure'),
    #Output(component_id='graph4', component_property='figure'),
    Output(component_id='graph5', component_property='figure')],
    [Input(component_id='Year', component_property='value'),
    Input(component_id='Month', component_property='value'),
    Input(component_id='Day', component_property='value')#,
    #Input('my-date-picker-range', 'start_date'),
    #Input('my-date-picker-range', 'end_date')
    ])
#def update_output(Year, Month, Day, start_date, end_date):
def update_output(Year, Month, Day):    
    Input_Date=Year+Month+Day
    data11, data22 = DB_Data_Extraction(Input_Date)
    data1=data11.sort_values(by=['Time'], axis=0)
    data2=data22.sort_values(by=['Time'], axis=0)
    
    #start_date_str=start_date[0:4]+start_date[5:7]+start_date[8:10]
    #end_date_str=end_date[0:4]+end_date[5:7]+end_date[8:10]
    #week_data1, week_data2 , date_list, radiation_list, air_temp_list = DB_Data_Extraction_Week(start_date_str,end_date_str)

    #x_time=[]
    #for i in range(0,len(week_data1)):
    #    #try:
    #    tmp_time=datetime.strptime(week_data1['Date'][i]+week_data1['Time'][i], '%Y%m%d%H:%M:%S')
    #    x_time=np.append(x_time,tmp_time)
    #    #except KeyError:
    #    #    pass
    
    fig1 = go.Figure()
    for kk in range(0,9):
        fig1.add_trace(go.Scatter(
            x = data1['Time'],
            y = data1[data_name[kk]],
            mode='lines',
            name = 'SN'+SN_List[0][-3:]+':'+data_name[kk]
        )),

        fig1.add_trace(go.Scatter(
            x = data2['Time'],
            y = data2[data_name[kk]],
            mode='lines',
            name = 'SN'+SN_List[1][-3:]+':'+data_name[kk]
        )),

    cumsum1 = np.cumsum(pd.to_numeric(data1[data_name[0]])/1000)
    cumsum2 = np.cumsum(pd.to_numeric(data2[data_name[0]])/1000)
    fig1.add_trace(go.Scatter(
            x = data1['Time'],
            y = cumsum1,
            mode='lines',
            name = 'SN'+SN_List[0][-3:]+':'+'Amount of Solar Radiation (k)'
        )),

    fig1.add_trace(go.Scatter(
            x = data2['Time'],
            y = cumsum2,
            mode='lines',
            name = 'SN'+SN_List[1][-3:]+':'+'Amount of Solar Radiation (k)'
        )),

    fig1.update_layout(
         title={
             'text': Input_Date,
             'y':0.9,
             'x':0.5,
             'xanchor':'center',
             'yanchor':'top'},
         xaxis_title = 'Time [H:M:S]',
         yaxis_title = 'Sensor / Calc. Data',
         height = 600
        )
    fig1.update_xaxes(rangeslider_visible=True)

    # fig2 = go.Figure()
    # for kk in range(0,9):
    #     fig2.add_trace(go.Scatter(
    #         x = x_time,
    #         y = week_data1[data_name[kk]],
    #         mode='lines',
    #         name = 'SN'+SN_List[0][-3:]+':'+data_name[kk]
    #     )),
    #     fig2.add_trace(go.Scatter(
    #         x = x_time,
    #         y = week_data2[data_name[kk]],
    #         mode='lines',
    #         name = 'SN'+SN_List[1][-3:]+':'+data_name[kk]
    #     )),

    # fig2.update_layout(
    #      title={
    #          'text': start_date_str+ ' ~ ' +end_date_str,
    #          'y':0.9,
    #          'x':0.5,
    #          'xanchor':'center',
    #          'yanchor':'top'},
    #      xaxis_title = 'Date time',
    #      yaxis_title = 'Sensor / Calc. Data',
    #      height = 600
    #     )
    # fig2.update_xaxes(rangeslider_visible=True)

    #data_name = ['Light','Air_Temp','Leaf_Temp','Humidity','CO2','Dewpoint','EvapoTranspiration','HD','VPD']
    fig3 = make_subplots(specs=[[{"secondary_y": True}]])
    for kk2 in range(1,3):
        fig3.add_trace(go.Scatter(
            x = data1['Time'],
            y = data1[data_name[kk2]],
            mode='lines',
            name = 'SN'+SN_List[0][-3:]+':'+data_name[kk2]
        ),secondary_y=False),
        fig3.add_trace(go.Scatter(
            x = data2['Time'],
            y = data2[data_name[kk2]],
            mode='lines',
            name = 'SN'+SN_List[1][-3:]+':'+data_name[kk2]
        ),secondary_y=False),
    for kk3 in range(3,4):
        fig3.add_trace(go.Scatter(
            x = data1['Time'],
            y = data1[data_name[kk3]],
            mode='lines',
            name = 'SN'+SN_List[0][-3:]+':'+data_name[kk3]
        ),secondary_y=True),
        fig3.add_trace(go.Scatter(
            x = data2['Time'],
            y = data2[data_name[kk3]],
            mode='lines',
            name = 'SN'+SN_List[1][-3:]+':'+data_name[kk3]
        ),secondary_y=True),

    fig3.update_layout(
         title={
             'text': 'Temperature vs. Humidity',
             'y':0.9,
             'x':0.5,
             'xanchor':'center',
             'yanchor':'top'},
         xaxis_title = 'Time [H:M:S]',
         yaxis_title = 'Sensor / Calc. Data',
         height = 600
        )
    fig3.update_xaxes(rangeslider_visible=True)
    fig3.update_yaxes(title_text="<b>Temperature </b>[Deg.]", secondary_y=False)
    fig3.update_yaxes(title_text="<b>Humidity </b>%", secondary_y=True)
    
    # fig4 = go.Figure()
    # fig4.add_trace(go.Scatter(
    #     x = radiation_list,
    #     y = air_temp_list,
    #     mode='markers',
    #     name = 'SN'+SN_List[0][-3:]+':'+'RTR'
    # )),
    
    # fig4.update_layout(
    #      title={
    #          'text': 'RTR: Radiation vs. Temperature Ratio',
    #          'y':0.9,
    #          'x':0.5,
    #          'xanchor':'center',
    #          'yanchor':'top'},
    #      xaxis_title = 'Amount of Radiation [J]',
    #      yaxis_title = 'Mean Air Temperature [Deg.]',
    #      height = 600
    #     )
    # fig4.update_xaxes(rangeslider_visible=True)

    
    #data_name = ['Light','Air_Temp','Leaf_Temp','Humidity','CO2','Dewpoint','EvapoTranspiration','HD','VPD']
    VPD1 = pd.to_numeric(data1[data_name[8]])/1000
    VPD2 = pd.to_numeric(data2[data_name[8]])/1000
    fig5 = make_subplots(specs=[[{"secondary_y": True}]])
    for kk2 in range(1,3):
        fig5.add_trace(go.Scatter(
            x = data1['Time'],
            y = data1[data_name[kk2]],
            mode='lines',
            name = 'SN'+SN_List[0][-3:]+':'+data_name[kk2]
        ),secondary_y=False),
        fig5.add_trace(go.Scatter(
            x = data2['Time'],
            y = data2[data_name[kk2]],
            mode='lines',
            name = 'SN'+SN_List[1][-3:]+':'+data_name[kk2]
        ),secondary_y=False),
    for kk3 in range(8,9):
        fig5.add_trace(go.Scatter(
            x = data1['Time'],
            y = VPD1,
            mode='lines',
            fill='tozeroy',
            name = 'SN'+SN_List[0][-3:]+':'+data_name[kk3]
        ),secondary_y=True),
        fig5.add_trace(go.Scatter(
            x = data2['Time'],
            y = VPD2,
            mode='lines',
            fill='tonexty',
            name = 'SN'+SN_List[1][-3:]+':'+data_name[kk3]
        ),secondary_y=True),

    fig5.update_layout(
         title={
             'text': 'VPD Monitor',
             'y':0.9,
             'x':0.5,
             'xanchor':'center',
             'yanchor':'top'},
         xaxis_title = 'Time [H:M:S]',
         yaxis_title = 'Sensor / Calc. Data',
         height = 600
        )
    fig5.update_xaxes(rangeslider_visible=True)
    fig5.update_yaxes(title_text="<b>Temperature </b>[Deg.]", secondary_y=False)
    fig5.update_yaxes(title_text="<b>VPD </b>[kPa]", secondary_y=True)

    #return fig1, fig2, fig3, fig4, fig5\
    return fig1, fig3, fig5

if __name__ == '__main__':
    app.run_server(debug=False, port=28057, host='0.0.0.0')