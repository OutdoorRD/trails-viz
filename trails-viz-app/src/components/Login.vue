<template>
  <b-row class="login-div" no-gutters>
    <b-col offset-xl="3" xl="6" offset-lg="3" lg="6" offset-md="2" md="8" sm="12">
      <b-card header="Login to Social Trails" class="login-card">
        <b-card-body>
          <b-form v-on:submit="login" v-on:reset="clear">
            <b-form-group label-for="userName">
              <b-form-input id="userName" v-model="userName" placeholder="User Name"
                            autocomplete="off" required></b-form-input>
            </b-form-group>
            <b-form-group label-for="password">
              <b-form-input id="password" v-model="password" placeholder="Password" type="password"
                            autocomplete="off" required></b-form-input>
            </b-form-group>

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

  export default {
    name: "Login",
    data() {
      return {
        prevRoute: null,
        userName: '',
        password: ''
      }
    },
    beforeRouteEnter(to, from, next) {
      next(self => {
        self.prevRoute = from
      })
    },
    methods: {
      login(event) {
        event.preventDefault();
        // authentication code will go here
        this.$store.dispatch('setLoggedInUser', this.userName);
        Cookie.set('userName', this.userName, 1);
        this.$router.push(this.prevRoute);
      },
      clear(event) {
        event.preventDefault();
        this.userName = '';
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
