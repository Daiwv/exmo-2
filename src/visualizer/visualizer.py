import json

from root import root
from src.visualizer.chart import *

pygame.init()

jsonText = open(root + '\data\candles.json').read()
candleData = json.loads(jsonText)
chart = Chart(1280, 720)
surf = chart.CreateSurface()
chart.PushBlock(candleData)
# chart.PushBlock(candleData, ChartBlock('0x000000FF', '0xFFFFFFFF', '0xFFFF00FF'))

if __name__ == '__main__':
    while True:
        for event in pygame.event.get():
            chart.HandleEvent(event)
            if event.type == pygame.QUIT:
                break
