<template>
  <v-container>
    <v-row>
      <v-col>
        <h1>Information about the source of the musical piece</h1>
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
              <v-col cols="6">
                <v-text-field
                  v-model="title"
                  label="Title"
                  :rules="rules"
                  hint="Use ' | ', i.e. space colon space, to separate title and subtitle"
                  persistent-hint
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="right"
                  label="Rights"
                  :items="this.getItemsNameByType(1)"
                  :rules="rules"
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-date-picker
                  v-model="this.selectedDate"
                  @update:modelValue="formatDate"
                  :rules="rules"
                ></v-date-picker>
              </v-col>
              <v-col cols="6">
                <h2>Fecha seleccionada: {{ this.date }}</h2>
              </v-col>

              <v-col cols="6  ">
                <h2>Creators</h2>
              </v-col>
              <v-col cols="6">
                <v-btn @click="addFieldsCreators()">Add creator</v-btn>
              </v-col>

              <v-container v-for="(c, index) in creadores" :key="index">
                <v-row>
                  <v-col cols="6">
                    <v-text-field
                      v-model="c.name"
                      @input="updateCreator()"
                      label="Name or URI"
                      :rules="rules"
                      persistent-hint
                    ></v-text-field>
                    <span>
                      <a href="http://www.dib.ie" target="_blank">URI examples</a>
                    </span>
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
                  <v-col cols="1">
                    <v-btn @click="removeFieldCreator(index)">
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>

              <v-col cols="6  ">
                <h2>Contributors</h2>
              </v-col>
              <v-col cols="6">
                <v-btn @click="addFields()">Add contributor</v-btn>
              </v-col>
              <v-container v-for="(c, index) in contribuidores" :key="index">
                <v-row>
                  <v-col cols="6">
                    <v-text-field
                      v-model="c.name"
                      @input="updateContributor()"
                      label="Name or URI"
                      persistent-hint
                    ></v-text-field>
                    <span>
                      <a href="http://www.dib.ie" target="_blank">URI examples</a>
                    </span>
                  </v-col>
                  <v-col cols="5">
                    <v-select
                      v-model="c.role"
                      @input="updateContributor()"
                      label="Role"
                      :items="getItemsNameByType(6)"
                    ></v-select>
                  </v-col>
                  <v-col cols="1">
                    <v-btn @click="removeField(index)">
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
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-text-field v-model="source" label="Source"></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="description"
                  label="Description"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field v-model="format" label="Format"></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field v-model="extent" label="Extent"></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="publisher"
                  label="Publisher"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="subject"
                  label="Subject"
                  hint="Multiple subjects must be separated by '|'"
                  persistent-hint
                ></v-text-field>
                <span>You can check the subject <a href="https://www.vwml.org/song-subject-index" target="_blank">here</a></span>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="language"
                  label="Language code"
                  persistent-hint
                ></v-text-field>
                <span>You can check the code <a href="https://www.loc.gov/standards/iso639-2/php/code_list.php" target="_blank">here</a></span>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="relation"
                  label="Relation"
                  hint=" Multiple subjects must be separated by '|'"
                  persistent-hint=""
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="coverage"
                  label="Coverage"
                ></v-text-field>
              </v-col>

              <v-col cols="12">
                <h2>Spatial</h2>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="spatialCountry"
                  label="Country"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="spatialState"
                  label="State"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="spatialLocation"
                  label="Location"
                ></v-text-field>
              </v-col>

              <v-col cols="12">
                <h2>Temporal</h2>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="temporalCentury"
                  label="Century"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="temporalDecade"
                  label="Decade"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="temporalYear"
                  label="Year"
                ></v-text-field>
              </v-col>

              <v-col cols="12">
                <v-text-field
                  v-model="rights_holder"
                  label="Rights Holder"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="deep-purple lighten-2" text @click="saveCollection()">
              Save collection
            </v-btn>
            <v-btn color="deep-purple lighten-2" text @click="importFile()">
              Import File
            </v-btn>
            <input
              type="file"
              ref="fileInput"
              class="d-none"
              accept=".xlsx, .xls, .mei, .mxml"
              @change="handleFileChange"
            />
          </v-card-actions>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapActions, mapState, mapGetters } from "vuex";
import { VDatePicker } from "vuetify/labs/VDatePicker";

export default {
  components: {
    VDatePicker,
  },
  data() {
    return {
      contribuidores: [],
      creadores: [],
      selectedDate: null,
      rules: [(value) => !!value || "Required."],
    };
  },
  computed: {
    ...mapState(["error", "collectionForm", "defaultSelections"]),
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
      "saveDataCollection",
      "addContributor",
      "addCreator",
      "formatAndSaveDate",
      "removeContributor",
      "removeCreator",
      "resetCollectionForm",
    ]),
    saveCollection() {
      if (
        this.title != "" &&
        this.date &&
        this.right != "" &&
        this.creator.length > 0
      )
        this.saveDataCollection();
      else window.alert("You must fill the required fields");
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
      debugger
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
  },

  created() {
    this.resetCollectionForm();
    this.contribuidores = structuredClone(this.contributor);
    this.creadores = structuredClone(this.creator);
  },
};
</script>
