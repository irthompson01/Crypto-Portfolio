##### IMPORTS #####
import streamlit as st
import pandas as pd
from requests import Request, Session
import json
import pprint

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
        "symbol": 'BTC,ETH,ADA,XMR,ERG,LINK,VET,ALGO,LTC,HBAR,BNB,SOL,XRP,DOT,MATIC,CRO,FIL,ONE,LRC,LOOKS',
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
    col1, col2, col3, col4 = st.columns(4)
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
    for tick in cryptos:
        col1, col2 = st.columns(2)
        sub_tick = sub[sub['Symbol'] == tick]
        total = getTotalAmount(sub_tick)
        col1.metric(tick, "{:,}".format(total))
        col2.metric("Value (USD)", "$"+ str("{:,}".format(round(total*prices['data'][tick]['quote']['USD']['price'], 2))))


    #st.dataframe(sum_amount)
    st.write("Transaction History")
    st.dataframe(sub)

def getSlug(tick):
    slug = prices['data'][tick]['slug'].capitalize()
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
            st.write(i.replace("_", " ").capitalize() + ": " + str(round(prices['data'][tick]['quote']['USD'][i], 2)))

def displayMetric(col, tick, slug):
    col.metric(slug  + '-' + tick, "$"+getMetric(tick, 'price'), getMetric(tick, 'percent_change_24h')+"%")
    with col.expander(str(tick) + " Metrics"):
        getAllMetrics(tick)

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
