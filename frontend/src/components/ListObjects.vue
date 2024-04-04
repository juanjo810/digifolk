<template>
    <v-card>
      <v-card-title class="text-h5 text-center">{{ this.title }}</v-card-title>
      <v-card-text>
        <v-list dense>
          <v-list-item
            v-for="(l, index) in list"
            :key="index"
            @click="redirectToPiece(l)"
          >
            <v-list-item-title class="text-center">{{ Array.isArray(l.title) ? l.title[0] : l.title }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>
  </template>
  
<script>
  export default {
    props: {
      list: {
        type: Array,
        required: true,
      },
      redirect: {
        type: String,
        required: true,
      },
      title: {
        type: String,
        required: true,
      },
    },
    methods: {
      redirectToPiece(myObject) {
        // console.log("Voy a pasarla: ",myObject.music_id || myObject.col_id)
        this.$store.commit('SET_OBJECTFROMLIST',myObject.music_id || myObject.col_id);
        this.$router.push({ name: this.redirect});
      },
    },
  };
</script>
  