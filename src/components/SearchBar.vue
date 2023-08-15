<template>
  <div>
      <v-row>
          <v-toolbar dense floating>
            <v-text-field
              hide-details
              prepend-icon="mdi-magnify"
              single-line
              v-model="searchQuery"
            ></v-text-field>
          </v-toolbar>
      </v-row>
      <v-row>
      <v-list v-if="searchQuery">
        <v-list-item
          v-for="piece in filteredPieces"
          :key="piece.id"
          @click="console.log(piece.id)"
        >
          <v-list-item-title>{{ piece.title[0] }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-row>
  </div>
</template>

<script>
import { mapState, mapGetters } from "vuex";

export default {
  data() {
    return {
      searchQuery: "",
      cosas: [
        {
          title: ["hola"],
          id: 1,
        },
        {
          title: ["adios"],
          id: 2,
        },
        {
          title: ["que tal"],
          id: 3,
        },
        {
          title: ["hola2"],
          id: 4,
        },
      ],
    };
  },
  props: {
    objects: {
      type: String,
      required: true,
    },
  },
  computed: {
    ...mapState(["pieces", "collections"]),
    ...mapGetters([]),
    filteredPieces() {
      if (this.objects === "pieces") {
        return this.pieces.filter((piece) =>
          piece.title[0].toLowerCase().includes(this.searchQuery.toLowerCase())
        );
      } else if (this.objects === "collections") {
        return this.cosas.filter((collection) =>
          collection.title[0]
            .toLowerCase()
            .includes(this.searchQuery.toLowerCase())
        );
      }
      return [];
    },
  },
};
</script>
