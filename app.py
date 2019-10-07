from flask import (Flask, request, jsonify)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=['200 per day', '50 per hour'],
    headers_enabled=True
)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'message': f'ERROR: Ratelimit exceeded {e.description}'}), 429

def get_header_data(header_name):
    if header_name in request.headers:
        return request.headers[header_name]
    else:
        return None

def check_authorization(api_key):
    if api_key == '1234567890':   # Todo : Check api_token implementation
        return True
    else:
        return False

def api_token_require(func, *args, **kwargs):
    def wrapperFunc(*args, **kwargs):
        if(check_authorization(get_header_data('X-Api-Token')) == False):
            return jsonify({'message': 'ERROR: Unauthorized'}), 401
        else:
            returnValue = func(*args, **kwargs)
            return returnValue
    return wrapperFunc

@app.route('/', methods=['GET', 'POST'])
@limiter.limit('10 per minute')
@api_token_require
def default():
    if request.method == 'POST':        
        return jsonify({'message': 'OK POST: Authorized'}), 200
    else:
        return jsonify({'message': 'OK GET: Authorized'}), 200

if __name__ == '__main__':
   app.run(host="0.0.0.0", use_reloader=True, debug=True)