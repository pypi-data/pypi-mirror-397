"""Metrics registry and management.

This module provides the central registry for all Scrapy metrics, including
real-time counters and gauges. It manages Prometheus metric instances and
provides convenient methods for metric updates.
"""

# Standard library imports
# (none)

# Third-party imports
from prometheus_client import Counter, Gauge, CollectorRegistry

# Local imports
# (none)


class MetricsRegistry:
    """Central registry for all Scrapy metrics.

    Manages Prometheus metric instances (Counters and Gauges) for Scrapy
    metrics collection. Provides real-time counters via signals and state
    gauges for pending/active requests.

    The registry creates and manages:
        - Counters for items scraped/dropped (with spider label)
        - Counters for requests by method (with spider + method labels)
        - Counters for responses by status (with spider + status labels)
        - Gauges for pending and active requests (with spider label)

    Note:
        Additional metrics from Scrapy stats are created dynamically by
        the StatsCollector and registered separately.

    Example:
        >>> registry = MetricsRegistry()
        >>> registry.increment_items_scraped('my_spider')
        >>> registry.set_requests_pending('my_spider', 5)
    """

    def __init__(self):
        """Initialize the metrics registry.

        Creates a new Prometheus CollectorRegistry and sets up all default
        metric instances (counters and gauges).
        """
        self.registry = CollectorRegistry()
        self._metrics = {}
        self._setup_metrics()

    def _setup_metrics(self):
        """Setup all default metrics.

        Creates Counter and Gauge instances for standard Scrapy metrics:
        items, requests, responses, and request states.
        """
        # Items metrics
        self._metrics['items_scraped'] = Counter(
            'scrapy_items_scraped_total',
            'Total number of items scraped',
            ['spider'],
            registry=self.registry
        )

        self._metrics['items_dropped'] = Counter(
            'scrapy_items_dropped_total',
            'Total number of items dropped',
            ['spider'],
            registry=self.registry
        )

        # Request metrics
        self._metrics['requests_total'] = Counter(
            'scrapy_requests_total',
            'Total number of requests',
            ['spider', 'method'],
            registry=self.registry
        )

        # Response metrics
        self._metrics['responses_total'] = Counter(
            'scrapy_responses_total',
            'Total number of responses',
            ['spider', 'status'],
            registry=self.registry
        )

        # Stats metrics (gauges for current state)
        self._metrics['requests_pending'] = Gauge(
            'scrapy_requests_pending',
            'Number of pending requests',
            ['spider'],
            registry=self.registry
        )

        self._metrics['requests_active'] = Gauge(
            'scrapy_requests_active',
            'Number of active requests',
            ['spider'],
            registry=self.registry
        )

    def get_metric(self, name):
        """Get a metric instance by name.

        Args:
            name: Metric name (internal key, not Prometheus name).

        Returns:
            Prometheus metric instance (Counter or Gauge), or None if not found.
        """
        return self._metrics.get(name)

    def get_registry(self):
        """Get the underlying Prometheus CollectorRegistry.

        Returns:
            CollectorRegistry: Registry containing all metrics.
        """
        return self.registry

    def increment_items_scraped(self, spider_name):
        """Increment the items scraped counter.

        Args:
            spider_name: Name of the spider that scraped the item.
        """
        self._metrics['items_scraped'].labels(spider=spider_name).inc()

    def increment_items_dropped(self, spider_name):
        """Increment the items dropped counter.

        Args:
            spider_name: Name of the spider that dropped the item.
        """
        self._metrics['items_dropped'].labels(spider=spider_name).inc()

    def increment_request(self, spider_name, method='GET'):
        """Increment the request counter.

        Args:
            spider_name: Name of the spider making the request.
            method: HTTP method (GET, POST, etc.). Defaults to 'GET'.
        """
        self._metrics['requests_total'].labels(spider=spider_name, method=method).inc()

    def increment_response(self, spider_name, status):
        """Increment the response counter.

        Args:
            spider_name: Name of the spider receiving the response.
            status: HTTP status code (200, 404, etc.).
        """
        status_str = str(status)
        self._metrics['responses_total'].labels(spider=spider_name, status=status_str).inc()

    def set_requests_pending(self, spider_name, value):
        """Set the pending requests gauge value.

        Args:
            spider_name: Name of the spider.
            value: Number of pending requests in the scheduler.
        """
        self._metrics['requests_pending'].labels(spider=spider_name).set(value)

    def set_requests_active(self, spider_name, value):
        """Set the active requests gauge value.

        Args:
            spider_name: Name of the spider.
            value: Number of currently active requests in the downloader.
        """
        self._metrics['requests_active'].labels(spider=spider_name).set(value)
