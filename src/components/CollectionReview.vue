<template>
  <v-card>
    <v-container>
      <h1>Review collection</h1>
      <v-card-text>
        <v-row>
          <v-col cols="6">
            <v-text-field
              v-model="this.collectionForm.title"
              label="Title"
            ></v-text-field>
          </v-col>

          <v-col cols="6">
            <v-select
              v-model="this.collectionForm.rights"
              label="Rights"
              :items="this.getItemsNameByType(1)"
            ></v-select>
          </v-col>

          <v-col cols="12">
            <h2>Selected date: {{ this.collectionForm.date }}</h2>
          </v-col>

          <v-col cols="6">
            <h2>Creators</h2>
          </v-col>

          <v-container v-for="(c, index) in creadores" :key="index">
            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model="c.name"
                  @input="updateCreator()"
                  label="Name or URI"
                  :rules="rules"
                  hint="URI example in http://www.dib.ie"
                  persistent-hint
                ></v-text-field>
              </v-col>
              <v-col cols="5">
                <v-select
                  v-model="c.role"
                  @update:modelValue="updateCreator()"
                  label="Role"
                  :items="getItemsNameByType(5)"
                  :rules="rules"
                ></v-select>
              </v-col>
            </v-row>
          </v-container>

          <v-col cols="6">
            <h2>Contributors</h2>
          </v-col>
          <v-container v-for="(c, index) in contribuidores" :key="index">
            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model="c.name"
                  @input="updateContributor()"
                  label="Name or URI"
                  hint="URI example in http://www.dib.ie"
                  persistent-hint
                ></v-text-field>
              </v-col>
              <v-col cols="5">
                <v-select
                  v-model="c.role"
                  @update:modelValue="updateContributor()"
                  label="Role"
                  :items="getItemsNameByType(6)"
                ></v-select>
              </v-col>
            </v-row>
          </v-container>

          <v-col cols="6">
            <v-select
              v-model="this.collectionForm.source_type"
              label="Type"
              :items="getItemsNameByType(7)"
            ></v-select>
          </v-col>

          <v-col cols="6">
            <v-text-field
              v-model="this.collectionForm.source"
              label="Source"
            ></v-text-field>
          </v-col>

          <v-col cols="6">
            <v-text-field
              v-model="this.collectionForm.description"
              label="Description"
            ></v-text-field>
          </v-col>

          <v-col cols="6">
            <v-text-field
              v-model="this.collectionForm.formatting"
              label="Format"
            ></v-text-field>
          </v-col>

          <v-col cols="6">
            <v-text-field
              v-model="this.collectionForm.extent"
              label="Extent"
            ></v-text-field>
          </v-col>

          <v-col cols="6">
            <v-text-field
              v-model="this.collectionForm.publisher"
              label="Publisher"
            ></v-text-field>
          </v-col>

          <v-col cols="6">
            <v-text-field
              v-model="this.collectionForm.subject"
              label="Subject"
            ></v-text-field>
          </v-col>

          <v-col cols="6">
            <v-text-field
              v-model="this.collectionForm.language"
              label="Language code"
            ></v-text-field>
          </v-col>

          <v-col cols="6">
            <v-text-field
              v-model="this.collectionForm.relation"
              label="Relation"
            ></v-text-field>
          </v-col>

          <v-col cols="6">
            <v-text-field
              v-model="this.collectionForm.coverage"
              label="Coverage"
            ></v-text-field>
          </v-col>

          <v-col cols="12">
            <h2>Spatial</h2>
          </v-col>
          <v-col cols="4">
            <v-text-field
              v-model="this.collectionForm.spatial.country"
              label="Country"
            ></v-text-field>
          </v-col>
          <v-col cols="4">
            <v-text-field
              v-model="this.collectionForm.spatial.state"
              label="State"
            ></v-text-field>
          </v-col>
          <v-col cols="4">
            <v-text-field
              v-model="this.collectionForm.spatial.location"
              label="Location"
            ></v-text-field>
          </v-col>

          <v-col cols="12">
            <h2>Temporal</h2>
          </v-col>
          <v-col cols="4">
            <v-text-field
              v-model="this.collectionForm.temporal.century"
              label="Century"
            ></v-text-field>
          </v-col>
          <v-col cols="4">
            <v-text-field
              v-model="this.collectionForm.temporal.decade"
              label="Decade"
            ></v-text-field>
          </v-col>
          <v-col cols="4">
            <v-text-field
              v-model="this.collectionForm.temporal.year"
              label="Year"
            ></v-text-field>
          </v-col>

          <v-col cols="12">
            <v-text-field
              v-model="this.collectionForm.rights_holder"
              label="rights_holder"
            ></v-text-field>
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="deep-purple lighten-2" text @click="validate">
          Validate piece
        </v-btn>
        <v-btn color="deep-purple lighten-2" text @click="reject">
          Reject piece
        </v-btn>
      </v-card-actions>
    </v-container>
  </v-card>
