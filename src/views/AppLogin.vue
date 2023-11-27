<template>
  <div>
    <v-card class="mx-auto my-12" max-width="374">
      <v-img height="250" style="margin: 5px" src="@/assets/logo.png"></v-img>

      <v-card-title>Login</v-card-title>

      <v-card-text>
        <v-row>
          <v-col cols="12">
            <v-text-field
              v-model="user"
              label="Username"
              required
            ></v-text-field>
          </v-col>

          <v-col cols="12">
            <v-text-field
              v-model="password"
              :append-icon="visible ? 'mdi-eye' : 'mdi-eye-off'"
              :type="visible ? 'text' : 'password'"
              label="Password"
              counter
              @click:append="visible = !visible"
              v-on:keyup.enter="logIn"
            ></v-text-field>
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>

        <v-btn color="deep-purple lighten-2" text @click="logIn()">
          <span v-if="fetchingUser">Iniciando sesion...</span
          ><span v-else>Iniciar sesión</span>
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapState } from "vuex";

export default {
  data() {
    return {
      user: "",
      password: "",
      visible: false,
    };
  },
  computed: {
    ...mapState(["fetchingUser", "error"]),
    ...mapGetters(["getUser"]),
  },
  methods: {
    ...mapActions(["loginUser"]),
    logIn() {
      if (this.user !== "" || this.password !== "") {
        this.loginUser({ user: this.user, password: this.password })
          .then(() => {
            console.log("OK");
            this.user = this.password = "";
            this.$router.push({ name: "dashboard" });
          })
          .catch(console.log);
      } else {
        this.$store.commit("LOGIN_USER_FAILURE", {
          error: "Please, fill all the fields",
        });
      }
    },
  },
  created() {
    console.log(process.env.VUE_APP_GTAT_ID)
  },
};
</script>
