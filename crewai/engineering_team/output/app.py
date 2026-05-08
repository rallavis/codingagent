import gradio as gr
from accounts import Account, get_share_price

account = None

def create_account(initial_deposit):
    global account
    try:
        account = Account(initial_deposit)
        return f"Account created with initial deposit ${initial_deposit:.2f}"
    except ValueError as e:
        return f"Error: {e}"

def deposit(amount):
    global account
    if account is None:
        return "Please create an account first."
    try:
        account.deposit(amount)
        return f"Deposited ${amount:.2f}. Balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {e}"

def withdraw(amount):
    global account
    if account is None:
        return "Please create an account first."
    try:
        account.withdraw(amount)
        return f"Withdrew ${amount:.2f}. Balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {e}"

def buy_shares(symbol, quantity):
    global account
    if account is None:
        return "Please create an account first."
    try:
        cost = account.buy_shares(symbol, quantity)
        return f"Bought {quantity} shares of {symbol} for ${cost:.2f}. Balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {e}"

def sell_shares(symbol, quantity):
    global account
    if account is None:
        return "Please create an account first."
    try:
        proceeds = account.sell_shares(symbol, quantity)
        return f"Sold {quantity} shares of {symbol} for ${proceeds:.2f}. Balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {e}"

def get_portfolio_value():
    global account
    if account is None:
        return "Please create an account first."
    total_value = account.get_total_value()
    profit_loss = account.get_profit_loss()
    return f"Portfolio Value: ${total_value:.2f}\nProfit/Loss: ${profit_loss:.2f}"

def get_holdings():
    global account
    if account is None:
        return "Please create an account first."
    holdings = account.get_holdings()
    if not holdings:
        return "No shares held."
    result = ""
    for symbol, qty in holdings.items():
        price = get_share_price(symbol)
        result += f"{symbol}: {qty} shares @ ${price:.2f}\n"
    return result.strip()

def get_transactions():
    global account
    if account is None:
        return "Please create an account first."
    transactions = account.get_transactions()
    if not transactions:
        return "No transactions yet."
    result = ""
    for t in transactions:
        result += f"{t['type']}: {t['details']}\n"
    return result.strip()

with gr.Blocks(title="Trading Simulator Demo") as demo:
    gr.Markdown("## Trading Simulator Demo")
    gr.Markdown("Manage a single account: create, deposit, withdraw, buy/sell shares, and view portfolio summary.")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Account Setup")
            initial_deposit = gr.Number(label="Initial Deposit ($)", value=10000)
            create_btn = gr.Button("Create Account")
            create_output = gr.Textbox(label="Result", interactive=False)
        
        with gr.Column():
            gr.Markdown("### Deposit / Withdraw")
            amount = gr.Number(label="Amount ($)", value=100)
            deposit_btn = gr.Button("Deposit")
            withdraw_btn = gr.Button("Withdraw")
            cash_output = gr.Textbox(label="Result", interactive=False)
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Buy Shares")
            buy_symbol = gr.Dropdown(label="Symbol", choices=["AAPL", "TSLA", "GOOGL"], value="AAPL")
            buy_qty = gr.Number(label="Quantity", value=10, precision=0)
            buy_btn = gr.Button("Buy")
            buy_output = gr.Textbox(label="Result", interactive=False)
        
        with gr.Column():
            gr.Markdown("### Sell Shares")
            sell_symbol = gr.Dropdown(label="Symbol", choices=["AAPL", "TSLA", "GOOGL"], value="AAPL")
            sell_qty = gr.Number(label="Quantity", value=10, precision=0)
            sell_btn = gr.Button("Sell")
            sell_output = gr.Textbox(label="Result", interactive=False)
    
    with gr.Row():
        portfolio_btn = gr.Button("View Portfolio Value")
        portfolio_output = gr.Textbox(label="Portfolio", interactive=False)
    
    with gr.Row():
        holdings_btn = gr.Button("View Holdings")
        holdings_output = gr.Textbox(label="Holdings", interactive=False, lines=5)
    
    with gr.Row():
        transactions_btn = gr.Button("View Transactions")
        transactions_output = gr.Textbox(label="Transactions", interactive=False, lines=8)
    
    create_btn.click(create_account, inputs=[initial_deposit], outputs=[create_output])
    deposit_btn.click(deposit, inputs=[amount], outputs=[cash_output])
    withdraw_btn.click(withdraw, inputs=[amount], outputs=[cash_output])
    buy_btn.click(buy_shares, inputs=[buy_symbol, buy_qty], outputs=[buy_output])
    sell_btn.click(sell_shares, inputs=[sell_symbol, sell_qty], outputs=[sell_output])
    portfolio_btn.click(get_portfolio_value, inputs=[], outputs=[portfolio_output])
    holdings_btn.click(get_holdings, inputs=[], outputs=[holdings_output])
    transactions_btn.click(get_transactions, inputs=[], outputs=[transactions_output])

if __name__ == "__main__":
    demo.launch()