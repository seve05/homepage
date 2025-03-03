import yfinance as yf
import pandas as pd
import requests
import json
from tabulate import tabulate
from datetime import datetime
import matplotlib.pyplot as plt

def get_company_ticker(company_input):
    """Get company ticker from either company name or ticker symbol"""
    try:
        df = pd.read_json('company_tickers.json').T
    except FileNotFoundError:
        url = "https://www.sec.gov/files/company_tickers.json"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        df = pd.read_json(response.text).T
        df.to_json('company_tickers.json')
    
    # Check if input is a ticker
    company_input = company_input.upper()  # Tickers are usually uppercase
    ticker_match = df[df['ticker'] == company_input]
    if not ticker_match.empty:
        return company_input
    
    # If not a ticker, search by company name
    df['title'] = df['title'].str.lower()
    company_input = company_input.lower()
    
    matches = df[df['title'].str.contains(company_input, case=False, na=False)]
    if len(matches) == 0:
        raise ValueError(f"No company found matching '{company_input}'")
    elif len(matches) > 1:
        print("Multiple matches found:")
        for _, row in matches.iterrows():
            print(f"- {row['title']} (Ticker: {row['ticker']})")
        raise ValueError("Please provide a more specific company name or use the ticker symbol")
    
    return matches.iloc[0]['ticker']

def get_financial_metrics(ticker):
    """Get current and historical financial metrics using Yahoo Finance"""
    company = yf.Ticker(ticker)
    
    # Get historical stock data
    stock_history = company.history(period="max")

    
    # Get financial statements
    income_stmt = company.financials
    balance_sheet = company.balance_sheet
    # Create metrics dictionary
    metrics = {
        'Date': [],
        'Stock Price': [],
        'Shares Outstanding': [],
        'Market Cap': [],
        'Revenue': [],
        'Revenue Growth': [],
        'Gross Profit': [],
        'Total Debt': [],
        'Cash': []
    }
    
    previous_revenue = None
    
    def get_price_for_date(history, target_date):
        """Try to get price for date or next available trading day"""
        try:
            price = history.loc[target_date]['Close']
            return price
        except KeyError:
            # Try next 5 business days
            for i in range(1, 6):
                try:
                    next_date = pd.to_datetime(target_date) + pd.Timedelta(days=i)
                    price = history.loc[next_date.strftime('%Y-%m-%d')]['Close']
                    return price
                except KeyError:
                    continue
        return None
    
    # Process quarterly financial data
    for date in income_stmt.columns:
        metrics['Date'].append(date.strftime('%Y-%m-%d'))
        
        # Get stock price for that date or next available trading day
        price = get_price_for_date(stock_history, date.strftime('%Y-%m-%d'))
        metrics['Stock Price'].append(price)
        
        # Get shares outstanding
        try:
            shares = company.info['sharesOutstanding']
        except:
            shares = None
        metrics['Shares Outstanding'].append(shares)
        
        # Calculate market cap
        if price and shares:
            market_cap = price * shares
        else:
            market_cap = None
        metrics['Market Cap'].append(market_cap)
        
        # Get revenue and calculate growth
        current_revenue = income_stmt.loc['Total Revenue'][date] if 'Total Revenue' in income_stmt.index else None
        metrics['Revenue'].append(current_revenue)
        
        # Calculate revenue growth and mark increases
        if previous_revenue is not None and current_revenue is not None:
            if previous_revenue != 0:
                growth = ((current_revenue - previous_revenue) / previous_revenue) * 100
            else:
                growth = None
                
            # Mark growth if current revenue is higher, regardless of percentage
            if current_revenue > previous_revenue:
                metrics['Revenue Growth'].append(True)
            else:
                metrics['Revenue Growth'].append(False)
        else:
            metrics['Revenue Growth'].append(None)
        
        previous_revenue = current_revenue
        
        # Get other metrics
        metrics['Gross Profit'].append(income_stmt.loc['Gross Profit'][date] if 'Gross Profit' in income_stmt.index else None)
        
        # Get debt and cash from balance sheet
        if date in balance_sheet.columns:
            metrics['Total Debt'].append(balance_sheet.loc['Total Debt'][date] if 'Total Debt' in balance_sheet.index else None)
            metrics['Cash'].append(balance_sheet.loc['Cash And Cash Equivalents'][date] 
                                 if 'Cash And Cash Equivalents' in balance_sheet.index else None)
        else:
            metrics['Total Debt'].append(None)
            metrics['Cash'].append(None)
    
    return pd.DataFrame(metrics)

