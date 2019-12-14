import Vue from 'vue'
import VueRouter from 'vue-router'
import VuePageTransition from 'vue-page-transition'
import LandingPage from './components/LandingPage'
import Dashboard from './components/Dashboard'

Vue.use(VueRouter);
Vue.use(VuePageTransition);

const routes = [
  {
    path: '/',
    component: LandingPage,
    meta: {transition: 'fade'}
  },
  {
    path: '/dashboard/:project',
    name: 'dashboard',
    component: Dashboard,
    meta: {transition: 'fade'}
  }
];

const router = new VueRouter({
  routes,
  mode: 'history'
});

export default router;
