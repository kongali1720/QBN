import sys, os
from main import app

# Menambahkan path aplikasi ke sistem
sys.path.insert(0, os.path.dirname(__file__))

# Menggunakan ASGI ke WSGI wrapper untuk FastAPI
from a2wsgi import ASGIMiddleware
application = ASGIMiddleware(app)
