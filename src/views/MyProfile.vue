<template>
  <v-container>
    <h1>Mi perfil</h1>
    <user-dropdown :user="user.userInfo" :isAdmin="isAdmin" />
    <div class="pa-4 text-end">
      <v-btn class="me-2" @click="this.visible = true"> Change password </v-btn>
      <v-btn @click="this.visibleDelete = true"> Delete account </v-btn>
    </div>
    <v-dialog v-model="visible" max-width="500">
      <v-card>
        <v-container>
          <h2>Modify password</h2>
          <v-card-text>
            <v-text-field
              v-model="currentPassword"
              :append-icon="visible3 ? 'mdi-eye' : 'mdi-eye-off'"
              :type="visible3 ? 'text' : 'password'"
              label="Current password"
              counter
              @click:append="visible3 = !visible3"
            ></v-text-field>
            <v-text-field
              v-model="password"
              :append-icon="visible1 ? 'mdi-eye' : 'mdi-eye-off'"
              :type="visible1 ? 'text' : 'password'"
              label="New password"
              counter
              @click:append="visible1 = !visible1"
            ></v-text-field>
            <v-text-field
              v-model="password2"
              :append-icon="visible2 ? 'mdi-eye' : 'mdi-eye-off'"
              :type="visible2 ? 'text' : 'password'"
              label="Repeat new password"
              counter
              @click:append="visible2 = !visible2"
            ></v-text-field>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="changePassword()"> Change password </v-btn>
          </v-card-actions>
        </v-container>
      </v-card>
    </v-dialog>
    <v-dialog v-model="visibleDelete" persistent max-width="600">
      <v-card>
        <v-container>
          <h2>Delete account</h2>
          <v-card-text>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="email"
                  label="Email"
                  :rules="rulesEmail"
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="password3"
                  :append-icon="visible4 ? 'mdi-eye' : 'mdi-eye-off'"
                  :type="visible4 ? 'text' : 'password'"
                  label="Password"
                  counter
                  @click:append="visible4 = !visible4"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="visibleDelete = false"> Close </v-btn>
            <v-btn color="red" text @click="deleteAccount()">
              Delete account
            </v-btn>
          </v-card-actions>
        </v-container>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { mapState, mapActions } from "vuex";
import UserDropdown from "@/components/UserDropdown.vue";

export default {
  components: {
    UserDropdown,
  },
  data() {
    return {
      isAdmin: false,
      visible: false,
      visible1: false,
      visible2: false,
      visible3: false,
      visible4: false,
      visibleDelete: false,
      currentPassword: "",
      password: "",
      password2: "",
      email: "",
      password3: "",
    };
  },
  computed: {
    ...mapState(["user"]),
  },
  methods: {
    ...mapActions([
      "getUserInfo",
      "fetchUsers",
      "changeUserPassword",
      "removeAccount",
    ]),
    changePassword() {
      if (this.password.length >= 6 && this.password === this.password2) {

        this.changeUserPassword({id: this.user.userInfo.user_id, currentPassword: this.currentPassword, newPassword: this.password})
        this.visible = false;
      } else {
        this.$store.commit(
          "CHANGE_PASSWORD_FAILURE",
          "Passwords do not match or are too short"
        );
      }
    },
    deleteAccount() {
      this.removeAccount({email: this.email, password: this.password3})
        .then(() => {
          this.visibleDelete = false;
          this.$router.push({ name: "login" });
        })
    },
  },
  mounted() {
    this.fetchUsers();
  },
};
</script>
