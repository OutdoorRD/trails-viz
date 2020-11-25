<template>
  <div>
    <b-row no-gutters>
      <b-col offset-xl="1" xl="5" offset-lg="1" lg="5" md="6" sm="12">
        <b-card-body>
          <b-list-group>
            <b-list-group-item button variant="info" v-on:click="showAddUserView">
              <b-icon icon="person-plus"></b-icon>
                  add new
            </b-list-group-item>
            <b-list-group-item button v-for="user in allUsers" :key="user" v-on:click="showEditUserView">
              {{user}}
              <b-icon icon="pencil-square" class="icons-right"></b-icon>
            </b-list-group-item>
          </b-list-group>
          <p class="text-success user-form">
            {{successMessage}}
          </p>
        </b-card-body>
      </b-col>
      <b-col xl="5" lg="5" md="6" sm="12">
        <b-card-body>
          <b-list-group>
            <b-list-group-item button variant="info" v-show="mode === 'add'">
              Adding New User
            </b-list-group-item>
            <b-list-group-item button variant="info" v-show="mode === 'edit'">
              Editing  {{currentUser}}
            </b-list-group-item>
          </b-list-group>
          <b-form class="user-form" v-show="mode !== 'view'" v-on:submit="addUpdateUser">
            <b-form-group label="User Name" label-for="username" label-cols-sm="4"  label-cols-lg="3">
              <b-form-input id="username" v-model="userInfo.username" autocomplete="off" required
                placeholder="allowed chars: a-z . - _" :disabled="mode === 'edit'"></b-form-input>
            </b-form-group>
            <b-form-group label="Name" label-for="name" label-cols-sm="4"  label-cols-lg="3">
              <b-form-input id="name" v-model="userInfo.name" autocomplete="off" required></b-form-input>
            </b-form-group>
            <b-form-group label="Email" label-for="email" label-cols-sm="4"  label-cols-lg="3">
              <b-form-input id="email" v-model="userInfo.email" autocomplete="off" required></b-form-input>
            </b-form-group>
            <b-form-group label="Role" label-for="role" label-cols-sm="4"  label-cols-lg="3">
              <b-form-select id="role" v-model="userInfo.role" value-field="item"
                             text-field="name" :options="validRoles" required></b-form-select>
            </b-form-group>
            <b-form-group label="Password" label-for="password" label-cols-sm="4"  label-cols-lg="3">
              <b-form-input id="password" v-model="userInfo.password" type="password"
                            placeholder="Enter new password to update, leave blank to keep existing password"
                            autocomplete="off"></b-form-input>
            </b-form-group>

            <p class="text-danger">
              {{errorMessage}}
            </p>
            <b-button type="submit" class="pb-2 form-button action-buttons" variant="info">Save</b-button>
            <b-button type="button" class="pb-2 form-button action-buttons" variant="danger"
                      v-show="mode === 'edit'" v-on:click="deleteUser">Delete</b-button>
          </b-form>
        </b-card-body>
      </b-col>
      <b-col xl="5" lg="5" md="6" sm="12">
        <b-card-body>

        </b-card-body>
      </b-col>
    </b-row>
  </div>
</template>

<script>
import axios from 'axios';

export const MODE = {
    VIEW: 'view',
    ADD: 'add',
    EDIT: 'edit'
  };

  export default {
    name: "Administration",

    data() {
      return {
        mode: MODE.VIEW,
        allUsers: [],
        currentUser: '',
        userInfo: {},
        successMessage: '',
        errorMessage: '',
        validRoles: [
          {item: 'admin', name: 'Admin'},
          {item: 'manager', name: 'Manager'},
        ]
      }
    },
    mounted() {
      let self = this;

      axios.get(self.$apiEndpoint + '/users/listAll')
        .then(response => {
          self.allUsers = response.data;
        })
    },
    methods: {
      showAddUserView: function () {
        this.mode = MODE.ADD;
      },
      showEditUserView: function (event) {
        let self = this;
        let username = event.target.innerText;
        axios.get(self.$apiEndpoint + '/users/' + username)
          .then(response => {
            self.userInfo = response.data;
            self.currentUser = username;
          });
        this.mode = MODE.EDIT;
      },
      addUpdateUser: function(event) {
        if (this.mode === MODE.ADD) {
          this.addUser(event)
        } else if (this.mode === MODE.EDIT) {
          this.updateUser(event)
        }
      },
      addUser: function(event) {
        let self = this;
        event.preventDefault();

        let username = self.userInfo.username;
        if (self.allUsers.includes(username)) {
          self.errorMessage = 'username: ' + username + ' already taken';
          setTimeout(() => self.errorMessage = '', 5000);
          return
        }

        axios.post(self.$apiEndpoint + '/users/' + username, self.userInfo)
          .then(response => {
            username = response.data.username;
            self.successMessage = 'User Successfully Added!';
            self.allUsers.push(username);

            setTimeout(() => self.successMessage = '', 5000);
            self.mode = MODE.VIEW;
            self.userInfo = {};
          })
      },
      updateUser: function(event) {
        let self = this;
        event.preventDefault();

        let username = self.currentUser;
        axios.put(self.$apiEndpoint + '/users/' + username, self.userInfo)
          .then(response => {
            username = response.data.username;
            self.successMessage = 'User Successfully Updated';

            setTimeout(() => self.successMessage = '', 5000);
            self.mode = MODE.VIEW;
            self.userInfo = {};
          })
      },
      deleteUser: function () {
        let self = this;
        axios.delete(self.$apiEndpoint + '/users/' + self.currentUser, self.userInfo)
          .then(response => {
            self.successMessage = response.data.msg;
            self.allUsers = self.allUsers.filter(user => user !== self.currentUser);
            setTimeout(() => self.successMessage = '', 5000);
            self.currentUser = '';
            self.mode = MODE.VIEW;
            self.userInfo = {}
          })
      }
    }
  }
</script>

<style scoped>
  .icons-right {
    float: right;
  }
  .user-form {
    margin: 20px 0 0 20px;
  }
  .action-buttons {
    margin-right: 20px;
  }
</style>
