<template>
  <div id="borderScatterDiv">
    <div id='ScatterView' ref='root'>
      <div id="divControl">
      </div>
      <svg id="svgScatter" :width="svgSize.svg.width" :height="svgSize.svg.height">
        <g id="GInformation">
          <text x="20px" :y="svgSize.heightInf" style="fill: rgb(89, 89, 89)">Nonlinear Pattern</text>
        </g>
      </svg>
    </div>
  </div>
</template>

<script>
import * as d3 from "d3";

export default {
  name: "ScatterView"
  ,
  data() {
    return {
      svgSize: {
        svg: {height: 380, width: 360},
        svgScatter: {height: 260, width: 360},
        heightInf: 20
      },
      marginSize: {
        margin: {top: 40, right: 20, bottom: 0, left: 40},  // 折线主图边距 上边距实际为20 为了不修改过多代码 将heightInf合在一起了
      },
      color: {
        0: '#7986CA',
        1: '#AFD7F7',
        2: '#C8B4E1',
        3: '#E6C9E1',
        4: '#F4E6BA'
      },
      code: {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e'},
      // 用于保存重新发送recolor时的数据，可当作缓存使用，将添加clusters后传输回折线视图
      controlValue: {
        feature: null,
        interval: null,
        window: null,
        rank: null,
        clusters: null
      },
      // 用于向控制面板传输结果数据
      result: {
        curFeature: null,
        curResult: null
      },
      // 存储当前表现形式
      showSave: {}
    }
  }
  ,
  methods: {
    init() {
      // 初始化当前结果数据
      for (let key in this.result) {
        this.result[key] = null
      }
      // for (let key in this.controlValue) {
      //   this.controlValue[key] = null
      // }  一般来说 肯定会刷新数据再recolor的 这里可能会存在异步问题 所以暂时不处理
    },
    drawScatter(dataScatter) {
      d3.select('#gScatter').remove()
      var width = this.svgSize.svgScatter.width - this.marginSize.margin.left - this.marginSize.margin.right,
          height = this.svgSize.svgScatter.height - this.marginSize.margin.top - this.marginSize.margin.bottom,
          indexMin = d3.min(dataScatter, d => d.x),
          indexMax = d3.max(dataScatter, d => d.x),
          gScatter = d3.select('#svgScatter')
              .append('g')
              .attr('transform', `translate(${this.marginSize.margin.left}, ${this.marginSize.margin.top})`)
              .attr('id', 'gScatter')
      // 散点图X轴比例尺
      var xScaleScatter = d3.scaleLinear()
          .domain([indexMin, indexMax])
          .range([width, 0])

      // 散点图Y轴比例尺
      var yScaleScatter = d3.scaleLinear()
          .domain([d3.min(dataScatter, d => d.y), d3.max(dataScatter, d => d.y)])
          .range([height, 0])

      // 先画指示背景
      gScatter.append('g')
          .attr('id', 'scatterRect')
          .append('rect')
          .attr('x', xScaleScatter(0))
          .attr('y', -1)
          .attr('height', height + 1)
          .attr('width', xScaleScatter(indexMin) - xScaleScatter(0))
          .attr('fill', 'rgb(216, 224, 228)')
          .attr('opacity', 0.5)

      // 创建蒙版
      d3.select('#svgScatter')
          .append('clipPath')
          .attr('id', 'scatterClipPath')
          .append('rect')
          .attr('x', -30)  // 让左侧可以超出
          .attr('y', -30)
          .attr('width', width + 60)  // 让右侧可以超出
          .attr('height', height + 29) // 未知原因不对称 上移一像素

      // 创建图层引用蒙版
      var gScatterCircle = gScatter.append('g')
          .attr('id', 'gScatterCircle')
          .attr('clip-path', 'url(#scatterClipPath)')
      for (let i = 0; i <= d3.max(dataScatter, d => d.z); i++) {
        this.drawCircle(gScatterCircle, dataScatter, xScaleScatter, yScaleScatter, i)
      }
      // 在class为axis的分组中添加坐标轴
      gScatter.append('g')
          .attr('class', 'axis')
          .attr('transform', `translate(0, ${height - 1})`)   // 未知原因不对称 上移一像素
          .call(d3.axisBottom(xScaleScatter)
              .tickValues([indexMax, 0, indexMin])
              .tickFormat(d3.format(".0%")))
    },
    drawCircle(gScatter, dataScatter, xScaleScatter, yScaleScatter, i) {
      var tempScatter = dataScatter.filter(value => value.z == i)
      // 绘制散点
      gScatter.selectAll(`circle.${this.code[i]}`)
          .data(tempScatter)
          .enter()
          .append('circle')
          .attr('class', `${this.code[i]}`)
          .attr('fill', `${this.color[i]}`)
          .attr('cx', d => xScaleScatter(d.x))
          .attr('cy', d => yScaleScatter(d.y))
          .attr('r', 8)
          .attr('opacity', '0.5')
          .on('mouseover', function (d) {
            // 改变显示
            d3.select(this)
                .attr('opacity', '1')
            // 增加显示标签
            var pos = d3.mouse(this)
            var grow = d.x,
                rate = d.y
            // 如果没有标签 则添加
            if (d3.select('#tip')) {   // 好像写错了
              gScatter.append('text')
                  .attr('id', 'tip')
                  .attr('x', pos[0] - 35)
                  .attr('y', pos[1] - 20)
                  .text(`grow:${d3.format('.1%')(grow)}`)
              gScatter.append('text')
                  .attr('id', 'tip2')
                  .attr('x', pos[0] - 35)
                  .attr('y', pos[1] - 8)
                  .text(`rate:${d3.format('.1%')(rate)}`)
            }
          })
          .on('mouseout', function () {
            // 恢复显示
            d3.select(this)
                .attr('opacity', '0.5')
            // 删除标签
            d3.select('#tip').remove()
            d3.select('#tip2').remove()
          })
    },
    // 控制面板
    drawControl() {
      d3.select('#svgControlScatter').remove()
      d3.select('#divControlScatter').remove()
      var svgControlScatter = d3.select('#divControl')
          .append('svg')
          .attr('id', 'svgControlScatter')
      this.drawText(svgControlScatter)
      var divControlScatter = d3.select('#divControl')
          .append('div')
          .attr('id', 'divControlScatter')
          .style('position', 'absolute')
          .style('left', '0')
          .style('top', '0')
      this.drawButton(divControlScatter)
      this.drawSecondRow(divControlScatter)
    },
    drawText(svgControlScatter) {
      svgControlScatter.append('text')
          .attr('class', 'shallowColorText')
          .attr('x', 15)
          .attr('y', 20)
          .text('Cluster:')
      svgControlScatter.append('text')
          .attr('id', 'textFeature')
          .attr('class', 'deepColorText')
          .attr('x', 15)
          .attr('y', 59.5)
          .text(`${this.result.curFeature}:`)
    },
    drawButton(divControlScatter) {
      // 两个按钮同步
      divControlScatter.append('button')
          .attr('class', 'whiteButton')
          .style('position', 'absolute')
          .style('left', '210px')
          .style('top', '0.5px')
          .text('Recolor')
          .on('click', () => {
            this.$axios.post('/cluster_feature_data', this.controlValue)
                .then((res) => {
                  var data = res.data
                  console.log(data)
                  this.drawScatter(data[2].value)
                  this.$bus.$emit('reRectSg', data)
                })
                .catch((error) => {
                  console.log('sg_feature_data', error)
                })
          })
      divControlScatter.append('button')
          .attr('class', 'blueButton')
          .style('position', 'absolute')
          .style('left', '210px')
          .style('top', '40px')
          .text('Save')
          .on('click', () => {
            // 将离散效果显示在右侧
            if (this.result.curResult != null) {
              // 注意深浅拷贝问题
              this.$bus.$emit('PostResult', {
                interval: this.controlValue.interval,
                result: JSON.parse(JSON.stringify(this.result.curResult)),
                feature: this.result.curFeature
              })
            }
            // 保存该特征表现形式
            this.showSave[this.controlValue.feature] = {}
            this.showSave[this.controlValue.feature].clusters = this.controlValue.clusters
            this.showSave[this.controlValue.feature].resultParts = document.getElementById('tdResultInput').value
            // 折线图保存
            this.$bus.$emit('SaveResult')
          })
      // 两个图标同步
      divControlScatter.append('i')
          .attr('class', 'el-icon-s-open')
          .style('color', 'rgb(89, 89, 89)')
          .style('position', 'absolute')
          .style('top', '6px')
          .style('left', '224px')
      divControlScatter.append('i')
          .attr('class', 'el-icon-check')
          .style('color', 'white')
          .style('position', 'absolute')
          .style('top', '45.5px')
          .style('left', '224px')
    },
    drawSecondRow(divControlScatter) {
      // 选择框
      var selectControlScatter = divControlScatter.append('select')
          .attr('class', 'form-select form-select-sm')
          .attr('id', 'selectCluster')
          .on('change', () => {
            var clusters = document.getElementById('selectCluster').value
            this.controlValue.clusters = clusters
          })
          .style('background-position', 'right 0.5rem center')
          .style('padding-top', '0.1rem')
          .style('height', '25px')
          .style('width', '55px')
          .style('position', 'absolute')
          .style('top', '2px')
          .style('left', '113px')
      for (let i = 3; i < 6; i++) {
        selectControlScatter
            .append('option')
            .attr('value', i)
            .text(i)
      }
      // 结果展示
      divControlScatter.append('input')
          .attr('id', "tdResultInput")
          .attr('class', "form-control")
          .attr('type', "text")
          .style('position', 'absolute')
          .style('top', '40px')
          .style('left', '105px')
          .style('height', '25px')
          .style('width', '90px')
          .style('border-style', 'none')
    }
  }
  ,
  mounted() {
    //  获取特征值；如果面板已经存在，则清空接收特征
    this.$bus.$on('Init', (d) => {
      //  初始化result缓存数据
      this.init()  // 小心响应异步问题
      //  特征获取与文字显示
      this.result.curFeature = d['feature']
      var textFeature = d3.select('#textFeature')
      if (textFeature) textFeature.text(`${d['feature']}:`)
      //  聚类系数与结果调整：主要调整的是没有保存时，相关特征的控制面板的显示问题
      var selectCluster = document.getElementById('selectCluster'),
          tdResultInput = document.getElementById('tdResultInput')
      //  清空内容
      if (Object.keys(this.showSave).indexOf(d['feature']) < 0) {
        if (selectCluster) selectCluster.value = null
        if (tdResultInput) tdResultInput.value = null
      }
    })
    //  初始化
    this.$bus.$on('Bd', (d) => {
      //  初始化result缓存数据
      this.init()
      this.result.curFeature = d['feature']
      //  判断是否创建
      if (document.getElementById('selectCluster')) {
        //  聚类系数与结果初始化
        document.getElementById('selectCluster').value = null
        document.getElementById('tdResultInput').value = null
      }
    })
    //  创建面板和视图的入口
    this.$bus.$on('Scatter', (d) => {
          // 当恢复缓存时，控制面板会被删除并重新创建；创建时特征文字已经在函数中被更新
          this.drawControl()
          this.drawScatter(d)
          var feature = this.result.curFeature,
              selectCluster = document.getElementById('selectCluster'),
              tdResultInput = document.getElementById('tdResultInput')
          if (Object.keys(this.showSave).indexOf(feature) >= 0) {  // 如果有的话，则赋予初始值
            selectCluster.value = this.showSave[feature].clusters
            tdResultInput.value = this.showSave[feature].resultParts
          } else {
            selectCluster.value = 3  // 初始的drawScatter为3
          }
        }
    )
    //  缓存sg的数据
    this.$bus.$on('Sg', d => {
      for (let key of Object.keys(d)) {
        this.controlValue[key] = d[key]
      }
    })
    //  当图像由缓存数据触发时，不会获取到Sg数据，因此额外设置一个发送事件；原先需要由reColor按钮触发的事件需要在这里自动地重新走一遍——但是直接执行又涉及到异步问题
    this.$bus.$on('postCurSg', d => {
      var data = JSON.parse(JSON.stringify(d))
      for (let key of Object.keys(data)) {
        this.controlValue[key] = data[key]
      }
      // // 将数据调回
      // this.$axios.post('/cluster_feature_data', this.controlValue)
      //     .then((res) => {
      //       var data = res.data
      //       this.drawScatter(data[2].value)
      //       this.$bus.$emit('reRectSg', data)
      //     })
      //     .catch((error) => {
      //       console.log('sg_feature_data', error)
      //     })
    })
    // 接收结果并修改表现
    this.$bus.$on('postCurResult', d => {
      let length = Object.keys(d).length
      document.getElementById('tdResultInput').value = `${length} Parts`
      this.result.curResult = {}
      for (let index in d) {
        this.result.curResult[index] = d[index][0]  // 在这里处理了代码层数
      }
    })
    this.$bus.$on('changeCurResult', d => {
      var index = d['index'],
          curResult = this.result.curResult[index],
          start = d['start'],
          end = d['end']
      curResult[0] += start
      curResult[1] += end
      if (curResult[0] > curResult[1]) {
        let length = Object.keys(this.result.curResult).length
        delete this.result.curResult[index]
        document.getElementById('tdResultInput').value = `${length - 1} Parts`
      }
    })
  }
}
</script>

<style>

#borderScatterDiv {
  --bs-gutter-x: 0;
  height: 378px;
  border-width: 0 1px 1px 0;
  border-style: solid;
  border-color: rgb(240, 242, 245);
  position: absolute;
}

#ScatterView {
  --bs-gutter-x: 0;
  width: 360px;
  height: 377px;
  position: relative;
  left: -1.8px;
  border-width: 1px 1px 1px 0px;
  border-style: solid;
  border-color: rgb(232, 232, 232);
  border-radius: 0 0 2px 0;
}

#divControl {
  width: 320px;
  height: 100px;
  position: absolute;
  top: 290px;
  left: 20px;
  /*border: 2px solid black;*/
}

.blueButton {
  color: white;
  border: none;
  background: rgb(24, 144, 255);
  border-radius: 3px;
  padding-left: 13px;
  font-size: 14px;
  width: 110px
}

.whiteButton {
  color: rgb(89, 89, 89);
  border-color: rgba(217, 217, 217);
  border-style: solid;
  padding-left: 30px;
  background: white;
  border-radius: 5px;
  font-size: 14px;
  width: 110px
}

.shallowColorText {
  fill: rgb(111, 109, 109)
}

.deepColorText {
  fill: rgb(89, 89, 89);
}
</style>