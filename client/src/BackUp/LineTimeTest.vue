<template>
  <div id='line-time-test' ref='mainRef'>
    <div id='divPanel'></div>
    <div id='divLine'></div>
    <div id='divTree'></div>
    <div id='divResult'></div>
    <div id='divDiscrtization'></div>
  </div>
</template>
<style>
#line-time-test {
  height: 720px;
  width: 1427px; /*整体画布减边距*/
  border-top: 1px solid #ffffff;
  box-shadow: darkgrey 10px 10px 30px 5px;
  font-size: 20px;
  color: black;
  position: absolute;
  top: 50px;
  left: 3px;
}

#divPanel {
  height: 300px;
  width: 300px;
  position: absolute;
  left: 3px;
  top: 0;
  border-top: 1px solid #ffffff;
  box-shadow: darkgrey 5px 5px 15px 2px;
  display: block;
}

#divResult {
  height: 300px;
  width: 800px;
  position: absolute;
  top: 0px;
  left: 309px;
  border-top: 1px solid #ffffff;
  box-shadow: darkgrey 10px 10px 30px 5px;
}

#divLine {
  height: 400px;
  width: 800px;
  position: absolute;
  top: 310px;
  left: 3px;
  border-top: 1px solid #ffffff;
  box-shadow: darkgrey 10px 10px 30px 5px;
  font-size: 20px;
  color: black;
}

#divTree {
  height: 400px;
  width: 300px;
  position: absolute;
  top: 310px;
  left: 809px;
  border-top: 1px solid #ffffff;
  box-shadow: darkgrey 10px 10px 30px 5px;
}

#divDiscrtization {
  height: 720px;
  width: 312px;
  position: absolute;
  top: 0;
  left: 1115px;
  border-top: 1px solid #ffffff;
  box-shadow: darkgrey 10px 10px 30px 5px;
}

#controlPanel {
  position: absolute;
  bottom: 0;
  height: 150px;
  width: 1200px;
}

#changeDiv {
  position: absolute;
  left: 0;
  top: 645px;
  width: 200px;
}

#backDiv {
  position: absolute;
  left: 1000px;
  top: 645px;
  width: 200px;
}

/*折线操作面板三块*/
#bdDiv {
  position: absolute;
  left: 25px;
  top: 10px;
}

#npDiv {
  position: absolute;
  left: 25px;
  top: 40px;
}

#tdDiv {
  position: absolute;
  left: 25px;
  top: 60px;
}

#scatterDiv {
  position: absolute;
  left: 400px;
  top: 70px;
}

#timeButton {
  position: absolute;
  left: 75px; /* 居中 */
  top: 150px;
}

.axis line {
  fill: none;
  stroke: black;
  shape-rendering: crispEdges;
}
</style>
<script>
import * as d3 from 'd3'

