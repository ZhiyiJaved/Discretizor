<template>
  <div id='FeatureDiscretizedView' ref='root'>
    <!--    控制面板容器-->
    <div id='ControlView'>
      <!--      标题容器，构成了一部分边线-->
      <div
          style="width: 350px; position: absolute;z-index: 1;height:50px;border-width: 0 0 1.5px 1.5px; border-style: inset; border-color: rgb(238, 238, 238) transparent">
        <!--      标题容器-->
        <svg style="height: 50px;width: 500px">
          <!--          标题-->
          <text class='deepColorText' x="5" y="35" style="font-size: 18px">Control Panel</text>
        </svg>
      </div>
      <!--        按钮容器，构成了一部分边线-->
      <div
          style="height: 185px; width:350px; position: absolute;z-index: 0;top:87px; border-width: 3px 0 1.5px 0;border-style: solid; border-color: rgb(154, 154, 154) transparent rgb(232, 232, 232) transparent">
        <!--     增加一个div，方便调整所有按钮组件的垂直位置   -->
        <div style="width: 350px;position: relative; top:10px">
          <!--          所有的文字部分-->
          <svg>
            <text style="font-size: 16px" class='deepColorText' :x="text.position.featurePosition.domainPosition.x"
                  y="20">Model:
            </text>
            <text style="font-size: 16px" class='shallowColorText' :x="text.position.featurePosition.domainPosition.x"
                  y="50">Interval:
            </text>
            <text style="font-size: 16px" class='deepColorText' :x="text.position.featurePosition.domainPosition.x"
                  y="80">Window:
            </text>
            <text style="font-size: 16px" class='deepColorText'
                  :x="text.position.featurePosition.domainPosition.x"
                  y="112">Rank:
            </text>
            <text style="font-size: 16px" class='deepColorText'
                  :x="text.position.featurePosition.domainPosition.x"
                  y="148">Deepth:
            </text>
          </svg>
          <!--          所有的按钮-->
          <input id='nameInput' v-model="controlValue.modelName"
                 style="position: absolute; top:2px; left:90px; height:25px; width: 190px; border-style: none"
                 type="text" class="form-control"
                 placeholder="Enter the model name">
          <input id='intervalInput' v-model="controlValue.interval" @input="chageInterval" type="range"
                 class="form-range"
                 :min="controlValue.intervalRange.minInterval" :max="controlValue.intervalRange.maxInterval"
                 :step="(controlValue.intervalRange.maxInterval - controlValue.intervalRange.minInterval) / 20"
                 style="width: 220px; position: absolute; top:33px; left: 100px">
          <input id='windowInput' v-model="controlValue.window" @input="sgFilter" type="range" class="form-range"
                 min="5" :max="controlValue.length - 1"
                 step="1"
                 style="width: 220px; position: absolute; top:63px; left: 100px">
          <select id='rankSelect' v-model="controlValue.rank" @change="sgFilter" class="form-select form-select-sm"
                  aria-label=".form-select-sm example"
                  style="height:25px ;width: 55px; position: absolute; top:93px; left:100px; background-position: right 0.5rem center; padding-top: 0.1rem">
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
          </select>
          <select id='deepthSelect' v-model="controlValue.deepth" class="form-select form-select-sm"
                  aria-label=".form-select-sm example"
                  style="height:25px; width: 55px; position: absolute; top:130px; left:100px; background-position: right 0.5rem center; padding-top: 0.1rem">
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
          </select>
          <button @click="treeDiscretize" class="whiteButton"
                  style="position: absolute;top: 92px; left: 204px ;height: 28px; width: 115px; padding-left: 34px">
            Discretize
          </button>
          <i class="el-icon-s-help" style="color:rgb(89, 89, 89); position: absolute; top:98px; left:216px"></i>
          <button @click="predict" class="blueButton"
                  style="position: absolute;top: 128px; left: 205px ;height: 28px; width: 115px; padding-left: 13px">
            Predict
          </button>
          <i class="el-icon-caret-right" style="color:white; position: absolute; top:134px; left:216px"></i>
        </div>
      </div>
    </div>
    <!--    特征筛选容器-->
    <div id='FeaturePanel' style="position: absolute; top: 273px">
      <!--      生成滚动条右侧的边线-->
      <div id="PositionDiv">
        <!--        滚动条的背景阴影-->
        <div id="HideDiv"></div>
        <!--        滚动条容器-->
        <div id="ScrollDiv">
          <!--          循环创建特征容器并构成左侧滚动条边线-->
          <div v-for="feature in features.category" :key=feature class="DivFeature">
            <!--            所有文字、横线与圆圈部分-->
            <svg style="width: 400px" :id="feature +`Svg`">
              <text class="deepColorText" :x="text.position.featurePosition.titlePosition.x"
                    :y="text.position.featurePosition.titlePosition.y">
                {{ feature }}
              </text>
              <path :d="line.lineSize.lineTitile" stroke="darkgrey" :stroke-width="line.lineStyle.size.lineTitile"
                    opacity="0.5"></path>
              <text class="deepColorText" :x="text.position.featurePosition.domainPosition.x"
                    :y="text.position.featurePosition.domainPosition.y">
                Domain
              </text>
              <path :d="line.lineSize.lineDomain" stroke="rgb(145,213,255)"
                    :stroke-width="line.lineStyle.size.lineDomain"></path>
              <text class="deepColorText" :x="text.position.featurePosition.minPosition.x"
                    :y="text.position.featurePosition.minPosition.y"
                    style="transform: rotate(-50deg); transform-origin: 100px 65px; font-size: 12px">
                {{ features.describe[feature].min }}
              </text>
              <circle :r="circle.circleStyle.size.initial.big" :fill="circle.circleStyle.color.big"
                      :cx="circle.circlePosition.circleLeft.x" :cy="circle.circlePosition.circleLeft.y"></circle>
              <circle :r="circle.circleStyle.size.initial.small" :fill="circle.circleStyle.color.small"
                      :cx="circle.circlePosition.circleLeft.x" :cy="circle.circlePosition.circleLeft.y"></circle>
              <text class="deepColorText" :x="text.position.featurePosition.maxPosition.x"
                    :y="text.position.featurePosition.maxPosition.y"
                    style="transform: rotate(-50deg); transform-origin: 300px 65px; font-size: 12px">
                {{ features.describe[feature].max }}
              </text>
              <circle :r="circle.circleStyle.size.initial.big" :fill="circle.circleStyle.color.big"
                      :cx="circle.circlePosition.circleRight.x" :cy="circle.circlePosition.circleRight.y"></circle>
              <circle :r="circle.circleStyle.size.initial.small" :fill="circle.circleStyle.color.small"
                      :cx="circle.circlePosition.circleRight.x"
                      :cy="circle.circlePosition.circleRight.y"></circle>
              <text class="shallowColorText" :x="text.position.featurePosition.inputPosition.x"
                    :y="text.position.featurePosition.inputPosition.y">
                Input
              </text>
            </svg>
            <!--            获取特征按钮-->
            <button @click="getFeatureData(feature)"
                    class="blueButton" style="width:160px; position: relative; top: -48px; left: 130px">Get Details
            </button>
            <!--            <input type='checkbox' :id="feature +`Input`" @click="selectFeature(feature)">-->
            <!--            选中特征按钮-->
            <div class="form-check form-switch">
              <input class="form-check-input" role="switch" type='checkbox' :id="feature +`Input`"
                     @click="selectFeature(feature)"
                     style="width: 35px; height:15px; position: relative; top: -71px;left: 60px">
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from "d3";

