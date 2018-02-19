import pygame
import sys


class ChartInputs:
    def __init__(self):
        self.lmb = False
        self.rmb = False
        self.mpos = [0, 0]
        self.mdelta = [0, 0]

    def MouseButtonDown(self, e: pygame.event.EventType):
        if e.button == 0x1:
            self.lmb = True
            self.mdelta = [0, 0]
        elif e.button == 0x3:
            self.rmb = True

    def MouseButtonUp(self, e: pygame.event.EventType):
        if e.button == 0x1:
            self.lmb = False
            self.mdelta = [0, 0]
        elif e.button == 0x3:
            self.rmb = False

    def MouseMotion(self, e: pygame.event.EventType):
        if self.lmb:
            self.mdelta[0] += e.pos[0] - self.mpos[0]
            self.mdelta[1] += e.pos[1] - self.mpos[1]

        self.mpos = e.pos


class ChartSettings:
    def __init__(self):
        self.candleWidth = 7
        self.candleGapHalf = 1
        self.candleLookaround = 0.64  # * GetMaxCandlesOnScreen(); highestHigh & lowestLow boundaries from UpdateSurface
        self.highlightHeight = 21
        self.highlightColor = pygame.Color('0x00AAFFFF')
        self.highlightPriceColor = pygame.Color('0xFFFFFFFF')
        self.gridColor = pygame.Color('0xE8EAECFF')
        self.priceColor = pygame.Color('0x929398FF')
        self.priceSize = 13
        self.priceFont = 'Roboto,Helvetica,Consolas,Tahoma,Courier New,Arial'
        self.priceBold = True
        self.priceItalic = False
        self.priceNotchOffset = 0.03
        self.priceTextOffset = 0.06
        self.backgroundColor = pygame.Color('0xFFFFFFFF')
        self.bullCandleColor = pygame.Color('0x3BC195FF')
        self.bearCandleColor = pygame.Color('0xF83F5DFF')


class ChartBlock:
    def __init__(self, bckgClr='0xFFFFFFFF', bullClr='0x3BC195FF', bearClr='0xF83F5DFF'):
        self.backgroundColor = pygame.Color(bckgClr)
        self.bullCandleColor = pygame.Color(bullClr)
        self.bearCandleColor = pygame.Color(bearClr)
        self.candlesFrom = 0
        self.candlesTo = 0  # not inclusive