export default {
  name: 'LineTimeTest',
  data() {
    return {}
  },
  props: [],
  methods: {
    initialize() {
      //  初始化面板添加标题
      var initialPanel = d3.select('#divPanel')
      initialPanel
          .append('svg')
          .attr('width', '500px')
          .append('text')
          .attr('x', '120px')
          .attr('y', '35px')
          .text('Panel')

      //  添加操作面板与标题
      var svgPanelTitle = d3.select('#line-time-test')
          .append('div')
          .attr('id', 'controlPanel')
          .style('display', 'block')
          .append('svg')
          .attr('width', '500px')
      svgPanelTitle.append('text')
          .attr('x', '30px')
          .attr('y', '35px')
          .attr('id', 'titleControlPanel')
      //  添加初始化按钮
      initialPanel.append('input')
          .attr('type', 'button')
          .attr('value', 'initialize the time data')
          .attr('id', 'timeButton')
          .on('click', () => {
                this.$axios.get('/get_data_time')
                    .then((res) => {
                      var data = res.data
                      console.log(data)
                      this.drawScatter(data[1].value)
                      this.drawInitialLine(data[0].value)
                      this.drawLinePanel()
                      // this.addChangeDiv()
                      // d3.select('#controlPanel').style('display', 'block') // 显示操作面板
                      // d3.select('#backDiv').style('display', 'block')  // 显示返回按钮
                    })
                    .catch((error) => {
                      console.log('get_data_time', error)
                    })
              }
          )

      //  添加返回按钮
      d3.select('#line-time-test')
          .append('div')
          .attr('id', 'backDiv')
          .attr('align', 'right')
          .style('display', 'none')
          .append('input')
          .attr('type', 'button')
          .attr('value', 'Back to Initial Panel')
          .attr('class', 'backButton')
          .on('click', function () {
            d3.select("#initialPanel").style('display', 'block')  // 显示初始化面板
            d3.select('#controlPanel').style('display', 'none')  // 隐藏操作面板
            d3.select('#svgScatter').remove() // 删除散点图
            d3.select('#svgLine').remove()  // 删除折线图
            d3.select('#changeDiv').remove()  // 删除切换按钮
            d3.select('#titleControlPanel').remove()  //删除操作标题
            d3.select('#backDiv').style('display', 'none')  //删除操作标题
          })
    }
    ,
    drawInitialLine(dataLine) {
      // 统一主图边距
      var margin = {top: 80, right: 20, bottom: 80, left: 40},
          width = 800 - margin.left - margin.right,
          height = 400 - margin.top - margin.bottom

      // 折线图全局画板
      var svgLine = d3.select('#divLine').append('svg')
          .attr('id', 'svgLine')
          .attr('width', 800).attr('height', 400)
          .attr('visibility', 'visible')

      // 基本折线图-主视图偏移容器
      var gLineBd = svgLine.append('g')
          .attr('transform', `translate(${margin.left}, ${margin.top})`)

      // 折线图X轴比例尺
      var xScaleLine = d3.scaleLinear()
          .domain([0, d3.max(dataLine, function (d) {
            return d.x
          })])
          .range([0, width])

      // 折线图Y轴比例尺
      var yScaleLine = d3.scaleLinear()
          .domain([0, d3.max(dataLine, function (d) {
            return d.y
          })])
          .range([height, 0])
      // 画折线
      gLineBd.append('g')
          .attr('class', 'path')
          .append('path')
          .datum(dataLine)
          .attr('fill', 'none')
          .attr('stroke', 'steelblue')
          .attr('stroke-width', 1.5)
          .attr('d', d3.line()
              .x(function (d) {
                return xScaleLine(d.x)
              })
              .y(function (d) {
                return yScaleLine(d.y)
              })
          )
      // 在class为axis的分组中根据比例尺添加坐标轴
      gLineBd.append('g')
          .attr('class', 'axis')
          .attr('transform', `translate(0, ${height})`)
          .call(d3.axisBottom(xScaleLine))
      gLineBd.append('g')
          .attr('class', 'axis')
          .call(d3.axisLeft(yScaleLine))
      // 为折线图添加标题
      svgLine.append('text')
          .text('Data Visualization after Basic Discretization')
          .attr('x', '50px')
          .attr('y', '50px')
    }
    ,
    drawLine(dataLine, dataNew, idLine, colorLine) {
      console.log(dataLine, dataNew, idLine, colorLine)
      // 统一主图边距
      var margin = {top: 100, right: 30, bottom: 100, left: 60},
          width = 1200 - margin.left - margin.right,
          height = 500 - margin.top - margin.bottom
      // 基础折线图X轴比例尺
      var xScaleLine = d3.scaleLinear()
          .domain([0, d3.max(dataLine, function (d) {
            return d.x
          })])
          .range([0, width])

      // 基础折线图Y轴比例尺
      var yScaleLine = d3.scaleLinear()
          .domain([0, d3.max(dataLine, function (d) {
            return d.y
          })])
          .range([height, 0])

      // 获取折线画布
      var svgLine = d3.select('#svgLine')

      // 添加Sg折线偏移容器
      var gLineSg = svgLine.append('g')
          .attr('transform', `translate(${margin.left}, ${margin.top})`)
          .attr('id', idLine)

      // 添加折线
      gLineSg.append('g')
          .attr('class', 'path')
          .append('path')
          .datum(dataNew)
          .attr('fill', 'none')
          .attr('stroke', colorLine)
          .attr('stroke-width', 1.5)
          .attr('d', d3.line()
              .x(function (d) {
                return xScaleLine(d.x)
              })
              .y(function (d) {
                return yScaleLine(d.y)
              })
          )
    }
    ,
    drawLinePanel() {
      // 获取控制面板并设置标题
      var controlPanel = d3.select('#divPanel')

      // 第一部分-基本离散化
      var bdDiv = controlPanel.append('div')
          .attr('id', `bdDiv`)
          .attr('class', 'divLineControl')
      // 输入
      bdDiv.append('input')
          .attr('size', '29px')
          .attr('type', 'text')
          .attr('id', 'bdInput')
          .attr('placeholder', 'Input interval to discrete the data')
      // 触发按钮
      bdDiv.append('input')
          .attr('type', 'button')
          .attr('value', 'submit')
          .attr('class', 'submit')
          .on('click', () => {
            var bdInput = document.getElementById('bdInput')
            var bdValue = bdInput.value
            this.$axios.post('/get_data_time', {interval: bdValue})
                .then((res) => {
                  var data = res.data
                  console.log(data)
                  d3.select('#svgLine').remove()  // 删除折线画布
                  this.drawInitialLine(data[0].value)  // 根据新的数据重新初始化折线图
                  d3.select('#svgScatter').remove()  // 删除初始化散点图
                  this.drawScatter(data[1].value)  // 根据新的数据重新画散点图
                  d3.select('#changeDiv').remove()  // 删去切换按钮
                  this.addChangeDiv()  // 重新绑定切换按钮
                })
                .catch((error) => {
                  console.log('get_data_time', error)
                })
          })

      // 第二部分-噪声处理
      var npDiv = controlPanel
          .append('div')
          .attr('id', `npDiv`)
          .attr('class', 'divLineControl')
      npDiv.append('input')
          .attr('size', '18px')
          .attr('type', 'text')
          .attr('placeholder', 'Input size of window')
          .attr('id', 'npInputWindow')
      npDiv.append('input')
          .attr('size', '8px')
          .attr('type', 'text')
          .attr('placeholder', 'Input rank')
          .attr('id', 'npInputRank')
      npDiv.append('input')
          .attr('type', 'button')
          .attr('value', 'submit')
          .on('click', () => {
            d3.select('#gLineSg').remove()  // 删除原来的lineSg
            var bdInput = document.getElementById('bdInput')
            var bdValue = bdInput.value
            var npInputWindow = document.getElementById('npInputWindow')
            var npValueWindow = npInputWindow.value
            var npInputRank = document.getElementById('npInputRank')
            var npValueRank = npInputRank.value
            this.$axios.post('/get_data_time', {
              interval: bdValue,
              window: npValueWindow,
              rank: npValueRank
            })
                .then((res) => {
                  var data = res.data
                  console.log(data)
                  this.drawLine(data[0].value, data[1].value, 'gLineSg', 'red')
                })
                .catch((error) => {
                  console.log('get_data_time', error)
                })
          })


      // 第三部分-决策树离散化
      var tdDiv = controlPanel.append('div')
          .attr('id', `tdDiv`)
          .attr('class', 'divLineControl')

      tdDiv.append('input')
          .attr('size', '22px')
          .attr('type', 'text')
          .attr('id', 'tdInput')
          .attr('placeholder', 'Input max deepth of tree')
      tdDiv.append('input')
          .attr('type', 'button')
          .attr('value', 'submit')
          .on('click', () => {
            d3.select('#gLineTd').remove()  // 删除原来的lineTd
            var bdInput = document.getElementById('bdInput')
            var bdValue = bdInput.value
            var tdInput = document.getElementById('tdInput')
            var tdValue = tdInput.value
            this.$axios.post('/get_data_time', {
              interval: bdValue,
              maxDeepth: tdValue
            })
                .then((res) => {
                  var data = res.data
                  console.log(data)
                  this.drawLine(data[0].value, data[1].value, 'gLineTd', 'black')
                })
                .catch((error) => {
                  console.log('get_data_time', error)
                })
          })

    }
    ,
    drawScatter(dataScatter) {
      // 统一主图边距
      var margin = {top: 100, right: 30, bottom: 100, left: 60},
          width = 1200 - margin.left - margin.right,
          height = 500 - margin.top - margin.bottom
      // 散点图画布
      var svgScatter = d3.select('#line-time-test').append('svg')
          .attr('width', 1200).attr('height', 500)
          .attr('visibility', 'hidden')
          .attr('id', 'svgScatter')
          .style('position', 'absolute')
          .style('up', '0px')
          .style('left', '8px')  //  偏了8像素，尚不了解原因
      // 偏移主视图
      var gScatter = svgScatter.append('g')
          .attr('transform', `translate(${margin.left}, ${margin.top})`)

      // 散点图X轴比例尺
      var xScaleScatter = d3.scaleLinear()
          .domain([0, d3.max(dataScatter, function (d) {
            return d.x
          })])
          .range([0, width])

      // 散点图Y轴比例尺
      var yScaleScatter = d3.scaleLinear()
          .domain([0, d3.max(dataScatter, function (d) {
            return d.y
          })])
          .range([height, 0])
      // 绘制散点
      gScatter.selectAll('circle')
          .data(dataScatter)
          .enter()
          .append('circle')
          .attr('cx', function (d) {
            return xScaleScatter(d.x)
          })
          .attr('cy', function (d) {
            return yScaleScatter(d.y)
          })
          .attr('r', 5)
      // 在class为axis的分组中添加坐标轴
      gScatter.append('g')
          .attr('class', 'axis')
          .attr('transform', `translate(0, ${height})`)
          .call(d3.axisBottom(xScaleScatter))
      gScatter.append('g')
          .attr('class', 'axis')
          .call(d3.axisLeft(yScaleScatter))
      // 为主图添加标题
      svgScatter.append('text')
          .text('2D Feature Data Visualization')
          .attr('x', '50px')
          .attr('y', '50px')


      // 2D-散点放缩
      var controlPanel = d3.select('#controlPanel')
      var scatterDiv = controlPanel.append('div')
          .attr('id', `scatterDiv`)
          .style('display', 'none')
      var adjustForm = scatterDiv.append('form')
      adjustForm.append('input')
          .attr('type', 'submit')
          .attr('value', 'Scale the View of')
      adjustForm.append('input')
          .attr('size', '2px')
      var clusterForm = scatterDiv.append('form')
      clusterForm.append('input')
          .attr('type', 'submit')
          .attr('value', 'Cluster the Current Data with kinds of')
      clusterForm.append('input')
          .attr('size', '2px')
    }
    ,
    addChangeDiv() {
      var svgScatter = d3.select('#svgScatter')
      var svgLine = d3.select('#svgLine')
      var titleControlPanel = d3.select('#titleControlPanel')
      // 切换按钮
      var changeButton = d3.select('#line-time-test')
          .append('div')
          .attr('id', 'changeDiv')
          .attr('align', 'left')
          .append('input')
          .attr('type', 'button')
          .attr('value', 'Futher Explore the 2D Feature')
          .attr('class', 'changeButton')
          .on('click', function () {
            if (getComputedStyle(document.getElementById('svgLine'), null)['visibility'] === 'visible') {
              svgLine.attr('visibility', 'hidden')  // 隐藏折线图
              svgScatter.attr('visibility', 'visible')  // 显示散点图
              changeButton.attr('value', 'Back to the 1D View')
              titleControlPanel.text('2D Feature Control Panel')
              d3.selectAll(".divLineControl").style('display', 'none')
              d3.select("#scatterDiv").style('display', 'block')
            } else {
              svgLine.attr('visibility', 'visible')  // 显示折线图
              svgScatter.attr('visibility', 'hidden')  // 隐藏散点图
              changeButton.attr('value', 'Futher Explore the 2D Feature')
              titleControlPanel.text('Single Feature Control Panel')
              d3.selectAll(".divLineControl").style('display', 'block')
              d3.select("#scatterDiv").style('display', 'none')
            }
          })
    }

  },
  computed: {},
  watch: {},
  created() {

  }
  ,
  mounted() {
    this.initialize()
  }

}
</script>
