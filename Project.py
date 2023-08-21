import streamlit as st 
from streamlit_option_menu import option_menu
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import time
from isodate import parse_duration
from datetime import datetime
import pymongo
from pymongo import MongoClient
import pymysql
import sqlalchemy
from sqlalchemy import create_engine
import plotly.express as px

#streamlit page configure
st.set_page_config(page_title= " YouTube Data Analysis | By DineshKumar",page_icon= "🧮",layout='wide',
    initial_sidebar_state="expanded",menu_items={'About': """# This app is created by Dinesh Kumar!"""})
# steamlit menu bar
selected = option_menu("YouTube Data Management and Visualization Tool", ["HOME","EXTRACT","MIGRATION","ANALYSIS","DOWNLOAD"], 
            icons=["person-fill","briefcase","database","graph-up","book"],
            default_index=0,
            orientation="horizontal",
            styles={"nav-link": {"font-size": "20px", "text-align": "center", "margin": "2px", 
                                "--hover-color": "#C80101"},
                    "icon": {"font-size": "30px"},
                    "container" : {"max-width": "6000px"},
                    "nav-link-selected": {"background-color": "#C80101"}})
##--------------------------API Request----------------------## 
# Get API = Google Account-->Google Cloud Console-->Create a Project-->Enable YouTube API-->Create API Key-->Restrict API Key (Recommended)
# channel Id = YouTube--> Channel page--> right "click" view page source --> search "Channel_id" 
api_key = '**************************************' #can you use your API Key 
channel_id=[]    
youtube = build('youtube', 'v3', developerKey=api_key)
##--------------------------Channel Details----------------------## 
def get_channel_stats(channel_id):
    all_data = []
    response = youtube.channels().list(part='snippet,contentDetails,statistics',id=','.join(channel_id)).execute()

    for item in response['items']:
        data = {
            'channel_id': item['id'],
            'channel_name': item['snippet']['title'],
            'channel_description': item['snippet']['description'],
            'channel_views': int(item['statistics']['viewCount']),
            'channel_subcription_count': int(item['statistics']['subscriberCount']),
            'channel_video_count': int(item['statistics']['videoCount']),
            'playlist_id': item['contentDetails']['relatedPlaylists']['uploads']
        }
        all_data.append(data)

    return all_data
channel_data=[]
##--------------------------Playlist_ID Details----------------------## 
def get_playlist_id(channel_data):
    playlist_ids=[]
    for pls in channel_data:
        pl = pls['playlist_id']
        playlist_ids.append(pl)
    return playlist_ids

playlist_ids =[]
##--------------------------Video_ID Details----------------------##
def get_video_ids(playlist_ids):
    video_ids = []
    for playlist_id in playlist_ids:
        next_page_token = None
        more_pages = True
        while more_pages:
            response = youtube.playlistItems().list(part='contentDetails',playlistId=playlist_id,maxResults=50,pageToken=next_page_token).execute()
            for item in response.get('items', []):
                video_ids.append(item['contentDetails']['videoId'])
            next_page_token = response.get('nextPageToken')
            if next_page_token is None:
                more_pages = False
    return video_ids
