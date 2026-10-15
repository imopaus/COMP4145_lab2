import json

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from trading_strategy import build_dashboard_data


@st.cache_data
def load_dashboard_data():
    try:
        with open('dashboard_data.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return build_dashboard_data()


def render_price_chart(data):
    symbol = data.get('symbol', 'MSFT')
    price_history = pd.DataFrame(data.get('price_history', []))
    trades = pd.DataFrame(data.get('trades', []))

    if price_history.empty:
        st.warning('No price history available.')
        return

    price_history['Date'] = pd.to_datetime(price_history['Date'], utc=True).dt.tz_localize(None)

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(price_history['Date'], price_history['Close'], label='Close Price', color='#2563eb', linewidth=2)
    ax.plot(price_history['Date'], price_history['MA50'], label='MA 50', color='#f59e0b', linewidth=2)
    ax.plot(price_history['Date'], price_history['MA200'], label='MA 200', color='#10b981', linewidth=2)

    if not trades.empty:
        buy_dates = pd.to_datetime(trades['BuyDate'], utc=True).dt.tz_localize(None)
        sell_dates = pd.to_datetime(trades['SellDate'], utc=True).dt.tz_localize(None)
        ax.scatter(buy_dates, trades['BuyPrice'], color='green', s=80, label='Buy Signal', zorder=5)
        ax.scatter(sell_dates, trades['SellPrice'], color='red', s=80, label='Sell Signal', zorder=5)

    ax.set_title(f'{symbol} Price and Moving Averages')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price (USD)')
    ax.legend()
    fig.autofmt_xdate()
    st.pyplot(fig)


def render_trade_statistics(data):
    summary = data.get('summary', {})

    st.subheader('Overall Trade Statistics')
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric('Total Trades', summary.get('total_trades', 0))
    c2.metric('Winning Trades', summary.get('win_trades', 0))
    c3.metric('Losing Trades', summary.get('loss_trades', 0))
    c4.metric('Win Rate', f"{summary.get('win_rate', 0):.2f}%")
    c5.metric('Average Profit', f"{summary.get('avg_profit', 0):.2f}%")
    c6.metric('Avg Holding', f"{summary.get('avg_holding', 0):.1f} days")

    with st.expander('More summary details'):
        st.json(summary)


def render_detailed_trades(data):
    trades = pd.DataFrame(data.get('trades', []))

    if trades.empty:
        st.warning('No trades recorded.')
        return

    display = trades.copy()
    display['BuyDate'] = pd.to_datetime(display['BuyDate'], utc=True).dt.tz_localize(None).dt.strftime('%Y-%m-%d')
    display['SellDate'] = pd.to_datetime(display['SellDate'], utc=True).dt.tz_localize(None).dt.strftime('%Y-%m-%d')
    display['BuyPrice'] = display['BuyPrice'].map(lambda value: f"{float(value):.2f}")
    display['SellPrice'] = display['SellPrice'].map(lambda value: f"{float(value):.2f}")
    display['ProfitPct'] = display['ProfitPct'].map(lambda value: f"{float(value):.2f}%")

    st.dataframe(display, use_container_width=True, hide_index=True)


def main():
    st.set_page_config(page_title='Trading Strategy Dashboard', layout='wide')
    st.title('MSFT Golden Cross Strategy Dashboard')

    data = load_dashboard_data()
    tab1, tab2, tab3 = st.tabs(['Price Chart', 'Trade Statistics', 'Detailed Trades'])

    with tab1:
        render_price_chart(data)

    with tab2:
        render_trade_statistics(data)

    with tab3:
        render_detailed_trades(data)


if __name__ == '__main__':
    main()
