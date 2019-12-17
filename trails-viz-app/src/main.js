import Vue from 'vue'
import App from './App.vue'
import BootstrapVue from 'bootstrap-vue'
import store from "./store"
import router from "./router"

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.config.productionTip = false
Vue.prototype.$apiEndpoint = process.env.VUE_APP_API_ENDPOINT
Vue.use(BootstrapVue)

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
