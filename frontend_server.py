"""
Simple frontend server for chitty.cc/trust interface
Serves the trust frontend that connects to trust.chitty.cc API
"""

from flask import Flask, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
@app.route('/trust')
def trust_interface():
    """Serve the trust frontend interface"""
    return render_template('trust_frontend.html')

if __name__ == '__main__':
    print("🌐 ChittyOS Trust Frontend Server")
    print("📱 Serving frontend interface")
    print("🔗 Visit: http://localhost:3000/trust")
    print("🔌 Connects to API: localhost:5000 (dev) or trust.chitty.cc (prod)")

    app.run(host='0.0.0.0', port=3000, debug=True)