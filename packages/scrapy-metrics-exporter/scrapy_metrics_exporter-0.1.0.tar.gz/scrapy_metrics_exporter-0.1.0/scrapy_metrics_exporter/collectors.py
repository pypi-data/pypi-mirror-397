"""Metrics collectors for Scrapy.

This module provides two types of collectors:
    - SignalCollector: Real-time metrics via Scrapy signals
    - StatsCollector: Periodic metrics via Scrapy stats polling

The collectors work together to provide comprehensive metrics coverage,
combining real-time event counting with periodic state snapshots.
"""

# Standard library imports
import re

# Third-party imports
from scrapy import signals
from twisted.internet import task
from prometheus_client import Gauge

# Local imports
# (none)


class SignalCollector:
    """Collects metrics from Scrapy signals in real-time.

    Connects to Scrapy's signal system to capture events as they happen,
    providing real-time counters for items, requests, and responses.

    Collected signals:
        - item_scraped: Increment items scraped counter
        - item_dropped: Increment items dropped counter
        - request_scheduled: Increment requests counter (by method)
        - response_received: Increment responses counter (by status)

    Note:
        Signal-based metrics are Counters that only increment, providing
        accurate cumulative counts. For current state, see StatsCollector.

    Example:
        >>> from scrapy_metrics_exporter.metrics import MetricsRegistry
        >>> registry = MetricsRegistry()
        >>> collector = SignalCollector(registry)
        >>> collector.setup_signals(crawler)
    """

    def __init__(self, metrics_registry):
        """Initialize the signal collector.

        Args:
            metrics_registry: MetricsRegistry instance for metric updates.
        """
        self.metrics = metrics_registry

    def setup_signals(self, crawler):
        """Connect signal handlers to Scrapy signals.

        Args:
            crawler: Scrapy crawler instance providing signals interface.
        """
        crawler.signals.connect(self.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(self.item_dropped, signal=signals.item_dropped)
        crawler.signals.connect(self.request_scheduled, signal=signals.request_scheduled)
        crawler.signals.connect(self.response_received, signal=signals.response_received)

    def item_scraped(self, item, spider):
        """Handle item_scraped signal.

        Increments the items scraped counter when a spider successfully
        scrapes an item.

        Args:
            item: Scraped item (not used, signature required by signal).
            spider: Spider instance that scraped the item.
        """
        self.metrics.increment_items_scraped(spider.name)

    def item_dropped(self, item, spider, exception):
        """Handle item_dropped signal.

        Increments the items dropped counter when an item is dropped
        (e.g., by pipeline validation or duplicate filtering).

        Args:
            item: Dropped item (not used, signature required by signal).
            spider: Spider instance that dropped the item.
            exception: Exception that caused the drop (not used).
        """
        self.metrics.increment_items_dropped(spider.name)

    def request_scheduled(self, request, spider):
        """Handle request_scheduled signal.

        Increments the requests counter when a request is scheduled for
        download. Tracks HTTP method as a label.

        Args:
            request: Scrapy Request instance that was scheduled.
            spider: Spider instance that scheduled the request.
        """
        method = request.method
        self.metrics.increment_request(spider.name, method)

    def response_received(self, response, request, spider):
        """Handle response_received signal.

        Increments the responses counter when a response is received.
        Tracks HTTP status code as a label.

        Args:
            response: Scrapy Response instance that was received.
            request: Original Request instance (not used).
            spider: Spider instance that received the response.
        """
        status = response.status
        self.metrics.increment_response(spider.name, status)


class StatsCollector:
    """Collects metrics from Scrapy stats periodically.

    Polls Scrapy's stats collector at regular intervals to export all
    numeric stats as Prometheus metrics. Creates metrics dynamically
    based on discovered stats.

    Features:
        - Automatic export of ALL numeric Scrapy stats
        - Dynamic metric creation (no manual configuration needed)
        - Periodic updates (default: every 30 seconds)
        - Manual metrics for calculated values (pending/active requests)

    The collector:
        1. Updates immediately on start
        2. Updates periodically during execution
        3. Updates one final time on stop

    Note:
        Custom stats created in spiders/pipelines are automatically
        exported without any configuration.

    Example:
        >>> from scrapy_metrics_exporter.metrics import MetricsRegistry
        >>> registry = MetricsRegistry()
        >>> collector = StatsCollector(registry, crawler, update_interval=30)
        >>> collector.start()  # Begin periodic collection
        >>> # ... spider runs ...
        >>> collector.stop()   # Stop and final update
    """

    def __init__(self, metrics_registry, crawler, update_interval=30):
        """Initialize the stats collector.

        Args:
            metrics_registry: MetricsRegistry instance for manual metrics.
            crawler: Scrapy crawler instance providing stats access.
            update_interval: Seconds between stats updates. Defaults to 30.
        """
        self.metrics = metrics_registry
        self.crawler = crawler
        self.update_interval = update_interval
        self.task = None
        # Cache for dynamically created metrics
        self._dynamic_metrics = {}

    def start(self):
        """Start periodic stats collection.

        Updates stats immediately, then starts a looping task to update
        stats at the configured interval.
        """
        # Update stats immediately on start
        self.update_stats()
        # Then start periodic updates
        self.task = task.LoopingCall(self.update_stats)
        self.task.start(self.update_interval, now=False)

    def stop(self):
        """Stop periodic stats collection.

        Performs one final stats update before stopping the looping task,
        ensuring final metrics are captured.
        """
        # Update stats one final time before stopping
        self.update_stats()
        if self.task and self.task.running:
            self.task.stop()

    def _normalize_metric_name(self, stat_name):
        """Convert Scrapy stat name to valid Prometheus metric name.

        Transforms Scrapy stat names (e.g., 'memusage/max') into valid
        Prometheus metric names (e.g., 'scrapy_memusage_max').

        Rules:
            - Replace '/' with '_'
            - Replace invalid characters with '_'
            - Prefix with 'scrapy_'
            - Add 'stat_' prefix if name starts with digit

        Args:
            stat_name: Original Scrapy stat name (e.g., 'memusage/max').

        Returns:
            str: Valid Prometheus metric name (e.g., 'scrapy_memusage_max').

        Example:
            >>> collector._normalize_metric_name('memusage/max')
            'scrapy_memusage_max'
            >>> collector._normalize_metric_name('custom/api_calls')
            'scrapy_custom_api_calls'
        """
        # Replace / with _
        name = stat_name.replace('/', '_')
        # Replace any other invalid characters with _
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Ensure it doesn't start with a number
        if name[0].isdigit():
            name = 'stat_' + name
        return f'scrapy_{name}'

    def _get_or_create_metric(self, metric_name, description):
        """Get existing metric or create new one dynamically.

        Maintains a cache of dynamically created metrics to avoid
        recreating them on each update cycle.

        Args:
            metric_name: Prometheus metric name.
            description: Human-readable metric description.

        Returns:
            Gauge: Existing or newly created Gauge metric instance.
        """
        if metric_name not in self._dynamic_metrics:
            self._dynamic_metrics[metric_name] = Gauge(
                metric_name,
                description,
                ['spider'],
                registry=self.metrics.get_registry()
            )
        return self._dynamic_metrics[metric_name]

    def update_stats(self):
        """Update metrics from Scrapy stats.

        Performs two types of updates:
            1. Manual metrics: Calculated values (pending/active requests)
            2. Automatic metrics: ALL numeric stats from Scrapy

        All numeric stats found in Scrapy's stats collector are
        automatically converted to Prometheus Gauge metrics and exported.

        Note:
            Non-numeric stats (strings, datetime objects, etc.) are ignored.
        """
        stats = self.crawler.stats.get_stats()
        spider_name = getattr(self.crawler.spider, 'name', 'unknown')

        # Update manual metrics (calculated from multiple stats)
        pending = stats.get('scheduler/enqueued', 0) - stats.get('scheduler/dequeued', 0)
        self.metrics.set_requests_pending(spider_name, max(0, pending))

        active = stats.get('downloader/request_count', 0) - stats.get('downloader/response_count', 0)
        self.metrics.set_requests_active(spider_name, max(0, active))

        # Automatically export ALL numeric stats from Scrapy
        for stat_name, stat_value in stats.items():
            # Only export numeric values
            if isinstance(stat_value, (int, float)):
                metric_name = self._normalize_metric_name(stat_name)
                description = f'Scrapy stat: {stat_name}'

                # Get or create the metric dynamically
                metric = self._get_or_create_metric(metric_name, description)
                metric.labels(spider=spider_name).set(stat_value)
