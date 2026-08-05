# Idempotent Batch Processing 429 Retries

This example demonstrates how to prevent duplicate batch job execution when automatic retries occur after an HTTP 429 (Too Many Requests) error. It simulates a server that might return a 429 even after successfully processing a batch, and a client that retries on 429. The server uses an idempotency key to ensure the batch processing logic runs only once, preventing data corruption.

## Language

`python`

## How to Run

1. Install dependencies: `pip install Flask requests`
2. Run the script: `python main.py`
3. Observe the console output showing server processing, simulated 429s, client retries, and the idempotency mechanism preventing duplicate work.

## Original Article

This example accompanies the Turkish article: [429 Retries ve Çift Yüklenen Batch İşleri Engelleme](https://fatihsoysal.com/blog/429-retries-ve-cift-yuklenen-batch-isleri-engelleme/).

## License

MIT — see [LICENSE](LICENSE).