export default {
  name: "FeatureDiscretizedView"
  ,
  data: function () {
    return {
      features: {category: [], describe: {}, count: {}, intervalRange: {}},
      predictData: {drawPlace: null, fatherData: {fatherMetrix: null, fatherImportance: null}},
      controlValue: {
        currentFeature: null,
        interval: null,
        intervalRange: {maxInterval: null, minInterval: null},
        window: null,
        length: null,
        rank: null,
        deepth: null,
        modelName: null
      },
      // 结果对应
      resultRecord: {},
      // 美化数据
      line: {
        lineSize: {
          lineTitile: this.curve_generator()([{x: 5, y: 33}, {x: 300, y: 33}]),
          lineDomain: this.curve_generator()([{x: 90, y: 75}, {x: 290, y: 75}]),
          lineBorder: this.curve_generator()([{x: -3.5, y: 50.5}, {x: 520, y: 50.5}])
        },
        lineStyle: {size: {lineTitile: 2, lineDomain: 4, lineBorder: 3}}
      },
      // circle跟line同步
      circle: {
        circleStyle: {
          size: {initial: {big: 8, small: 5}, added: {big: 4, small: 2}},
          color: {big: 'rgb(145,213,255)', small: 'white'}
        },
        circlePosition: {
          circleLeft: {x: 90, y: 75},
          circleRight: {x: 290, y: 75}
        }
      },
      text: {
        position: {
          featurePosition: {
            titlePosition: {x: 5, y: 25},
            domainPosition: {x: 10, y: 80},
            minPosition: {x: 100, y: 65},  // 右10px 上10px
            maxPosition: {x: 300, y: 65},
            inputPosition: {x: 10, y: 120},
            detailPosition: {x: 150, y: 120}
          },
        },
        style: {
          describe: {}
        }
      },
    }
  }
  ,
  methods: {
    // 用于产生折线数据
    getFeatureData(feature) {
      this.$bus.$emit(`Init`, {feature: feature})  // 发送绘制该特征折线图的信号
      this.controlValue.currentFeature = feature
      this.controlValue.intervalRange = this.features.intervalRange[this.controlValue.currentFeature]  // 获取该特征的interval范围
      this.$bus.$emit(`infInterval`, {
        infInterval: {
          maxInterval: this.controlValue.intervalRange.maxInterval,
          minInterval: this.controlValue.intervalRange.minInterval
        }
      })  // 发送折线图横坐标信号
    }
    ,
    chageInterval() {
      this.$bus.$emit('Bd', {feature: this.controlValue.currentFeature, interval: this.controlValue.interval})
    }
    ,
    sgFilter() {
      if ((this.controlValue.rank != null) && (this.controlValue.window != null)) {
        this.$bus.$emit('Sg', {
          feature: this.controlValue.currentFeature,
          interval: this.controlValue.interval,
          window: this.controlValue.window,
          rank: this.controlValue.rank
        })
      }
    }
    ,
    treeDiscretize() {
      this.$bus.$emit('Td', {
        feature: this.controlValue.currentFeature,
        interval: this.controlValue.interval,
        deepth: this.controlValue.deepth
      })
    }
    ,
    // 为Input绑定发送特征信号的响应函数
    selectFeature(feature) {
      if (document.getElementById(`${feature}Input`).checked) {
        // 判断当前是否有结果
        if (this.resultRecord[`${feature}`] == undefined) {
          this.resultRecord[`${feature}`] = {}
          this.resultRecord[`${feature}`]['result'] = null
          this.resultRecord[`${feature}`]['interval'] = null
          var result = null
          var interval = null
        } else {
          result = JSON.parse(JSON.stringify(this.resultRecord[`${feature}`]['result']))
          if (this.resultRecord[`${feature}`]['interval'] != null) {
            interval = this.resultRecord[`${feature}`]['interval']
          } else {
            // 这里的数据来源于散点图给予的sg数据，如果sg没有设置interval，那么就必须要赋予初始值
            interval = (this.features.intervalRange[`${feature}`].maxInterval + this.features.intervalRange[`${feature}`].minInterval) / 2
          }
        }
        this.$bus.$emit('SelectFeature', {
          feature: feature,
          result: result,
          interval: interval
        })
      } else {
        this.$bus.$emit('DropFeature', {feature: feature})
      }
    }
    ,
    curve_generator() {
      var f = d3.line()
          .x((d) => (d.x))
          .y((d) => (d.y))
      return f
    }
    ,
    // 为预测按钮绑定响应函数
    predict() {
      this.$bus.$emit('Predict', {
        modelName: this.controlValue.modelName,
        drawPlace: this.predictData.drawPlace,
        fatherData: JSON.parse(JSON.stringify(this.predictData.fatherData))
      })
    }
    ,
    drawResult(curFeature, curResult) {
      d3.select(`#gResultCircle${curFeature}`).remove()
      var length = curResult[Object.keys(curResult).length - 1][1] // 继承的Rect结构，树模型只有一个范围->[0]；但为了保持一致性，不修改数据结构；其中标号对应的是类
      // delete curResult[Object.keys(curResult).length - 1]  不要tmd乱用，草
      var scale = d3.scaleLinear()
              .domain([0, length])
              .range([this.circle.circlePosition.circleLeft.x, this.circle.circlePosition.circleRight.x]),
          gResultCircle = d3.select(`#${curFeature}Svg`)
              .append('g')
              .attr('id', `gResultCircle${curFeature}`)

      var temp = Object.values(curResult),
          indexMax = d3.max(Object.keys(curResult), d => d)
      for (let index in temp) {
        if (index != indexMax) {
          var dataTemp = temp[index]
          gResultCircle.append('circle')
              .attr('cx', scale(dataTemp[1]))
              .attr('cy', this.circle.circlePosition.circleLeft.y)
              .attr('r', this.circle.circleStyle.size.added.small)
              .attr('fill', this.circle.circleStyle.color.small)
        }
      }

    }
  }
  ,
  mounted() {
    // 获取数据的基本信息
    this.$axios.post('/describe_feature_data')
        .then((res) => {
          var data = res.data
          console.log(data)
          this.features.category = data['features']
          this.features.describe = data['describe']
          this.features.intervalRange = data['intervalRange']
        })
        .catch((error) => {
          console.log('describe_feature_data', error)
        })
    this.$bus.$on('PostLength', (d) => {
      this.controlValue.length = d['length']
    })
    // 监听选中模型并存储绘画位置，父模型多边形和圆形的数据
    this.$bus.$on('SelectPlace', (d) => {
      this.predictData.drawPlace = d['drawPlace']
      this.predictData.fatherData['fatherMetrix'] = d['fatherData']['fatherMetrix']
      this.predictData.fatherData['fatherImportance'] = d['fatherData']['fatherImportance']
    })
    // 取消选中，将相关信息清空
    this.$bus.$on('DropPlace', () => {
      this.predictData.drawPlace = null
      this.predictData.fatherData['fatherMetrix'] = null
      this.predictData.fatherData['fatherImportance'] = null
    })
    // 结果导入
    this.$bus.$on('PostResult', d => {
      this.resultRecord[d['feature']] = {}
      // 记录结果
      this.resultRecord[d['feature']]['result'] = d['result']
      // 记录间隔
      this.resultRecord[d['feature']]['interval'] = d['interval']
      // 表现结果
      this.drawResult(d['feature'], d['result'])
      // // 将相应特征开关关闭，撤回特征输入
      // this.$bus.$emit('DropFeature', {feature: d['feature']})
      // d3.select(`#${d['feature']}Input`)
      //     .attr('checked', false)
    })
  }
}
</script>

