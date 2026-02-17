
import re
from datetime import datetime, timezone, timedelta
from app import exceptions
from app.repositories import (
    orders_repo,
    product_repo,
    transactions_repo,
    transaction_items_repo,
    transaction_categories_repo,
    cash_repo,
    cash_ledger_repo,
)

def get_cashflow_transactions_service(date_filter, category_filter, page, per_page):
    if date_filter:
        day = datetime.strptime(date_filter, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    else:
        day = datetime.now(timezone.utc)

    start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)

    result = transactions_repo.get_by_date_range(
        start.isoformat(),
        end.isoformat(),
        category_filter,
        page,
        per_page
    )

    transactions = result.data or []
    total_count = result.count
    total_pages = (total_count + per_page - 1) // per_page if total_count else 1

    list_id_order = []
    list_id_item = []

    for transaction in transactions:
        if transaction['reference_type'] == 'orders':
            list_id_order.append(transaction['reference_id'])
        if transaction['reference_type'] == 'transaction_items':
            list_id_item.append(transaction['id'])

    items = transaction_items_repo.get_by_transaction_ids(list_id_item)
    orders = orders_repo.get_orders_by_ids(list_id_order)

    categories = transaction_categories_repo.get_all_map()

    combined = []

    for tx in transactions:
        category = categories.get(tx['category_id'], {})
        tx_data = {
            'date': tx.get('transaction_date') or tx['created_at'],
            'transaction_id': tx['id'],
            'amount': float(tx['amount']),
            'description': tx['description'],
            'reference': tx.get('reference_type'),
            'reference_id': tx.get('reference_id'),
            'category': category.get('name'),
            'category_type': category.get('type'),
            'type': None,
            'items': []
        }

        if tx_data['reference'] == 'transaction_items':
            for item in items:
                if item['transaction_id'] == tx['id']:
                    tx_data['type'] = 'transaction_items'
                    tx_data['items'].append({
                        'name': item['description'] or item['products']['name'],
                        'unit': item['products']['unit'] if item.get('products') else None,
                        'quantity': float(item['quantity']),
                        'price': float(item['price']),
                        'subtotal': float(item['subtotal']),
                    })

        if tx_data['reference'] == 'orders':
            order = orders.get(tx['reference_id'])
            if order:
                if re.search(r'(?i)delivery', tx_data['description'] or ''):
                    tx_data['type'] = 'delivery_order'
                else:
                    tx_data['type'] = 'order'
                    tx_data['customer_name'] = order['customers']['name']

                    for oi in order['order_items']:
                        tx_data['items'].append({
                            'name': oi['products']['name'],
                            'unit': oi['products']['unit'],
                            'quantity': float(oi['quantity']),
                            'buy_price': float(oi['buy_price']),
                            'sell_price': float(oi['sell_price']),
                            'subtotal': float(oi['quantity'] * oi['sell_price'])
                        })

        if not tx_data['type']:
            tx_data['type'] = 'general'

        combined.append(tx_data)

    combined.sort(key=lambda x: x['date'], reverse=True)

    for i, row in enumerate(combined):
        print('=========================================')
        print(i, row)

    return {
        'transactions': combined,
        'total_count': total_count,
        'total_pages': total_pages,
        'date': date_filter or day.strftime('%Y-%m-%d'),
        'category': category_filter
    }

def insert_transaction(user_id, category_id, desc, amount, transaction_date, products):
    new_balance = 0
    direction = ''
    amount = float(amount)

    # 1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣🔟
    # 1️⃣ Get category type (income / expense)
    category = transaction_categories_repo.get_category_name(category_id)

    # 2️⃣ Insert cashflow transaction
    transaction_id = transactions_repo.insert_transaction(
        category_id=category_id,
        transaction_type=category['type'],
        amount=amount,
        desc=desc,
        reference_id=None,
        created_by=user_id,
        transaction_date=transaction_date
    )

    # 3️⃣ Update cash and cash ledgers (id = 1)
    if category['type'] == 'expense':
        amount = -amount
        direction = 'out'
    else:
        direction = 'in'

    balance = int(cash_repo.update_cash_balance(
        id=1,
        amount=int(amount)
    ))

    cash_ledger_repo.create_ledger(
        cash_id=1,
        amount=int(amount),
        balance_after=balance,
        direction=direction,
        transaction_id=transaction_id
    )

    # 4️⃣ If product purchases → insert purchase items & update inventory
    if products:
        for product_item in products:
            product_id = int(product_item['product_id'])
            qty = float(product_item['quantity'])
            buy_price = float(product_item['buy_price'])

            # Insert into product_purchase_items
            transaction_items_repo.insert_item(
                transaction_id=transaction_id,
                item_type='product',
                product_id=product_id,
                quantity=qty,
                price=buy_price
            )
            
            # Update product inventory
            product = product_repo.get_product_by_id(product_id)

            old_stock = float(product['stock'])
            old_price = float(product['buy_price'])

            new_stock = old_stock + qty

            new_price = (
                (old_stock * old_price + qty * buy_price) / new_stock
                if new_stock > 0 else buy_price
            )

            product_repo.update_product(
                product_id,
                {
                    'stock': new_stock,
                    'buy_price': round(new_price, 2)
                }
            )

    return new_balance