class Chart:
    def __init__(self, w, h, settings=ChartSettings()):
        self.width = w
        self.height = h
        self.surf = pygame.Surface((w, h))
        self.inp = ChartInputs()
        self.offset = 0  # this is the offset of the last candle from its default position
        self.stableOffset = self.offset  # this offset is used as a reference while calculating the prev. one
        self.candles = list()
        self.sizes = list()
        self.blocks = list()
        # self.count = 0
        self.ss = settings

    def GetMaxCandlesOnScreen(self, px: int) -> int:
        return int(px // (self.ss.candleWidth + 2 * self.ss.candleGapHalf))

    def CreateSurface(self) -> pygame.Surface:
        self.surf = pygame.display.set_mode((self.width, self.height))
        return self.surf

    def DrawGrid(self, left, right, top, bottom, freq):  # freq == how many squares there will be in a column
        deltaY = bottom - top
        if deltaY <= 0:
            return

        if right <= left:
            return

        sqSide = deltaY / freq
        if sqSide <= 0:
            return

        # draw horizontal lines
        for i in range(freq + 1):
            lineY = top + round(i * sqSide)
            pygame.draw.line(self.surf, self.ss.gridColor, (left, lineY), (right, lineY), 1)

        # draw vertical lines
        lineX = float(right)
        while lineX >= left:
            pygame.draw.line(self.surf, self.ss.gridColor, (round(lineX), top), (round(lineX), bottom), 1)
            lineX -= sqSide

    @staticmethod
    def GetPriceOnPixel(y, refY, refPrice, pricePerPixel) -> float:
        return refPrice + (refY - y) * pricePerPixel

    def DrawPrices(self, right, top, bottom, freq, refY, refPrice, pricePerPixel):
        deltaY = bottom - top
        if deltaY <= 0:
            return

        sqSide = deltaY / freq
        if sqSide <= 0:
            return

        # draw accent line
        pygame.draw.line(self.surf, self.ss.priceColor, (right, top), (right, bottom), 1)

        x = right + round((self.width - right) * self.ss.priceTextOffset)
        font = pygame.font.SysFont(self.ss.priceFont, self.ss.priceSize, self.ss.priceBold, self.ss.priceItalic)
        for i in range(freq + 1):
            y = (top + round(i * sqSide))

            # draw notches to the price tags
            pygame.draw.line(self.surf, self.ss.priceColor, (right, y),
                             (right + round((self.width - right) * self.ss.priceNotchOffset), y), 1)

            text = str(round(Chart.GetPriceOnPixel(y, refY, refPrice, pricePerPixel), 3))
            surfText = font.render(text, True, self.ss.priceColor, self.ss.backgroundColor)

            if surfText.get_height() > self.ss.highlightHeight:
                self.ss.highlightHeight = surfText.get_height()

            self.surf.blit(surfText, pygame.Rect(x, y - (surfText.get_height() // 2), 1, 1))

    def DrawHighlight(self, y, left, right, text):
        # first draw the line
        pygame.draw.line(self.surf, self.ss.highlightColor, (right, y), (left, y), 1)

        font = pygame.font.SysFont(self.ss.priceFont, self.ss.priceSize, self.ss.priceBold, self.ss.priceItalic)
        surfText = font.render(text, True, self.ss.highlightPriceColor, self.ss.highlightColor)
        x = right + round((self.width - right) * self.ss.priceTextOffset)

        self.surf.fill(self.ss.highlightColor, pygame.Rect(right, y - (self.ss.highlightHeight // 2),
                                                           self.width - right, self.ss.highlightHeight))

        self.surf.blit(surfText, pygame.Rect(x, y - (surfText.get_height() // 2), 1, 1))
        return

    def DrawBackgrounds(self, left, right, top, bottom, lastCandle, lastCandleX):
        candleWidthTotal = self.ss.candleWidth + self.ss.candleGapHalf * 2
        h = bottom - top + 1

        prevBlocksSum = 0
        blockI = 0
        candleNum = len(self.candles) - lastCandle
        for i, size in enumerate(reversed(self.sizes)):
            if prevBlocksSum + size >= candleNum:
                blockI = len(self.sizes) - 1 - i
                break
            else:
                prevBlocksSum += size

        block = self.blocks[blockI]

        lastFirstCandleX = lastCandleX + candleWidthTotal
        firstCandleX = lastFirstCandleX - candleWidthTotal * (self.sizes[blockI] + prevBlocksSum - candleNum + 1)

        self.surf.fill(block.backgroundColor, pygame.Rect(lastFirstCandleX, top, right - lastFirstCandleX, h))

        if firstCandleX <= left or blockI == 0:
            firstCandleX = left

        self.surf.fill(block.backgroundColor, pygame.Rect(firstCandleX, top, lastFirstCandleX - firstCandleX, h))

        while firstCandleX > left:
            blockI -= 1
            size = self.sizes[blockI]
            block = self.blocks[blockI]
            lastFirstCandleX = firstCandleX
            firstCandleX -= candleWidthTotal * size

            if firstCandleX <= left or blockI == 0:
                firstCandleX = left

            self.surf.fill(block.backgroundColor, pygame.Rect(firstCandleX, top, lastFirstCandleX - firstCandleX, h))

            self.surf.fill(block.backgroundColor,
                           pygame.Rect(firstCandleX, top, lastFirstCandleX - firstCandleX, h))

    def UpdateSurface(self):
        self.surf.fill(self.ss.backgroundColor)

        borderRight = int(self.width * 0.9)  # leave some % for prices and stuff
        borderLeft = 8
        borderTop = int(self.height * 0.05)
        borderBottom = int(self.height * 0.95)

        drawPxX = borderRight - borderLeft - 1
        drawPxY = borderBottom - borderTop - 1

        verticalPad = round(drawPxY * 0.04)
        limitTop = borderTop + verticalPad  # this is where highestHigh is
        limitBottom = borderBottom - verticalPad  # this is where lowestLow is
        pricePx = limitBottom - limitTop + 1

        maxCandles = self.GetMaxCandlesOnScreen(drawPxX)
        getCandles = maxCandles
        maxLastCandle = len(self.candles) - 1
        lastCandle = maxLastCandle

        if self.offset < 0:
            minOffset = -maxCandles
            if self.offset < minOffset:
                self.offset = minOffset

            getCandles += self.offset
        else:
            maxOffset = maxLastCandle
            if self.offset > maxOffset:
                self.offset = maxOffset

            lastCandle -= self.offset

        if lastCandle < 0:
            return

        firstCandle = lastCandle - getCandles + 1
        if firstCandle < 0:
            firstCandle = 0
            # getCandles = lastCandle + 1

        candleWidthTotal = self.ss.candleWidth + self.ss.candleGapHalf * 2
        candleX = borderRight - candleWidthTotal  # this is where the rightmost candle is
        if self.offset < 0:
            candleX += self.offset * candleWidthTotal

        self.DrawBackgrounds(borderLeft, borderRight, borderTop, borderBottom, lastCandle, candleX)
        self.DrawGrid(borderLeft, borderRight, borderTop, borderBottom, 16)

        highLowExtension = round(maxCandles * self.ss.candleLookaround)

        highLowLastCandle = lastCandle + highLowExtension
        if highLowLastCandle > maxLastCandle:
            highLowLastCandle = maxLastCandle

        highLowFirstCandle = firstCandle - highLowExtension
        if highLowFirstCandle < 0:
            highLowFirstCandle = 0

        # these candles are only used for pricePerPixelc calc.
        highLowCandles = self.candles[highLowFirstCandle:highLowLastCandle + 1]

        highs = [float(c['high']) for c in highLowCandles]
        lows = [float(c['low']) for c in highLowCandles]

        highestHigh = max(highs)
        lowestLow = min(lows)

        deltaPrice = highestHigh - lowestLow
        pricePerPixel = deltaPrice / pricePx

        self.DrawPrices(borderRight, borderTop, borderBottom, 16, limitTop, highestHigh, pricePerPixel)

        prevBlocksSum = 0
        candleBlockI = 0
        candleNum = len(self.candles) - lastCandle
        for i, size in enumerate(reversed(self.sizes)):
            if prevBlocksSum + size >= candleNum:
                candleBlockI = len(self.sizes) - 1 - i
                break
            else:
                prevBlocksSum += size

        for i in range(lastCandle, firstCandle - 1, -1):
            candle = self.candles[i]
            block = self.blocks[candleBlockI]

            candleBodyX = candleX + self.ss.candleGapHalf
            candleColor = block.bullCandleColor

            candleClose = candle['close']
            candleOpen = candle['open']
            candleHigh = candle['high']
            candleLow = candle['low']

            candleBodyTop = limitBottom - round((candleClose - lowestLow) / pricePerPixel)
            candleBodyBottom = limitTop + round((highestHigh - candleOpen) / pricePerPixel)

            if candleClose < candleOpen:
                candleColor = block.bearCandleColor

            if candleBodyTop > candleBodyBottom:
                candleBodyTop, candleBodyBottom = candleBodyBottom, candleBodyTop

            candleMiddleX = candleBodyX + (self.ss.candleWidth // 2)
            candleHighY = limitTop + round((highestHigh - candleHigh) / pricePerPixel)
            candleLowY = limitBottom - round((candleLow - lowestLow) / pricePerPixel)

            # draw the candle's... tail? high-low line? whatever you call it...
            pygame.draw.aaline(self.surf, candleColor, (candleMiddleX, candleHighY), (candleMiddleX, candleLowY))

            # draw the candle's body
            self.surf.fill(candleColor, pygame.Rect(candleBodyX, candleBodyTop, self.ss.candleWidth,
                                                    candleBodyBottom - candleBodyTop + 1))

            candleX -= candleWidthTotal
            candleNum += 1
            if prevBlocksSum + self.sizes[candleBlockI] < candleNum:
                candleBlockI -= 1
                if candleBlockI < 0:
                    candleBlockI = 0

        if self.inp.rmb:
            my = self.inp.mpos[1]
            if my in range(borderTop, borderBottom + 1):
                self.DrawHighlight(my, borderLeft, borderRight,
                                   str(round(self.GetPriceOnPixel(my, limitTop, highestHigh, pricePerPixel), 3)))

        pygame.display.flip()

    def PushBlock(self, cs, block=ChartBlock()):
        block.candlesFrom = len(self.candles)
        self.candles.extend(cs)
        block.candlesTo = len(self.candles)
        self.sizes.append(len(cs))
        self.blocks.append(block)

    def PopBlock(self):
        s = self.sizes.pop()
        del self.candles[-s:]
        b = self.blocks.pop()
        b.candlesFrom = 0
        b.candlesTo = 0
        return b

    def HandleEvent(self, event: pygame.event.EventType):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        else:
            bUpdate = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.inp.MouseButtonDown(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                # 0x1: LMB
                # 0x2: Wheel click
                # 0x3: RMB
                # 0x4: Wheel up
                # 0x5: Wheel down

                self.inp.MouseButtonUp(event)

                if event.button == 0x1:
                    self.stableOffset = self.offset
                elif event.button == 0x2:
                    self.offset = 0
                    self.stableOffset = 0
            elif event.type == pygame.MOUSEMOTION:
                self.inp.MouseMotion(event)

                if self.inp.lmb:
                    self.offset = self.stableOffset + (self.inp.mdelta[0] //
                                                       (self.ss.candleWidth + 2*self.ss.candleGapHalf))
            else:
                bUpdate = False

            if bUpdate:
                self.UpdateSurface()  # update on almost any event, cuz fps is not a problem and also cuz fuck you
