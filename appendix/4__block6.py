class RetryManager:
    def __init__(self, max_retries=3, backoff_factor=2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    def execute_with_retry(self, func, *args, **kwargs):
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                wait_time = self.backoff_factor ** attempt
                print(f"Attempt {attempt+1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
        raise last_exception
