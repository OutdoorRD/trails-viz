<template>
  <b-row class="login-div" no-gutters>
    <b-col offset-xl="3" xl="6" offset-lg="3" lg="6" offset-md="2" md="8" sm="12">
      <b-card header="Login to Social Trails" class="login-card">
        <b-card-body>
          <b-form v-on:submit="login" v-on:reset="clear">
            <b-form-group label-for="userName">
              <b-form-input id="userName" v-model="username" placeholder="User Name"
                            autocomplete="off" required></b-form-input>
            </b-form-group>
            <b-form-group label-for="password">
              <b-form-input id="password" v-model="password" placeholder="Password" type="password"
                            autocomplete="off" required></b-form-input>
            </b-form-group>
            <p class="text-danger">
              {{errorMessage}}
            </p>
            <b-button type="submit" class="pb-2 form-button" variant="info">Login</b-button>
            <b-button type="reset" class="pb-2 form-button" variant="danger">Reset</b-button>
          </b-form>
        </b-card-body>
      </b-card>
    </b-col>
  </b-row>
</template>

<script>

  import {Cookie} from '../cookie'
  import axios from 'axios';

  export default {
    name: "Login",
    data() {
      return {
        prevRoute: null,
        username: '',
        password: '',
        errorMessage: ''
      }
    },
    beforeRouteEnter(to, from, next) {
      next(self => {
        self.prevRoute = from
      })
    },
    methods: {
      login(event) {
        let self = this;
        event.preventDefault();
        self.errorMessage = '';
        axios.post(self.$apiEndpoint + '/users/authenticate', {
            username: self.username,
            password: self.password
          }).then(response => {
            if (response.status === 200) {
              let userJson = response.data;
              let authHeader = userJson['token'];
              let userRole = userJson['role'];

              self.$store.dispatch('setLoggedInUser', userJson['username']);
              self.$store.dispatch('setAuthHeader', authHeader);
              self.$store.dispatch('setUserRole', userRole);

              // set axios auth header after new login
              axios.defaults.headers.common['Authorization'] = self.$store.getters.getAuthHeader;

              Cookie.set('username', self.username, 1);
              Cookie.set('authHeader', authHeader, 1);
              Cookie.set('userRole', userRole, 1);

              self.$router.push(self.prevRoute ? self.prevRoute : '/');
            }
        }).catch(error => {
          if (error.response.status === 401) {
            self.errorMessage = error.response.data['error'];
          } else {
            throw error
          }
        })
      },
      clear(event) {
        event.preventDefault();
        this.username = '';
        this.password = '';
      }
    }
  }
</script>

<style scoped>
  .login-div {
    height: calc(100vh - 60px);
    background-image: linear-gradient(#cce3e3, #ffffff);
    align-content: center !important;
  }

  .login-card {
    background-color: transparent;
  }

  .form-button {
    margin: 10px 10px 0 0;
  }
</style>
