<template>
    <v-container>
    <v-row>
        <v-col cols="12">
            <list-object :list="collections" redirect="viewCollection" title="List of collections"/>
        </v-col>
    </v-row>
    </v-container>
  </template>
  
<script>
import { mapState } from 'vuex';
import ListObject from '@/components/ListObjects.vue'; // Adjust the path as needed

export default {
  components: {
    ListObject,
  },
    data() {
    },
    computed:{
        ...mapState(['collections'])
    },
    methods: {
      // Method to redirect to piece component
      redirectToPiece() {
        // Redirect to the component for the selected piece
        //this.$router.push({ name: 'Piece', params: { id: pieceId } });
      },
    },
  };
  </script>
  