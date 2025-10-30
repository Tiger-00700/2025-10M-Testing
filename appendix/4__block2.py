class TestExecutorFactory:
    @staticmethod
    def create_executor(executor_type, config):
        if executor_type == "spark":
            return SparkTestExecutor(config)
        elif executor_type == "hadoop":
            return HadoopTestExecutor(config)
        elif executor_type == "flink":
            return FlinkTestExecutor(config)
        else:
            raise ValueError(f"Unsupported executor type: {executor_type}")
