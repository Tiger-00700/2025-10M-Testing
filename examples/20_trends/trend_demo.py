#!/usr/bin/env python3
"""Tiny trend demo: compute simple moving average over an inline series."""
data = [10, 12, 11, 13, 12, 14]
window = 3
def sma(series, w):
    return [sum(series[i:i+w])/w for i in range(len(series)-w+1)]

print('data:', data)
print('sma:', sma(data, window))
