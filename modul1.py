from flask import Flask
import json
import time
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
start_time = time.time()
wib = timezone(timedelta(hours=7))

@app.route('/health', methods=['GET'])
def health_page():
    uptime_seconds = int(time.time() - start_time)
    h, remain = divmod(uptime_seconds, 3600)
    m, s = divmod(remain, 60)

    data_set = {
        'nama': 'Hazza Danta',
        'nrp': '5025241117',
        'status': 'UP',
        'timestamp': datetime.now(wib).strftime('%Y-%m-%d %H:%M:%S'),
        'uptime': f"{h:02d}:{m:02d}:{s:02d}"
    }
    return app.response_class(
        response=json.dumps(data_set),
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6767)
