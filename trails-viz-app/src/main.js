import Vue from 'vue'
import App from './App.vue'
import {BootstrapVue, BootstrapVueIcons} from 'bootstrap-vue'
import store from "./store"
import router from "./router"

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import {Cookie} from "./cookie"
import axios from "axios";

Vue.config.productionTip = false
Vue.prototype.$apiEndpoint = process.env.VUE_APP_API_ENDPOINT
Vue.use(BootstrapVue)
Vue.use(BootstrapVueIcons)

// Check cookies if user is logged in
let username = Cookie.get('username');
if (username !== undefined) {
  store.dispatch('setLoggedInUser', username);
  store.dispatch('setAuthHeader', Cookie.get('authHeader'));
  store.dispatch('setUserRole', Cookie.get('userRole'));
  // set axios to send auth header in every request
  axios.defaults.headers.common['Authorization'] = store.getters.getAuthHeader;
}

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
