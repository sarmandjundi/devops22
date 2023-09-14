import json
import sys
import logging
from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics


class StructuredFormatter(logging.Formatter):
    """
    Structure log entries as JSON objects and add request context if available
    """

    def format(self, record):
        log_entry = {
            "level": record.levelname,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record),
        }
        if request:
            log_entry.update(
                {
                    "path": request.path,
                    "method": request.method,
                    "remote_addr": request.remote_addr,
                }
            )
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


app = Flask(__name__)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(StructuredFormatter())

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

logging.getLogger("werkzeug").addHandler(handler)


metrics = PrometheusMetrics(app)

metrics.info("app_info", " Service 1", version="1.0.0")


@metrics.counter(
    "requests_by_method",
    " Number of requests per method",
    labels={"method": lambda r: r.method},
)
@app.route("/")
def hello_world():
    app.logger.info("Service 1 called")
    return "Hello, World!"


app.run(host="0.0.0.0", port=5001, debug=False)