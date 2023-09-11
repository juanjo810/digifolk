<template>
  <div>
    <v-card class="mx-auto my-12" max-width="374">
      <template>
        <v-progress-linear
          color="deep-purple"
          height="10"
          indeterminate
        ></v-progress-linear>
      </template>

      <v-img height="250" style="margin: 5px" src="@/assets/logo.png"></v-img>

      <v-card-title>Retrieve password</v-card-title>

      <v-card-text>
        <v-row>
          <v-col cols="12">
            <v-text-field v-model="email" label="Email" required></v-text-field>
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="deep-purple lighten-2" text @click="restablecerPass()">
          Retrieve password
        </v-btn>
      </v-card-actions>
    </v-card>
    <v-dialog v-model="this.visibility" persistent max-width="600">
      <v-card>
        <v-card-title class="text-h5"> Sent email </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <b>The email has been sent successfully.</b><br />
              Please, <b>reset your password</b> by clicking on the link we have
              sent to your email address.
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="green darken-1" text @click="continuar()"> Next </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapActions } from "vuex";

export default {
  data() {
    return {
      email: "",
      visibility: false,
    };
  },
  methods: {
    ...mapActions([
      //'resetPassword'
    ]),
    restablecerPass() {
      /*this.resetPassword(this.email)
        .then(() => {
          this.email = ''
          this.visibility = true
        })*/

      this.email = "";
      this.visibility = true;
    },
    continuar() {
      this.visibility = false;
      this.$router.push({ name: "login" });
    },
  },
};
</script>
