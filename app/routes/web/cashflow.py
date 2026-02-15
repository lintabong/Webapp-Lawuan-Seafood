
from flask import (
    Blueprint,
    render_template,
)
from app.helpers.auth import login_required
from app.repositories.product_repo import list_product
from app.repositories.transaction_categories_repo import (
    list_transaction_categories
)


cashflow_bp = Blueprint('cashflow', __name__)


@cashflow_bp.route('/cashflow/create')
@login_required
def cashflow_create():
    categories = list_transaction_categories()
    products = list_product()

    return render_template(
        'cash/cashflow_create.html',
        categories=categories,
        products=products
    )

@cashflow_bp.route('/cashflow/transactions')
@login_required
def cashflow_transactions():
    categories = list_transaction_categories()

    return render_template(
        'cash/cashflow_transactions.html',
        categories=categories
    )
