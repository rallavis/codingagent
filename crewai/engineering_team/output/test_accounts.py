import unittest
from accounts import Account, Transaction, InsufficientFundsError, InsufficientSharesError, get_share_price


class TestGetSharePrice(unittest.TestCase):
    """Tests for the get_share_price function."""
    
    def test_known_symbols(self):
        """Should return correct prices for known symbols."""
        self.assertEqual(get_share_price('AAPL'), 150.0)
        self.assertEqual(get_share_price('TSLA'), 700.0)
        self.assertEqual(get_share_price('GOOGL'), 2800.0)
    
    def test_case_insensitivity(self):
        """Should handle case-insensitive symbol input."""
        self.assertEqual(get_share_price('aapl'), 150.0)
        self.assertEqual(get_share_price('Aapl'), 150.0)
        self.assertEqual(get_share_price('TSLA'), 700.0)
        self.assertEqual(get_share_price('tsla'), 700.0)
    
    def test_unknown_symbol(self):
        """Should raise ValueError for unknown symbols."""
        with self.assertRaises(ValueError):
            get_share_price('MSFT')
        with self.assertRaises(ValueError):
            get_share_price('')
        with self.assertRaises(ValueError):
            get_share_price('AMZN')


class TestTransaction(unittest.TestCase):
    """Tests for the Transaction class."""
    
    def test_deposit_transaction_repr(self):
        """Deposit transaction repr should show deposit type and amount."""
        t = Transaction('deposit', 1000.0, 1000.0)
        self.assertIn('Deposit', repr(t))
        self.assertIn('1000.00', repr(t))
    
    def test_withdrawal_transaction_repr(self):
        """Withdrawal transaction repr should show withdrawal type and amount."""
        t = Transaction('withdrawal', -500.0, 500.0)
        self.assertIn('Withdrawal', repr(t))
        self.assertIn('500.00', repr(t))
    
    def test_buy_transaction_repr(self):
        """Buy transaction repr should show buy details."""
        t = Transaction('buy', -1500.0, 8500.0, 'AAPL', 10, 150.0)
        self.assertIn('Buy', repr(t))
        self.assertIn('AAPL', repr(t))
        self.assertIn('10', repr(t))
        self.assertIn('150.00', repr(t))
    
    def test_sell_transaction_repr(self):
        """Sell transaction repr should show sell details."""
        t = Transaction('sell', 750.0, 9250.0, 'AAPL', 5, 150.0)
        self.assertIn('Sell', repr(t))
        self.assertIn('AAPL', repr(t))
        self.assertIn('5', repr(t))

    def test_transaction_attributes(self):
        """Transaction should store all provided attributes."""
        t = Transaction('buy', -1500.0, 8500.0, 'AAPL', 10, 150.0)
        self.assertEqual(t.type, 'buy')
        self.assertEqual(t.symbol, 'AAPL')
        self.assertEqual(t.quantity, 10)
        self.assertEqual(t.amount, -1500.0)
        self.assertEqual(t.price_per_share, 150.0)
        self.assertEqual(t.balance_after, 8500.0)


class TestAccountInitialization(unittest.TestCase):
    """Tests for Account initialization."""
    
    def test_default_owner(self):
        """Default owner should be 'Default User'."""
        acc = Account()
        self.assertEqual(acc.owner, 'Default User')
        self.assertEqual(acc.cash_balance, 0.0)
        self.assertEqual(acc.holdings, {})
        self.assertEqual(acc.transactions, [])
    
    def test_custom_owner(self):
        """Should accept custom owner name."""
        acc = Account('John Doe')
        self.assertEqual(acc.owner, 'John Doe')
    
    def test_initial_balance_zero(self):
        """Initial balance should be zero."""
        acc = Account()
        self.assertEqual(acc.get_balance(), 0.0)
    
    def test_initial_portfolio_value_zero(self):
        """Initial portfolio value should be zero."""
        acc = Account()
        self.assertEqual(acc.get_portfolio_value(), 0.0)
    
    def test_initial_profit_loss_zero(self):
        """Initial P&L should be zero."""
        acc = Account()
        self.assertEqual(acc.get_profit_loss(), 0.0)
    
    def test_initial_holdings_empty(self):
        """Initial holdings should be empty."""
        acc = Account()
        self.assertEqual(acc.get_holdings(), {})
    
    def test_initial_transactions_empty(self):
        """Initial transaction history should be empty."""
        acc = Account()
        self.assertEqual(acc.get_transaction_history(), [])


