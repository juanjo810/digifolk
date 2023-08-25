<template>
  <v-container>
    <v-expansion-panels>
      <v-expansion-panel>
        <v-expansion-panel-title>
          {{ getUserName(user) }}
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-row>
            <v-col cols="4">
              <v-text-field
                label="Username"
                v-model="currentUser.username" ></v-text-field>
            </v-col>
            <v-col cols="4">
              <v-text-field
                label="Name"
                v-model="currentUser.first_name" ></v-text-field>
            </v-col>
            
            <v-col cols="4">
              <v-text-field
                label="Surname"
                v-model="currentUser.last_name" ></v-text-field>
            </v-col>
            
            <v-col cols="6">
              <v-text-field
                label="Email"
                v-model="currentUser.email" ></v-text-field>
            </v-col>
            
            <v-col cols="4">
              <v-text-field
                label="Institution"
                v-model="currentUser.institution" ></v-text-field>
            </v-col>
            
            <v-col cols="2">
              <v-checkbox
                label="Admin"
                v-model="currentUser.is_admin" ></v-checkbox>
            </v-col>
          </v-row>
          <v-btn @click="editUser()"> Save user </v-btn>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-container>
</template>

<script>
import { mapActions, mapGetters } from "vuex";

export default {
  props: {
    user: {
      type: Object,
      required: true
    },
    index: {
      type: Number,
      required: true}
  },
  data () {
    return {
      currentUser: {
        user_id: this.user.user_id,
        username: this.user.username,
        first_name: this.user.first_name,
        last_name: this.user.last_name,
        email: this.user.email,
        institution: this.user.institution,
        is_admin: this.user.is_admin,
        piece: [],
        password: 'admin'
      }
    }
  },
  computed: {
    ...mapGetters(["getUserName"])
  },
  methods: {
    ...mapActions([
      "editUserInfo"
    ]),
    editUser() {
      this.editUserInfo({user: this.currentUser, oldMail: this.user.email});
    }
  }
};
</script>
