
def currency_filter(value):
    """Format value as Indonesian Rupiah"""
    try:
        return f"Rp {value:,.0f}".replace(',', '.')
    except (ValueError, TypeError):
        return value

def register_filters(app):
    """Register custom template filters"""
    app.jinja_env.filters['currency'] = currency_filter