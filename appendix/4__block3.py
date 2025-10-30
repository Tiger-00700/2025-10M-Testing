class ValidationStrategy:
    def validate(self, actual, expected):
        pass

class ExactMatchStrategy(ValidationStrategy):
    def validate(self, actual, expected):
        return actual == expected

class ApproximateMatchStrategy(ValidationStrategy):
    def __init__(self, tolerance=0.01):
        self.tolerance = tolerance
    
    def validate(self, actual, expected):
        if expected == 0:
            return actual == 0
        return abs(actual - expected) / expected <= self.tolerance
