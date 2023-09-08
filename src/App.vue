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
          width="60"
          style="cursor: pointer"
          @click="$router.push({name: 'dashboard'})"
        />
      </div>
      
        <v-app-bar-title>Digifolk</v-app-bar-title>
        <v-menu v-if="this.user.tokenSession" location="bottom">
          <template v-slot:activator="{ props }">
            <v-btn icon dark v-bind="props">
              <v-icon>mdi-file-music</v-icon>
              <span>Pieces</span>
            </v-btn>
          </template>
          <v-list>
            <v-list-item @click="$router.push({name: 'viewPiece'})">
              <v-list-item-title>View piece</v-list-item-title>
            </v-list-item>
            <v-list-item @click="$router.push({name: 'sheetpiece'})">
              <v-list-item-title>View sheetpiece</v-list-item-title>
            </v-list-item>
            <v-list-item @click="this.goToPieceForm">
              <v-list-item-title>Upload piece</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
        <v-spacer></v-spacer>
        
        <v-menu v-if="this.user.tokenSession" location="bottom">
          <template v-slot:activator="{ props }">
            <v-btn icon dark v-bind="props">
              <v-icon>mdi-folder-music-outline</v-icon>
              <span>Collections</span>
            </v-btn>
          </template>
          <v-list>
            <v-list-item @click="$router.push({name: 'viewCollection'})">
              <v-list-item-title>
                View collection
              </v-list-item-title>
            </v-list-item>
            <v-list-item @click="this.goToCollectionForm">
              <v-list-item-title>Upload collection</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
        <v-spacer></v-spacer>
        <v-spacer></v-spacer>
        <v-spacer></v-spacer>
        <v-menu v-if="this.user.tokenSession" location="bottom">
          <template v-slot:activator="{ props }">
            <v-btn icon dark v-bind="props">
              <v-icon>mdi-account</v-icon>
            </v-btn>
          </template>
          <v-list>
            <v-list-item @click="$router.push({name: 'profile'})">
              <v-list-item-title>Profile</v-list-item-title>
            </v-list-item>
            <div v-if="this.user.userInfo.is_admin">
              <v-list-item @click="$router.push({name: 'modifyItems'})">
                <v-list-item-title>Modify items</v-list-item-title>
              </v-list-item>
              <v-list-item @click="$router.push({name: 'reviews'})">
                <v-list-item-title>Reviews</v-list-item-title>
              </v-list-item>
              <v-list-item @click="$router.push({name: 'users'})">
                <v-list-item-title>View users</v-list-item-title>
              </v-list-item>
            </div>
            <v-list-item @click="logout()">
              <v-list-item-title>Logout</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>

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
import { mapState, mapActions } from 'vuex';

export default {
  name: 'App',

  data: () => ({
    //
  }),
  computed: {
    ...mapState([
      'error',
      'user'
    ]),
    otroError: {
      get () {
        return this.error
      },
      set (value) {
        this.$store.commit('RESET_ERROR', value)
      }
    }
  },
  methods: {
    ...mapActions([
      'logOut',
      'resetPieceForm',
      'resetCollectionForm'
    ]),
    logout() {
      this.logOut()
      .then(() => {
        this.$router.push({name: 'login'})
      })
    },
    goToCollectionForm() {
      this.resetCollectionForm()
      this.$router.push({name: 'collectionForm'})
    },
    goToPieceForm() {
      this.resetPieceForm()
      this.$router.push({name: 'uploadPiece'})
    }
  }
};
</script>
