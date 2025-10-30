class TestExecutionSubject:
    def __init__(self):
        self.observers = []
    
    def register_observer(self, observer):
        self.observers.append(observer)
    
    def notify_observers(self, event_type, data):
        for observer in self.observers:
            observer.update(event_type, data)

class LoggingObserver:
    def update(self, event_type, data):
        print(f"Event: {event_type}, Data: {data}")

class ReportingObserver:
    def update(self, event_type, data):
        # 更新测试报告
        pass
