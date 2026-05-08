```python
"""
accounts.py - A simple account management system for a trading simulation platform.

This module provides the Account class to manage user portfolios, track transactions,
and prevent invalid operations (overdrafts, insufficient funds for purchases, short selling).
It relies on a provided get_share_price(symbol) function (with a test implementation included).
"""

# Test implementation of get_share_price (provided in requirements)
def get_share_price(symbol: str) -> float:
    """
    Return the current price of a given stock symbol.

    For simulation purposes, returns fixed prices for AAPL, TSLA, GOOGL.
    Raises ValueError for unknown symbols.

    :param symbol: Stock ticker symbol (e.g., "AAPL")
    :return: Current price as float
    """
    prices = {
        "AAPL": 150.0,
        "TSLA": 700.0,
        "GOOGL": 2800.0
    }
    symbol = symbol.upper()
    if symbol not in prices:
        raise ValueError(f"Unknown symbol: {symbol}")
    return prices[symbol]


class InsufficientFundsError(Exception):
    """Exception raised when an account does not have enough funds for withdrawal or purchase."""
    pass


class InsufficientSharesError(Exception):
    """Exception raised when an account tries to sell more shares than it holds."""
    pass


class Transaction:
    """
    Represents a single financial transaction on an account.

    Attributes:
        type (str): 'deposit', 'withdrawal', 'buy', or 'sell'
        symbol (str, optional): Stock symbol if applicable
        quantity (int, optional): Number of shares if applicable
        amount (float): Monetary amount involved (positive for inward, negative for outward)
        price_per_share (float, optional): Price per share for buy/sell
        balance_after (float): Account cash balance after this transaction
    """

    def __init__(self, type: str, amount: float, balance_after: float,
                 symbol: str = None, quantity: int = None, price_per_share: float = None):
        self.type = type
        self.symbol = symbol
        self.quantity = quantity
        self.amount = amount
        self.price_per_share = price_per_share
        self.balance_after = balance_after

    def __repr__(self):
        if self.type in ('deposit', 'withdrawal'):
            return f"{self.type.capitalize()} of ${self.amount:.2f}"
        else:
            return f"{self.type.capitalize()} {self.quantity} shares of {self.symbol} at ${self.price_per_share:.2f}"


class Account:
    """
    A trading account with cash balance, share holdings, and transaction history.

    Attributes:
        owner (str): Name of the account owner
        cash_balance (float): Current cash held in the account
        holdings (dict): Dictionary mapping symbol -> number of shares owned
        transactions (list[Transaction]): History of all transactions
        initial_deposit (float): Total amount initially deposited (net of withdrawals)
    """

    def __init__(self, owner: str = "Default User"):
        """
        Initialize an account with zero balance and empty holdings.

        :param owner: Name of the account owner
        """
        self.owner = owner
        self.cash_balance = 0.0
        self.holdings = {}  # symbol -> shares
        self.transactions = []
        self.initial_deposit = 0.0  # Track total deposits for P&L calculation

    def deposit(self, amount: float) -> Transaction:
        """
        Deposit funds into the account.

        :param amount: Positive amount to deposit
        :return: Transaction record
        :raises ValueError: If amount is not positive
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.cash_balance += amount
        self.initial_deposit += amount
        txn = Transaction('deposit', amount, self.cash_balance)
        self.transactions.append(txn)
        return txn

    def withdraw(self, amount: float) -> Transaction:
        """
        Withdraw funds from the account. Prevents negative balance.

        :param amount: Positive amount to withdraw
        :return: Transaction record
        :raises ValueError: If amount is not positive
        :raises InsufficientFundsError: If withdrawal would cause negative balance
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.cash_balance:
            raise InsufficientFundsError(f"Cannot withdraw ${amount:.2f}. Available: ${self.cash_balance:.2f}")
        self.cash_balance -= amount
        txn = Transaction('withdrawal', -amount, self.cash_balance)
        self.transactions.append(txn)
        return txn

    def buy(self, symbol: str, quantity: int) -> Transaction:
        """
        Buy shares of a stock. Only deducts if sufficient cash.

        :param symbol: Stock ticker symbol
        :param quantity: Number of shares to buy (must be positive)
        :return: Transaction record
        :raises ValueError: If quantity is not positive or symbol is invalid
        :raises InsufficientFundsError: If purchase cost exceeds cash balance
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        symbol = symbol.upper()
        price = get_share_price(symbol)
        cost = price * quantity
        if cost > self.cash_balance:
            raise InsufficientFundsError(
                f"Cannot buy {quantity} shares of {symbol} at ${price:.2f} each. "
                f"Cost: ${cost:.2f}, Available balance: ${self.cash_balance:.2f}"
            )
        self.cash_balance -= cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        txn = Transaction('buy', -cost, self.cash_balance, symbol, quantity, price)
        self.transactions.append(txn)
        return txn

    def sell(self, symbol: str, quantity: int) -> Transaction:
        """
        Sell shares of a stock. Only sells if enough shares are held.

        :param symbol: Stock ticker symbol
        :param quantity: Number of shares to sell (must be positive)
        :return: Transaction record
        :raises ValueError: If quantity is not positive or symbol is invalid
        :raises InsufficientSharesError: If account holds fewer shares than quantity to sell
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        symbol = symbol.upper()
        current_shares = self.holdings.get(symbol, 0)
        if quantity > current_shares:
            raise InsufficientSharesError(
                f"Cannot sell {quantity} shares of {symbol}. Only {current_shares} held."
            )
        price = get_share_price(symbol)
        proceeds = price * quantity
        self.cash_balance += proceeds
        self.holdings[symbol] = current_shares - quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]  # Clean up zero holdings
        txn = Transaction('sell', proceeds, self.cash_balance, symbol, quantity, price)
        self.transactions.append(txn)
        return txn

    def get_holdings(self) -> dict:
        """
        Return a dictionary of current holdings: symbol -> number of shares.

        :return: Dictionary with symbol keys and share counts
        """
        return dict(self.holdings)

    def get_portfolio_value(self) -> float:
        """
        Calculate the total value of the portfolio (cash + shares * current prices).

        :return: Total portfolio value as float
        """
        total = self.cash_balance
        for symbol, shares in self.holdings.items():
            total += shares * get_share_price(symbol)
        return total

    def get_profit_loss(self) -> float:
        """
        Calculate the profit or loss from the initial deposit.

        Profit/Loss = Current portfolio value - Total deposits (net of withdrawals)
        Note: This uses net deposits (total deposits - total withdrawals) as basis.

        :return: Profit (positive) or loss (negative) as float
        """
        total_deposits = sum(t.amount for t in self.transactions if t.type == 'deposit')
        total_withdrawals = sum(-t.amount for t in self.transactions if t.type == 'withdrawal')
        net_deposits = total_deposits - total_withdrawals
        return self.get_portfolio_value() - net_deposits

    def get_transaction_history(self) -> list[Transaction]:
        """
        Return a list of all transactions in chronological order.

        :return: List of Transaction objects
        """
        return list(self.transactions)  # Return a copy to prevent external modification

    def get_balance(self) -> float:
        """
        Return the current cash balance.

        :return: Current cash balance as float
        """
        return self.cash_balance

# Example usage (for testing)
if __name__ == "__main__":
    # Create account
    acc = Account("TestUser")
    print("Initial balance:", acc.get_balance())

    # Deposit funds
    acc.deposit(10000)
    print("After deposit of $10,000:", acc.get_balance())

    # Buy shares
    acc.buy("AAPL", 10)
    print("After buying 10 AAPL:", acc.get_balance())
    print("Holdings:", acc.get_holdings())
    print("Portfolio value:", acc.get_portfolio_value())
    print("P&L:", acc.get_profit_loss())

    # Sell shares
    acc.sell("AAPL", 5)
    print("After selling 5 AAPL:", acc.get_balance())
    print("Holdings:", acc.get_holdings())

    # Attempt to buy more than possible
    try:
        acc.buy("TSLA", 100)  # Would cost $70,000, only have ~$8,500
    except InsufficientFundsError as e:
        print("Error:", e)

    # Attempt to sell more than held
    try:
        acc.sell("AAPL", 100)  # Only hold 5
    except InsufficientSharesError as e:
        print("Error:", e)

    # List transactions
    print("\nTransaction history:")
    for t in acc.get_transaction_history():
        print(t)
```