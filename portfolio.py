##### IMPORTS #####
import streamlit as st
import pandas as pd
from requests import Request, Session
import json
import pycoingecko
from pycoingecko import CoinGeckoAPI
from datetime import datetime
import altair as alt
#import matplotlib.pyplot as plt

##### Set Page Config #####
st.set_page_config(
 page_title="Crypto Portfolio",
 page_icon="🧊",
 layout="wide"
)

# https://github.com/tapaco/marametrics

##### Load Transaction Data #####
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

@st.cache(allow_output_mutation=True)
def load_CG_data():
    cg = CoinGeckoAPI()

    data = pd.DataFrame(cg.get_coins_markets(vs_currency = 'usd', order='market_cap_desc', price_change_percentage='1h,24h,7d,14d,30d,200d,1y'))
    ergo_data = pd.DataFrame(cg.get_coins_markets(ids='ergo',vs_currency = 'usd', order='market_cap_desc', price_change_percentage='1h,24h,7d,14d,30d,200d,1y', limit=10))

    data = pd.concat([data, ergo_data])

    data['symbol'] = data['symbol'].str.upper()
    data = data.reset_index()
    return data

prices = load_CMC_data()
df = load_transaction_data()
data = load_CG_data()


def main():
    ##  9285011099Seismic# ##
    ##### SIDEBAR #####

    st.sidebar.title("Select a Portfolio:")
    portfolio = st.sidebar.selectbox(
     '',
     ('Home','Ross & Amy', 'Casey y Luca', 'Smidget', 'Resources'))

    if portfolio == 'Home':
         #priceData()
         priceDataCG()

    elif portfolio == 'Ross & Amy':
        showData("RA", "2,500")

    elif portfolio == 'Casey y Luca':
        showData("CL", "3,000")

    elif portfolio == 'Smidget':
        showData("BT", "100")

    elif portfolio == 'Resources':
        showResources()


def priceDataCG():
    ##### Custom Style #####
    with open('./metric/style.css') as f:
        st.markdown(f'<style>{f.read()}<style>', unsafe_allow_html=True)

    st.title("Current Crypto Prices")
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]# col3, col4]
    days = st.sidebar.selectbox("Chart Interval (Days)", (1, 3, 7, 14, 30))
    symbols = ['BTC','ETH','ADA','XMR','ERG','LINK','VET','ALGO','LTC','HBAR','SOL','XRP','BNB','DOT','CRO','MATIC','FIL','ONE','LRC','LOOKS', 'XLM', 'ICP']
    #data_sub = data[data['symbol'].str.upper() in symbols]
    boolean_series = data['symbol'].isin(symbols)
    filtered_data = data[boolean_series]
    count = 0
    for index, row in filtered_data.iterrows():
        adj = count%len(cols)
        coin_data = row
        count += 1
        displayCGMetric(cols[adj], coin_data['symbol'].upper(), coin_data['name'], coin_data, days)

    f.close()

def showData(owner, investment):
    '''
    Candle Stick Chart:         https://altair-viz.github.io/gallery/candlestick_chart.html
    Area Chart With Gradient:   https://altair-viz.github.io/gallery/area_chart_gradient.html
    '''
    ##### Custom Style #####
    with open('./showData/style.css') as f:
        st.markdown(f'<style>{f.read()}<style>', unsafe_allow_html=True)

    port_dict = {"RA": "Ross & Amy", "CL": "Casey y Luca", "BT": "Smidget"}
    st.title(port_dict[owner] + "'s Crypto Portfolio")
    sub = df[df['Owner'] == owner]

    ##### Total Invested/Current Value #####
    st.header("Investment: $" + investment)

    ##### Breakdown by Coin #####
    cryptos = sub["Symbol"].unique()
    col1, col2, col3 = st.columns(3)
    col1.markdown("**Asset**")
    col2.markdown("**Price**")
    col3.markdown("**Value (USD)**")

    grand_total = 0
    for tick in cryptos:
        data_sub = data[data['symbol'] == tick]
        sub_tick = sub[sub['Symbol'] == tick]
        total = getTotalAmount(sub_tick)

        total_usd = total*data_sub['current_price'].values[0]
        grand_total += total_usd
        col1.metric(tick, "{:,}".format(total))
        col2.metric(tick + "-USD", "$"+str(data_sub['current_price'].values[0]))
        col3.metric("Value (USD)", "$"+ str("{:,}".format(round(total_usd, 2))))


    #st.dataframe(sum_amount)
    st.header("Total Value (USD): $" + str("{:,}".format(round(grand_total,2))))
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

