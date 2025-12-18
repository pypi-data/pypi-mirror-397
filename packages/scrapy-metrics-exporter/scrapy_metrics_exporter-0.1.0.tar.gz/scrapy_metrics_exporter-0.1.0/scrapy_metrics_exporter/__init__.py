"""Scrapy Metrics Exporter - Real-time metrics collection for Scrapy.

This package provides automatic exportation of Scrapy metrics in real-time.
It collects metrics via Scrapy signals and stats, exposing them through an
HTTP endpoint in OpenMetrics/Prometheus format.

Features:
    - Automatic collection of all numeric Scrapy stats
    - Real-time metrics via signals (items, requests, responses)
    - Custom metrics support via Scrapy stats API
    - Zero configuration required

Example:
    Add to your Scrapy project's settings.py:

    >>> EXTENSIONS = {
    ...     'scrapy_metrics_exporter.extension.MetricsExporter': 500,
    ... }

    Metrics will be available at http://localhost:9410/metrics
"""

__version__ = '0.1.0'

from .extension import MetricsExporter

__all__ = ['MetricsExporter']
