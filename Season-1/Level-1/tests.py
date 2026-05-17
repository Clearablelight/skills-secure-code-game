import unittest
import code as c

class TestOnlineStore(unittest.TestCase):

    # Example 1 - shows a valid and successful payment for a tv
    def test_1(self):
        tv_item = c.Item(type='product', description='tv', amount=1000.00, quantity=1)
        payment = c.Item(type='payment', description='invoice_1', amount=1000.00, quantity=1)
        order_1 = c.Order(id='1', items=[payment, tv_item])
        self.assertEqual(c.validorder(order_1), 'Order ID: 1 - Full payment received!')

    # Example 2 - successfully detects payment imbalance as tv was never paid
    def test_2(self):
        tv_item = c.Item(type='product', description='tv', amount=1000.00, quantity=1)
        order_2 = c.Order(id='2', items=[tv_item])
        self.assertEqual(c.validorder(order_2), 'Order ID: 2 - Payment imbalance: $-1000.00')

    # Example 3 - successfully reimburses client for a return so payment imbalance exists
    def test_3(self):
        tv_item = c.Item(type='product', description='tv', amount=1000.00, quantity=1)
        payment = c.Item(type='payment', description='invoice_3', amount=1000.00, quantity=1)
        payback = c.Item(type='payment', description='payback_3', amount=-1000.00, quantity=1)
        order_3 = c.Order(id='3', items=[payment, tv_item, payback])
        self.assertEqual(c.validorder(order_3), 'Order ID: 3 - Payment imbalance: $-1000.00')

    # Example 4 - handles invalid input such as placing an invalid order for 1.5 device
    def test_4(self):
        tv = c.Item(type='product', description='tv', amount=1000, quantity=1.5)
        order_1 = c.Order(id='1', items=[tv])
        try:
            c.validorder(order_1)
        except:
            self.fail("Invalid order detected")

    # Example 5 - handles an invalid item type called 'service'
    def test_5(self):
        service = c.Item(type='service', description='order shipment', amount=100, quantity=1)
        order_1 = c.Order(id='1', items=[service])
        self.assertEqual(c.validorder(order_1), 'Invalid item type: service')

    # Floating-point exploit: huge payment + reversal should not yield free item
    def test_6(self):
        tv_item = c.Item(type='product', description='tv', amount=1000.00, quantity=1)
        payment = c.Item(type='payment', description='invoice_4', amount=1e19, quantity=1)
        payback = c.Item(type='payment', description='payback_4', amount=-1e19, quantity=1)
        order_4 = c.Order(id='4', items=[payment, tv_item, payback])
        self.assertEqual(c.validorder(order_4), 'Order ID: 4 - Payment imbalance: $-1000.00')

    # Decimal precision: 1.1 + 2.2 must equal 3.3 exactly
    def test_7(self):
        small_item = c.Item(type='product', description='accessory', amount=3.3, quantity=1)
        payment_1 = c.Item(type='payment', description='invoice_5_1', amount=1.1, quantity=1)
        payment_2 = c.Item(type='payment', description='invoice_5_2', amount=2.2, quantity=1)
        order_5 = c.Order(id='5', items=[small_item, payment_1, payment_2])
        self.assertEqual(c.validorder(order_5), 'Order ID: 5 - Full payment received!')

    # Order total exceeding maximum should be rejected
    def test_8(self):
        num_items = 12
        items = [c.Item(type='product', description='tv', amount=99999, quantity=num_items)]
        for i in range(num_items):
            items.append(c.Item(type='payment', description='invoice_' + str(i), amount=99999, quantity=1))
        order_1 = c.Order(id='1', items=items)
        self.assertEqual(c.validorder(order_1), 'Total amount payable for an order exceeded')

        items = items[1:] + [items[0]]
        order_2 = c.Order(id='2', items=items)
        self.assertEqual(c.validorder(order_2), 'Total amount payable for an order exceeded')

if __name__ == '__main__':
    unittest.main()