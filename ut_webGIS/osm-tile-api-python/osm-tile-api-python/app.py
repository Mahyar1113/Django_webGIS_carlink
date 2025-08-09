import os
import shutil
from flask import Flask, send_file, abort, request
import requests

app = Flask(__name__)

# Configuration for OSM Tile
OSM_TILE_URL = "https://a.tile.openstreetmap.org/{z}/{x}/{y}.png"
TILES_DIR = os.path.join(os.getcwd(), "tiles")

def validate_params(z, x, y):
    try:
        z = int(z)
        x = int(x)
        y = int(y)
    except ValueError:
        return False, "Parameters must be numeric."
    
    if z < 0 or z > 19:
        return False, "z must be between 0 and 19."
    
    max_tile = 2 ** z
    if x < 0 or x >= max_tile or y < 0 or y >= max_tile:
        return False, f"x and y must be between 0 and {max_tile - 1}."
    
    return True, None

@app.route('/tile')
def get_tile():
    z = request.args.get('z')
    x = request.args.get('x')
    y = request.args.get('y')
    
    # Validate parameters
    is_valid, error = validate_params(z, x, y)
    if not is_valid:
        abort(400, error)
    
    # Path to save the Tile
    tile_path = os.path.join(TILES_DIR, str(z), str(x), f"{y}.png")
    
    # If the Tile exists, send it
    if os.path.exists(tile_path):
        return send_file(tile_path, mimetype='image/png')
    
    # Download Tile from OSM
    try:
        url = OSM_TILE_URL.format(z=z, x=x, y=y)
        headers = {'User-Agent': 'MyWebGIS/1.0'}  # <-- Added
        response = requests.get(url, stream=True, headers=headers)  # <-- Changed
        response.raise_for_status()
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(tile_path), exist_ok=True)
        
        # Save the Tile
        with open(tile_path, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)
        
        # Send the Tile to the user
        return send_file(tile_path, mimetype='image/png')
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")  # For debugging
        abort(500, "Error fetching Tile from OSM.")

if __name__ == '__main__':
    app.run(port=3000, debug=True)