<template>
  <v-container>
    <v-row>
      <v-col>
        <v-row>
          <v-col class="d-flex justify-center">
            <h1 class="text-h3">View collection</h1>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <SearchBar
              :objects="this.getNameCollections"
              :getInfo="loadCollectionInfo"
              typeObject="collections"
            ></SearchBar>
          </v-col>
        </v-row><br>
        <div>
          <template>
            <v-progress-linear
              color="deep-purple"
              height="10"
              indeterminate
            ></v-progress-linear>
          </template>
          <v-card-text>
            <v-row>
              <v-col cols="1">
                <v-text-field 
                  readonly
                  v-model="collectionForm.col_id"
                  label="ID"
                  :disabled="!editing || editing"
                ></v-text-field>
              </v-col>
              <v-col cols="2">
                <v-text-field 
                  readonly
                  v-model="collectionForm.code"
                  label="Code"
                  :disabled="!editing || editing"
                ></v-text-field>
              </v-col>
              <v-col cols="5">
                <v-text-field
                  v-model="title"
                  label="Title"
                  :rules="rules"
                  hint="Use ' | ', i.e. space colon space, to separate title and subtitle"
                  persistent-hint
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="4">
                <v-select
                  v-model="right"
                  label="Rights"
                  :items="this.getItemsNameByType(1)"
                  :rules="rules"
                  :disabled="!editing"
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-date-picker
                  v-model="selectedDate"
                  @update:modelValue="formatDate"
                  :rules="rules"
                  :disabled="!editing"
                ></v-date-picker>
              </v-col>
              <v-col cols="6">
                <h2 class="text-h5 text-center">Selected date: {{ date }}</h2>
              </v-col>

              <v-col cols="6">
                <h2 class="text-h5">Creators</h2>
              </v-col>
              <v-col cols="6">
                <v-btn @click="addFieldsCreators()" v-if="editing"
                  >Add creator</v-btn
                >
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
                      :disabled="!editing"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="5">
                    <v-select
                      v-model="c.role"
                      @update:modelValue="updateCreator()"
                      label="Role"
                      :items="getItemsNameByType(5)"
                      :rules="rules"
                      :disabled="!editing"
                    ></v-select>
                  </v-col>
                  <v-col cols="1">
                    <v-btn @click="removeFieldCreator(index)" v-if="editing">
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>

              <v-col cols="6">
                <h2 class="text-h5">Contributors</h2>
              </v-col>
              <v-col cols="6">
                <v-btn @click="addFields()" v-if="editing"
                  >Add contributor</v-btn
                >
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
                      :disabled="!editing"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="5">
                    <v-select
                      v-model="c.role"
                      @update:modelValue="updateContributor()"
                      label="Role"
                      :items="getItemsNameByType(6)"
                      :disabled="!editing"
                    ></v-select>
                  </v-col>
                  <v-col cols="1">
                    <v-btn @click="removeField(index)" v-if="editing">
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>

              <v-col cols="6">
                <v-select
                  v-model="type"
                  label="Type"
                  :items="getItemsNameByType(7)"
                  :disabled="!editing"
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="source"
                  label="Source"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="description"
                  label="Description"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="format"
                  label="Format"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="extent"
                  label="Extent"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="publisher"
                  label="Publisher"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="subject"
                  label="Subject"
                  hint="You can check the subject in https://www.vwml.org/song-subject-index. Multiple subjects must be separated by '|'"
                  persistent-hint
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="language"
                  label="Language code"
                  hint="You can check the code in https://www.loc.gov/standards/iso639-2/php/code_list.php"
                  persistent-hint
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="relation"
                  label="Relation"
                  hint="Multiple subjects must be separated by '|'"
                  persistent-hint
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="coverage"
                  label="Coverage"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="12">
                <h2 class="text-h5 text-center">Spatial</h2>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="spatialCountry"
                  label="Country"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="spatialState"
                  label="State"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="spatialLocation"
                  label="Location"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="12">
                <h2 class="text-h5 text-center">Temporal</h2>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="temporalCentury"
                  label="Century"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="temporalDecade"
                  label="Decade"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="temporalYear"
                  label="Year"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="12">
                <v-text-field
                  v-model="rights_holder"
                  label="rights_holder"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="12">
                <list-objects :list="this.collectionForm.pieces" redirect="viewPiece" title="List of pieces"/>
              </v-col>
            </v-row>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn
              color="blue"
              text
              @click="saveCollection"
              v-if="editing"
            >
              Save collection
            </v-btn>
            <v-btn
              color="blue"
              text
              @click="editFields"
              v-else
            >
              Edit fields
            </v-btn>
          </v-card-actions>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapActions, mapState, mapGetters } from "vuex";
import { VDatePicker } from "vuetify/labs/VDatePicker";
import SearchBar from "@/components/SearchBar.vue";
import ListObjects from "@/components/ListObjects.vue";

export default {
  components: {
    VDatePicker,
    SearchBar,
    ListObjects,
  },
  data() {
    return {
      contribuidores: [],
      creadores: [],
      selectedDate: null,
      rules: [(value) => !!value || "Required."],
      editing: false,
    };
  },
  computed: {
    ...mapState(["error", "collectionForm", "defaultSelections", "objectFromList"]),
    ...mapGetters(["getItemsNameByType", "getNameCollections"]),
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
      return this.collectionForm.creator_role;
    },
    contributor() {
      return this.collectionForm.contributor_role;
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
    ...mapActions([
      "editCollection",
      "addContributor",
      "addCreator",
      "formatAndSaveDate",
      "removeContributor",
      "removeCreator",
      "fetchCollections",
      "getCollectionInfo",
      "resetCollectionForm",
    ]),
    saveCollection() {
      if (
        this.title != "" &&
        this.date &&
        this.right != "" &&
        this.creator.length > 0
      )
        this.editCollection();
      else window.alert("You must fill the required fields");
      this.editing = false;
    },
    importFile() {
      this.$refs.fileInput.click();
    },
    handleFileChange(event) {
      const file = event.target.files[0];
      console.log("Archivo seleccionado:", file);
    },
    addFields() {
      this.addContributor("Collection");
      this.contribuidores.push({ name: "", role: "" });
    },
    addFieldsCreators() {
      this.addCreator("Collection");
      this.creadores.push({ name: "", role: "" });
    },
    removeField(index) {
      this.removeContributor({ index: index, form: "Collection" });
      this.contribuidores.splice(index, 1);
    },
    removeFieldCreator(index) {
      this.removeCreator({ index: index, form: "Collection" });
      this.creadores.splice(index, 1);
    },
    updateContributor() {
      this.$store.commit("UPDATE_COLLECTION_CONTRIBUTOR", this.contribuidores);
    },
    updateCreator() {
      this.$store.commit("UPDATE_COLLECTION_CREATOR", this.creadores);
    },
    formatDate() {
      if (this.selectedDate) {
        this.formatAndSaveDate({ date: this.selectedDate, form: "Collection" });
      }
    },
    editFields() {
      this.editing = true;
    },
    loadCollectionInfo(selectedCollection) {
      this.getCollectionInfo({
        collection: selectedCollection,
        creadores: this.creadores,
        contribuidores: this.contribuidores,
      });
    },
  },

  created() {
    this.resetCollectionForm();
    this.fetchCollections();
  },
  mounted() {
    if (this.objectFromList) {
      this.loadCollectionInfo(this.objectFromList);
      this.$store.commit('SET_OBJECTFROMLIST', null);
    }
  }
};
</script>
