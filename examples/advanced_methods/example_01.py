#!/usr/bin/env python3
"""Minimal Python example for examples/advanced_methods

This example demonstrates a tiny data-processing function and prints a small result.
"""

def summarize(nums):
    return {"count": len(nums), "sum": sum(nums), "mean": sum(nums)/len(nums) if nums else 0}

if __name__ == "__main__":
    data = [1, 2, 3, 5, 8]
    print("data:", data)
    print("summary:", summarize(data))
