import Vue from 'vue'
import VueRouter from 'vue-router'
import LandingPage from './components/LandingPage'
import Dashboard from './components/Dashboard'

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    component: LandingPage
  },
  {
    path: '/dashboard/:project',
    name: 'dashboard',
    component: Dashboard
  }
];

const router = new VueRouter({
  routes,
  mode: 'history'
});

export default router;
