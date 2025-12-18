# Scrapy Metrics Exporter

Export Scrapy metrics in real-time with automatic collection of all Scrapy stats and custom metrics.

**Current backend:** Prometheus (OpenMetrics format)

## Installation

```bash
pip install scrapy-metrics-exporter
```

## Quick Start

Add to your Scrapy project's `settings.py`:

```python
EXTENSIONS = {
    'scrapy_metrics_exporter.extension.MetricsExporter': 500,
}
```

That's it! Run your spider and metrics will be available at:

```
http://localhost:9410/metrics
```

## Configuration

Optional settings (with defaults):

```python
# Port for metrics server
METRICS_EXPORTER_PORT = 9410

# Host to bind to
METRICS_EXPORTER_HOST = '0.0.0.0'

# Stats update interval in seconds
METRICS_EXPORTER_UPDATE_INTERVAL = 30
```

## Features

✨ **Automatic Metrics Collection**
- Exports **all numeric Scrapy stats** automatically
- No manual configuration needed for new metrics
- Custom stats created in spiders/pipelines are exported automatically

📊 **Built-in Real-time Metrics**
- Items scraped/dropped (Counters with spider label)
- HTTP requests by method (Counters with spider + method labels)
- HTTP responses by status (Counters with spider + status labels)
- Pending/active requests (Gauges)

🔧 **Flexible & Extensible**
- Works with any Scrapy middleware or pipeline
- Support for custom metrics via Scrapy stats API
- Easy to add Histograms/Summaries when needed

## Available Metrics

### Real-time Counters (via signals)
- `scrapy_items_scraped_total{spider="..."}` - Total items scraped
- `scrapy_items_dropped_total{spider="..."}` - Total items dropped
- `scrapy_requests_total{spider="...", method="..."}` - Total requests by method
- `scrapy_responses_total{spider="...", status="..."}` - Total responses by status

### State Gauges
- `scrapy_requests_pending{spider="..."}` - Current pending requests
- `scrapy_requests_active{spider="..."}` - Current active requests

### Automatic Scrapy Stats (examples)
- `scrapy_memusage_max{spider="..."}` - Maximum memory usage
- `scrapy_downloader_request_bytes{spider="..."}` - Total bytes downloaded
- `scrapy_item_scraped_count{spider="..."}` - Item count from Scrapy stats
- And **all other numeric Scrapy stats** automatically!

### Custom Metrics
Any numeric stat you create in your spider or pipeline is automatically exported:

```python
# In your spider or pipeline
self.crawler.stats.inc_value('custom/my_metric')
self.crawler.stats.set_value('custom/avg_price', 42.5)
```

Appears automatically as:
```
scrapy_custom_my_metric{spider="..."} 10.0
scrapy_custom_avg_price{spider="..."} 42.5
```

## Query Examples (Prometheus)

```promql
# Total items scraped across all spiders
sum(scrapy_items_scraped_total)

# Items scraped by specific spider
scrapy_items_scraped_total{spider="my_spider"}

# Request rate per second
rate(scrapy_requests_total[5m])

# Top spiders by item count
topk(5, scrapy_items_scraped_total)
```

## Future Backends

The exporter is designed to be backend-agnostic. While it currently uses Prometheus (OpenMetrics format), the architecture allows for easy addition of other backends:

- **Prometheus** (current) - OpenMetrics format via `/metrics` endpoint
- **StatsD** (planned) - Send metrics to StatsD/Graphite
- **InfluxDB** (planned) - Direct InfluxDB integration
- **OpenTelemetry** (planned) - OTLP protocol support
- **Custom** - Easy to implement your own backend

## Architecture

The exporter uses a modular design:
- **Collectors** - Gather metrics from Scrapy (signals + stats)
- **Registry** - Store and manage metrics
- **Backend** - Format and expose metrics (currently Prometheus)
- **Server** - HTTP server for metrics endpoint (Twisted)

This separation makes it easy to add new backends without changing the core collection logic.

## License

MIT