def format_value(value, highlight=False):
    """Format large numbers for better readability with optional highlighting"""
    if pd.isna(value) or value is None:
        return 'N/A'
    elif isinstance(value, (int, float)):
        formatted = ''
        if abs(value) >= 1e9:
            formatted = f'${value/1e9:.2f}B'
        elif abs(value) >= 1e6:
            formatted = f'${value/1e6:.2f}M'
        elif abs(value) >= 1e3:
            formatted = f'${value/1e3:.2f}K'
        else:
            formatted = f'${value:.2f}'
        
        if highlight:
            return f'\033[92m{formatted}\033[0m'  # Green color for growth
        return formatted
    return str(value)

def plot_metrics(df, company_name):
    """Create plots for financial metrics over time"""
    fig, axes = plt.subplots(4, 2, figsize=(15, 20))
    fig.suptitle(f'Financial Metrics Over Time - {company_name}', fontsize=16)
    
    metrics = list(df.columns[1:])  # Skip 'Date' column
    for i, metric in enumerate(metrics):
        row = i // 2
        col = i % 2
        
        # Convert string dates to datetime
        dates = pd.to_datetime(df['Date'])
        values = pd.to_numeric(df[metric], errors='coerce')
        
        axes[row, col].plot(dates, values, marker='o')
        axes[row, col].set_title(metric)
        axes[row, col].set_xlabel('Date')
        axes[row, col].set_ylabel('Value ($)')
        axes[row, col].tick_params(axis='x', rotation=45)
        
        # Format y-axis labels
        axes[row, col].yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: format_value(x))
        )
    
    plt.tight_layout()
    plt.savefig(f'{company_name}_metrics.png')
    print(f"Plots saved as {company_name}_metrics.png")

def analyze_company_financials(company_input):
    """Main function to analyze and display company financials"""
    try:
        # Get company ticker
        ticker = get_company_ticker(company_input)
        
        # Get company name for display if input was a ticker
        try:
            df = pd.read_json('company_tickers.json').T
            company_name = df[df['ticker'] == ticker.upper()].iloc[0]['title']
        except:
            company_name = company_input
            
        print(f"\nAnalyzing financials for {company_name} ({ticker})")
        
        # Get financial metrics
        df = get_financial_metrics(ticker)
        
        # Format values for display with highlighting
        display_df = df.copy()
        for column in display_df.columns:
            if column == 'Revenue':
                # Highlight based on Revenue Growth being True/False rather than > 0
                display_df[column] = [format_value(val, growth if growth is not None else False) 
                                    for val, growth in zip(display_df[column], display_df['Revenue Growth'])]
            elif column != 'Date' and column != 'Revenue Growth':
                display_df[column] = display_df[column].apply(lambda x: format_value(x))
        
        display_df = display_df.drop('Revenue Growth', axis=1)
        
        print("\nFinancial Metrics Over Time:")
        print("(Green highlights indicate quarters with revenue growth)")
        print(tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))
        
        plot_metrics_with_growth(df, company_name)
        
    except Exception as e:
        print(f"Error: {e}")

def plot_metrics_with_growth(df, company_name):
    """Create plots for financial metrics over time with highlighted growth periods"""
    plt.rcParams['figure.figsize'] = [15, 20]
    plt.rcParams['figure.autolayout'] = True
    
    fig, axes = plt.subplots(4, 2)
    fig.suptitle(f'Financial Metrics Over Time - {company_name}', fontsize=16)
    
    metrics = [col for col in df.columns[1:] if col != 'Revenue Growth']  # Skip Date and Revenue Growth
    for i, metric in enumerate(metrics):
        row = i // 2
        col = i % 2
        
        # Convert string dates to datetime
        dates = pd.to_datetime(df['Date'])
        values = pd.to_numeric(df[metric], errors='coerce')
        
        ax = axes[row, col]
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.plot(dates, values, marker='o', color='navy', linewidth=2, markersize=6)
        
        # If this is the revenue plot, highlight growth periods
        if metric == 'Revenue':
            # Use boolean growth indicators instead of percentage comparison
            growth_periods = df['Revenue Growth'] == True
            growth_dates = dates[growth_periods]
            growth_values = values[growth_periods]
            ax.scatter(growth_dates, growth_values, color='green', s=100, label='Higher than Previous', zorder=5)
            ax.legend()
        
        ax.set_title(metric, pad=10, fontsize=12)
        ax.set_xlabel('Date', fontsize=10)
        ax.set_ylabel('Value ($)', fontsize=10)
        ax.tick_params(axis='x', rotation=45)
        
        # Format y-axis labels
        ax.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, p: format_value(x))
        )
    
    plt.tight_layout()
    plt.savefig(f'{company_name}_metrics.png', bbox_inches='tight', dpi=300)
    print(f"Plots saved as {company_name}_metrics.png")

if __name__ == "__main__":
    print("Enter company name or ticker symbol (e.g., 'Apple' or 'AAPL'):")
    company_input = input("> ")
    analyze_company_financials(company_input) 