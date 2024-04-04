<template>
    <v-card>
      <v-card-title>List of Pieces</v-card-title>
      <v-card-text>
        <v-list dense>
          <v-list-item
            v-for="(piece, index) in pieces"
            :key="index"
            @click="redirectToPiece(piece)"
          >
            <v-list-item-title>{{ piece.title[0] }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>
  </template>
  
<script>
import { mapState } from 'vuex';

  export default {
    props: {
      pieces: {
        type: Array,
        required: true,
      },
    },
    computed: {
      ...mapState(['pieceFromList']) 
    }, 
    methods: {
      redirectToPiece(myPiece) {
        console.log("Voy a pasarla: ",myPiece.music_id)
        this.$store.commit('SET_PIECEFROMLIST', myPiece.music_id);
        this.$router.push({ name: 'viewPiece'});
      },
    },
  };
</script>
  