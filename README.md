# YouTube Data Harvesting and Warehousing using SQL, MongoDB and Streamlit

# OUTLOOK:
This method includes crafting a Streamlit UI, pulling YouTube data via API, housing it within MongoDB, transferring to SQL warehouse, SQL querying, and presenting findings via Streamlit


Get API = Google Account-->Google Cloud Console-->Create a Project-->Enable YouTube API-->Create API Key-->Restrict API Key (Recommended)

channel Id = YouTube--> Channel page--> right "click" view page source --> search "Channel_id" 

# TECHNOLOGIES USED:

Youtube Data API--Authentication for accessing YouTube's data

Python--Interpreted

MongoDB--NoSQL(Binary JSON)

MySql--Structured Query Language

Streamlit--UI Creation (Python Package)

# In summary, this method encompasses these steps:
## 1.Streamlit UI Creation:
    
    Develop a user-friendly interface using Streamlit for seamless interaction.

## 2.YouTube API Connection:
    
    Retrieve YouTube data via the API, facilitated by the Python Google API client library.

## 3.Data Storage in MongoDB:
    
    Efficiently stores collected data in MongoDB, which adeptly handles unstructured and semi-structured information.

## 4.Migrate to SQL Data Warehouse:
    
    Transfer aggregated data to a SQL data warehouse like MySQL or PostgreSQL to enable comprehensive querying.

## 5.Utilize SQL Queries:
    
    Leverage SQL to join tables within the data warehouse, fetching precise channel insights based on user input.

## 6.Visual Display in Streamlit:
    Present curated data within the Streamlit app, employing its visualisation tools to generate informative charts and graphs.

