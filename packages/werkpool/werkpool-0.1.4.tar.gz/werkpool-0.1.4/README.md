# werkpool

**werkpool** is a Python library for managing asynchronous task execution with fine-grained control over concurrency and rate limiting. Built on `asyncio`, it provides a flexible worker pool that can handle various workload patterns efficiently.

## Features

- **Concurrency Control**: Limit the number of tasks executing simultaneously
- **Rate Limiting**: Control task execution rate (tasks per second)
- **Hybrid Mode**: Combine both concurrency and rate limits for precise control
- **Task Retries**: Built-in retry logic with configurable backoff strategies
- **Timeout Support**: Set per-task execution timeouts
- **Context Manager**: Clean resource management with `async with` syntax

## Installation

```bash
pip install werkpool
```

Or with Poetry:

```bash
poetry add werkpool
```

## Quick Start

```python
import asyncio
from werkpool import WorkerPool

async def fetch_data(url):
    # Your async task here
    return f"Data from {url}"

async def main():
    pool = WorkerPool(size=10, rate=100)
    
    # Schedule tasks
    future = pool.run(lambda: fetch_data("https://example.com"))
    result = await future
    
    await pool.shutdown()

asyncio.run(main())
```

## Usage Examples

### 1. Rate-Limited Pool (High Throughput)

**Use Case**: Making API requests with a rate limit of 100 requests per second. Ideal for services with generous rate limits where you want to maximize throughput without hitting rate caps.

```python
import asyncio
from werkpool import worker_pool

async def call_api(item_id):
    # Simulated API call
    await asyncio.sleep(0.01)
    return f"Processed {item_id}"

async def main():
    async with worker_pool(rate=100) as pool:  # 100 tasks per second
        tasks = [pool.run(lambda i=i: call_api(i)) for i in range(1000)]
        results = await asyncio.gather(*tasks)
        print(f"Completed {len(results)} tasks")

asyncio.run(main())
```

### 2. Rate-Limited Pool (Low Throughput)

**Use Case**: Calling a rate-restricted API that allows only 1 request every 20 seconds (3 per minute). Perfect for free-tier APIs or services with strict rate limits.

```python
import asyncio
from werkpool import WorkerPool

async def check_status(resource_id):
    # Expensive or rate-limited operation
    await asyncio.sleep(0.1)
    return f"Status of {resource_id}"

async def main():
    pool = WorkerPool(rate=0.05)  # 0.05 per second = 1 request per 20 seconds
    
    futures = []
    for i in range(10):
        future = pool.run(lambda i=i: check_status(i))
        futures.append(future)
    
    results = await asyncio.gather(*futures)
    print(f"All statuses checked: {len(results)} items")
    
    await pool.shutdown()

asyncio.run(main())
```

### 3. Worker-Limited Pool

**Use Case**: Preventing resource exhaustion by limiting concurrent connections. Ideal for database connections, file operations, or memory-intensive tasks where too many concurrent operations could overwhelm system resources.

```python
import asyncio
from werkpool import worker_pool

async def process_file(filename):
    # Memory or I/O intensive operation
    await asyncio.sleep(0.5)
    return f"Processed {filename}"

async def main():
    # Maximum 5 concurrent tasks at any time
    async with worker_pool(size=5) as pool:
        files = [f"file_{i}.txt" for i in range(50)]
        
        tasks = [pool.run(lambda f=f: process_file(f)) for f in files]
        results = await asyncio.gather(*tasks)
        
        print(f"Processed {len(results)} files")

asyncio.run(main())
```

### 4. Combined Rate and Worker Limiting

**Use Case**: Scraping websites where you need to respect both the server's rate limit (10 requests/second) AND limit concurrent connections (5 simultaneous) to be a good citizen and avoid overwhelming the target server.

**Rationale**: This provides the most precise control. The `size` parameter ensures you don't open too many connections at once (which could trigger DDoS protection), while `rate` ensures you don't exceed the API's rate limit even if workers complete quickly.

```python
import asyncio
from werkpool import WorkerPool

async def scrape_page(url):
    # Simulated web scraping
    await asyncio.sleep(0.2)
    return f"Content from {url}"

async def main():
    # Max 5 concurrent requests, but only 10 requests per second
    pool = WorkerPool(size=5, rate=10)
    
    urls = [f"https://example.com/page/{i}" for i in range(100)]
    
    futures = [pool.run(lambda u=u: scrape_page(u)) for u in urls]
    results = await asyncio.gather(*futures)
    
    print(f"Scraped {len(results)} pages successfully")
    
    await pool.shutdown()

asyncio.run(main())
```

### 5. Advanced: Retries and Timeouts

```python
import asyncio
from werkpool import WorkerPool

async def unreliable_api_call(endpoint):
    # Might fail occasionally
    import random
    if random.random() < 0.3:
        raise ConnectionError("Network error")
    await asyncio.sleep(0.1)
    return f"Data from {endpoint}"

async def main():
    pool = WorkerPool(size=10, rate=50)
    
    future = pool.run(
        lambda: unreliable_api_call("/data"),
        timeout=5,  # Max 5 seconds per attempt
        retries=3,  # Retry up to 3 times
        retryable_exceptions=[ConnectionError, TimeoutError]
    )
    
    try:
        result = await future
        print(f"Success: {result}")
    except Exception as e:
        print(f"Failed after retries: {e}")
    
    await pool.shutdown()

asyncio.run(main())
```

## API Reference

### WorkerPool

```python
WorkerPool(size: int | None = None, rate: float | None = None)
```

- **size**: Maximum number of concurrent workers (None = unlimited)
- **rate**: Maximum executions per second (None = unlimited)

#### Methods

**run()** - Schedule a task for execution

```python
pool.run(
    task: Callable[[], Awaitable[T]],
    timeout: int | None = None,
    retries: int = 0,
    retryable_exceptions: List[type[Exception]] = [Exception],
    backoff: Callable[[int], float] = lambda attempts: 2**attempts + random.uniform(0, 1)
) -> asyncio.Future[T]
```

**shutdown()** - Wait for all tasks to complete

```python
await pool.shutdown()
```

**kill()** - Cancel all pending tasks immediately

```python
await pool.kill()
```

### worker_pool (Context Manager)

```python
async with worker_pool(size=10, rate=100) as pool:
    # Use pool
    pass
# Automatically calls shutdown
```

## When to Use Each Mode

| Mode | Parameters | Use Case |
|------|-----------|----------|
| **Rate-Limited Only** | `rate=N` | API rate limits, throttling requests to external services |
| **Worker-Limited Only** | `size=N` | Resource constraints (DB connections, memory), CPU-bound tasks |
| **Combined** | `size=N, rate=M` | Web scraping, respecting both connection and rate limits |

## Contributing

Found a bug? Have a feature request? Please [open an issue](https://github.com/FlexDW/py-workers/issues) on GitHub!

We welcome:
- 🐛 Bug reports
- 💡 Feature requests
- 📖 Documentation improvements
- 🔧 Pull requests

## License

MIT License - see LICENSE file for details.

## Links

- **GitHub**: https://github.com/FlexDW/py-workers
- **Issues**: https://github.com/FlexDW/py-workers/issues
- **PyPI**: https://pypi.org/project/werkpool/
