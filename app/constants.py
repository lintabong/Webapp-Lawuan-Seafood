
VALID_STATUSES = {
    'pending',
    'paid',
    'prepared',
    'picked up',
    'delivered',
    'cancelled'
}

IDLE_CASHFLOW_STATUSES = ['pending', 'prepared', 'cancelled']
INSERT_CASHFLOW_STATUSES = ['paid', 'delivered', 'picked up']

CASHFLOW_ITEMS_PER_PAGE = 10
ORDER_ITEMS_PER_PAGE = 25
