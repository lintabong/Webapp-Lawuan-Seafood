1.1.0
- Major Update from MySQL to Supabase

1.2.0
- Edit dashboard info
- Pretify FE: cashflow_create.html
- Pretify FE: create_order.html

1.3.0
- Create cashflow transaction
- Create new table

1.4.0
- Dashboard: change from total product to current cash

1.5.0
- Edit orders.html layout
- New logic on cashflow
- Change customer route to `customer-map`

1.6.0
- Edit dashboard: add KPI
- Edit cashflow display

1.7.0
- Add new folder: models to save supabase model
- Create models/customer.py and models/product.py

1.8.0
- Major edit on foldering

1.9.0
- Merge delivery orders into orders

1.10.0
- Split Cashflow web and api

1.11.0
- Apply model on `transaction_categories` and `products`
- Modularized orders
- Add dashboard logger
- Split API and Web on product-route

1.11.1
- Fix product api

1.12.0
- Fix Session get User Id
- Add exceptions.py

1.13.0
- Major update on cash account to cash and cashflow to transactions
- Remove print

1.14.0
- Created RPC: apply_cash_inflow
- Created RPC: create_order_full
- Created RPC: update_order_full
- Use RPC instead single query in order services
- Changed FE: order list to table, not card anymore
- Created new API: Order items
- Simpler list order in order_repositories

1.15.0
- Add queries on sql folder
- Add details on services/order_service.py func `update_order_service`
- Add new route: financial_report

2.1.0
- Add product variant on product query
- Change delivery fee step from 1000 to 1 (FE)
