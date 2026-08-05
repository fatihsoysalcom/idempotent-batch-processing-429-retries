# idempotent-batch-processing-429-retries
This example demonstrates how to prevent duplicate batch job execution when automatic retries occur after an HTTP 429 (Too Many Requests) error. It simulates a server that might return a 429 even after successfully processing a batch, and a client that retries on 429. The server uses an idempotency key to ensure the batch processing logic runs only
