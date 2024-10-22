import Vue from 'vue'
import VueRouter from 'vue-router'
import LandingPage from './components/LandingPage'
import Dashboard from './components/Dashboard'
import Login from './components/Login'
import UserProfile from "./components/UserProfile";
import Administration from "./components/Administration";

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    component: LandingPage
  },
  {
    path: '/login',
    component: Login
  },
  {
    path: '/administration',
    component: Administration
  },
  {
    path: '/user/:username',
    name: 'user',
    component: UserProfile
  },
  {
    path: '/dashboard/:project',
    name: 'dashboard',
    component: Dashboard
  }
];

const router = new VueRouter({
  routes,
  mode: 'history',
  base: process.env.NODE_ENV === 'production' ? '/trails-viz/' : '/'
});

export default router;