<style>
/*滚动条设置*/
::-webkit-scrollbar {
  width: 8px;
  background-color: white;
}

::-webkit-scrollbar-thumb {
  min-height: 300px;
  background-color: rgba(169, 169, 169, 0.8);
  border-bottom-left-radius: 5px;
  border-bottom-right-radius: 5px;
}

.form-check-input:checked {
  background-color: rgb(24, 144, 255);
  border-color: rgb(24, 144, 255);
}

.deepColorText {
  fill: rgb(89, 89, 89);
}

.shallowColorText {
  fill: rgb(111, 109, 109)
}

#FeatureDiscretizedView {
  height: 760px;
  width: 370px;
  border-width: 0 0 1px 1px;
  border-style: solid;
  border-color: rgb(232, 232, 232);
  border-radius: 5px 0 0 3px;
}

#FeaturePanel {
  width: 350px;
  height: 450px;
  position: relative;
  top: 30px;
}

#PositionDiv {
  width: 343px;
  height: 518px;
  position: relative;
  top: 3px;
  border-width: 0 1px 0 0;
  border-color: rgba(169, 169, 169, 0.3);
  border-style: solid;
}

/*放滚动条*/
#ScrollDiv {
  width: 340px;
  height: 518px;
  overflow-y: scroll;
  overflow-x: hidden;
}

/*特征子块*/
.DivFeature {
  width: 330px;
  height: 150px;
  border-width: 0px 1px 2px 0px;
  border-style: solid;
  border-color: rgba(169, 169, 169, 0.3);
}

#HideDiv {
  position: absolute;
  left: 330px;
  width: 13px;
  height: 518px;
  background: black;
  opacity: 0.05;
}

/*蓝色按钮*/
.blueButton {
  color: white;
  border: none;
  background: rgb(24, 144, 255);
  border-radius: 3px;
  font-size: 14px;
  width: 160px
}

.whiteButton {
  color: rgb(89, 89, 89);
  border-color: rgba(217, 217, 217);
  border-style: solid;
  background: white;
  border-radius: 5px;
  font-size: 14px;
}

#FeatureDiscretizedView button {
  font-size: 14px;
}

/*控制面板*/
#ControlView {
  width: 350px;
  height: 350px;
}

</style>
