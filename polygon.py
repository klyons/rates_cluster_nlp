import requests
import pandas as pd
import pdb
import time
from datetime import date, datetime, timedelta

#https://polygon.io/docs/stocks/getting-started

polygon_api_key = "JlgRBshWYNKUeDMpSLOjvk7slj1GCpBh"  #JlgRBshWYNKUeDMpSLOjvk7slj1GCpBh
polygon_rest_baseurl = "https://api.polygon.io/v2/"  #maybe trie v3as well

limit = 100000

def get_tickers():
    request_url = "https://api.polygon.io/v3/reference/tickers?active=true&limit=1000&apiKey={0}".format(polygon_api_key)
    data = requests.get(request_url).json()
    if data['status'] == 'OK':
        df = pd.DataFrame(data['results'])
        next_d = data['next_url']
        while(next_d != {}):
            next_d = "%s&apiKey=%s"%(next_d, polygon_api_key)
            data = requests.get(next_d).json()
            if data['status'] == 'OK':
                tdf = pd.DataFrame(data['results'])
                df = pd.concat([df, tdf])
            if "next_url" in data.keys():
                next_d = data['next_url']
            else:
                break
        df.to_csv("tickers.csv")
        print("Dumped all tickers to tickers.csv")
    else:
        print("No tickers downloaded")

def pull_data(symbol, start_time, multiplier, timespan):
    """
    date is a python date format
    symbol is of the form XXXUSD
    """

    # newest data at the bottom
    sort = "asc"

    if not start_time:
        start_time = datetime.today() - timedelta(days=365*5) # polygon has a 5 year limitation
        start_time =  datetime.date(start_time)
    end_time = today = date.today()

    ## this means the symbol is an index and requires a differant API call

    request_url2 = f"{polygon_rest_baseurl}aggs/ticker/{symbol}/range/{multiplier}/" +\
            f"{timespan}/{start_time}/{end_time}?adjusted=true&sort={sort}&" + \
            f"limit={limit}&apiKey={polygon_api_key}"

    if symbol[:2] == 'I:' or symbol[:2] == 'i:':  ## add string for index or symbol to allow for adjustment
        request_url = "{0}aggs/ticker/{1}/range/{2}/{3}/{4}/{5}?adjusted=true&sort={6}&limit={7}&apiKey={8}".format(polygon_rest_baseurl, symbol, multiplier, timespan, start_time, end_time, sort, limit, polygon_api_key)

    else:
        request_url = "{0}aggs/ticker/{1}/range/{2}/{3}/{4}/{5}?adjusted=true&sort={6}&limit={7}&apiKey={8}".format(polygon_rest_baseurl, symbol, multiplier, timespan, start_time, end_time, sort, limit, polygon_api_key)


    # If there is a connection error, the following try and catch should prevent Python from
    # exiting. Instead, return no data and let the caller try again
    try:
        data = requests.get(request_url).json()
    except:
        print("Connection Error, try again")
        return None 

    if "results" in data:
        return data["results"]
    else:
        return None


def pull_dividend_data(symbol, start_time, multiplier, timespan):
    """
    date is a python date format
    symbol is of the form XXXUSD
    """

    # newest data at the bottom
    sort = "asc"

    if not start_time:
        start_time = datetime.today() - timedelta(days=365*5) # polygon has a 5 year limitation
        start_time =  datetime.date(start_time)
    end_time = today = date.today()

    ## this means the symbol is an index and requires a differant API call
    url = f'https://api.polygon.io/v3/reference/dividends/{symbol}?from={start_date}&to={end_date}&apiKey={polygon_api_key}'


    request_url2 = f"{polygon_rest_baseurl}aggs/ticker/{symbol}/range/{multiplier}/" +\
            f"{timespan}/{start_time}/{end_time}?adjusted=true&sort={sort}&" + \
            f"limit={limit}&apiKey={polygon_api_key}"

    if symbol[:2] == 'I:' or symbol[:2] == 'i:':  ## add string for index or symbol to allow for adjustment
        request_url = "{0}aggs/ticker/{1}/range/{2}/{3}/{4}/{5}?adjusted=true&sort={6}&limit={7}&apiKey={8}".format(polygon_rest_baseurl, symbol, multiplier, timespan, start_time, end_time, sort, limit, polygon_api_key)

    else:
        request_url = "{0}aggs/ticker/{1}/range/{2}/{3}/{4}/{5}?adjusted=true&sort={6}&limit={7}&apiKey={8}".format(polygon_rest_baseurl, symbol, multiplier, timespan, start_time, end_time, sort, limit, polygon_api_key)


    # If there is a connection error, the following try and catch should prevent Python from
    # exiting. Instead, return no data and let the caller try again
    try:
        data = requests.get(request_url).json()
    except:
        print("Connection Error, try again")
        return None 

    if "results" in data:
        return data["results"]
    else:
        return None


def get_data(start_day, symbol, multiplier=1, timespan='hour', silent=False):
    # start_day must be of datetime.date() format
    # symbol must be uppercase
    bars = []
    mdf = pd.DataFrame()
    interval = timespan
    symbol = symbol.upper()
    while(1):
        bars = pull_data(symbol, start_day, multiplier, interval)
        if not bars:
            if not silent:
                print("No data available for %s in this range %s "%(symbol, start_day))
            break
        df = pd.DataFrame(bars)
        df["date_time"] = pd.to_datetime(df["t"], unit = "ms")
        if ':' in symbol:
            df = df[["date_time","o","h","c","l"]]
            df.columns = ["date_time","open","high","low","close"]
        if not ':' in symbol:    
            df =  df[["date_time","o","h","c","l","v","vw"]]
            df.columns = ["date_time","open","high","low","close","volume","vwap"]
        df = df.sort_values("date_time")
        if not silent and not df.empty:
            print("Downloaded %s: %s - %s"%(symbol, df['date_time'].iloc[0], df['date_time'].iloc[-1]))

        # When a symbol does not have anymore data, check for the start and end date here
        # and if they are the same, then exit
        if df['date_time'].iloc[0] == df['date_time'].iloc[-1]:
            mdf = df
            break

        df.set_index(['date_time'], inplace=True)
        # Make sure to get all of the data to this date
        td = pd.to_datetime(date.today()) - df.index[-1]
        if td.days > 1 or td.days == -1:
            start_day = bars[-1]['t']
            if interval == 'hour':
                start_day = start_day + 60*60*1000*multiplier
            elif interval == 'minute':
                start_day = start_day + 60*1000*multiplier
            elif interval == 'day':
                start_day = start_day + 24*60*60*1000
            else:
                print("error, please pass in correct string for time granularity")
            if mdf.empty:
                mdf = df
            else:
                mdf = pd.concat([mdf, df], axis=0)
        else:
            if mdf.empty:
                mdf = df
                break
            else:
                mdf = pd.concat([mdf, df], axis=0)
                break
    return mdf

if __name__ == '__main__':
    get_tickers()