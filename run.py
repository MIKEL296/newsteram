#!/usr/bin/env python
import os
import sys
from dotenv import load_dotenv
from app import create_app
from app.utils.logger_config import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()

# Create Flask app
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
