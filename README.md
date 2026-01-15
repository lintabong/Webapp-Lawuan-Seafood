# 🦐 Lawuan Seafood Distribution System

A Flask-based web application for managing seafood distribution, delivery routes, customers, and inventory.

## Features

- 🗺️ **Interactive Delivery Route Mapping** - Visualize delivery routes on an interactive map with Leaflet.js
- 👥 **Customer Management** - Track customer information and delivery locations
- 📦 **Product Inventory** - Manage seafood products, prices, and stock levels
- 🚚 **Route Optimization** - Plan efficient delivery routes using OSRM routing

## Prerequisites

- Python 3.8+
- MySQL 8.0+
- Modern web browser

## Installation

### 1. Clone or Download the Project

Create a project directory with the following structure:
```
lawuan_seafood/
├── app.py
├── requirements.txt
├── templates/
│   ├── index.html
│   ├── map.html
│   ├── customers.html
│   └── products.html
└── README.md
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup MySQL Database

1. Import your SQL dump file:
```bash
mysql -u root -p < lawuanseafood_db.sql
```

2. Update database credentials in `app.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'lawuanseafood_db',
    'user': 'your_username',      # Change this
    'password': 'your_password'    # Change this
}
```

### 4. Run the Application

```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## Usage

### Dashboard (`/`)
- Overview of total customers, products, and active routes
- Quick navigation to all features

### Delivery Routes (`/map`)
- Interactive map showing depot and all customer locations
- Automated route planning from depot → customers → depot
- Click on customers in sidebar to focus on map
- Route optimization (coming soon)

### Customer Management (`/customers`)
- View all customers with location data
- Display contact information and coordinates

### Product Inventory (`/products`)
- Browse all seafood products
- View buy/sell prices and profit margins
- Check stock levels with color-coded indicators

## Database Schema

### Tables Used:
- **customers** - Customer information and delivery locations
- **products** - Product catalog with pricing and stock
- **users** - System users (admin, staff, drivers)
- **orders** - Customer orders
- **order_items** - Order line items
- **delivery_routes** - Planned delivery routes

## Technologies Used

- **Backend**: Flask (Python)
- **Database**: MySQL 8.0
- **Frontend**: HTML5, CSS3, JavaScript
- **Mapping**: Leaflet.js, Leaflet Routing Machine
- **Routing**: OSRM (Open Source Routing Machine)

## Customization

### Change Depot Location
Update the depot coordinates in `app.py`:
```python
depot = {
    'lat': -7.588081,  # Your latitude
    'lng': 110.944142,  # Your longitude
    'name': 'Your Business Name'
}
```

### Styling
All styling is embedded in the HTML templates for easy customization. Modify the `<style>` sections in each template.

## API Endpoints

- `GET /api/customers` - Returns JSON list of all customers
- `GET /api/products` - Returns JSON list of all products

## Future Enhancements

- [ ] Order management system
- [ ] Real-time route tracking
- [ ] TSP (Traveling Salesman Problem) optimization algorithm
- [ ] Driver assignment
- [ ] Delivery status updates
- [ ] Sales reporting and analytics
- [ ] Mobile app integration

## Troubleshooting

### Database Connection Issues
- Verify MySQL is running: `sudo service mysql status`
- Check credentials in `app.py`
- Ensure database exists: `SHOW DATABASES;`

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

### Map Not Loading
- Check internet connection (required for map tiles)
- Verify customer coordinates are valid latitude/longitude values

## License

This project is for educational and business use.

## Support

For issues or questions, please check the database connection and ensure all dependencies are installed correctly.

---

**Developed for Lawuan Seafood Distribution** 🦐