video_ids=[]
##--------------------------Video Details----------------------##
def get_video_details(video_ids):
    all_video_info = []
    for i in range(0, len(video_ids), 50):
        response = youtube.videos().list(part="snippet,contentDetails,statistics",id=','.join(video_ids[i:i + 50])).execute()
        for video in response['items']:
            publish_date_string = video['snippet']['publishedAt']
            publish_date = datetime.strptime(publish_date_string, "%Y-%m-%dT%H:%M:%SZ")
            formatted_publish_date = publish_date.strftime("%d-%m-%Y") #change date formate
            video_info = {
                'video_id': video['id'],
                'video_name': video['snippet']['title'],
                'channel_name': video['snippet']['channelTitle'],
                'video_description': video['snippet']['description'],
                'publish_date': formatted_publish_date,
                'view_count': int(video['statistics']['viewCount']),   # datatype convertion object into integer
                'like_count': int(video['statistics'].get('likeCount',0)),
                'comment_count': int(video['statistics'].get('commentCount',0)),
                ##-------------------Change time into seconds----------------------------##
                'video_duration': int(parse_duration(video['contentDetails']['duration']).total_seconds()), # change time in seconds
                'publish_year': int(datetime.strptime(video['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ').year) 
                }
            all_video_info.append(video_info) 
    return all_video_info
##--------------------------HOME PAGE----------------------##
if selected == "HOME":

    st.header(":green[Hello, Data Explorers!]")
    st.markdown("#### Welcome to our YouTube Data Management and Visualization Tool! With this tool, you can seamlessly gather, store, and visualize YouTube channel and video data for analysis. Whether you're a content creator, marketer, or data enthusiast, this application streamlines the process of harnessing insights from YouTube content.")
    col1,col2 =st.columns(2,gap="large") # define column in seperate the page 
    with col1:
        st.markdown("#### :green[DOMAIN🌏]:")
        st.markdown("#### Social Ⓜ️edia")
        st.markdown("#### :green[OUTLOOK🔍]:")
        st.markdown("#### This method includes crafting a Streamlit UI, pulling YouTube data via API, housing it within MongoDB, transferring to SQL warehouse, SQL querying, and presenting findings via Streamlit")
        st.markdown("#### 1)Enter channel ID, view details, select for migration.")
        st.markdown("#### 2)Fetch YouTube data using API, store in MongoDB.")
        st.markdown("#### 3)Migrate to SQL warehouse, query with SQL.")
        st.markdown("#### 4)Visualize insights in Streamlit with charts.")
    with col2:
        st.markdown("#### :green[TECHNOLOGIES USED👨‍💻]:") 
        st.markdown("#### Youtube Data API🔑--Authentication for accessing YouTube's data")
        st.markdown("#### Python🐍--Interpreted")
        st.markdown("#### MongoDB🍃--NoSQL(Binary JSON)")
        st.markdown("#### MySql🐳--Structured Query Language")
        st.markdown("#### Streamlit🍁--UI Creation")
##--------------------------EXTRACT PAGE----------------------##    
if selected == "EXTRACT":
    st.header(":green[Channel Data Extract]")
    st.write("Our app efficiently gathers detailed information about channels and videos using the YouTube API. This data becomes a valuable resource for your next steps in analysis and exploration.")
    st.write(":green[📈 **Ready to Begin? Enter a Channel ID and Let's Get Started!**]")
    
    #------------------------CHANNEL ID INPUT-------------------#
    channel_id = st.text_input(":red[Enter Channel IDs]").split(',')  
    extract_button = st.button(":green[Extract Data]")
    if channel_id and extract_button:  
        channel_data = get_channel_stats(channel_id)
        ex = pd.DataFrame(channel_data) 
        st.write(ex)
##--------------------------MIGRATION PAGE----------------------##
if selected=="MIGRATION": 
    client = pymongo.MongoClient('mongodb://127.0.0.1:27017/')  # MongoDB connect you can use your connect link
    mydb = client["youtube"] #CREATE DATABASE
    #CREATE COLLECTIONS
    chl_coll = mydb['Channel_Data']
    vdo_coll = mydb['Channel_Video_Data']
    st.subheader(":green[Data Stored into MongoDB Database]") 
    st.write("We organize YouTube data smartly in MongoDB, creating a user-friendly storage space that handles both structured and semi-structured information with ease. This makes managing data simple and flexible.") 
    channel_id = st.text_input(":red[Enter Channel IDs]").split(',')  
    submit = st.button(" :green[Data Store into MongoDB Database]") 
            #--------------DATA STORED into MongoDB Database----------------#  
    if channel_id and submit:
        channel_data = get_channel_stats(channel_id)
        playlist_ids = get_playlist_id(channel_data)
        video_ids = get_video_ids(playlist_ids)
        video_data = get_video_details(video_ids)
        with st.spinner("Processing, don't go anywhere🔗..."):
            time.sleep(5)
            # upsert --> inserts a new record if it doesn't exist or updates an existing record if it does
            for i in channel_data:
                unique_field = {'channel_id': i['channel_id']}  # select unique id
                chl_coll.update_one(unique_field, {'$set': i}, upsert=True)    
            for i in video_data:
                unique_field = {'video_id': i['video_id']}  
                vdo_coll.update_one(unique_field, {'$set': i}, upsert=True)
        with st.spinner("Almost there, fetching updates🌐..."):
            time.sleep(5)
            st.success('Done!,Data Successfully Stored in MongoDB Database',icon="🛢️")

    def channel_names():   
        ch_name = []
        for i in mydb.Channel_Data.find():
            ch_name.append(i['channel_name'])
        return ch_name
            #--------------DATA Migrate into MySQL Database----------------# 
    st.subheader(":blue[ Migrate  Data  into MySQL ]")
    st.write("When you're set, smoothly move your collected data to a SQL data warehouse. This step unlocks powerful tools for in-depth analysis and querying, taking your insights to the next level.")
    user_input =st.multiselect(":green[Select the channel to be inserted into MySQL Tables]",options = channel_names())
    Transfer = st.button(":blue[Migrate data into MySQL]") 
    if Transfer:
        with st.spinner('Please wait a bit'):
            def get_channel_details(user_input): # selct the channel data variable
                query = [{'$match': {'channel_name': {'$in':user_input}}},{'$project': { '_id': 0,'channel_id': 1,'channel_name': 1,'channel_views': 1,'channel_subcription_count': 1,'channel_video_count': 1,'playlist_id': 1 }}]
                x = chl_coll.aggregate(query)
                channel_table = pd.DataFrame(list(x))
                return channel_table 
            Channel_Data=get_channel_details(user_input) 

            def get_video_details(user_input):   # selct the Video data variable
                query = [{'$match': {'channel_name': {'$in':user_input}}},{'$project': {"_id":0,"video_id":1,"channel_name":1,"channel_name":1,"video_name":1,"publish_date":1,"view_count":1,"like_count":1,"comment_count":1,"video_duration":1,'publish_year':1}}]
                x = vdo_coll.aggregate(query)
                video_table = pd.DataFrame(list(x))
                return video_table
            Video_Data = get_video_details(user_input)

            client.close()   # close MongoDB Connection's
        
        #--------------Connect MySQL Database----------------#
            myconnection = pymysql.connect(host="127.0.0.1",user="root",passwd="********")  # use your MySql password
            cur = myconnection.cursor()
            cur.execute("CREATE DATABASE IF NOT EXISTS YOUTUBE_DB") #Create Database into MySQL
            #-----------------------------SQL ENGINE CREATE-----------------------------#
            engine = create_engine('mysql+pymysql://root:********@localhost/YOUTUBE_DB') # use your MySql password
                            #---------Migrate Channel Details----------#
            try:  
                Channel_Data.to_sql('channel_data', con=engine, if_exists='replace', index=False, method='multi')
                print("Data inserted successfully")
            except Exception as e:
                print("An error occurred:", e) 
                            #---------Migrate video Details----------#
            try:
                Video_Data.to_sql('video_data', con=engine, if_exists='replace', index=False,method='multi')
                print("Data inserted successfully")
            except Exception as e:
                print("An error occurred:", e)
            st.success("Data Migrated Successfully",icon="🎯")
            st.success("Happy analyzing!",icon="🧚‍♂️")
            engine.dispose()
            myconnection.close()    # close engine and SQL connection
##--------------------------ANALYSIS PAGE----------------------##        
if selected=="ANALYSIS":
    st.header(":green[Finaly we reached analysis the data]")
    st.write("📈 **Ready to Dive In? Let's Start Analyzing!**")
    myconnection = pymysql.connect(host="127.0.0.1",user="root",passwd="***********",database='YOUTUBE_DB') # use your MySql password
    cur = myconnection.cursor()
#-- Connect The MySQL DATABASE--#
#--Queries is dict fortmat key means question and then value means MySQL Query --#
    queries={"1) What are the names of all the videos and their corresponding channels?":"""SELECT VIDEO_NAME,CHANNEL_NAME FROM VIDEO_DATA""",
            "2) Which channels have the most number of videos, and how many videos do they have?":"""SELECT CHANNEL_NAME,CHANNEL_VIDEO_COUNT FROM CHANNEL_DATA ORDER BY CHANNEL_VIDEO_COUNT DESC""",
            "3) What are the top 10 most viewed videos and their respective channels?":"""SELECT VIDEO_NAME, CHANNEL_NAME, VIEW_COUNT FROM (SELECT VIDEO_NAME, CHANNEL_NAME, VIEW_COUNT,ROW_NUMBER() OVER (PARTITION BY CHANNEL_NAME ORDER BY VIEW_COUNT DESC) AS RN FROM VIDEO_DATA) RANKED WHERE RN <= 10""",
            "4) How many comments were made on each video, and what are theircorresponding video names?":"""SELECT DISTINCT VIDEO_NAME,COMMENT_COUNT,CHANNEL_NAME FROM VIDEO_DATA ORDER BY COMMENT_COUNT DESC""",
            "5) Which videos have the highest number of likes, and what are their corresponding channel names?":"""SELECT VIDEO_NAME, CHANNEL_NAME, LIKE_COUNT FROM (SELECT VIDEO_NAME, CHANNEL_NAME, LIKE_COUNT,ROW_NUMBER() OVER (PARTITION BY CHANNEL_NAME ORDER BY LIKE_COUNT DESC) AS RN FROM VIDEO_DATA) RANKED WHERE RN <= 1""",
            "6) What is the total number of likes for each video, and what are their corresponding video names?":"""SELECT DISTINCT VIDEO_NAME,LIKE_COUNT,CHANNEL_NAME FROM VIDEO_DATA ORDER BY LIKE_COUNT  DESC""",
            "7) What is the total number of views for each channel, and what are their corresponding channel names?":"""SELECT DISTINCT CHANNEL_NAME,CHANNEL_VIEWS FROM CHANNEL_DATA ORDER BY CHANNEL_VIEWS DESC""",
            "8) What are the names of all the channels that have published videos in the year 2022?":"""SELECT DISTINCT VIDEO_NAME,PUBLISH_YEAR,CHANNEL_NAME FROM VIDEO_DATA WHERE PUBLISH_YEAR =2022""",
            "9) What is the average duration of all videos in each channel, and what are their corresponding channel names?":"""SELECT DISTINCT CHANNEL_NAME AS CHANNEL_NAME, AVG(VIDEO_DURATION) AS AVERAGE_DURATION FROM VIDEO_DATA GROUP BY CHANNEL_NAME ORDER BY AVERAGE_DURATION DESC""",
            "10) Which videos have the highest number of comments, and what are their corresponding channel names?":"""SELECT CHANNEL_NAME, VIDEO_NAME, COMMENT_COUNT AS MAX_COMMENT FROM (SELECT CHANNEL_NAME,VIDEO_NAME,COMMENT_COUNT,ROW_NUMBER() OVER (PARTITION BY CHANNEL_NAME ORDER BY COMMENT_COUNT DESC) AS RN FROM VIDEO_DATA) RANKED WHERE RN = 1"""
            }
    #--Question selections And Query Execute--#
    selected_question = st.selectbox(":orange[Select a question]", list(queries.keys()))
    DATA = None
    columns = []
    display = st.checkbox(":green[Display Data]")

    if display:
        selected_query = queries[selected_question]
        DATA = pd.read_sql(selected_query,myconnection)
        columns=list(DATA.columns)
    if DATA is not None:
        st.write(DATA)
    ##--------------------Visualization--------------------------##   
    Type =['scatter','barchart']
    st.sidebar.subheader(":green[📊 **Visualizing the Story**]")
    st.sidebar.write("Question Number :green[2,5,7,9,10] To Use :green[Barchat] its good visuvalize")
    st.sidebar.write("Question Number :green[3,4,6,8] To Use :green[Scatterchat] its good visuvalize")
    chart_type = st.sidebar.selectbox("select to vizualize the chart",Type)
    x_value=st.sidebar.selectbox("select the colum name of x-axis",columns, key="x_selectbox")
    # COL2=columns.copy()
    # COL2.remove(x_value)
    y_value = st.sidebar.selectbox("select the colum name of y-axis",columns, key="y_selectbox")
    depend_on_color = st.sidebar.selectbox("select the column name variate the chart color",columns,key="color")
    if x_value is not None and y_value is not None:
        Title_name = x_value + " vs " + y_value   # TITLE OF CHART
    else:
        Title_name = "Title Not Available"
    Visuvalize = st.sidebar.button(":green1[visualize Data]")
    if Visuvalize:
            if chart_type == 'barchart':
                chart = px.bar(DATA, x=x_value, y=y_value, color=depend_on_color,title=Title_name)
                st.plotly_chart(chart)
            elif chart_type == 'scatter':
                S_CHART = px.scatter(DATA, x=x_value, y=y_value, color=depend_on_color,title=Title_name)
                st.plotly_chart(S_CHART)
    myconnection.close()
##--------------------------DOWNLOAD PAGE----------------------##
# @st.cache_data
def convert_df(df):
        return df.to_csv().encode('utf-8') # DataFrame is convert to csv
if selected == "DOWNLOAD":
    #--------------channel_data_Download----------------#
    st.header(":green[DOWNLOAD SMALL COLLECTIONS OF DATA]")
    st.write("Its More Useful To Analysis Many More Questions Depends On Your Thinking")    
    channel_id = st.text_input(":red[Enter Channel IDs]").split(',')   
    channel_data = get_channel_stats(channel_id)
    my_large_df = pd.DataFrame(channel_data)
    csv = convert_df(my_large_df)
    st.download_button(label=":green[Download CHANNEL DATA]",data=csv,file_name='channel_data.csv',mime='text/csv')
    st.balloons()#celebratory animation
    #--------------video_data_Download----------------#
    playlist_ids = get_playlist_id(channel_data)
    video_ids = get_video_ids(playlist_ids)
    video_data = get_video_details(video_ids)
    my_large= pd.DataFrame(video_data)
    CXC = convert_df(my_large)         
    st.download_button(label=":green[Download VIDEO DATA]",data=CXC,file_name='video_data.csv',mime='text/csv')
    st.snow()#celebratory animation
    st.subheader("Thanks all meet again next analysis soon")