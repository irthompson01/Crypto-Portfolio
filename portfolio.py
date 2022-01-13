##### IMPORTS #####
import streamlit as st
import pandas as pd
from requests import Request, Session
import json
import pprint

##### Load CMC Data #####
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

parameters = {
    "symbol": 'BTC,ETH,ADA,XMR',
    "convert": "USD"
}

headers = {
    'Accepts':'application/json', #telling CMC API that we want json format in response
    'X-CMC_PRO_API_KEY': 'c57ac442-3e7c-4a75-8d1f-a18e34b9bce6' #Auth token -
    }

##### Load Transaction Data #####
file_curr = './transactions.csv'

@st.cache(persist=True)
def load_transaction_data():
    df = pd.read_csv(file_curr)
    #del df['Unnamed: 0']
    return df

@st.cache(persist=True)
def load_CMC_data():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

    parameters = {
        "symbol": 'BTC,ETH,ADA,XMR',
        "convert": "USD"
    }

    headers = {
        'Accepts':'application/json', #telling CMC API that we want json format in response
        'X-CMC_PRO_API_KEY': 'c57ac442-3e7c-4a75-8d1f-a18e34b9bce6' #Auth token -
        }
    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)
    response = json.loads(response.text)
    return response

prices = load_CMC_data()
df = load_transaction_data()



def main():
    #st.write(response['data']['XMR']['quote']['USD']['price'])
    st.sidebar.title("Select a Portfolio:")
    portfolio = st.sidebar.selectbox(
     '',
     ('Home','Ross & Amy', 'Casey y Luca', 'Ian'))

    if portfolio == 'Home':
         priceData()

    elif portfolio == 'Ross & Amy':
        showData("RA")

    elif portfolio == 'Casey y Luca':
        showData("CL")

def priceData():
    st.title("Current Crypto Prices")
    col1, col2, col3 = st.columns(3)
    col1.metric("Bitcoin", "$"+str(round(prices['data']['BTC']['quote']['USD']['price'], 2)), str(round(prices['data']['BTC']['quote']['USD']['percent_change_24h'], 2))+"%")
    col2.metric("Ethereum", "$"+str(round(prices['data']['ETH']['quote']['USD']['price'], 2)), str(round(prices['data']['ETH']['quote']['USD']['percent_change_24h'], 2))+"%")
    col3.metric("Cardano", "$"+str(round(prices['data']['ADA']['quote']['USD']['price'], 2)), str(round(prices['data']['ADA']['quote']['USD']['percent_change_24h'], 2))+"%")

def showData(owner):
    port_dict = {"RA": "Ross & Amy", "CL": "Casey y Luca"}
    st.title(port_dict[owner] + "'s Crypto Portfolio")
    sub = df[df['Owner'] == owner]



    cryptos = sub["Symbol"].unique()

    for tick in cryptos:
        col1, col2 = st.columns(2)
        sub_tick = sub[sub['Symbol'] == tick]
        total = getTotalAmount(sub_tick)
        col1.metric(tick, total)
        col2.metric("Value (USD)", total*round(prices['data'][tick]['quote']['USD']['price'], 2))


    #st.dataframe(sum_amount)
    st.write("Transaction History")
    st.dataframe(sub)

def getTotalAmount(df):
    sum_amount = df['Amount']
    total = 0
    for i in sum_amount:
        total += float(str(i).replace(',',''))
    return total

if __name__ == "__main__":
    main()