</template>

<script>
import { mapActions, mapGetters } from "vuex";

export default {
  data() {
    return {
      collectionForm: null,
    };
  },
  props: {
    collection: {
      type: Object,
      required: true,
    },
  },
  computed: {
    ...mapGetters(["getItemsNameByType"]),
    title: {
      get() {
        return this.collectionForm.title;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_TITLE", value);
      },
    },
    right: {
      get() {
        return this.collectionForm.rights;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_RIGHT", value);
      },
    },
    creator() {
      return this.collection.creator_role;
    },
    contributor() {
      return this.collection.contributor_role;
    },
    date() {
      return this.collectionForm.date;
    },
    description: {
      get() {
        return this.collectionForm.description;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_DESCRIPTION", value);
      },
    },
    type: {
      get() {
        return this.collectionForm.source_type;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_TYPE", value);
      },
    },
    format: {
      get() {
        return this.collectionForm.formatting;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_FORMAT", value);
      },
    },
    subject: {
      get() {
        return this.collectionForm.subject;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_SUBJECT", value);
      },
    },
    language: {
      get() {
        return this.collectionForm.language;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_LANGUAGE", value);
      },
    },
    relation: {
      get() {
        return this.collectionForm.relation;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_RELATION", value);
      },
    },
    coverage: {
      get() {
        return this.collectionForm.coverage;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_COVERAGE", value);
      },
    },
    spatialCountry: {
      get() {
        return this.collectionForm.spatial.country;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_SPATIALCOUNTRY", value);
      },
    },
    spatialState: {
      get() {
        return this.collectionForm.spatial.state;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_SPATIALSTATE", value);
      },
    },
    spatialLocation: {
      get() {
        return this.collectionForm.spatial.location;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_SPATIALLOCATION", value);
      },
    },
    temporalCentury: {
      get() {
        return this.collectionForm.temporal.century;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_TEMPORALCENTURY", value);
      },
    },
    temporalDecade: {
      get() {
        return this.collectionForm.temporal.decade;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_TEMPORALDECADE", value);
      },
    },
    temporalYear: {
      get() {
        return this.collectionForm.temporal.year;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_TEMPORALYEAR", value);
      },
    },
    source: {
      get() {
        return this.collectionForm.source;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_SOURCE", value);
      },
    },
    extent: {
      get() {
        return this.collectionForm.extent;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_EXTENT", value);
      },
    },
    publisher: {
      get() {
        return this.collectionForm.publisher;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_PUBLISHER", value);
      },
    },
    rights_holder: {
      get() {
        return this.collectionForm.rights_holder;
      },
      set(value) {
        this.$store.commit("UPDATE_COLLECTION_rights_holder", value);
      },
    },
  },
  methods: {
    ...mapActions(["validateCollection", "deleteCollection"]),
    validate() {
      this.validateCollection(this.collectionForm);
      this.$emit("hide");
    },
    reject() {
      this.deleteCollection(this.collectionForm.col_id);
      this.$emit("hide");
    },
  },
  created() {
    this.collectionForm = this.collection;
  },
};
</script>
