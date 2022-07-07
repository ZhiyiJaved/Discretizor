import Vue from 'vue'
import App from './App.vue'
import axios from './http.js'
import * as bootstrap from 'bootstrap'
import '../node_modules/bootstrap/dist/css/bootstrap.css'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
Vue.config.productionTip = false
Vue.prototype.$axios = axios
Vue.prototype.$bus = new Vue()
Vue.use(bootstrap)
Vue.use(ElementUI);

new Vue({
  el: '#app',
  render: h => h(App),
}).$mount('#app')
