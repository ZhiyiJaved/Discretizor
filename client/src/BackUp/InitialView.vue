<template>
  <div id='InitialView' ref='root'>
    <svg width="500px">
      <text x="80px" y="85px">Initial Panel</text>
    </svg>
  </div>
</template>

<script>
import * as d3 from "d3";

export default {
  name: "InitialView"
  ,
  methods: {
    initialize() {
      var initialPanel = d3.select('#InitialView')
      initialPanel.append('input')
          .attr('type', 'button')
          .attr('value', 'initialize the time data')
          .attr('id', 'timeButton')
      .on('click', () => {
            this.$axios.get('/get_data_time')
                .then((res) => {
                  var data = res.data
                  console.log(data)
                  // this.drawScatter(data[1].value)
                  this.drawInitialLine(data[0].value)
                  this.drawLinePanel()
                  // this.addChangeDiv()
                  // d3.select("#initialPanel").style('display', 'none')  // 隐藏初始化面板
                  // d3.select('#controlPanel').style('display', 'block') // 显示操作面板
                  // d3.select('#backDiv').style('display', 'block')  // 显示返回按钮
                })
                .catch((error) => {
                  console.log('get_data_time', error)
                })
          }
      )
    }
  }

  ,
  mounted() {
    this.initialize()
  }
}
</script>

<style scoped>

</style>