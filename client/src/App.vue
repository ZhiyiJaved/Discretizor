<template>
  <div id="app">
    <!--标题部分-->
    <header class="navbar navbar-dark sticky-top flex-md-nowrap p-0" style="background: rgb(53,58, 63)">
      <a class="navbar-brand col-md-3 col-lg-2 me-0 px-3" href="#">DiscretizOR: Interpretability-Aware Feature Discretization for Logistic Regression</a>
    </header>
    <div class="container-fluid">
      <div class="row">
        <div class="col-md-9">
          <div class="row">
            <MainView></MainView>
          </div>
        </div>
        <div class="col-md-3">
          <div class="row">
            <FeatureDiscretizedView></FeatureDiscretizedView>
          </div>
        </div>
        <div class="col-md-6" style="position: relative; bottom:380px">
          <div class="row">
            <LineView></LineView>
          </div>
        </div>
        <div class="col-md-3" style="position: relative; bottom:380px">
          <div class="row">
            <ScatterView></ScatterView>
          </div>
        </div>
      </div>
    </div>
  </div>
  <!--    <LineTimeTest></LineTimeTest>-->
</template>
<style>
#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-family: system-ui;
  text-align: left;
}
</style>
<script>
import MainView from './components/MainView.vue'
import FeatureDiscretizedView from './components/FeatureDiscretizedView.vue'
import LineView from './components/LineView.vue'
import ScatterView from './components/ScatterView.vue'

export default {
  name: 'App',
  components: {
    MainView: MainView,
    FeatureDiscretizedView: FeatureDiscretizedView,
    LineView:LineView,
    ScatterView:ScatterView
  }
}
</script>


