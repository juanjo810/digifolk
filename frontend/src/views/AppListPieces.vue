<template>
    <v-container>
    <v-row>
        <v-col cols="12">
            <list-object :list="pieces" redirect="viewPiece" title="List of pieces"/>
        </v-col>
    </v-row>
    <v-container>
      <v-row>
        <v-spacer></v-spacer>
        <v-btn @click="exportPieces">Export all pieces</v-btn>
      </v-row>
    </v-container>
    </v-container>
  </template>
  
<script>
import { mapState, mapActions } from 'vuex';
import ListObject from '@/components/ListObjects.vue'; // Adjust the path as needed

export default {
  components: {
    ListObject,
  },
    data() {
    },
    computed:{
        ...mapState(['user', 'pieces'])
    },
    methods: {
      ...mapActions(['exportAllPieces']),
      exportPieces() {
        this.exportAllPieces();
      },
    },
  };
  </script>
  