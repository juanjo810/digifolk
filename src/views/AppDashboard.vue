<template>
  <v-container>
    <v-row justify="center">
      <v-card max-width="1000" width="100%">
        <v-bottom-navigation>
          <v-btn value="excel" @click="$router.push({name: 'userForm'})">
            <span>XML user data</span>
            <v-icon>mdi-account</v-icon>
          </v-btn>

          <v-btn value="xml" @click="$router.push({name: 'sheetForm'})">
            <span>Music sheet data</span>
            <v-icon>mdi-file-music</v-icon>
          </v-btn>

          <v-btn value="reports" @click="$router.push({name: 'collectionForm'})"
          >
            <span>Source data</span>
            <v-icon>mdi-folder-music-outline</v-icon>
          </v-btn>
        </v-bottom-navigation>

        <router-view></router-view>
      </v-card>
    </v-row>
  </v-container>
</template>

<script>
import { mapState } from "vuex";

export default {
  computed: {
    ...mapState(["user"]),
  },
};
</script>
