'''
Please note:

The first file that you should run in this level is tests.py for database creation, with all tests passing.
Remember that running the hack.py will change the state of the database, causing some tests inside tests.py
to fail.

If you like to return to the initial state of the database, please delete the database (level-4.db) and run
the tests.py again to recreate it.
'''

import unittest
import code as c

class TestDatabase(unittest.TestCase):

    # tests for correct retrieval of stock info given a symbol
    def test_1(self):
        op = c.DB_CRUD_ops()
        expected_output = "[METHOD EXECUTED] get_stock_info\n[QUERY] SELECT * FROM stocks WHERE symbol = 'MSFT'\n[RESULT] ('2022-01-06', 'MSFT', 300.0)"
        actual_output = op.get_stock_info('MSFT')
        self.assertEqual(actual_output, expected_output)

    # tests for correct retrieval of stock price
    def test_3(self):
        op = c.DB_CRUD_ops()
        expected_output = "[METHOD EXECUTED] get_stock_price\n[QUERY] SELECT price FROM stocks WHERE symbol = 'MSFT'\n[RESULT] (300.0,)\n"
        actual_output = op.get_stock_price('MSFT')
        self.assertEqual(actual_output, expected_output)

    # tests for correct update of stock price given symbol and updated price
    def test_4(self):
        op = c.DB_CRUD_ops()
        expected_output = "[METHOD EXECUTED] update_stock_price\n[QUERY] UPDATE stocks SET price = '300' WHERE symbol = 'MSFT'\n"
        actual_output = op.update_stock_price('MSFT', 300.0)
        self.assertEqual(actual_output, expected_output)

    # SQL injection in get_stock_info should not execute the injected query
    def test_sqli_get_stock_info(self):
        op = c.DB_CRUD_ops()
        # Inject a DROP attempt — the table must survive
        op.get_stock_info("MSFT'; DROP TABLE stocks--")
        # If injection succeeded, the next call would fail; it must still return data
        result = op.get_stock_info('MSFT')
        self.assertIn('[RESULT]', result)

    # SQL injection in get_stock_price must not alter the database
    def test_sqli_get_stock_price(self):
        op = c.DB_CRUD_ops()
        # Attempt to change price via injection
        op.get_stock_price("MSFT'; UPDATE stocks SET price = '9999' WHERE symbol = 'MSFT'--")
        # Price must still be 300.0 — the injection must not have executed
        result = op.get_stock_price('MSFT')
        self.assertIn('300.0', result)

    # SQL injection in update_stock_price symbol field must not succeed
    def test_sqli_update_stock_price(self):
        op = c.DB_CRUD_ops()
        op.update_stock_price("MSFT'; DROP TABLE stocks--", 300.0)
        # Table must still be queryable
        result = op.get_stock_price('MSFT')
        self.assertIn('[RESULT]', result)

    # exec_multi_query and exec_user_script must not exist (removed as too dangerous)
    def test_dangerous_methods_removed(self):
        op = c.DB_CRUD_ops()
        self.assertFalse(hasattr(op, 'exec_multi_query'),
                         "exec_multi_query should not exist — it allows arbitrary SQL injection")
        self.assertFalse(hasattr(op, 'exec_user_script'),
                         "exec_user_script should not exist — it allows arbitrary SQL injection")

if __name__ == '__main__':
    unittest.main()
