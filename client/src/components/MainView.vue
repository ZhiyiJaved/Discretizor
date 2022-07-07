<template>
  <div id='MainView' ref='root'>
    <svg id="SvgMain" width="1080px" height="380px">
      <g id="GIforamtion">
        <text x='20px' :y="size.heightInf" style="fill: rgb(89, 89, 89)">Evolution View</text>
      </g>
      <g id="GScale" transform="translate(30, 210)">
        <line class="LineScale" x1="0" y1="0" :x2=size.widthMirror y2="0"></line>
        <line class="LineScale" :x1=size.widthMirror y1="0" :x2=size.widthMirror :y2=size.heightMirror></line>
        <line class="LineScale" :x1=size.widthMirror :y1=size.heightMirror x2="0" :y2=size.heightMirror></line>
        <line class="LineScale" x1="0" :y1=size.heightMirror x2="0" y2="0"></line>
      </g>
    </svg>
  </div>
</template>

<script>

import * as d3 from 'd3'
import * as scheme from 'd3-scale-chromatic'

export default {
  name: 'PerformanceView',
  data() {
    return {
      size: {
        height: 380,
        heightInf: 20,
        heightPie: 360,
        leftPadding: 100,
        upPadding: 10,
        outerRadius: 30,
        innerRadius: 23,
        heightMirror: 160,
        widthMirror: 150
      },
      border: {
        upBorder: null,
        bottomBorder: null
      },
      controlValue: {feature_composition: [], result: [], interval: []},
      record_model: {},  // 以绘画位置作为键，对应该模型后的两个可选节点
      model_tree: {},
      draw_condition: false,
      draw_temp: {},
      pieScale: {
        rScale: {
          accuracy: null,
          auc: null,
          f1: null,
          precision: null,
          recall: null
        },
        opacityScale: null
      }
    }
  },

  props: [],
  methods: {
    draw_pie: function (data_metrix, data_importance, model_name, draw_place, fatherData) {
      // 初始化该模型的可选子节点
      this.record_model[`${draw_place.top},${draw_place.left}`] = ['down', 'up']
      // 饼图画布
      var gPie = d3.select('#SvgMain')
          .append('g')
          .attr('id', `pie_${model_name}`)
      if (fatherData) {
        this.draw_son_pie(model_name, draw_place, gPie, data_metrix, data_importance, fatherData)
      } else {
        this.draw_initial_pie(model_name, draw_place, gPie, data_metrix, data_importance)
      }
      // 选中按钮
      gPie.append('text')
          .text(`model_${model_name}`)
          .attr('y', `${draw_place.top + this.size.outerRadius + 13}`)
          .attr('x', `${draw_place.left - 1.2 * this.size.outerRadius}`)
          .attr('id', `text_${model_name}`)
          .style('font-family', 'sans-serif')
          .style('font-size', '12px')
          .on('click', () => {
            this.control_text(model_name, draw_place, gPie, data_metrix, data_importance)
          })
    }
    ,
    draw_initial_pie: function (model_name, draw_place, gPie, data_metrix, data_importance) {
      // 根据位置创建容器
      var gPieMain = gPie.append('g')
              .attr('id', `pie_${model_name}_main`)
              .attr("transform", `translate(${draw_place.left},  ${draw_place.top})`),
          innerRadius = this.size.innerRadius,
          outerRadius = this.size.outerRadius
      // 外部圆环
      this.draw_ring(model_name, draw_place, gPieMain, data_importance, outerRadius, innerRadius, false)
      // 内部背景
      var value_metrix = Object.values(data_metrix),
          metrix_key = Object.keys(data_metrix),
          anglePiece = Math.PI * 2 / value_metrix.length,
          length = metrix_key.length
      this.draw_pie_background(gPieMain, anglePiece, innerRadius, length)
      //内部点与折线
      var data_points = [],
          temp,
          index
      //  通过旋转角求各点坐标
      index = 0
      for (let i in data_metrix) {
        data_points.push({
          x: 0.5 * innerRadius * Math.sin(index * anglePiece),
          y: -0.5 * innerRadius * Math.cos(index * anglePiece)
        })
        temp = data_metrix[i]
        // 基于该数据适配比例尺
        if (i != 'ne') {
          this.pieScale.rScale[i] = d3.scaleLinear()
              .domain([0.92 * temp, 1.08 * temp])
              .range([0, innerRadius])
        } else {
          this.pieScale.rScale[i] = d3.scaleLinear()
              .domain([1.08 * temp, 0.92 * temp])
              .range([0, innerRadius])
        }
        index += 1
      }
      this.draw_line_circle_polygon(gPieMain, data_points, metrix_key, value_metrix, innerRadius, outerRadius, 'cur')
      return gPieMain
    }
    ,
    draw_son_pie: function (model_name, draw_place, gPie, data_metrix, data_importance, fatherData) {
      // 根据位置创建容器
      var gPieMain = gPie.append('g')
          .attr('id', `pie_${model_name}_main`)
          .attr("transform", `translate(${draw_place.left},  ${draw_place.top})`)
      var innerRadius = this.size.innerRadius,
          outerRadius = this.size.outerRadius
      this.draw_ring(model_name, draw_place, gPieMain, data_importance, outerRadius, innerRadius, fatherData)
      // 内部背景
      var metrix_key = Object.keys(data_metrix),
          anglePiece = Math.PI * 2 / metrix_key.length,
          length = metrix_key.length
      this.draw_pie_background(gPieMain, anglePiece, innerRadius, length)

      // 内部点与折线
      var temp,
          fatherMetrix = fatherData['fatherMetrix'],
          tempFather
      // 通过旋转角求各点坐标
      var data_points = [],
          farther_points = [],
          index
      index = 0
      for (let key of metrix_key) {
        let data_scale = this.pieScale.rScale[key](data_metrix[key])
        temp = {
          x: data_scale * Math.sin(index * anglePiece),
          y: -data_scale * Math.cos(index * anglePiece)
        }
        data_points.push(temp)
        let father_scale = this.pieScale.rScale[key](fatherMetrix[key])
        tempFather = {
          x: father_scale * Math.sin(index * anglePiece),
          y: -father_scale * Math.cos(index * anglePiece)
        }
        farther_points.push(tempFather)
        index += 1
      }
      var value_metrix = Object.values(data_metrix),
          value_farther = Object.values(fatherMetrix)
      this.draw_line_circle_polygon(gPieMain, farther_points, metrix_key, value_farther, innerRadius, outerRadius, 'farther')
      // 父子节点指标一致
      this.draw_line_circle_polygon(gPieMain, data_points, metrix_key, value_metrix, innerRadius, outerRadius, 'cur')
      return gPieMain
    }
    ,
    draw_ring: function (model_name, draw_place, gPieMain, data_importance, outerRadius, innerRadius, fatherData) {
      var value_importance = Object.values(data_importance),
          importance_key = Object.keys(data_importance)
      //  新增的特征
      if (fatherData) {
        var keyFatherImportance = Object.keys(fatherData['fatherImportance'])
        var newKeyImportance = importance_key.filter(d => !keyFatherImportance.includes(d))
      } else {
        newKeyImportance = []
      }
      //  记录原先的位置
      var index
      var index_importance = {}
      index = 0
      for (let importance of value_importance) {
        index_importance[importance] = index
        index += 1
      }

      //  重要性排序
      value_importance.sort((cur, next) => cur - next)
      //  找到数字为正的边界
      var postiveBorder = value_importance.findIndex(d => d > 0)
      //  将所有数字转换为正值
      var pie_importance = value_importance.map(d => {
        let data
        if (d < 0) data = -d
        else data = d
        return data
      })
      // 环形图
      var arc = d3.arc()
          .innerRadius(innerRadius)
          .outerRadius(outerRadius)
          .padAngle(0.08)
      // 颜色比例尺
      var blue = d3.scaleSequential(scheme.interpolateBlues)
              .domain([0, d3.max(value_importance)]),
          red = d3.scaleSequential(scheme.interpolateReds)
              .domain([0, d3.min(value_importance)])
      gPieMain.selectAll(`g.pie_${model_name}`)
          .data(d3.pie()(pie_importance))
          .enter()
          .append('g')
          .attr('class', `pie_${model_name}`)
          .append('path')
          .attr('fill', (d, i) => {
            let color
            if (i < postiveBorder) color = red(-d.data)
            else color = blue(d.data)
            return color
          })
          .attr('opacity', `0.8`)
          .attr('d', d => arc(d))
          .attr('transform', (d, i) => {
            let transform
            if ((i < postiveBorder)&&(newKeyImportance.includes(importance_key[index_importance[-d.data]]))) transform = 'scale(1.1)'
            else if ((i > postiveBorder)&&(newKeyImportance.includes(importance_key[index_importance[d.data]]))) transform = 'scale(1.1)'
            return transform
          })
          .on('mouseover', function (d, i) {
            d3.select(this).attr('opacity', `1`)
              let text = gPieMain.append('text')
                  .attr('id', 'tip')
                  .attr('x', -innerRadius - 10)
                  .attr('y', -outerRadius - 3)
            if (i < postiveBorder) text.text(`${importance_key[index_importance[-d.data]]}: ${d3.format('.2%')((d.endAngle - d.startAngle) / (2 * Math.PI))}`)
            else text.text(`${importance_key[index_importance[d.data]]}: ${d3.format('.2%')((d.endAngle - d.startAngle) / (2 * Math.PI))}`)
          })
          .on('mouseout', function () {
            d3.select(this).attr('opacity', `0.8`)
            d3.select('#tip').remove()
          })
    }
    ,
    draw_pie_background: function (gPieMain, anglePiece, innerRadius, length) {
      var pieBackground = []
      // 旋转角数据
      for (let i = 1; i <= 2 * Math.PI / anglePiece; i++) {
        pieBackground.push({startAngle: (i - 1) * anglePiece, endAngle: i * anglePiece})
      }
      var index = 0
      // 绘制多边形背景
      for (let i = 0.8; i > 0;) {
        let flag = index % 2 === 0
        gPieMain.selectAll(`g.pie_background_${index}`)
            .data(pieBackground)
            .enter()
            .append('g')
            .attr('class', `pie_background_${index}`)
            .append('path')
            .attr('fill', () => {
              var color
              if (flag) color = 'rgb(235, 235, 235)'
              else color = 'rgb(204, 204, 204)'
              return color
            })
            .attr('opacity', () => {
              if (index == 0) return 0.5
            })
            .attr('d', d => {
                  var data
                  if (index == 0) {
                    let arc = d3.arc()
                        .innerRadius((i - 0.05) * innerRadius)
                        .outerRadius(i * innerRadius)
                    data = arc(d)
                  } else if (flag) {
                    // 最外圈
                    let arc = d3.arc()
                        .innerRadius((i - 0.1) * innerRadius)
                        .outerRadius(i * innerRadius)
                    data = arc(d)
                  } else {
                    let arc = d3.arc()
                        .innerRadius((i - 0.05) * innerRadius)
                        .outerRadius(i * innerRadius)
                    data = arc(d)
                  }
                  return data
                }
            )
        if (index == 0) i = i - 0.05
        else if (flag) i = i - 0.1
        else i = i - 0.05
        index += 1
      }
      // 长方形背景
      for (let i = 0; i < length; i++) {
        gPieMain.append('rect')
            .attr('x', -2)
            .attr('y', -innerRadius)
            .attr('width', '4px')
            .attr('height', innerRadius)
            .attr('fill', 'white')
            .attr('transform', `rotate(${(i * anglePiece) * (360 / (Math.PI * 2))}, 0, 0)`)
      }
    }
    ,
    draw_line_circle_polygon: function (gPieMain, data_points, metrix_key, value_metrix, innerRadius, outerRadius, kind) {
      // 连点
      for (let i = 0; i < data_points.length; i++) {
        gPieMain.append('line')
            .attr('x1', data_points[i % data_points.length].x)
            .attr('y1', data_points[i % data_points.length].y)
            .attr('x2', data_points[(i + 1) % data_points.length].x)
            .attr('y2', data_points[(i + 1) % data_points.length].y)
            .attr('stroke', () => {
              let color
              if (kind === 'cur') color = 'rgb(238, 135, 55)'
              else color = 'rgb(84, 118, 167)'
              return color
            })
            .attr('stroke-width', '1.5px')
            .attr('opacity', 0.8)
      }
      // 画点
      gPieMain.selectAll('circle.now')
          .data(data_points)
          .enter()
          .append('circle')
          .attr('class', `${kind}`)
          .attr('cx', d => d.x)
          .attr('cy', d => d.y)
          .attr('r', 2)
          .attr('fill', () => {
            let color
            if (kind === 'cur') color = 'rgb(238, 135, 55)'
            else color = 'rgb(84, 118, 167)'
            return color
          })
          .attr('opacity', 0.8)
          .on('mouseover', function (d, i) {
            d3.select(this).attr('opacity', `1`)
            gPieMain.append('text')
                .attr('id', 'tip')
                .attr('x', -innerRadius)
                .attr('y', -outerRadius - 10)
                .text(() => {
                  let text
                  if (metrix_key[i] != 'ne') text = `${metrix_key[i]}: ${d3.format('.2%')((value_metrix[i]))}`
                  else text = `${metrix_key[i]}: ${d3.format('.2f')((value_metrix[i]))}`
                  return text
                })
          })
          .on('mouseout', function () {
            d3.select('#tip').remove()
            d3.select(this).attr('opacity', 0.8)
          })

      // 获取多边形数据格式
      var data_polygon = ''
      for (let i = 0; i < data_points.length; i++) {
        data_polygon += `${data_points[i].x},${data_points[i].y} `
      }
      // 绘制多边形
      gPieMain.append('polygon')
          .attr('points', data_polygon)
          .attr('opacity', '0.3')
          .attr('fill', () => {
            let color
            if (kind === 'cur') color = 'rgb(238, 135, 55)'
            else color = 'rgb(84, 118, 167)'
            return color
          })
    }
    ,
    control_text: function (model_name, draw_place, gPie, data_metrix, data_importance) {
      // 根据模型名称ID选择文本实例从而获取它的字体样式
      var text_model = d3.select(`#text_${model_name}`)
      if (text_model.style('font-weight') === '400') {
        // 镜像
        this.draw_mirror(model_name)
        // 从标准体变为粗体
        text_model.style('font-weight', 'bold')
        // 从本地记录中查看下一个空余位置，并确定大小：高度为八个单位，宽度为四个单位
        let nextDirection = this.record_model[`${draw_place.top},${draw_place.left}`].pop(),
            unitHeight = 0.32 * this.size.outerRadius,
            unitWidth = 1.5 * this.size.outerRadius
        // 判断下一个位置是否超出边界并获取下一个图形的位置
        let nextPlace = this.get_next_place(draw_place, nextDirection, unitHeight, unitWidth),
            codeNextPlace = `${nextPlace.top},${nextPlace.left}`
        // 如果出现被其它模型已经占掉的情况，则水平创建图形
        if (this.draw_condition === false) {
          this.draw_condition = Object.keys(this.record_model).indexOf(codeNextPlace) > 0
          if (this.draw_condition) nextPlace.top = draw_place.top
        }
        // 以当前图形位置为键临时记录这一次下一个图形的位置以及方向
        this.draw_temp[`${draw_place.top},${draw_place.left}`] = {
          nextPlace: codeNextPlace,
          nextDirection: nextDirection
        }
        // 绘画出曲线
        this.draw_line(gPie, draw_place, nextDirection, model_name, unitHeight, unitWidth)
        // 发送下一个图形的位置、父节点多边形与散点的数据到操作面板
        this.$bus.$emit('SelectPlace', {
          drawPlace: nextPlace,
          fatherData: {fatherMetrix: data_metrix, fatherImportance: data_importance}
        })
      } else {
        // 若为粗体则将字体变为标准体
        text_model.style('font-weight', 'initial')
        // 判断上一次临时存储的地址是否被记录在本地模型数据中
        let ifDraw = Object.keys(this.record_model).indexOf(this.draw_temp[`${draw_place.top},${draw_place.left}`].nextPlace)
        // 读取临时存储的下一次模型的方向
        let nextDirection = this.draw_temp[`${draw_place.top},${draw_place.left}`].nextDirection
        if (ifDraw > 0
        ) {
          // 若已画出，则初始化下一次绘画的位置
          this.$bus.$emit('DropPlace')
        } else {
          // 否则，将已画出的折线删除
          var pathNodes = document.getElementsByClassName(`path_${model_name}_${nextDirection}`)
          var length = pathNodes.length
          // 注意：链表倒着删
          for (let i = 0; i < length; i++) {
            pathNodes[0].parentNode.removeChild(pathNodes[length - i - 1])
          }
          // 并从前往后重新插入空余方向的位置，这使得我们能够通过点击调整下一次图形绘画的位置
          this.record_model[`${draw_place.top},${draw_place.left}`].splice(0, 0, nextDirection)
        }
      }
    }
    ,
    draw_mirror: function (model_name) {
      let mirror = document.getElementById(`pie_mirror`)
      if ((mirror == null) || (mirror.getAttribute('belong') != model_name)) {
        d3.select('#pie_mirror').remove()
        d3.select('#pie_mirror_text').remove()
        let self_mirror = document.getElementById(`pie_${model_name}_main`)
            .cloneNode(true)
        self_mirror.setAttribute('belong', `${model_name}`)
        self_mirror.setAttribute('id', `pie_mirror`)
        self_mirror.setAttribute('transform', `translate(${this.size.widthMirror / 2}, ${this.size.outerRadius * 2 + 10}) scale(2)`)
        document.getElementById('GScale').appendChild(self_mirror)
        d3.select('#GScale')
            .append('text')
            .text(`model_${model_name}`)
            .attr('id', 'pie_mirror_text')
            .attr('x', `${this.size.widthMirror / 5}`)
            .attr('y', `${this.size.heightMirror - 10}`)
      }
    }
    ,
    get_next_place: function (draw_place, nextDirection, unitHeight, unitWidth) {
      var nextPlace;
      if (nextDirection === 'up') {
        nextPlace = {
          top: draw_place.top - 8 * unitHeight,
          left: this.size.outerRadius * 2 + draw_place.left + 4 * unitWidth
        }
      } else if (nextDirection === 'down') {
        nextPlace = {
          top: draw_place.top + 8 * unitHeight,
          left: this.size.outerRadius * 2 + draw_place.left + 4 * unitWidth
        }
      } else {
        console.log('该模型尚不支持更多的子图')
      }
      // 判断是否超出边界
      this.draw_condition = (nextPlace.top <= this.border.upBorder) || (nextPlace.top >= this.border.bottomBorder)

      if (this.draw_condition) {
        nextPlace.top = draw_place.top
      }
      return nextPlace
    }
    ,
    draw_line: function (gPie, draw_place, nextDirection, model_name, unitHeight, unitWidth) {
      var curve_generator = d3.line()
          .x((d) => (d.x))
          .y((d) => (d.y))
          .curve(d3.curveBasis)
      //  移一个单位
      if (document.getElementById(`path_${model_name}_${nextDirection}`) != null) {
        d3.select(`#path_${model_name}_${nextDirection}`).remove()
      }
      var gPieLine = gPie.append('g')
          .attr('transform', `translate(${draw_place.left + this.size.outerRadius}, ${draw_place.top})`)
          .attr('id', `path_${model_name}_${nextDirection}`)
      if (this.draw_condition) {
        gPieLine.append('path')
            .attr('d', curve_generator([{x: 0, y: 0}, {
              x: 4 * unitWidth,
              y: 0
            }]))
            .attr('stroke', 'darkgrey')
            .attr('stroke-width', 2)
            .attr('fill', 'none')
            .attr('class', `path_${model_name}_${nextDirection}`)
      } else if (nextDirection === 'up') {
        //通过两个简单曲线连接为一个弯折的曲线
        gPieLine.append('path')
            .attr('d', curve_generator([{x: 0, y: 0}, {
              x: 1 * unitWidth,
              y: -1 * unitHeight
            }, {x: 2 * unitWidth, y: -4 * unitHeight}]))
            .attr('stroke', 'darkgrey')
            .attr('stroke-width', 2)
            .attr('fill', 'none')
            .attr('class', `path_${model_name}_${nextDirection}`)
        gPieLine.append('path')
            .attr('d', curve_generator([{x: 2 * unitWidth, y: -4 * unitHeight}, {
              x: 3 * unitWidth,
              y: -7 * unitHeight
            }, {x: 4 * unitWidth, y: -8 * unitHeight}]))
            .attr('stroke', 'darkgrey')
            .attr('stroke-width', 2)
            .attr('fill', 'none')
            .attr('class', `path_${model_name}_${nextDirection}`)
      } else if (nextDirection === 'down') {
        gPieLine.append('path')
            .attr('d', curve_generator([{x: 0, y: 0}, {
              x: 1 * unitWidth,
              y: 1 * unitHeight
            }, {x: 2 * unitWidth, y: 4 * unitHeight}]))
            .attr('stroke', 'darkgrey')
            .attr('stroke-width', 2)
            .attr('fill', 'none')
            .attr('class', `path_${model_name}_${nextDirection}`)
        gPieLine.append('path')
            .attr('d', curve_generator([{
              x: 2 * unitWidth,
              y: 4 * unitHeight
            }, {
              x: 3 * unitWidth,
              y: 7 * unitHeight
            }, {
              x: 4 * unitWidth,
              y: 8 * unitHeight
            }]))
            .attr('stroke', 'darkgrey')
            .attr('stroke-width', 2)
            .attr('fill', 'none')
            .attr('class', `path_${model_name}_${nextDirection}`)
      } else {
        console.log('当前模型不支持更多子节点')
      }
    }
    ,
    initial_indicator: function () {
      let blue = d3.scaleSequential(scheme.interpolateBlues)
              .domain([0, 100]),
          red = d3.scaleSequential(scheme.interpolateReds)
              .domain([-100, 0]),
          gInf = d3.select('#GIforamtion'),
          data = d3.range(200).map(d => d - 100).reverse()
      gInf.selectAll('rect')
          .data(data)
          .enter()
          .append('rect')
          .attr('x', (d, i) => {
            let x
            if (d > 0) x = 550 + i * 0.8
            else x = 720 + i * 0.8
            return x
          })
          .attr('y', this.size.heightInf / 2)
          .attr('width', 1.2)
          .attr('height', 10)
          .style('fill', (d) => {
            let color
            if (d > 0) color = blue(d)
            else color = red(d)
            return color
          })
      gInf.append('line')
          .attr('x1', 160)
          .attr('x2', 175)
          .attr('y1', this.size.heightInf / 1.3)
          .attr('y2', this.size.heightInf / 1.3)
          .attr('stroke', `rgb(238, 135, 55)`)
          .attr('stroke-width', `2px`)
      gInf.append('text')
          .attr('x', 185)
          .attr('y', this.size.heightInf)
          .attr('fill', 'rgb(238, 135, 55)')
          .text('Current Performance')
      gInf.append('line')
          .attr('x1', 360)
          .attr('x2', 375)
          .attr('y1', this.size.heightInf / 1.3)
          .attr('y2', this.size.heightInf / 1.3)
          .attr('stroke', `rgb(73, 119, 171)`)
          .attr('stroke-width', `2px`)
      gInf.append('text')
          .attr('x', 385)
          .attr('y', this.size.heightInf)
          .attr('fill', 'rgb(73, 119, 171)')
          .text('Parent Performance')
      gInf.append('text')
          .attr('x', 650)
          .attr('y', this.size.heightInf)
          .attr('fill', 'rgb(33, 72, 134)')
          .text('Positive Strength')
      gInf.append('text')
          .attr('x', 900)
          .attr('y', this.size.heightInf)
          .attr('fill', 'rgb(130, 30, 28)')
          .text('Negative Strength')
    }
  }
  ,
  computed: {}
  ,
  watch: {}
  ,
  created() {

  }
  ,
  mounted() {
    // 画渐变色块
    this.initial_indicator()
    this.border.upBorder = this.size.heightInf + this.size.upPadding + this.size.outerRadius
    this.border.bottomBorder = this.size.height - this.size.upPadding - this.size.outerRadius
    //  监听控制面板特征选中与取消的事件，在本地变量feature_composition中添加或删除相关特征。其中离散结果与特征数组始终在顺序上彼此对应。
    this.$bus.$on('SelectFeature', d => {
      if (d['result'] != undefined) {
        var featureResult = JSON.parse(JSON.stringify(d['result']))
        this.controlValue.result.push(featureResult)
      } else {
        this.controlValue.result.push(null)  // 补齐位置
      }
      var featureSelected = d['feature'],
          featureInterval = d['interval']
      this.controlValue.feature_composition.push(featureSelected)
      this.controlValue.interval.push(featureInterval)
      console.log(`Have selecting ${featureSelected}, [${this.controlValue.feature_composition}] are selected now`)
    })
    this.$bus.$on('DropFeature', d => {
      var featureSelected = JSON.parse(JSON.stringify(d['feature']))
      var index_delete = this.controlValue.feature_composition.indexOf(d.feature)  // 获取需要删除的特征位置
      this.controlValue.feature_composition.splice(index_delete, 1)  // 删除对应元素
      this.controlValue.result.splice(index_delete, 1)  // 删除对应结果
      this.controlValue.interval.splice(index_delete, 1)  // 删除对应间隔
      console.log(`Have deleting ${featureSelected}, [${this.controlValue.feature_composition}] are selected now`)
    })
    //  监听控制面板中的预测事件，将既有特征组合发送给后台处理
    this.$bus.$on('Predict', (d) => {
      // 发送存储的一系列数组
      this.$axios.post('/predict', {
        feature_composition: this.controlValue.feature_composition,
        result: this.controlValue.result,
        interval: this.controlValue.interval,
      })
          .then((res) => {
            var data = res.data
            console.log(data)
            if (d["drawPlace"]) {  // 判断是否存在绘画位置信息
              this.draw_pie(data[0]['metrix'], data[1]['feature_importance'], d['modelName'], d['drawPlace'], d['fatherData'])  // 绘画模型结果图
            } else {
              var initialPlace = {
                top: this.size.heightInf + this.size.heightPie / 3,
                left: this.size.leftPadding
              }
              this.draw_pie(data[0]['metrix'], data[1]['feature_importance'], d['modelName'], initialPlace, false)
            }
          })
          .catch((error) => {
            console.log('predict', error)
          })
    })
  }
}

</script>

<style>
#MainView {
  --bs-gutter-x: 0;
  border-width: 0 1px 1px 2px;
  border-style: solid;
  border-color: rgb(240, 242, 245);
}

.axis path,
.axis line {
  fill: none;
  stroke: black;
  shape-rendering: crispEdges;
}

.LineScale {
  stroke: black;
  stroke-linecap: round;
  stroke-width: 3px
}
</style>
