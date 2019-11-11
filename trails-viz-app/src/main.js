import Vue from 'vue'
import App from './App.vue'
import BootstrapVue from 'bootstrap-vue'
import store from "./store"

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.config.productionTip = false
Vue.prototype.$apiEndpoint = process.env.VUE_APP_API_ENDPOINT
Vue.use(BootstrapVue)

new Vue({
  render: h => h(App),
  store,
}).$mount('#app')
