<template>
  <div>
    <b-row class="profile-div" no-gutters>
      <b-col offset-xl="3" xl="6" offset-lg="3" lg="6" offset-md="2" md="8" sm="12">
        <b-card header="Profile" class="profile-card">
          <b-card-body>
            <b-form v-on:submit="updateUserInfo">
              <p class="text-success">
                {{successMessage}}
              </p>
              <b-form-group label="User Name" label-for="username" label-cols-sm="4"  label-cols-lg="3">
                <b-form-input id="username" v-model="userInfo.username" autocomplete="off" disabled></b-form-input>
              </b-form-group>
              <b-form-group label="Name" label-for="name" label-cols-sm="4"  label-cols-lg="3">
                <b-form-input id="name" v-model="userInfo.name" autocomplete="off" required></b-form-input>
              </b-form-group>
              <b-form-group label="Email" label-for="email" label-cols-sm="4"  label-cols-lg="3">
                <b-form-input id="email" v-model="userInfo.email" autocomplete="off" required></b-form-input>
              </b-form-group>
              <b-form-group label="Role" label-for="role" label-cols-sm="4"  label-cols-lg="3">
                <b-form-input id="role" v-model="userInfo.role" autocomplete="off" required disabled></b-form-input>
              </b-form-group>
              <b-form-group label="Password" label-for="password" label-cols-sm="4"  label-cols-lg="3">
                <b-form-input id="password" v-model="userInfo.password" type="password" v-on:keyup="matchPassword"
                              placeholder="Enter new password to update, leave blank to keep existing password"
                              autocomplete="off"></b-form-input>
              </b-form-group>
              <b-form-group label="Confirm Password" label-for="confirmPassword" label-cols-sm="4"  label-cols-lg="3">
                <b-form-input id="confirmPassword" v-model="confirmPassword" type="password" v-on:keyup="matchPassword"
                              placeholder="Confirm new password to update, leave blank to keep existing password"
                              autocomplete="off"></b-form-input>
              </b-form-group>
              <p class="text-danger">
                {{errorMessage}}
              </p>
              <b-button type="submit" class="pb-2 form-button" variant="info">Save</b-button>
            </b-form>
          </b-card-body>
        </b-card>
      </b-col>
    </b-row>
  </div>
</template>

<script>
  import axios from 'axios';

  export default {
    name: "UserProfile",
    data() {
      return {
        username: '',
        userInfo: {},
        confirmPassword: '',
        errorMessage: '',
        successMessage: ''
      }
    },
    mounted() {
      let self = this;

      self.username = self.$route.params.username;
      axios.get(self.$apiEndpoint + '/users/' + self.username)
        .then(response => {
          self.userInfo = response.data;
        })
    },
    methods: {
      updateUserInfo: function (event) {
        let self = this;
        event.preventDefault();
        if (self.userInfo.password !== self.confirmPassword) {
          self.errorMessage = 'Password and confirm password do not match!';
          return
        }

        axios.put(self.$apiEndpoint + '/users/' + self.username, self.userInfo)
          .then(respose => {
            self.userInfo = respose.data;
            self.confirmPassword = '';
            self.successMessage = 'Details Successfully Updated!';
          })

      },
      matchPassword: function() {
        let self = this;
        if (self.userInfo.password !== self.confirmPassword) {
          self.errorMessage = 'Password and confirm password do not match!';
        } else {
          self.errorMessage = '';
        }
      }
    }
  }
</script>

<style scoped>
  .profile-div {
    height: calc(100vh - 60px);
    background-image: linear-gradient(var(--color-secondary), var(--color-white));
    align-content: center !important;
    font-family: 'Roboto Condensed', sans-serif;
  }

  .profile-card {
    background-color: transparent;
  }
</style>
