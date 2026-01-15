
import os
from dotenv import load_dotenv

load_dotenv()

DEPOT = {
    'lat': float(os.getenv('DEPOT_LAT', -7.7956)),
    'lng': float(os.getenv('DEPOT_LON', 110.3695)),
    'name': 'Lawuan Seafood Depot'
}