def displayCGMetric(col, tick, slug, coin_data, days=7):

    with st.container():
        new_col1, new_col2 = st.columns(2)
        col.image(coin_data['image'], width = 50)
        col.metric(str(coin_data['market_cap_rank']) + '. ' + slug.capitalize()  + '-' + tick, "$"+str("{:,}".format(coin_data['current_price'])), str("{:,}".format(round(coin_data['price_change_percentage_24h_in_currency'], 2),',')+"%"))

        with col.expander(str(tick) + " Chart(" + str(days) + "d)"):
            st.altair_chart(getCGChart(coin_data['id'], days))

        with col.expander(str(tick) + " Metrics"):
            getAllCGMetrics(coin_data)

def getAllCGMetrics(coin_data):
    bad_keys = ['index', 'id', 'symbol', 'market_cap_rank', 'name', 'image', 'ath_date', 'atl_date', 'roi', 'last_updated', 'fully_diluted_valuation']
    for key in coin_data.keys():
        if key not in bad_keys:
            try:
                st.write(key.replace("_", " ").capitalize() + ": " + str("{:,}".format(round(coin_data[key],2))))
            except TypeError:
                pass
    #st.write(slug)
    # with col.expander(str(tick) + " Chart"):
    #     getCGChart(slug)

@st.cache(allow_output_mutation=True)
def getCGChart(id, days=7):
    cg = CoinGeckoAPI()
    chart_data = pd.DataFrame(cg.get_coin_market_chart_by_id(id, 'usd', days))

    chart_data['index'] = range(0, len(chart_data))

    chart_data['Timestamp'] = [chart_data['prices'][i][0] for i in range(0,len(chart_data))]
    chart_data['Date'] = pd.to_datetime(chart_data['Timestamp'])

    chart_data['Price'] = [chart_data['prices'][i][1] for i in range(0,len(chart_data))]
    chart_data['Price Format'] = [ "$"+str("{:,}".format(round(chart_data['Price'][i], 2))) for i in range(0,len(chart_data))]
    chart_data['Market Cap'] = [chart_data['market_caps'][i][1] for i in range(0,len(chart_data))]
    chart_data['Volume'] = [chart_data['total_volumes'][i][1] for i in range(0,len(chart_data))]

    if chart_data['Price'][0] < chart_data['Price'][len(chart_data)-1]:
        line_color = 'darkgreen'
    else:
        line_color = 'darkred'

    chart = alt.Chart(chart_data).configure(background='black').mark_area(
            line={'color':line_color},
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='white', offset=0),
                       alt.GradientStop(color=line_color, offset=1)],
                x1=1,
                x2=1,
                y1=1,
                y2=0
            )
        ).encode(
            alt.X('index:Q', axis = alt.Axis(labels=False,tickMinStep=10, title='', gridColor='darkgrey', gridOpacity=0.6)),
            alt.Y('Price:Q', axis = alt.Axis(format="$", tickCount=4, gridColor='darkgrey', gridOpacity=0.6, labelColor='white'),
                  scale=alt.Scale(domain=[chart_data['Price'].min(), chart_data['Price'].max()])),
            tooltip = alt.Tooltip('Price Format:N', title='Price')
            ).properties(width=300, height=200).configure_view(strokeOpacity=0)

    return chart

def getMetric(tick, metric):
    metric = "{:,}".format(round(prices['data'][tick]['quote']['USD'][metric], 2))
    return str(metric)

def showResources():
    col1, col2 = st.columns(2)
    col1.subheader("What is Blockchain?")
    col1.video('https://www.youtube.com/watch?v=SSo_EIwHSd4')
    col2.subheader("Proof-of-Work")
    col2.video('https://www.youtube.com/watch?v=3EUAcxhuoU4')
    col1.subheader('Proof-of-Stake')
    col1.video('https://www.youtube.com/watch?v=M3EFi_POhps')
    col2.subheader('What is Cardano?')
    col2.video('https://www.youtube.com/watch?v=Do8rHvr65ZA')


def priceData():
    ##### Custom Style #####
    with open('./metric/style.css') as f:
        st.markdown(f'<style>{f.read()}<style>', unsafe_allow_html=True)

    st.title("Current Crypto Prices")
    col1, col2, col3, col4 = st.columns([1,1,1, 1])
    cols = [col1, col2, col3, col4]

    ticks = [tick for tick in prices['data']]

    for t in range(len(ticks)):
        adj = t%len(cols)
        displayMetric(cols[adj], ticks[t], getSlug(ticks[t]))

    f.close()

def displayMetric(col, tick, slug):

    with st.container():
        col.metric(slug.capitalize()  + '-' + tick, "$"+getMetric(tick, 'price'), getMetric(tick, 'percent_change_24h')+"%")
        with col.expander(str(tick) + " Metrics"):
            getAllMetrics(tick)

def getAllMetrics(tick):
    for i in prices['data'][tick]['quote']['USD']:
        if i != 'last_updated':
            st.write(i.replace("_", " ").capitalize() + ": " + str("{:,}".format(round(prices['data'][tick]['quote']['USD'][i], 2))))

if __name__ == "__main__":
    main()
