<template>
  <v-container>
    <v-row justify="center">
      <v-card max-width="1000" width="100%">

        <router-view></router-view>
      </v-card>
    </v-row>
  </v-container>
</template>

<script>
import { mapState, mapActions } from "vuex";

export default {
  computed: {
    ...mapState(["user"])
  },
  methods: {
    ...mapActions([
      'fetchItems',
      'fetchCollections',
      'fetchPieces'
    ]),
  },
  mounted () {
    this.fetchItems()
    this.fetchCollections()
    this.fetchPieces()
  }
};
</script>
