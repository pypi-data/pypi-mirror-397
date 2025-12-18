"""HTTP server for metrics exposition.

This module provides a Twisted-based HTTP server that exposes metrics
in Prometheus/OpenMetrics format through a /metrics endpoint.
"""

# Standard library imports
import logging

# Third-party imports
from twisted.web import server, resource
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Local imports
# (none)

logger = logging.getLogger(__name__)


class MetricsResource(resource.Resource):
    """HTTP resource that serves Prometheus metrics.

    Twisted web resource that handles GET requests to the /metrics endpoint,
    returning metrics in Prometheus/OpenMetrics text format.

    Attributes:
        isLeaf: True to indicate this is a leaf resource (no children).
        registry: Prometheus CollectorRegistry containing metrics to expose.

    Example:
        >>> from prometheus_client import CollectorRegistry
        >>> registry = CollectorRegistry()
        >>> resource = MetricsResource(registry)
        >>> # Resource is typically used by MetricsServer, not directly
    """
    isLeaf = True

    def __init__(self, registry):
        """Initialize the metrics resource.

        Args:
            registry: Prometheus CollectorRegistry instance.
        """
        resource.Resource.__init__(self)
        self.registry = registry

    def render_GET(self, request):
        """Handle GET requests to /metrics endpoint.

        Generates metrics in Prometheus text format and returns them with
        appropriate content-type header.

        Args:
            request: Twisted Request instance.

        Returns:
            bytes: Metrics in Prometheus text format.
        """
        request.setHeader(b'Content-Type', CONTENT_TYPE_LATEST.encode('utf-8'))
        metrics = generate_latest(self.registry)
        return metrics


class MetricsServer:
    """Twisted web server for exposing metrics.

    HTTP server that exposes a /metrics endpoint for Prometheus scraping.
    Uses Twisted's asynchronous web server for efficient handling of
    concurrent requests.

    The server binds to a configurable host and port, creating a root
    resource with a single child resource (/metrics) that serves the
    metrics data.

    Configuration:
        port: Server port (default: 9410)
        host: Bind address (default: '0.0.0.0' for all interfaces)

    Note:
        The server runs in the same Twisted reactor as Scrapy, ensuring
        non-blocking operation alongside spider execution.

    Example:
        >>> from twisted.internet import reactor
        >>> from prometheus_client import CollectorRegistry
        >>> registry = CollectorRegistry()
        >>> server = MetricsServer(registry, reactor, port=9410)
        >>> server.start()
        >>> # Server runs until stop() is called
        >>> server.stop()
    """

    def __init__(self, registry, reactor, port=9410, host='0.0.0.0'):
        """Initialize the metrics server.

        Args:
            registry: Prometheus CollectorRegistry containing metrics.
            reactor: Twisted reactor instance for server lifecycle.
            port: Port to bind to. Defaults to 9410.
            host: Host interface to bind to. Defaults to '0.0.0.0' (all interfaces).
        """
        self.registry = registry
        self.reactor = reactor
        self.port = port
        self.host = host
        self.listener = None

    def start(self):
        """Start the metrics server.

        Creates a Twisted web site with /metrics endpoint and starts
        listening on the configured port and host.

        Returns:
            IListeningPort: Twisted listener port object.

        Raises:
            Exception: If server fails to start (port in use, permission denied, etc.).

        Note:
            Logs success message on successful start, error message on failure.
        """
        try:
            root = resource.Resource()
            root.putChild(b'metrics', MetricsResource(self.registry))

            site = server.Site(root)
            self.listener = self.reactor.listenTCP(self.port, site, interface=self.host)

            logger.info(f'Metrics server successfully started on {self.host}:{self.port}')
            return self.listener
        except Exception as e:
            logger.error(f'Failed to start metrics server: {e}')
            raise

    def stop(self):
        """Stop the metrics server.

        Gracefully stops the server if it's running, closing all connections.

        Returns:
            Deferred or None: Deferred that fires when server stops, or None
                            if server was not running.
        """
        if self.listener:
            logger.info('Stopping metrics server')
            return self.listener.stopListening()
