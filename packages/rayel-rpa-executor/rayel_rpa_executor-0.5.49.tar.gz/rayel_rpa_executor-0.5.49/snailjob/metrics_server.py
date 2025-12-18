"""
HTTP server for Prometheus metrics endpoint
"""
from __future__ import annotations

import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional

from snailjob.config import SnailJobSettings
from snailjob.log import SnailLog
from snailjob.metrics import get_metrics


class MetricsHTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for metrics endpoint"""

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/actuator/prometheus':
            self._handle_metrics()
        elif self.path == '/health':
            self._handle_health()
        else:
            self._handle_404()

    def _handle_metrics(self):
        """Handle /metrics endpoint"""
        try:
            metrics = get_metrics()
            # 更新系统指标
            metrics.update_system_metrics()
            
            metrics_data = metrics.get_metrics()
            content_type = metrics.get_content_type()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(metrics_data.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(metrics_data.encode('utf-8'))
        except Exception as e:
            SnailLog.LOCAL.error(f"Error serving metrics: {e}")
            self._handle_500()

    def _handle_health(self):
        """Handle /health endpoint"""
        health_data = '{"status": "healthy", "timestamp": ' + str(int(time.time())) + '}'
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(health_data)))
        self.end_headers()
        self.wfile.write(health_data.encode('utf-8'))

    def _handle_404(self):
        """Handle 404 errors"""
        self.send_response(404)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Not Found')

    def _handle_500(self):
        """Handle 500 errors"""
        self.send_response(500)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Internal Server Error')

    def log_message(self, format, *args):
        """Override to use SnailLog instead of default logging"""
        SnailLog.LOCAL.debug(f"HTTP {format % args}")


class MetricsHTTPServer:
    """HTTP server for serving Prometheus metrics"""

    def __init__(self, settings: SnailJobSettings):
        """Initialize metrics HTTP server
        
        Args:
            settings: Snail Job settings
        """
        self.settings = settings
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def start(self) -> None:
        """Start the metrics HTTP server"""
        if not self.settings.snail_prometheus_enabled:
            SnailLog.LOCAL.info("Prometheus metrics disabled, skipping HTTP server")
            return

        try:
            self.server = HTTPServer(
                (self.settings.snail_prometheus_host, self.settings.snail_prometheus_port),
                MetricsHTTPRequestHandler
            )
            
            self.thread = threading.Thread(
                target=self._run_server,
                name="snailjob-metrics-server",
                daemon=True
            )
            self.thread.start()
            
            SnailLog.LOCAL.info(
                f"Prometheus metrics server started on "
                f"{self.settings.snail_prometheus_host}:{self.settings.snail_prometheus_port}"
                f"{self.settings.snail_prometheus_path}"
            )
        except Exception as e:
            SnailLog.LOCAL.error(f"Failed to start metrics server: {e}")

    def _run_server(self) -> None:
        """Run the HTTP server in a separate thread"""
        try:
            self.server.serve_forever()
        except Exception as e:
            SnailLog.LOCAL.error(f"Metrics server error: {e}")

    def stop(self) -> None:
        """Stop the metrics HTTP server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            SnailLog.LOCAL.info("Prometheus metrics server stopped")

    def is_running(self) -> bool:
        """Check if the server is running"""
        return self.server is not None and self.thread is not None and self.thread.is_alive()


def start_metrics_server(settings: SnailJobSettings) -> MetricsHTTPServer:
    """Start the metrics HTTP server
    
    Args:
        settings: Snail Job settings
        
    Returns:
        MetricsHTTPServer: The started server instance
    """
    server = MetricsHTTPServer(settings)
    server.start()
    return server