class TestDeposit(unittest.TestCase):
    """Tests for the deposit method."""
    
    def setUp(self):
        self.acc = Account('TestUser')
    
    def test_deposit_positive(self):
        """Depositing positive amount should increase balance."""
        txn = self.acc.deposit(1000.0)
        self.assertEqual(self.acc.cash_balance, 1000.0)
        self.assertEqual(self.acc.initial_deposit, 1000.0)
        self.assertEqual(txn.type, 'deposit')
        self.assertEqual(txn.amount, 1000.0)
        self.assertEqual(txn.balance_after, 1000.0)
        self.assertEqual(len(self.acc.transactions), 1)
    
    def test_multiple_deposits(self):
        """Multiple deposits should accumulate."""
        self.acc.deposit(500.0)
        self.acc.deposit(300.0)
        self.acc.deposit(200.0)
        self.assertEqual(self.acc.cash_balance, 1000.0)
        self.assertEqual(len(self.acc.transactions), 3)
    
    def test_deposit_zero_raises_error(self):
        """Depositing zero should raise ValueError."""
        with self.assertRaises(ValueError):
            self.acc.deposit(0.0)
        self.assertEqual(self.acc.cash_balance, 0.0)
    
    def test_deposit_negative_raises_error(self):
        """Depositing negative amount should raise ValueError."""
        with self.assertRaises(ValueError):
            self.acc.deposit(-100.0)
        self.assertEqual(self.acc.cash_balance, 0.0)
    
    def test_deposit_returns_transaction(self):
        """Deposit should return a Transaction object."""
        txn = self.acc.deposit(500.0)
        self.assertIsInstance(txn, Transaction)
        self.assertIs(txn, self.acc.transactions[-1])
    
    def test_deposit_float_precision(self):
        """Deposit should handle float amounts correctly."""
        self.acc.deposit(0.1)
        self.acc.deposit(0.2)
        self.assertAlmostEqual(self.acc.cash_balance, 0.3, places=10)


class TestWithdraw(unittest.TestCase):
    """Tests for the withdraw method."""
    
    def setUp(self):
        self.acc = Account('TestUser')
        self.acc.deposit(1000.0)
    
    def test_withdraw_valid(self):
        """Withdrawing valid amount should decrease balance."""
        txn = self.acc.withdraw(500.0)
        self.assertEqual(self.acc.cash_balance, 500.0)
        self.assertEqual(txn.type, 'withdrawal')
        self.assertEqual(txn.amount, -500.0)
        self.assertEqual(txn.balance_after, 500.0)
    
    def test_withdraw_exact_balance(self):
        """Withdrawing full balance should result in zero."""
        txn = self.acc.withdraw(1000.0)
        self.assertEqual(self.acc.cash_balance, 0.0)
        self.assertEqual(txn.balance_after, 0.0)
    
    def test_withdraw_more_than_balance_raises_error(self):
        """Withdrawing more than balance should raise InsufficientFundsError."""
        with self.assertRaises(InsufficientFundsError):
            self.acc.withdraw(1500.0)
        self.assertEqual(self.acc.cash_balance, 1000.0)
    
    def test_withdraw_zero_raises_error(self):
        """Withdrawing zero should raise ValueError."""
        with self.assertRaises(ValueError):
            self.acc.withdraw(0.0)
    
    def test_withdraw_negative_raises_error(self):
        """Withdrawing negative amount should raise ValueError."""
        with self.assertRaises(ValueError):
            self.acc.withdraw(-50.0)
    
    def test_withdraw_from_empty_account(self):
        """Withdrawing from empty account should raise InsufficientFundsError."""
        acc = Account()
        with self.assertRaises(InsufficientFundsError):
            acc.withdraw(10.0)
    
    def test_withdraw_returns_transaction(self):
        """Withdraw should return a Transaction object."""
        txn = self.acc.withdraw(500.0)
        self.assertIsInstance(txn, Transaction)
    
    def test_withdraw_negative_amount_in_error_message(self):
        """Error message should contain relevant information."""
        with self.assertRaises(InsufficientFundsError) as cm:
            self.acc.withdraw(1500.0)
        self.assertIn('1500.00', str(cm.exception))
        self.assertIn('1000.00', str(cm.exception))


