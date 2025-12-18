"""Scrapy extension for metrics exportation.

This module provides the main extension class that integrates with Scrapy
to collect and export metrics in real-time.
"""

# Standard library imports
# (none)

# Third-party imports
from scrapy import signals
from twisted.internet import reactor

# Local imports
from .metrics import MetricsRegistry
from .collectors import SignalCollector, StatsCollector
from .server import MetricsServer


class MetricsExporter:
    """Scrapy extension for exporting metrics in real-time.

    This extension integrates with Scrapy to collect metrics via signals
    and stats, exposing them through an HTTP endpoint. It automatically
    exports all numeric Scrapy stats and provides real-time counters for
    items, requests, and responses.

    The extension creates:
        - MetricsRegistry: Manages Prometheus metrics
        - SignalCollector: Collects real-time events via Scrapy signals
        - StatsCollector: Polls Scrapy stats periodically
        - MetricsServer: HTTP server exposing /metrics endpoint

    Configuration (optional, in settings.py):
        METRICS_EXPORTER_PORT: Server port (default: 9410)
        METRICS_EXPORTER_HOST: Bind host (default: '0.0.0.0')
        METRICS_EXPORTER_UPDATE_INTERVAL: Stats update interval in seconds (default: 30)

    Example:
        Add to settings.py:

        >>> EXTENSIONS = {
        ...     'scrapy_metrics_exporter.extension.MetricsExporter': 500,
        ... }
        >>> METRICS_EXPORTER_PORT = 9410
    """

    def __init__(self, crawler):
        """Initialize the metrics exporter extension.

        Sets up all components needed for metrics collection and exportation:
        registry, collectors, and HTTP server. Connects to Scrapy signals
        for lifecycle management.

        Args:
            crawler: Scrapy crawler instance providing access to settings,
                    signals, and stats.

        Note:
            This method is called by from_crawler() class method. Components
            are initialized but not started until spider_opened() is called.
        """
        self.crawler = crawler

        # Get settings
        settings = crawler.settings
        port = settings.getint('METRICS_EXPORTER_PORT', 9410)
        host = settings.get('METRICS_EXPORTER_HOST', '0.0.0.0')
        update_interval = settings.getint('METRICS_EXPORTER_UPDATE_INTERVAL', 30)

        # Initialize components
        self.metrics_registry = MetricsRegistry()
        self.signal_collector = SignalCollector(self.metrics_registry)
        self.stats_collector = StatsCollector(
            self.metrics_registry,
            crawler,
            update_interval
        )
        self.server = MetricsServer(
            self.metrics_registry.get_registry(),
            reactor,
            port=port,
            host=host
        )

        # Setup signal connections
        self.signal_collector.setup_signals(crawler)
        crawler.signals.connect(self.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(self.spider_closed, signal=signals.spider_closed)

    @classmethod
    def from_crawler(cls, crawler):
        """Create extension instance from Scrapy crawler.

        This is the standard Scrapy extension factory method that is called
        by Scrapy when initializing extensions.

        Args:
            crawler: Scrapy crawler instance.

        Returns:
            MetricsExporter: Initialized extension instance.
        """
        return cls(crawler)

    def spider_opened(self, spider):
        """Handle spider opened signal.

        Starts the metrics server and stats collector when a spider begins
        execution. Logs server status and endpoint URL.

        Args:
            spider: Spider instance that was opened.

        Note:
            If server fails to start, error is logged but spider execution
            continues normally. Metrics collection is non-blocking.
        """
        try:
            spider.logger.info(f'Starting metrics server on {self.server.host}:{self.server.port}')
            self.server.start()
            self.stats_collector.start()
            spider.logger.info(f'Metrics available at http://{self.server.host}:{self.server.port}/metrics')
        except Exception as e:
            spider.logger.error(f'Failed to start metrics exporter: {e}', exc_info=True)

    def spider_closed(self, spider):
        """Handle spider closed signal.

        Stops the stats collector and metrics server when spider finishes
        execution, ensuring clean shutdown.

        Args:
            spider: Spider instance that was closed.
        """
        spider.logger.info('Stopping metrics server')
        self.stats_collector.stop()
        self.server.stop()
