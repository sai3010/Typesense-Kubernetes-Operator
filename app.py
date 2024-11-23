from flask import Response, Flask
from prometheus_client import Counter, generate_latest, Gauge
import threading

'''
Define Prometheus metrics
'''
resource_create_count_success = Counter('tok_resource_create_success_total', 'Total success resource creation events by TOK')
resource_update_count_success = Counter('tok_resource_update_success_total', 'Total success resource update events by TOK')
resource_delete_count_success = Counter('tok_resource_delete_success_total', 'Total success resource deletion events by TOK')
operator_version = Gauge('tok_version_info', 'Information about the operator version', ['version'])
operator_version.labels(version='3.0').set(3.0)

app = Flask(__name__)

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype="text/plain")

def start_flask():
    app.run(host="0.0.0.0", port=8000)

flask_thread = threading.Thread(target=start_flask)
flask_thread.start()