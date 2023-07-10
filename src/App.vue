<template>
  <v-app>
    <v-app-bar
      app
      color="blue"
      dark
    >
      <div class="d-flex align-center">
        <v-img
          alt="Digifolk Logo"
          class="shrink mr-2"
          contain
          src="@/assets/logo.png"
          transition="scale-transition"
          width="40"
          style="cursor: pointer"
          @click="$router.push({name: 'dashboard'})"
        />
        <h1>Digifolk</h1>
        
      </div>

      <v-spacer></v-spacer>

    </v-app-bar>
    <v-dialog
    v-if="otroError!==''"
    v-model="otroError"
    max-width="400">
    <v-alert
      type="error"
      v-if="otroError!==''"
    >{{otroError}}</v-alert>
    </v-dialog>
    <v-main style="background-color: #456">
      <router-view/>
    </v-main>
  </v-app>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'App',

  data: () => ({
    //
  }),
  computed: {
    ...mapState([
      'error'
    ]),
    otroError: {
      get () {
        return this.error
      },
      set (value) {
        this.$store.commit('RESET_ERROR', value)
      }
    }
  }
};
</script>