class TestBuy(unittest.TestCase):
    """Tests for the buy method."""
    
    def setUp(self):
        self.acc = Account('TestUser')
        self.acc.deposit(10000.0)
    
    def test_buy_valid(self):
        """Buying shares should decrease cash and increase holdings."""
        txn = self.acc.buy('AAPL', 10)
        expected_cost = 10 * 150.0
        self.assertEqual(self.acc.cash_balance, 10000.0 - expected_cost)
        self.assertEqual(self.acc.holdings['AAPL'], 10)
        self.assertEqual(txn.type, 'buy')
        self.assertEqual(txn.symbol, 'AAPL')
        self.assertEqual(txn.quantity, 10)
        self.assertEqual(txn.price_per_share, 150.0)
    
    def test_buy_case_insensitive(self):
        """Buy should handle case-insensitive symbols."""
        self.acc.buy('aapl', 5)
        self.assertEqual(self.acc.holdings['AAPL'], 5)
    
    def test_buy_multiple_symbols(self):
        """Should be able to buy multiple different stocks."""
        self.acc.buy('AAPL', 10)
        self.acc.buy('TSLA', 5)
        self.assertEqual(self.acc.holdings['AAPL'], 10)
        self.assertEqual(self.acc.holdings['TSLA'], 5)
    
    def test_buy_additional_shares(self):
        """Buying more shares of existing holding should increase count."""
        self.acc.buy('AAPL', 10)
        self.acc.buy('AAPL', 5)
        self.assertEqual(self.acc.holdings['AAPL'], 15)
    
    def test_buy_exact_balance(self):
        """Should allow buying exactly up to available balance."""
        shares = int(10000.0 // 150.0)
        cost = shares * 150.0
        self.acc.buy('AAPL', shares)
        self.assertAlmostEqual(self.acc.cash_balance, 10000.0 - cost)
    
    def test_buy_insufficient_funds(self):
        """Buying beyond balance should raise InsufficientFundsError."""
        with self.assertRaises(InsufficientFundsError):
            self.acc.buy('TSLA', 100)
        self.assertEqual(self.acc.cash_balance, 10000.0)
        self.assertNotIn('TSLA', self.acc.holdings)
    
    def test_buy_zero_quantity(self):
        """Buying zero shares should raise ValueError."""
        with self.assertRaises(ValueError):
            self.acc.buy('AAPL', 0)
    
    def test_buy_negative_quantity(self):
        """Buying negative shares should raise ValueError."""
        with self.assertRaises(ValueError):
            self.acc.buy('AAPL', -5)
    
    def test_buy_unknown_symbol(self):
        """Buying unknown stock should raise ValueError."""
        with self.assertRaises(ValueError):
            self.acc.buy('MSFT', 10)
    
    def test_buy_returns_transaction(self):
        """Buy should return a Transaction object."""
        txn = self.acc.buy('AAPL', 5)
        self.assertIsInstance(txn, Transaction)


class TestSell(unittest.TestCase):
    """Tests for the sell method."""
    
    def setUp(self):
        self.acc = Account('TestUser')
        self.acc.deposit(10000.0)
        self.acc.buy('AAPL', 10)
    
    def test_sell_valid(self):
        """Selling shares should increase cash and decrease holdings."""
        txn = self.acc.sell('AAPL', 5)
        expected_proceeds = 5 * 150.0
        self.assertEqual(self.acc.cash_balance, 10000.0 - (10*150.0) + expected_proceeds)
        self.assertEqual(self.acc.holdings['AAPL'], 5)
        self.assertEqual(txn.type, 'sell')
        self.assertEqual(txn.symbol, 'AAPL')
        self.assertEqual(txn.quantity, 5)
        self.assertEqual(txn.price_per_share, 150.0)
    
    def test_sell_all_shares_removes_symbol(self):
        """Selling all shares of a symbol should remove it from holdings."""
        self.acc.sell('AAPL', 10)
        self.assertNotIn('AAPL', self.acc.holdings)
        self.assertEqual(self.acc.cash_balance, 10000.0)
    
    def test_sell_more_than_held_raises_error(self):
        """Selling more shares than held should raise InsufficientSharesError."""
        with self.assertRaises(InsufficientSharesError):
            self.acc.sell('AAPL', 15)
        self.assertEqual(self.acc.holdings['AAPL'], 10)
    
    def test_sell_unowned_symbol_raises_error(self):
        """Selling unowned stock should raise InsufficientSharesError."""
        with self.assertRaises(InsufficientSharesError):
            self.acc.sell('TSLA', 1)
    
    def test_sell_zero_quantity(self):
        """Selling zero shares should raise ValueError."""
        with self.assertRaises(ValueError):
            self.acc.sell('AAPL', 0)
    
    def test_sell_negative_quantity(self):
        """Selling negative shares should raise ValueError."""
        with self.assertRaises(ValueError):
            self.acc.sell('AAPL', -3)
    
    def test_sell_unknown_symbol(self):
        """Selling unknown stock should raise InsufficientSharesError (unowned)."""
        with self.assertRaises(InsufficientSharesError):
            self.acc.sell('MSFT', 1)
    
    def test_sell_then_buy_again(self):
        """Should be able to sell and then buy again the same symbol."""
        self.acc.sell('AAPL', 5)
        self.acc.buy('AAPL', 3)
        self.assertEqual(self.acc.holdings['AAPL'], 8)
    
    def test_sell_returns_transaction(self):
        """Sell should return a Transaction object."""
        txn = self.acc.sell('AAPL', 5)
        self.assertIsInstance(txn, Transaction)
    
    def test_sell_case_insensitive(self):
        """Sell should handle case-insensitive symbols."""
        self.acc.sell('aapl', 5)
        self.assertEqual(self.acc.holdings['AAPL'], 5)


class TestGetHoldings(unittest.TestCase):
    """Tests for the get_holdings method."""
    
    def test_empty_holdings(self):
        """New account should have empty holdings."""
        acc = Account()
        self.assertEqual(acc.get_holdings(), {})
    
    def test_holdings_after_purchase(self):
        """Should return correct holdings after purchases."""
        acc = Account()
        acc.deposit(10000.0)
        acc.buy('AAPL', 10)
        acc.buy('TSLA', 2)
        holdings = acc.get_holdings()
        self.assertEqual(holdings, {'AAPL': 10, 'TSLA': 2})
    
    def test_holdings_immutable(self):
        """Returned holdings should be a copy, not the original dict."""
        acc = Account()
        acc.deposit(10000.0)
        acc.buy('AAPL', 10)
        holdings = acc.get_holdings()
        holdings['AAPL'] = 100
        self.assertEqual(acc.holdings['AAPL'], 10)


class TestPortfolioValue(unittest.TestCase):
    """Tests for the get_portfolio_value method."""
    
    def test_portfolio_value_only_cash(self):
        """With only cash, portfolio value should equal balance."""
        acc = Account()
        acc.deposit(5000.0)
        self.assertEqual(acc.get_portfolio_value(), 5000.0)
    
    def test_portfolio_value_with_shares(self):
        """Portfolio value should include shares at current prices."""
        acc = Account()
        acc.deposit(10000.0)
        acc.buy('AAPL', 10)
        self.assertEqual(acc.get_portfolio_value(), 10000.0)
    
    def test_portfolio_value_mixed(self):
        """Portfolio value should sum cash and all share values."""
        acc = Account()
        acc.deposit(20000.0)
        acc.buy('AAPL', 10)
        acc.buy('TSLA', 5)
        expected = 20000.0
        self.assertEqual(acc.get_portfolio_value(), expected)
    
    def test_portfolio_value_after_sell(self):
        """Portfolio value should update after selling."""
        acc = Account()
        acc.deposit(10000.0)
        acc.buy('AAPL', 10)
        acc.sell('AAPL', 5)
        expected = 10000.0
        self.assertEqual(acc.get_portfolio_value(), expected)


class TestProfitLoss(unittest.TestCase):
    """Tests for the get_profit_loss method."""
    
    def test_no_transactions_pl_zero(self):
        """With no transactions, P&L should be zero."""
        acc = Account()
        self.assertEqual(acc.get_profit_loss(), 0.0)
    
    def test_just_deposit_pl_zero(self):
        """With just deposit and no trades, P&L should be zero."""
        acc = Account()
        acc.deposit(1000.0)
        self.assertEqual(acc.get_profit_loss(), 0.0)
    
    def test_deposit_and_buy_hold_pl_zero(self):
        """Buying and holding at same price should result in zero P&L."""
        acc = Account()
        acc.deposit(10000.0)
        acc.buy('AAPL', 10)
        self.assertAlmostEqual(acc.get_profit_loss(), 0.0)
    
    def test_profit_after_sell(self):
        """Selling at same price as bought should result in zero P&L."""
        acc = Account()
        acc.deposit(10000.0)
        acc.buy('AAPL', 10)
        acc.sell('AAPL', 10)
        self.assertAlmostEqual(acc.get_profit_loss(), 0.0)
    
    def test_pl_with_withdrawals(self):
        """Withdrawals should not affect P&L calculation."""
        acc = Account()
        acc.deposit(10000.0)
        acc.withdraw(2000.0)
        self.assertEqual(acc.get_profit_loss(), 0.0)
    
    def test_pl_with_multiple_deposits_withdrawals(self):
        """Multiple deposits and withdrawals should correctly affect P&L."""
        acc = Account()
        acc.deposit(5000.0)
        acc.deposit(3000.0)
        acc.withdraw(1000.0)
        self.assertEqual(acc.get_profit_loss(), 0.0)


class TestTransactionHistory(unittest.TestCase):
    """Tests for the get_transaction_history method."""
    
    def test_empty_history(self):
        """New account should have empty transaction history."""
        acc = Account()
        self.assertEqual(acc.get_transaction_history(), [])
    
    def test_transaction_order(self):
        """Transactions should be in chronological order."""
        acc = Account()
        acc.deposit(5000.0)
        acc.buy('AAPL', 10)
        acc.sell('AAPL', 5)
        history = acc.get_transaction_history()
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0].type, 'deposit')
        self.assertEqual(history[1].type, 'buy')
        self.assertEqual(history[2].type, 'sell')
    
    def test_history_immutable(self):
        """Returned history should be a copy, not the original list."""
        acc = Account()
        acc.deposit(500.0)
        history = acc.get_transaction_history()
        original_len = len(history)
        history.append('fake')
        self.assertEqual(len(acc.get_transaction_history()), original_len)
    
    def test_history_contains_all_transactions(self):
        """History should contain all executed transactions."""
        acc = Account()
        acc.deposit(1000.0)
        acc.withdraw(500.0)
        acc.deposit(300.0)
        history = acc.get_transaction_history()
        self.assertEqual(len(history), 3)


