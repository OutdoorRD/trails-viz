import Vue from 'vue'
import App from './App.vue'
import BootstrapVue from 'bootstrap-vue'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.config.productionTip = false
Vue.prototype.$apiEndpoint= 'http://localhost:5000/api'
Vue.use(BootstrapVue)

new Vue({
  render: h => h(App),
}).$mount('#app')
