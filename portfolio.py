##### IMPORTS #####
import streamlit as st
import pandas as pd
from requests import Request, Session
import json
import pprint
from pycoingecko import CoinGeckoAPI
import time
from datetime import datetime
import tzlocal
import altair as alt
import matplotlib.pyplot as plt


##### Load Transaction Data #####
#@st.cache(persist=True)



def load_transaction_data():
    file_curr = './transactions.csv'
    df = pd.read_csv(file_curr)
    #del df['Unnamed: 0']
    return df

##### Load CMC Data #####
def load_CMC_data():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

    parameters = {
        "symbol": 'BTC,ETH,ADA,XMR,ERG,LINK,VET,ALGO,LTC,HBAR,SOL,XRP,BNB,DOT,CRO,MATIC,FIL,ONE,LRC,LOOKS',
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

def getCGChart(slug):
    cg = CoinGeckoAPI()
    coins = cg.get_coins_list()
    coins_df = pd.DataFrame(coins)
    #x = cg.get_price(ids='bi', vs_currencies='usd')
    #ids = cg.get_coins_list()
    coin = cg.get_coin_market_chart_range_by_id(slug, 'usd', 1610851418, 1642387418)

    dates = [data[0] for data in coin['prices']]
    dailyprice = [data[1] for data in coin['prices']]

    d = {"Dates": dates, "Price": dailyprice}
    chart_data = pd.DataFrame(d)

    fig, ax = plt.subplots()
    ax.plot(dates, dailyprice)
    st.pyplot(fig)

def main():

    ##### COINGECKO API & CHART TEST #####
    
    ##### SIDEBAR #####
    st.sidebar.title("Select a Portfolio:")
    portfolio = st.sidebar.selectbox(
     '',
     ('Home','Ross & Amy', 'Casey y Luca', 'Resources'))

    if portfolio == 'Home':
         priceData()

    elif portfolio == 'Ross & Amy':
        showData("RA", "2,500")

    elif portfolio == 'Casey y Luca':
        showData("CL", "3,000")

    elif portfolio == 'Resources':
        showResources()

def priceData():
    st.title("Current Crypto Prices")
    col1, col2, col3, col4 = st.columns([1,1,1,1])
    cols = [col1, col2, col3, col4]

    ticks = [tick for tick in prices['data']]

    for t in range(len(ticks)):
        adj = t%len(cols)
        displayMetric(cols[adj], ticks[t], getSlug(ticks[t]))


def showData(owner, investment):
    port_dict = {"RA": "Ross & Amy", "CL": "Casey y Luca"}
    st.title(port_dict[owner] + "'s Crypto Portfolio")
    sub = df[df['Owner'] == owner]


    ##### Total Invested/Current Value #####
    st.header("Investment: $" + investment)


    ##### Breakdown by Coin #####
    cryptos = sub["Symbol"].unique()
    col1, col2, col3 = st.columns(3)
    col1.subheader("Asset")
    col2.subheader("Price")
    col3.subheader("Value (USD)")
    for tick in cryptos:

        sub_tick = sub[sub['Symbol'] == tick]
        total = getTotalAmount(sub_tick)

        col1.metric(tick, "{:,}".format(total))

        col2.metric(tick + "-USD", "$"+getMetric(tick, 'price'))

        col3.metric("Value (USD)", "$"+ str("{:,}".format(round(total*prices['data'][tick]['quote']['USD']['price'], 2))))


    #st.dataframe(sum_amount)
    st.write("Transaction History")
    st.dataframe(sub)

def getSlug(tick):
    slug = prices['data'][tick]['slug']
    return slug

def getTotalAmount(df):
    sum_amount = df['Amount']
    total = 0
    for i in sum_amount:
        total += float(str(i).replace(',',''))
    return total

def getAllMetrics(tick):
    for i in prices['data'][tick]['quote']['USD']:
        if i != 'last_updated':
            st.write(i.replace("_", " ").capitalize() + ": " + str("{:,}".format(round(prices['data'][tick]['quote']['USD'][i], 2))))

def displayMetric(col, tick, slug):
    col.metric(slug.capitalize()  + '-' + tick, "$"+getMetric(tick, 'price'), getMetric(tick, 'percent_change_24h')+"%")
    with col.expander(str(tick) + " Metrics"):
        getAllMetrics(tick)

    #st.write(slug)
    #with col.expander(str(tick) + " Chart"):


def getMetric(tick, metric):
    metric = "{:,}".format(round(prices['data'][tick]['quote']['USD'][metric], 2))
    return str(metric)

def showResources():
    st.subheader("What is Blockchain?")
    st.video('https://www.youtube.com/watch?v=SSo_EIwHSd4')
    st.subheader("Proof-of-Work")
    st.video('https://www.youtube.com/watch?v=3EUAcxhuoU4')
    st.subheader('Proof-of-Stake')
    st.video('https://www.youtube.com/watch?v=M3EFi_POhps')


if __name__ == "__main__":
    main()
