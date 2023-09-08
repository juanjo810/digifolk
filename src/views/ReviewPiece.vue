<template>
  <v-card>
    <v-container>
      <h1>Pieces list</h1>
      <v-list>
        <v-list-item v-for="(item, index) in this.getReviewPieces" :key="index">
          <v-container>
            <v-row>
              <v-col cols="4">
                  <v-list-item-title>{{ item.title[0] }}</v-list-item-title>
              </v-col>
              <v-list-item-action>
                <v-btn @click="goToDetailsPage(item)">Details</v-btn>
              </v-list-item-action>
            </v-row>
          </v-container>
        </v-list-item>
      </v-list>
      <h1>Collections list</h1>
      <v-list>
        <v-list-item v-for="(item, index) in this.getReviewCollections" :key="index">
          <v-container>
            <v-row>
            <v-col cols="4">  
              <v-list-item-title>{{ item.title[0] }}</v-list-item-title>
            </v-col>
            <v-list-item-action>
              <v-btn @click="goToCollectionPage(item)">Details</v-btn>
            </v-list-item-action>
          </v-row>
          </v-container>
        </v-list-item>
      </v-list>
    </v-container>
  </v-card>
  <v-dialog v-model="visiblePiece" max-width="1000">
    <PieceReview :piece="this.selectedItem" @hide="this.visiblePiece=false"/>
  </v-dialog>
  <v-dialog v-model="visibleCollection" max-width="1000">
    <CollectionReview :collection="this.selectedItem" @hide="this.visibleCollection=false"/>
  </v-dialog>
</template>

<script>
import { mapActions, mapGetters } from "vuex";
import PieceReview from "@/components/PieceReview.vue";
import CollectionReview from "@/components/CollectionReview.vue";

export default {
  components: {
    PieceReview,
    CollectionReview
  },
  data () {
    return{
      visiblePiece: false,
      visibleCollection: false,
      selectedItem: ''
    }
  },
  computed: {
    ...mapGetters(["getReviewPieces", "getReviewCollections"]),
  },
  methods: {
    ...mapActions([
      "getReviewPiece",
      "getReviewCollection"      
    ]),
    goToDetailsPage(item) {
      this.getReviewPiece(item)
        .then((p) => {
          this.selectedItem = p;
          if(p) this.visiblePiece = true;
        })
    },
    goToCollectionPage(item) {
      this.getReviewCollection(item.col_id)
        .then((c) => {
        debugger
          this.selectedItem = c;
          if(c) this.visibleCollection = true;
        })
    },
  },
};
</script>
