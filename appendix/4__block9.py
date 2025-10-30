class TestResultAnalyzer:
    def __init__(self):
        self.results = []
    
    def add_result(self, test_case, status, execution_time, error_message=None):
        result = {
            "test_case": test_case,
            "status": status,  # "PASS", "FAIL", "SKIP", "ERROR"
            "execution_time": execution_time,
            "error_message": error_message,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.results.append(result)
    
    def generate_summary(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        skipped = sum(1 for r in self.results if r["status"] == "SKIP")
        errors = sum(1 for r in self.results if r["status"] == "ERROR")
        
        pass_rate = (passed / total) * 100 if total > 0 else 0
        avg_execution_time = sum(r["execution_time"] for r in self.results) / total if total > 0 else 0
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "pass_rate": pass_rate,
            "avg_execution_time": avg_execution_time
        }
    
    def get_failed_tests(self):
        return [r for r in self.results if r["status"] in ["FAIL", "ERROR"]]
