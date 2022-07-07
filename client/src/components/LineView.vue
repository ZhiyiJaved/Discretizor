<template>
  <div id="borderLineDiv">
    <div id='LineView' ref='root'>
      <svg id="svgLine" :width="svgSize.svg.width + 360" :height="svgSize.svg.height">
        <g id="GInformation">
          <text x="20px" :y="svgSize.heightInf" style="fill: rgb(89, 89, 89)">Feature Assessment</text>
        </g>
      </svg>
    </div>
  </div>
</template>

<script>

import * as d3 from "d3";

export default {
  name: "LineView"
  ,
  data: function () {
    return {
      svgSize: {
        svg: {width: 700, height: 377},  // svg全尺寸
        svgLineUp: {width: 700, height: 260},  // 主图尺寸
        svgLineBottom: {width: 700, height: 100},  // 副图尺寸
        heightInf: 20
      },  // 画布大小，高度不超过380
      marginSize: {
        marginUp: {top: 40, right: 15, bottom: 0, left: 45},  // 折线主图边距
        marginBottom: {top: 20, right: 15, bottom: 10, left: 45}  // 折线副图边距
      },
      lineColor: {
        gLineBd: 'rgb(160,211, 251)',
        gLineSg: 'rgb(246, 183, 155)',
        gLineTd: 'yellow'
      },
      scale: {xScaleLine: null, yScaleLine: null},
      xHistScale: null,
      // 半个直方图宽度
      barWidth: null,
      symbol: {
        size: 5,
        position: {
          gLineBd: 250,
          gLineSg: 400,
          gLineTd: 500
        },
        text: {
          gLineBd: 'ratio',
          gLineSg: 'ratio_sg',
          gLineTd: 'tree'
        }
      },
      color: {
        0: '#7986CA',
        1: '#AFD7F7',
        2: '#C8B4E1',
        3: '#E6C9E1',
        4: '#F4E6BA'
      },
      code: {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e'},
      result: {
        curFeature: null,
        curBd: null,
        curSg: null,
        curTd: null,
        reRectSg: null
      },
      resultRecord: {},
      tdRectMousePlace: {on: null, out: null}
    }
  }
  ,
  methods: {
    // 初始化
    initial() {
      for (let key in this.result) {
        this.result[key] = null
      }
      d3.select('#gLineSg').remove()
      d3.select('#gLineTd').remove()
      d3.select('#gDerivative').remove()
      d3.select('#gScatter').remove()
      d3.select('#gRectSg').remove()
      d3.select('#gRectTd').remove()
    },
    // 画各种折线
    drawLine(dataScale, dataLine, gLineName) {
      //  删除相关图
      d3.select(`#${gLineName}`).remove()
      d3.select(`#${gLineName}Symbol`).remove()
      if (gLineName == 'gLineBd') {  // 虽然没有实际意义，是保证图层在上的一种做法
        d3.select(`#gRectCount`).remove()
        d3.select(`#gRectTd`).remove()
        d3.select('#svgLine')
            .append('g')
            .attr('id', `gRectCount`)
            .attr('transform', `translate(${this.marginSize.marginUp.left}, ${this.marginSize.marginUp.top})`)
        var xBorder = this.marginSize.marginBottom.left,
            yBorder = this.marginSize.marginBottom.top + this.svgSize.svgLineUp.height
        d3.select('#svgLine')
            .append('g')
            .attr('id', `gRectTd`)
            .attr('transform', `translate(${xBorder}, ${yBorder})`)
      }
      //  X轴长度
      var length = dataScale.length
      var maxRatio = d3.max(dataScale, value => value.y),
          minRatio = d3.min(dataScale, value => value.y),
          maxIndex = d3.max(dataScale, value => value.x),
          minIndex = d3.min(dataScale, value => value.x)
      //  发送该数据X轴长度
      this.$bus.$emit('PostLength', {length: length})
      // 统一主图边距
      var widthUp = this.svgSize.svgLineUp.width - this.marginSize.marginUp.left - this.marginSize.marginUp.right,
          heightUp = this.svgSize.svgLineUp.height - this.marginSize.marginUp.top - this.marginSize.marginUp.bottom
      // 折线图全局画板
      var gLine = d3.select('#svgLine')
          .append('g')
          .attr('id', `${gLineName}`)
          .attr('transform', `translate(${this.marginSize.marginUp.left}, ${this.marginSize.marginUp.top})`)
      // 折线图X轴比例尺
      var xScaleLine = d3.scaleLinear()
          .domain([minIndex, maxIndex])
          .range([0, widthUp])

      // 折线图Y轴比例尺
      var yScaleLine = d3.scaleLinear()
          .domain([minRatio, maxRatio])
          .range([heightUp, 0])

      // 公开标准图比例尺
      this.scale.xScaleLine = xScaleLine
      this.scale.yScaleLine = yScaleLine
      // 画折线
      gLine.append('g')
          .attr('class', 'path')
          .append('path')
          .datum(dataLine)
          .attr('id', `${gLineName}Line`)
          .attr('fill', 'none')
          .attr('stroke', `${this.lineColor[gLineName]}`)
          .attr('stroke-width', 1.5)
          .attr('d', d3.line()
              .x(d => xScaleLine(d.x))
              .y(d => yScaleLine(d.y))
              .curve(d3.curveMonotoneX)
          )
      // 在class为axis的分组中根据比例尺添加坐标轴
      var lineNumber = 5,
          // lineNumberIndex = 4,
          unitRatio = (maxRatio - minRatio) / lineNumber,
          barWidth = widthUp / (maxIndex - minIndex) / 4
      // 公开数据
      this.barWidth = barWidth
      // unitIndex = (maxIndex - minIndex) / lineNumberIndex
      // gLine.append('g')
      //     .attr('class', 'axis')
      //     .attr('transform', `translate(0, ${heightUp})`)
      //     .call(d3.axisBottom(xScaleLine)
      //         .tickValues([minIndex, Math.round(minIndex + unitIndex * 1), Math.round(minIndex + unitIndex * 2), Math.round(minIndex + unitIndex * 3), Math.round(minIndex + unitIndex * 4), maxIndex])
      //     )
      gLine.append('g')
          .attr('class', 'axis')
          .attr('transform', `translate(${-barWidth}, 0)`)
          .call(d3.axisLeft(yScaleLine)
              .tickValues([minRatio, minRatio + unitRatio * 1, minRatio + unitRatio * 2, minRatio + unitRatio * 3, maxRatio])
              .tickFormat(d3.format(".0%"))
          )
      //  画指示图标
      this.drawSymbol(gLineName)
      //  画指示线
      this.drawDirectedLine(lineNumber, gLine, widthUp, heightUp, barWidth)
    },
    drawSymbol(gLineName) {
      //  绘制图示标志
      var gSymbol = d3.select('#GInformation')
          .append('g')
          .attr('id', `${gLineName}Symbol`)
      gSymbol.append('circle')
          .attr('fill', `${this.lineColor[gLineName]}`)
          .attr('cx', this.symbol.position[`${gLineName}`])
          .attr('cy', this.svgSize.heightInf - this.symbol.size)
          .attr('r', this.symbol.size)
          .on('mouseover', function () {
            d3.select(this)
                .attr('r', '7')
            d3.select(`#${gLineName}Line`)
                .attr('stroke-width', 3)
            d3.select(`#${gLineName}`).raise()
          })
          .on('mouseout', function () {
            d3.select(this)
                .attr('r', '5')
            d3.select(`#${gLineName}Line`)
                .attr('stroke-width', 1.5)
            d3.select(`#${gLineName}`).order()
          })

      gSymbol.append('line')
          .attr('x1', this.symbol.position[`${gLineName}`] - 2 * this.symbol.size)
          .attr('y1', this.svgSize.heightInf - this.symbol.size)
          .attr('x2', this.symbol.position[`${gLineName}`] + 2 * this.symbol.size)
          .attr('y2', this.svgSize.heightInf - this.symbol.size)
          .attr('stroke', `${this.lineColor[gLineName]}`)
      gSymbol.append('text')
          .text(this.symbol.text[`${gLineName}`])
          .attr('x', this.symbol.position[`${gLineName}`] + 3 * this.symbol.size)
          .attr('y', this.svgSize.heightInf)
          .attr('fill', 'rgb(89, 89, 89)')
    },
    drawDirectedLine(lineNumber, gLine, widthUp, heightUp) {
      var unitHeight = heightUp / lineNumber,
          barWidth = this.barWidth
      // 五根指示线
      for (let i = 0; i < lineNumber + 1; i++) {
        gLine.append("line")
            .attr('x1', -barWidth)
            .attr('y1', 0.5 + unitHeight * i)
            .attr('x2', widthUp + 1000)
            .attr('y2', 0.5 + unitHeight * i)
            .attr('stroke-dasharray', '5,5')
            .attr('stroke', 'rgb(187, 187, 187)')
      }
    },
    // 画直方图边框
    drawCountBar(dataCount, gName) {
      d3.select(`#${gName}`).remove()
      var widthBottom = this.svgSize.svgLineBottom.width - this.marginSize.marginBottom.left - this.marginSize.marginBottom.right,
          heightBottom = this.svgSize.svgLineBottom.height - this.marginSize.marginBottom.top - this.marginSize.marginBottom.bottom,
          xBorder = this.marginSize.marginBottom.left,
          yBorder = this.marginSize.marginBottom.top + this.svgSize.svgLineUp.height
      // 挪动
      var gBarCount = d3.select('#svgLine')
          .append('g')
          .attr('id', `${gName}`)
          .attr('transform', `translate(${xBorder}, ${yBorder})`)
      this.drawBar(dataCount, gBarCount, widthBottom, heightBottom)
    },
    // 画直方图
    drawBar(dataCount, gBarCount, widthBottom, heightBottom) {
      var countMax = d3.max(dataCount, d => d.y)
      var dataCountPositive = dataCount.filter(value => value.y >= 0.1 * countMax)
      var dataCountNegative = dataCount.filter(value => value.y < 0.1 * countMax)
      var xScaleLine = this.scale.xScaleLine,
          barWidth = this.barWidth
      // 柱形图Y轴比例尺
      var yScaleLine = d3.scaleLinear()
          .domain([0, countMax])
          .range([0, heightBottom])
      // 画标签
      gBarCount.selectAll('text.tipCount')
          .data(dataCount)
          .enter()
          .append('text')
          .attr('class', 'tipCount')
          .attr('x', d => xScaleLine(d.x) - barWidth / 2)
          .attr('y', heightBottom + barWidth)
          .style('font-size', `${barWidth}px`)
          .text(d => `${d3.format('d')(d.x)}`)
      // 画正常的
      gBarCount.append('g')
          .attr('id', 'barCountPositive')
          .selectAll('rect')
          .data(dataCountPositive)
          .enter()
          .append('rect')
          .attr('x', d => xScaleLine(d.x) - barWidth)
          .attr('y', d => heightBottom - yScaleLine(d.y))
          .attr('width', barWidth * 2)
          .attr('height', d => yScaleLine(d.y))
          .attr('fill', 'rgb(0, 143, 196)')
          .attr('opacity', 0.7)
          .on('mouseover', function (d) {
            gBarCount.raise()
            d3.select(this)
                .attr('opacity', 1)
            var barCountPositive = d3.select(`#barCountPositive`)
            barCountPositive.append('text')
                .attr('id', 'tip')
                .attr('x', xScaleLine(d.x) - 3.5 * (barWidth / 2))
                .attr('y', heightBottom - yScaleLine(d.y) - barWidth)
                .style('font-size', `${1.5 * barWidth}px`)
                .text(`${d3.format('d')(d.y)}`)
          })
          .on('mouseout', function () {
            d3.select(this)
                .attr('opacity', 0.7)
            d3.select(`#barCountPositive`).order()
            d3.select(`#tip`).remove()
          })
      // 画不正常的
      gBarCount.append('g')
          .attr('id', 'barCountNegative')
          .selectAll('rect')
          .data(dataCountNegative)
          .enter()
          .append('rect')
          .attr('x', d => xScaleLine(d.x) - barWidth)
          .attr('y', d => heightBottom - yScaleLine(d.y))
          .attr('width', barWidth * 2)
          .attr('height', d => yScaleLine(d.y))
          .attr('fill', 'rgb(231, 20, 71)')
          .attr('opacity', 0.7)
          .on('mouseover', function (d) {
            gBarCount.raise()
            d3.select(this)
                .attr('opacity', 1)
            var barCountPositive = d3.select(`#barCountNegative`).raise()
            barCountPositive.append('text')
                .attr('id', 'tip')
                .attr('x', xScaleLine(d.x) - barWidth / 2)
                .attr('y', heightBottom - yScaleLine(d.y) - 5)
                .text(`${d3.format('d')(d.y)}`)
          })
          .on('mouseout', function () {
            d3.select(this)
                .attr('opacity', 0.7)
            d3.select(`#barCountPositive`).order()
            d3.select(`#tip`).remove()
          })
      this.drawCountRect(dataCountNegative)
    },
    // 数量图示
    drawCountRect(dataCountNegative) {
      var heightUp = this.svgSize.svgLineUp.height - this.marginSize.marginUp.top - this.marginSize.marginUp.bottom,
          xScaleLine = this.scale.xScaleLine,
          gRectCount = d3.select('#gRectCount'),
          indexMax = d3.max(dataCountNegative, d => d.x),
          barWidth = this.barWidth
      gRectCount.selectAll(`rect.count`)
          .data(dataCountNegative)
          .enter()
          .append('rect')
          .attr('class', 'count')
          .attr('x', d => {
            let x
            if (xScaleLine(d.x) - 2 * barWidth < 0) x = xScaleLine(d.x) - barWidth
            else x = xScaleLine(d.x) - 2 * barWidth
            return x
          })
          .attr('y', 0)
          .attr('width', d => {
            let width
            if (xScaleLine(d.x) - 2 * barWidth < 0) width = 3 * barWidth
            else if (d.x != indexMax) width = 4 * barWidth
            else width = 3 * barWidth
            return width
          })
          .attr('height', heightUp)
          .attr('fill', 'rgb(235, 239, 241)')
          .on('mouseover', function (d) {
            d3.select(this)
                .attr('fill', 'darkgray')
            gRectCount.append('text')
                .attr('id', 'tip')
                .attr('x', xScaleLine(d.x) - 40)
                .attr('y', heightUp + 15)
                .style('font-size', `11px`)
                .text(`area ${d3.format('d')(d.x)} don't have enough cases`)
          })
          .on('mouseout', function () {
            d3.select(this)
                .attr('fill', `rgb(235, 239, 241)`)
            d3.select(`#tip`).remove()
          })
    },
    // Sg拟合图示
    drawRectSg(dataLine, dataRecord, gName) {
      var xScaleLine = this.scale.xScaleLine,
          yscaleLine = this.scale.yScaleLine,
          unitWidth = this.barWidth * 4,
          barWidth = this.barWidth,
          widthBottom = this.svgSize.svgLineBottom.width - this.marginSize.marginBottom.left - this.marginSize.marginBottom.right
      d3.select(`#${gName}`).remove()
      var gRectSg = d3.select('#svgLine')
          .append('g')
          .attr('id', `${gName}`)
          .attr('transform', `translate(${this.marginSize.marginUp.left}, ${this.marginSize.marginUp.top})`)
      var gRect = gRectSg.append('g')
              .attr('id', 'gRectSgTrue'),
          gLineMedian = gRectSg.append('g')
              .attr('id', 'gRectSgMedian'),
          gLineMax = gRectSg.append('g')
              .attr('id', 'gLineSgMax'),
          gLineMin = gRectSg.append('g')
              .attr('id', 'gLineSgMin')
      for (let index in dataRecord) {
        var temp = dataRecord[index]
        // 画色块
        // 四分位数色块
        gRect.selectAll(`rect.${this.code[index]}`)
            .data(temp)
            .enter()
            .append('rect')
            .attr('class', this.code[index])
            .attr('x', d => {
              if (xScaleLine(dataLine[d[0]].x) == 0) return xScaleLine(dataLine[d[0]].x) - barWidth  //为美化考虑，第一个拓宽些
              else return xScaleLine(dataLine[d[0]].x) - 2 * barWidth
            })
            .attr('y', d => {
                  var tempLine = dataLine.slice(d[0], d[1] + 1)  // 切片要包括下一个
                  tempLine.sort((first, second) => first.y - second.y)  // 先排序后取分位数
                  var topTempLine = yscaleLine(d3.quantile(tempLine, 0.75, d => d.y))
                  return topTempLine
                }
            )
            .attr('width', d => {
              let width
              if (xScaleLine(dataLine[d[0]].x) == 0) width = (d[1] - d[0] + 1) * unitWidth - barWidth //为美化考虑，第一个拓宽些
              else if ((xScaleLine(dataLine[d[0]].x) + (d[1] - d[0] + 1) * unitWidth + barWidth) == widthBottom) width = (d[1] - d[0] + 1) * unitWidth //最后一个也宽一些
              else width = (d[1] - d[0] + 1) * unitWidth
              return width
            })  // d[0]只是序号，需要对应的x值
            .attr('height', d => {
              var tempLine = dataLine.slice(d[0], d[1] + 1)
              tempLine.sort((first, second) => first.y - second.y)
              var topTempLine = yscaleLine(d3.quantile(tempLine, 0.75, d => d.y)),
                  bottomTempLine = yscaleLine(d3.quantile(tempLine, 0.25, d => d.y))
              return bottomTempLine - topTempLine
            })
            .attr('fill', this.color[index])
            .attr('opacity', '0.5')
            .on('mouseover', function (d) {
              // 提升图层
              d3.select(`#${gName}`).raise()
              // 改变显示
              d3.select(this)
                  .attr('opacity', '1')
              // 增加显示标签
              // var pos = d3.mouse(this)
              var start = dataLine[d[0]].x,
                  end = dataLine[d[1]].x
              var tempLine = dataLine.slice(d[0], d[1] + 1)  // 切片要包括下一个
              tempLine.sort((first, second) => first.y - second.y)
              var median = d3.median(tempLine, d => d.y),
                  maximum = d3.max(tempLine, d => d.y)
              // 如果没有标签 则添加
              if (d3.select('#tip')) {
                gLineMin.append('text')
                    .attr('id', 'tip')
                    .attr('x', xScaleLine(start))
                    .attr('y', yscaleLine(maximum) - 10)
                    .text(`area:${start}-${end} median:${d3.format('.1%')(median)}`)
              }
            })
            .on('mouseout', function () {
              // 恢复显示
              d3.select(this)
                  .attr('opacity', '0.5')
              // 顺序调整
              d3.select(`#${gName}`).order()
              // 删除标签
              d3.select('#tip').remove()
            })
        // 最大值色块
        gLineMax.selectAll(`rect.${this.code[index]}`)
            .data(temp)
            .enter()
            .append('rect')
            .attr('class', this.code[index])
            .attr('x', d => {
              if (xScaleLine(dataLine[d[0]].x) == 0) return xScaleLine(dataLine[d[0]].x) - barWidth  //为美化考虑，第一个拓宽些
              else return xScaleLine(dataLine[d[0]].x) - 2 * barWidth
            })
            .attr('y', d => {
              var tempLine = dataLine.slice(d[0], d[1] + 1)  // 切片要包括下一个
              var maxTempLine = yscaleLine(d3.max(tempLine, d => d.y))
              return maxTempLine
            })
            .attr('width', d => {
              let width
              if (xScaleLine(dataLine[d[0]].x) == 0) width = (d[1] - d[0] + 1) * unitWidth - barWidth //为美化考虑，第一个拓宽些
              else if ((xScaleLine(dataLine[d[0]].x) + (d[1] - d[0] + 1) * unitWidth + barWidth) == widthBottom) width = (d[1] - d[0] + 1) * unitWidth //最后一个也宽一些
              else width = (d[1] - d[0] + 1) * unitWidth
              return width
            })
            .attr('height', d => {
              var tempLine = dataLine.slice(d[0], d[1] + 1)  // 切片要包括下一个
              tempLine.sort((first, second) => first.y - second.y)
              var maxTempLine = yscaleLine(d3.max(tempLine, d => d.y)),
                  topTempLine = yscaleLine(d3.quantile(tempLine, 0.75, d => d.y))
              return topTempLine - maxTempLine
            })
            .attr('fill', this.color[index])
            .attr('opacity', '0.2')
            .on('mouseover', function (d) {
              // 提升图层
              d3.select(`#${gName}`).raise()
              // 改变显示
              d3.select(this)
                  .attr('opacity', '1')
              // 增加显示标签
              var start = dataLine[d[0]].x,
                  end = dataLine[d[1]].x
              var tempLine = dataLine.slice(d[0], d[1] + 1)  // 切片要包括下一个
              tempLine.sort((first, second) => first.y - second.y)
              var quartile = d3.quantile(tempLine, 0.75, d => d.y),
                  maximum = d3.max(tempLine, d => d.y)
              // 如果没有标签 则添加
              if (d3.select('#tip')) {
                gLineMin.append('text')
                    .attr('id', 'tip')
                    .attr('x', xScaleLine(start))
                    .attr('y', yscaleLine(maximum) - 10)
                    .text(`area:${start}-${end} upper quartiles:${d3.format('.1%')(quartile)} maximum:${d3.format('.1%')(maximum)}`)
              }
            })
            .on('mouseout', function () {
              // 恢复显示
              d3.select(this)
                  .attr('opacity', '0.2')
              // 顺序调整
              d3.select(`#${gName}`).order()
              // 删除标签
              d3.select('#tip').remove()
            })
        // 最小值色块
        gLineMin.selectAll(`rect.${this.code[index]}`)
            .data(temp)
            .enter()
            .append('rect')
            .attr('class', this.code[index])
            .attr('x', d => {
              if (xScaleLine(dataLine[d[0]].x) == 0) return xScaleLine(dataLine[d[0]].x) - barWidth  //为美化考虑，第一个拓宽些
              else return xScaleLine(dataLine[d[0]].x) - 2 * barWidth
            })
            .attr('y', d => {
              var tempLine = dataLine.slice(d[0], d[1] + 1)  // 切片要包括下一个
              tempLine.sort((first, second) => first.y - second.y)
              var bottomTempLine = yscaleLine(d3.quantile(tempLine, 0.25, d => d.y))
              return bottomTempLine
            })
            .attr('width', d => {
              let width
              if (xScaleLine(dataLine[d[0]].x) == 0) width = (d[1] - d[0] + 1) * unitWidth - barWidth //为美化考虑，第一个拓宽些
              else if ((xScaleLine(dataLine[d[0]].x) + (d[1] - d[0] + 1) * unitWidth + barWidth) == widthBottom) width = (d[1] - d[0] + 1) * unitWidth //最后一个也宽一些
              else width = (d[1] - d[0] + 1) * unitWidth
              return width
            })
            .attr('height', d => {
              var tempLine = dataLine.slice(d[0], d[1] + 1)  // 切片要包括下一个
              tempLine.sort((first, second) => first.y - second.y)
              var minTempLine = yscaleLine(d3.min(tempLine, d => d.y)),
                  bottomTempLine = yscaleLine(d3.quantile(tempLine, 0.25, d => d.y))
              return minTempLine - bottomTempLine
            })
            .attr('fill', this.color[index])
            .attr('opacity', '0.2')
            .on('mouseover', function (d) {
              // 提升图层
              d3.select(`#${gName}`).raise()
              // 改变显示
              d3.select(this)
                  .attr('opacity', '1')
              // 增加显示标签
              // var pos = d3.mouse(this)
              var start = dataLine[d[0]].x,
                  end = dataLine[d[1]].x
              var tempLine = dataLine.slice(d[0], d[1] + 1)  // 切片要包括下一个
              tempLine.sort((first, second) => first.y - second.y)
              var quartile = d3.quantile(tempLine, 0.25, d => d.y),
                  minimum = d3.min(tempLine, d => d.y),
                  maximum = d3.max(tempLine, d => d.y)
              // 如果没有标签 则添加
              if (d3.select('#tip')) {
                gLineMin.append('text')
                    .attr('id', 'tip')
                    .attr('x', xScaleLine(start))
                    .attr('y', yscaleLine(maximum) - 10)
                    .text(`area:${start}-${end} lower quartiles:${d3.format('.1%')(quartile)} minimum:${d3.format('.1%')(minimum)}`)
              }
            })
            .on('mouseout', function () {
              // 恢复显示
              d3.select(this)
                  .attr('opacity', '0.2')
              // 顺序调整
              d3.select(`#${gName}`).order()
              // 删除标签
              d3.select('#tip').remove()
            })
        // 中位线
        gLineMedian.selectAll(`line.${this.code[index]}`)
            .data(temp)
            .enter()
            .append('line')
            .attr('class', this.code[index])
            .attr('x1', d => {
              if (xScaleLine(dataLine[d[0]].x) == 0) return xScaleLine(dataLine[d[0]].x) - barWidth  //为美化考虑，第一个拓宽些
              else return xScaleLine(dataLine[d[0]].x) - 2 * barWidth
            })
            .attr('y1', d => {
              var tempLine = dataLine.slice(d[0], d[1] + 1)  // 切片要包括下一个
              tempLine.sort((first, second) => first.y - second.y)
              var medianTempLine = yscaleLine(d3.median(tempLine, d => d.y))
              return medianTempLine
            })
            .attr('x2', d => xScaleLine(dataLine[d[0]].x) + (d[1] - d[0]) * unitWidth)
            .attr('x2', d => {
              let x2
              if (xScaleLine(dataLine[d[0]].x) == 0) x2 = (xScaleLine(dataLine[d[0]].x) - barWidth) + ((d[1] - d[0] + 1) * unitWidth - barWidth) //为美化考虑，第一个拓宽些
              else if ((xScaleLine(dataLine[d[0]].x) - 2 * barWidth) + ((d[1] - d[0] + 1) * unitWidth) > widthBottom) x2 = widthBottom   // 不超出去
              else x2 = (xScaleLine(dataLine[d[0]].x) - 2 * barWidth) + ((d[1] - d[0] + 1) * unitWidth)
              return x2
            })
            .attr('y2', d => {
              var tempLine = dataLine.slice(d[0], d[1] + 1),  // 切片要包括下一个
                  medianTempLine = yscaleLine(d3.median(tempLine, d => d.y))
              return medianTempLine
            })
            .attr('stroke', this.color[index])
            .attr('stroke-width', 3)
      }
    },
    // Sg数据波动
    drawDerivativeLine(dataDerivative, gName) {
      d3.select(`#${gName}`).remove()
      // 确定尺寸
      var widthBottom = this.svgSize.svgLineBottom.width - this.marginSize.marginBottom.left - this.marginSize.marginBottom.right,
          heightBottom = this.svgSize.svgLineBottom.height - this.marginSize.marginBottom.top - this.marginSize.marginBottom.bottom,
          xBorder = this.marginSize.marginBottom.left,
          yBorder = this.marginSize.marginBottom.top + this.svgSize.svgLineUp.height,
          barWidth = this.barWidth,
          yScaleLine = d3.scaleLinear()
              .domain([d3.min(dataDerivative, d => d.y), d3.max(dataDerivative, (d) => d.y)])
              .range([heightBottom, 0]),
          xScaleLine = d3.scaleLinear()
              .domain([d3.min(dataDerivative, d => d.x), d3.max(dataDerivative, (d) => d.x) + 1])  // 加一很关键
              .range([barWidth * 2, widthBottom + barWidth * 2])
      // 折线图全局画板
      var gDerivative = d3.select('#svgLine')
          .append('g')
          .attr('id', `gDerivative`)
          .attr('transform', `translate(${xBorder}, ${yBorder})`)
      // 画出指示点
      this.drawDerivativeCircle(dataDerivative, gDerivative, xScaleLine, yScaleLine)
      //指示线
      gDerivative.append("line")
          .attr('x1', -barWidth)
          .attr('y1', yScaleLine(0))
          .attr('x2', widthBottom + barWidth)
          .attr('y2', yScaleLine(0))
          .attr('stroke-dasharray', '2,2')
          .attr('stroke', 'rgb(187, 187, 187)')
      gDerivative.append("text")
          .attr('x', -32)
          .attr('y', yScaleLine(0) + 3)
          .text("0%")
          .style('font-size', '11px')
          .style('font-family', 'sans-serif')
    },
    drawDerivativeCircle(dataDerivative, gDerivative, xScaleLine, yScaleLine) {
      // 折线图Y轴比例尺
      var dataDerivativePositive = dataDerivative.filter(value => value.y > 0),
          dataDerivativeNegative = dataDerivative.filter(value => value.y < 0)
      // 指示直方图
      var grectDerivative = gDerivative.append('g')
          .attr('id', 'rectDerivative')
      grectDerivative.selectAll(`rect.derivativePositive`)
          .data(dataDerivativePositive)
          .enter()
          .append('rect')
          .attr('class', 'derivativePositive')
          .attr('x', d => xScaleLine(d.x) - 0.5)
          .attr('y', d => yScaleLine(d.y))
          .attr('width', 1)
          .attr('height', d => (yScaleLine(0) - yScaleLine(d.y)))
          .attr('fill', 'rgb(55, 141, 191)')
          .attr('opacity', 0.7)
      grectDerivative.selectAll(`rect.derivativeNegative`)
          .data(dataDerivativeNegative)
          .enter()
          .append('rect')
          .attr('class', 'derivativeNegative')
          .attr('x', d => xScaleLine(d.x) - 0.5)
          .attr('y', yScaleLine(0))
          .attr('width', 1)
          .attr('height', d => yScaleLine(d.y) - yScaleLine(0))
          .attr('fill', 'rgb(224, 113, 28)')
          .attr('opacity', 0.7)
      //指示点
      var gcircleDerivative = gDerivative.append('g')
          .attr('id', 'circleDerivative')
      gcircleDerivative.selectAll('circle.derivativePositive')
          .data(dataDerivativePositive)
          .enter()
          .append('circle')
          .attr('class', 'derivativePositive')
          .attr('fill', 'rgb(55, 141, 191)')
          .attr('cx', d => xScaleLine(d.x))
          .attr('cy', d => yScaleLine(d.y))
          .attr('r', 1)
          .attr('opacity', 0.7)
      gcircleDerivative.selectAll('circle.derivativeNegative')
          .data(dataDerivativeNegative)
          .enter()
          .append('circle')
          .attr('class', 'derivativeNegative')
          .attr('fill', 'rgb(224, 113, 28)')
          .attr('cx', d => xScaleLine(d.x))
          .attr('cy', d => yScaleLine(d.y))
          .attr('r', 1)
          .attr('opacity', 0.7)
    },
    // 树离散化图示
    drawRectTd(dataLine, dataRecord, gName) {
      d3.select(`#${gName}True`).remove()
      // 调用外部函数需要保存全局对象
      var that = this
      // 确定尺寸
      var heightBottom = this.svgSize.svgLineBottom.height - this.marginSize.marginBottom.top - this.marginSize.marginBottom.bottom,
          xScale = this.scale.xScaleLine
      // 树离散化示意图全局画板
      var gRect = d3.select(`#${gName}`)
          .append('g')
          .attr('id', `${gName}True`)
      // 单个柱形间隔
      var unitWidth = this.barWidth * 2,
          number = +d3.max(Object.keys(dataRecord)) + 1
      // 绘画矩形
      for (let index in dataRecord) {
        gRect.selectAll(`rect_${this.code[index]}`)  // 很神奇，不知道为什么就可以
            .data(dataRecord[index])
            .enter()
            .append('rect')
            .attr('id', `tdRect_${index}`)
            .attr('class', `tdRect`)
            .attr('x', d => {
              var x
              if (index == 0) x = xScale(dataLine[d[0]].x) - 0.5 * unitWidth
              else x = xScale(dataLine[d[0]].x) - unitWidth
              return x
            })  // 注意x轴数据
            .attr('y', 0)
            .attr('width', d => {
              var width
              if (index == 0) width = ((d[1] - d[0]) + 1) * 2 * unitWidth - 0.5 * unitWidth
              else width = ((d[1] - d[0]) + 1) * 2 * unitWidth
              return width
            })  // d[0]只是序号，需要对应的x值
            .attr('height', heightBottom)
            .attr('fill', () => {
              var color
              if (index % 2 == 0) color = 'rgb(235, 239, 241)'
              else color = 'rgb(1, 1, 1, 0)'
              return color
            })
            //  区间标记
            .attr('start', d => dataLine[d[0]].x)
            .attr('end', d => dataLine[d[1]].x)
            .attr('last', () => {
              if (index == number - 1) return true
            })
            // 表现形式
            .on('mouseover', this.mouseoverTdRect(dataLine, xScale, gRect))
            .on('mouseout', function () {
              // 更改透明度
              d3.selectAll('.tdRect').attr('opacity', '1')
              // 降低图层
              d3.select(`#${gName}`).lower()
              // 恢复显示
              d3.select(this)
                  .attr('stroke', 'none')
                  .on('mousemove', null)
              // 删除标签
              d3.select('#tip').remove()
            })
            .on('mousedown', function () {
              if (index < number - 1) {
                // 提升图层
                d3.select(`#${gName}`).raise()
                // 改变显示文字
                d3.select('#tip').text("Don't release your mouse until you have made it where you want")
                // 改变透明度
                d3.selectAll('.tdRect').attr('opacity', '0.7')
                // 绑定移动事件
                var startPosition = d3.mouse(this)[0]
                d3.select(this).on('mousemove', that.mousemoveTdRect(startPosition, unitWidth, number))
              }
            })
            .on('mouseup', function (d) {
              if (index < number - 1) {
                d3.select(`#${gName}`).lower()
                d3.select(this).on('mousemove', null)
                d3.selectAll('.tdRect').attr('opacity', '1')
                var start = dataLine[d[0]].x,
                    end = dataLine[d[1]].x
                d3.select('#tip').text(`area:${start}-${end}, press the mouse and move to change area.`)
              }
            })
      }
    },
    mouseoverTdRect(dataLine, xScale, gRect) {
      return function (d) {
        var cur = d3.select(this)
        var start = +d3.select(this).attr('start'),
            end = +d3.select(this).attr('end')
        // 改变显示与标签
        cur.attr('stroke-dasharray', '5,5')
            .attr('stroke', 'rgb(187, 187, 187)')
        // 如果没有标签 则添加
        if (d3.select('#tip')) {
          gRect.append('text')
              .attr('id', 'tip')
              .attr('x', xScale(dataLine[d[0]].x))
              .attr('y', -5)
              .text(`area:${start}-${end}, press the mouse and move to change area.`)
        }
      }
    },
    mousemoveTdRect(startPosition, unitWidth, number) {
      var that = this
      return function () {
        var cur = d3.select(this),
            cur_width = +cur.attr('width'),
            // 注意不同变量类型
            cur_index = +cur.attr('id').slice(7, 8),
            move = d3.mouse(this)[0] - startPosition,
            changeStandard = unitWidth * 1.5
        if (move > 0) var move_unit = Math.floor(move / changeStandard)
        else move_unit = Math.ceil(move / changeStandard)
        if (move_unit != 0) {
          // 改变当前end标签
          var cur_end = +cur.attr('end')
          cur.attr('end', cur_end + move_unit)
          that.$bus.$emit('changeCurResult', {index: cur_index, start: 0, end: move_unit})
          // 且一旦触发便会将初始点改变，从而延缓速度
          startPosition = d3.mouse(this)[0]
          cur.attr('width', cur_width + move_unit * 2 * unitWidth)
          // 所有的显示块都向后挪，并改变标签
          for (let i = cur_index + 1; i < number; i++) {
            if (d3.select(`#tdRect_${i}`).attr('last') === 'true') {
              that.$bus.$emit('changeCurResult', {index: i, start: move_unit, end: 0})
              let next = d3.select(`#tdRect_${i}`),
                  next_x = +next.attr('x'),
                  next_width = +next.attr('width'),
                  next_start = +next.attr('start')
              next.attr('x', next_x + move_unit * 2 * unitWidth)
              next.attr('width', next_width - move_unit * 2 * unitWidth)
              next.attr('start', next_start + move_unit)
              if (next.attr('start') > next.attr('end')) {
                next.remove()
                var new_last = d3.select(`#tdRect_${i - 1}`)
                new_last.attr('last', true)
                new_last.on('mousedown', null)
              }
              break
            } else {
              that.$bus.$emit('changeCurResult', {index: i, start: move_unit, end: move_unit})
              let next = d3.select(`#tdRect_${i}`),
                  next_x = +next.attr('x'),
                  next_start = +next.attr('start'),
                  next_end = +next.attr('end')
              next.attr('x', next_x + move_unit * 2 * unitWidth)
              next.attr('start', next_start + move_unit)
              next.attr('end', next_end + move_unit)
            }
          }
        }
      }
    },
    watchBd(d) {
      // 初始化界面
      this.initial()
      // 发送并记录当前特征
      this.result.curFeature = d['feature']
      // 缓存当前Bd参数
      this.result.curBd = d
      // 获取基础数据
      this.$axios.post('/get_feature_data', d)
          .then((res) => {
            var data = res.data
            console.log(data)
            this.drawLine(data[0].value, data[0].value, 'gLineBd')
            this.$axios.post('/count_feature_data', d)  // 画好折线后再画柱状图
                .then((res) => {
                  var data = res.data
                  console.log(data)
                  this.drawCountBar(data[d['feature']], 'gBarCount')
                })
                .catch((error) => {
                  console.log('count_feature_data', error)
                })
          })
          .catch((error) => {
            console.log('get_feature_data', error)
          })
    },
    watchSg(d) {
      // 发送并记录当前数据
      this.result.curSg = d
      this.$axios.post('/sg_feature_data', d)
          .then((res) => {
            var data = res.data
            console.log(data)
            d3.select('#derivativeBorderLeft').remove()
            this.$bus.$emit('Scatter', data[3].value)  // 返回值的第三个传出
            this.drawLine(data[0].value, data[1].value, 'gLineSg')
            this.drawDerivativeLine(data[2].value, `gDerivative`)
            this.drawRectSg(data[1].value, data[4].value, 'gRectSg')
          })
          .catch((error) => {
            console.log('sg_feature_data', error)
          })
    },
    watchTd(d) {
      // 发送并记录
      this.result.curTd = d
      this.$axios.post('/td_feature_data', d)
          .then((res) => {
            var data = res.data
            console.log(data)
            // this.drawLine(data[0].value, data[1].value, 'gLineTd')
            this.drawRectTd(data[0].value, data[2].value, 'gRectTd')
            this.$bus.$emit('postCurResult', data[2].value)
          })
          .catch((error) => {
            console.log('td_feature_data', error)
          })
    },
    reRectSg(d) {
      this.result.reRectSg = d
      this.drawRectSg(d[0].value, d[3].value, 'gRectSg')
    }
  }
  ,
  mounted() {
    //  初始化，主要功能是恢复布局并收取横坐标的参数
    this.$bus.$on('Init', d => {
      if (Object.keys(this.resultRecord).indexOf(d['feature']) >= 0) {
        var curBd = this.resultRecord[d['feature']].curBd,
            curSg = this.resultRecord[d['feature']].curSg,
            curTd = this.resultRecord[d['feature']].curTd
        if (curBd != null) this.watchBd(curBd)
        if (curTd != null) this.watchTd(curTd)
        if (curSg != null) this.watchSg(curSg)
        // 传出保存的sg参数，复盘散点图的recolor功能
        this.$bus.$emit('postCurSg', curSg)
      } else {
        this.watchBd(d)
      }
    })
    //  切换间格
    this.$bus.$on('Bd', d => {
      this.watchBd(d)
    })
    //  信息展示
    this.$bus.$on('Sg', d => {
      this.watchSg(d)
    })
    //  离散化
    this.$bus.$on('Td', d => {
      this.watchTd(d)
    })
    //  重新作散点方块
    this.$bus.$on('reRectSg', d => {
      this.reRectSg(d)
    })
    this.$bus.$on('SaveResult', () => {
      this.resultRecord[this.result.curFeature] = {}
      for (let key in this.result) {
        this.resultRecord[this.result.curFeature][key] = this.result[key]
      }
    })
  }
}
</script>

<style>
.axis path,
.axis line {
  fill: none;
  stroke: rgb(187, 187, 187);
  shape-rendering: crispEdges;
}

.axis text {
  font-family: sans-serif;
  font-size: 11px;
}

.tipCount {
  font-family: sans-serif;
}

#tip {
  font-family: sans-serif;
  font-size: 11px;
}

#tip2 {
  font-family: sans-serif;
  font-size: 11px;
}

#borderLineDiv {
  --bs-gutter-x: 0;
  height: 378px;
  border-width: 0 0 1px 0;
  border-style: solid;
  border-color: rgb(240, 242, 245);
}

#LineView {
  --bs-gutter-x: 0;
  height: 377px;
  border-width: 0 0 1px 2px;
  border-style: solid;
  border-color: rgb(232, 232, 232);
  border-radius: 2px
}

</style>