class TestEdgeCasesAndIntegration(unittest.TestCase):
    """Tests for edge cases and integration scenarios."""
    
    def test_large_numbers(self):
        """Should handle large numbers correctly."""
        acc = Account()
        acc.deposit(1_000_000_000.0)
        acc.buy('AAPL', 1_000_000)
        self.assertEqual(acc.holdings['AAPL'], 1_000_000)
        self.assertEqual(acc.cash_balance, 1_000_000_000.0 - 150_000_000.0)
    
    def test_float_precision(self):
        """Should handle float precision appropriately."""
        acc = Account()
        acc.deposit(100.0)
        acc.withdraw(33.33)
        acc.deposit(0.01)
        self.assertAlmostEqual(acc.get_balance(), 66.68, places=2)
    
    def test_complex_trading_scenario(self):
        """Complex scenario with multiple operations."""
        acc = Account('Investor')
        acc.deposit(10000.0)
        acc.buy('AAPL', 10)
        acc.buy('TSLA', 5)
        acc.sell('AAPL', 3)
        acc.deposit(2000.0)
        acc.withdraw(1000.0)
        acc.buy('GOOGL', 1)
        
        expected_cash = 10000 - 10*150 - 5*700 + 3*150 + 2000 - 1000 - 1*2800
        self.assertAlmostEqual(acc.get_balance(), expected_cash)
        
        self.assertEqual(acc.holdings['AAPL'], 7)
        self.assertEqual(acc.holdings['TSLA'], 5)
        self.assertEqual(acc.holdings['GOOGL'], 1)
        self.assertEqual(len(acc.get_transaction_history()), 7)
        
        expected_portfolio = expected_cash + (7*150) + (5*700) + (1*2800)
        self.assertAlmostEqual(acc.get_portfolio_value(), expected_portfolio)
        expected_pl = expected_portfolio - 11000.0
        self.assertAlmostEqual(acc.get_profit_loss(), expected_pl)
    
    def test_multiple_deposits_and_withdrawals(self):
        """Multiple deposits and withdrawals should maintain correct balance."""
        acc = Account()
        acc.deposit(1000.0)
        acc.deposit(500.0)
        acc.withdraw(200.0)
        acc.deposit(300.0)
        acc.withdraw(100.0)
        self.assertEqual(acc.cash_balance, 1500.0)
        self.assertEqual(len(acc.get_transaction_history()), 5)
    
    def test_holdings_cleaned_after_full_sell(self):
        """After selling all shares, the symbol should be removed from holdings."""
        acc = Account()
        acc.deposit(1000.0)
        acc.buy('AAPL', 5)
        acc.sell('AAPL', 5)
        self.assertNotIn('AAPL', acc.holdings)
        self.assertEqual(acc.get_holdings(), {})
    
    def test_buy_with_exact_money(self):
        """Buying with exactly the available money should work."""
        acc = Account()
        acc.deposit(1500.0)
        acc.buy('AAPL', 10)
        self.assertEqual(acc.cash_balance, 0.0)
        self.assertEqual(acc.holdings['AAPL'], 10)
    
    def test_multiple_owners_isolation(self):
        """Multiple accounts should not interfere with each other."""
        acc1 = Account('Alice')
        acc2 = Account('Bob')
        
        acc1.deposit(1000.0)
        acc1.buy('AAPL', 5)
        
        acc2.deposit(5000.0)
        acc2.buy('TSLA', 3)
        
        self.assertEqual(acc1.cash_balance, 1000.0 - 5*150.0)
        self.assertEqual(acc2.cash_balance, 5000.0 - 3*700.0)
        self.assertEqual(acc1.holdings, {'AAPL': 5})
        self.assertEqual(acc2.holdings, {'TSLA': 3})

    def test_get_balance_consistency(self):
        """get_balance should always match cash_balance attribute."""
        acc = Account()
        acc.deposit(1000.0)
        self.assertEqual(acc.get_balance(), acc.cash_balance)
        acc.buy('AAPL', 5)
        self.assertEqual(acc.get_balance(), acc.cash_balance)
        acc.sell('AAPL', 2)
        self.assertEqual(acc.get_balance(), acc.cash_balance)


if __name__ == '__main__':
    unittest.main(verbosity=2)
