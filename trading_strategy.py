import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

# Download 5 years of MSFT data
def get_stock_data(ticker, period="5y"):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data

# Calculate moving averages
def calculate_moving_averages(data):
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['MA200'] = data['Close'].rolling(window=200).mean()
    return data

# Identify golden cross (buy signals)
def identify_golden_cross(data):
    data['Signal'] = 0  # Initialize signal column with 0
    # Golden Cross occurs when MA50 crosses above MA200
    data['GoldenCross'] = (data['MA50'] > data['MA200']) & (data['MA50'].shift(1) <= data['MA200'].shift(1))
    return data

# Implement trading strategy
def implement_strategy(data):
    positions = []

    # Need at least 200 days to calculate the 200-day MA
    data = data.iloc[200:].copy()

    buy_dates = data[data['GoldenCross'] == True].index.tolist()

    for buy_date in buy_dates:
        # Get buy price
        buy_price = data.loc[buy_date, 'Close']

        # Calculate target sell price (15% profit)
        target_price = buy_price * 1.15

        # Set maximum holding period
        max_sell_date = buy_date + pd.Timedelta(days=60)

        # Get data slice for potential sell period
        sell_period = data.loc[buy_date:max_sell_date].copy()

        # Check if target price is reached during the period
        target_reached = sell_period[sell_period['Close'] >= target_price]

        if not target_reached.empty:
            # Sell at first date target is reached
            sell_date = target_reached.index[0]
            sell_price = target_reached.loc[sell_date, 'Close']
            sell_reason = "Target reached"
        else:
            # Sell at end of maximum holding period
            sell_date_candidates = sell_period.index.tolist()
            if sell_date_candidates:
                sell_date = sell_date_candidates[-1]
                sell_price = data.loc[sell_date, 'Close']
                sell_reason = "Max holding period"
            else:
                # Skip if no valid sell date (should not happen in practice)
                continue

        # Calculate holding period in calendar days
        holding_days = (sell_date - buy_date).days

        # Calculate profit
        profit_pct = (sell_price / buy_price - 1) * 100

        positions.append({
            'BuyDate': buy_date,
            'BuyPrice': buy_price,
            'SellDate': sell_date,
            'SellPrice': sell_price,
            'HoldingDays': holding_days,
            'ProfitPct': profit_pct,
            'SellReason': sell_reason
        })

    return pd.DataFrame(positions)

# Analyze the results
def summarize_positions(positions):
    if positions.empty:
        return {
            'total_trades': 0,
            'win_trades': 0,
            'loss_trades': 0,
            'win_rate': 0.0,
            'avg_profit': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'avg_holding': 0.0,
            'target_reached': 0,
            'max_period': 0,
        }

    total_trades = len(positions)
    win_trades = len(positions[positions['ProfitPct'] > 0])
    loss_trades = total_trades - win_trades
    win_rate = win_trades / total_trades * 100 if total_trades > 0 else 0

    avg_profit = positions['ProfitPct'].mean()
    avg_win = positions[positions['ProfitPct'] > 0]['ProfitPct'].mean() if win_trades > 0 else 0
    avg_loss = positions[positions['ProfitPct'] <= 0]['ProfitPct'].mean() if loss_trades > 0 else 0
    avg_holding = positions['HoldingDays'].mean()

    target_reached = len(positions[positions['SellReason'] == 'Target reached'])
    max_period = len(positions[positions['SellReason'] == 'Max holding period'])

    return {
        'total_trades': total_trades,
        'win_trades': win_trades,
        'loss_trades': loss_trades,
        'win_rate': win_rate,
        'avg_profit': avg_profit,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'avg_holding': avg_holding,
        'target_reached': target_reached,
        'max_period': max_period,
    }


def analyze_results(positions):
    if positions.empty:
        print("No trading signals detected")
        return positions

    summary = summarize_positions(positions)
    total_trades = summary['total_trades']
    win_trades = summary['win_trades']
    win_rate = summary['win_rate']
    avg_profit = summary['avg_profit']

    print("\n===== Trading Strategy Results (Golden Cross)=====")
    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {win_trades} ({win_rate:.2f}%)")
    print(f"Losing Trades: {summary['loss_trades']}")
    print(f"Average Profit: {avg_profit:.2f}%")

    return positions


def build_dashboard_data(symbol="MSFT"):
    data = get_stock_data(symbol)
    data = calculate_moving_averages(data)
    data = identify_golden_cross(data)
    positions = implement_strategy(data)
    summary = summarize_positions(positions)

    price_history = data.reset_index().rename(columns={'index': 'Date'})
    price_history = price_history[['Date', 'Close', 'MA50', 'MA200']].copy()
    price_history['Date'] = price_history['Date'].dt.strftime('%Y-%m-%d')

    sanitized_price_history = []
    for row in price_history.to_dict(orient='records'):
        sanitized_price_history.append({
            'Date': row['Date'],
            'Close': None if pd.isna(row['Close']) else float(row['Close']),
            'MA50': None if pd.isna(row['MA50']) else float(row['MA50']),
            'MA200': None if pd.isna(row['MA200']) else float(row['MA200']),
        })

    trades = positions.copy()
    if not trades.empty:
        trades = trades[['BuyDate', 'BuyPrice', 'SellDate', 'SellPrice', 'HoldingDays', 'ProfitPct', 'SellReason']].copy()
        trades['BuyDate'] = trades['BuyDate'].dt.strftime('%Y-%m-%d')
        trades['SellDate'] = trades['SellDate'].dt.strftime('%Y-%m-%d')
        sanitized_trades = []
        for row in trades.to_dict(orient='records'):
            sanitized_trades.append({
                'BuyDate': row['BuyDate'],
                'BuyPrice': None if pd.isna(row['BuyPrice']) else float(row['BuyPrice']),
                'SellDate': row['SellDate'],
                'SellPrice': None if pd.isna(row['SellPrice']) else float(row['SellPrice']),
                'HoldingDays': None if pd.isna(row['HoldingDays']) else int(row['HoldingDays']),
                'ProfitPct': None if pd.isna(row['ProfitPct']) else float(row['ProfitPct']),
                'SellReason': row['SellReason'],
            })
    else:
        sanitized_trades = []

    return {
        'symbol': symbol,
        'summary': summary,
        'price_history': sanitized_price_history,
        'trades': sanitized_trades,
    }


# Main function
def main():
    # Get stock data
    data = get_stock_data("MSFT")

    # Calculate moving averages
    data = calculate_moving_averages(data)

    # Identify golden cross
    data = identify_golden_cross(data)

    # Implement strategy
    positions = implement_strategy(data)

    # Analyze results
    analyze_results(positions)

    print("\nDetailed Trades:")
    if not positions.empty:
        print(positions.to_string())

    # Return the detailed positions dataframe
    return positions


if __name__ == "__main__":
    main()