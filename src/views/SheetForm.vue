<template>
  <v-container>
    <v-row>
      <v-col>
        <h1>Information about the musical piece</h1>
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
              <v-col cols="12">
                <v-select
                  v-model="this.right"
                  label="Rights*"
                  :items="getItemsNameByType(1)"
                  :rules="rules"
                ></v-select>
              </v-col>

              <v-col cols="6  ">
                <h2>Creators*</h2>
              </v-col>
              <v-col cols="6">
                <v-btn @click="addFieldsCreators()">Add creator</v-btn>
              </v-col>

              <v-container v-for="(c, index) in creadores" :key="index">
                <v-row>
                  <v-col cols="4">
                    <v-text-field
                      v-model="c.name"
                      @input="updateCreator()"
                      label="Name or URI"
                      :rules="rules"
                      hint="URI example in http://www.dib.ie"
                      persistent-hint
                    ></v-text-field>
                  </v-col>
                  <v-col cols="4">
                    <v-select
                      v-model="c.role"
                      @update:modelValue="updateCreator()"
                      label="Role"
                      :items="getItemsNameByType(3)"
                      :rules="rules"
                    ></v-select>
                  </v-col>
                  <v-col cols="3">
                    <v-select
                      v-model="c.gender"
                      @update:modelValue="updateCreator()"
                      label="Gender"
                      :items="getItemsNameByType(13)"
                    ></v-select>
                  </v-col>
                  <v-col cols="1">
                    <v-btn @click="removeFieldCreator(index)">
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>

              <v-col cols="6">
                <v-date-picker
                  v-model="this.selectedDate"
                  @update:modelValue="formatDate"
                ></v-date-picker>
              </v-col>
              <v-col cols="6">
                <h2>Selected date*: {{ this.date }}</h2>
              </v-col>

              <v-col cols="4">
                <v-select
                  v-model="key"
                  label="Key"
                  :items="getItemsNameByType(8)"
                  :rules="rules"
                ></v-select>
              </v-col>

              <v-col cols="4">
                <v-select
                  v-model="metre"
                  label="Metre"
                  :items="getItemsNameByType(9)"
                  :rules="rules"
                ></v-select>
              </v-col>

              <v-col cols="4">
                <v-select
                  v-model="tempo"
                  label="Tempo"
                  :items="getItemsNameByType(10)"
                  :rules="rules"
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="instrument"
                  label="Instruments"
                  :items="getItemsNameByType(11)"
                  multiple
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="genre"
                  label="Genre"
                  :items="getItemsNameByType(12)"
                  :rules="rules"
                  multiple
                ></v-select>
              </v-col>
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
                      :rules="rules"
                      hint="URI example in http://www.dib.ie"
                      persistent-hint
                    ></v-text-field>
                  </v-col>
                  <v-col cols="5">
                    <v-select
                      v-model="c.role"
                      @update:modelValue="updateContributor()"
                      label="Role"
                      :items="getItemsNameByType(4)"
                      :rules="rules"
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
                <v-text-field
                  v-model="altTitle"
                  label="Alternative title"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="mode"
                  label="Mode"
                  :items="getItemsNameByType(14)"
                ></v-select>
              </v-col>

              <v-col cols="12">
                <v-text-field
                  v-model="description"
                  label="Description"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="type"
                  label="Type"
                  :items="getItemsNameByType(7)"
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-text-field v-model="format" label="Format"></v-text-field>
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
                >
                </v-text-field>
                <span>You can check the code <a href="https://www.loc.gov/standards/iso639-2/php/code_list.php" target="_blank">here</a></span>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="relation"
                  label="Relation"
                  hint="Multiple relations must be separated by '|'"
                  persistent-hint
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="hasVersion"
                  label="HasVersion"
                  hint="Multiple versions must be separated by '|'"
                  persistent-hint
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="isVersionOf"
                  label="IsVersionOf"
                  hint="Multiple versions must be separated by '|'"
                  persistent-hint
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

              <v-col cols="4">
                <v-file-input
                  accept=".xml"
                  v-model="xml"
                  label="XML File"
                ></v-file-input>
              </v-col>

              <v-col cols="4">
                <v-file-input
                  accept=".mei"
                  v-model="mei"
                  label="MEI File"
                ></v-file-input>
              </v-col>

              <v-col cols="4">
                <v-file-input
                  accept=".mid"
                  v-model="midi"
                  label="MIDI File"
                ></v-file-input>
              </v-col>

              <v-col cols="4">
                <v-text-field v-model="audio" label="Audio URL"></v-text-field>
              </v-col>

              <v-col cols="4">
                <v-text-field v-model="video" label="Video URL"></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-select
                  label="Select collection"
                  :items="this.getNameCollectionsWithId"
                  v-model="this.col_id"
                ></v-select>
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="deep-purple lighten-2" text @click="saveData()">
              Save Data
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
    ...mapState(["error", "pieceForm", "defaultSelections"]),
    ...mapGetters(["getItemsNameByType", "getNameCollections", "getNameCollectionsWithId"]),
    right: {
      get() {
        return this.pieceForm.rightsp;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_RIGHT", value);
      },
    },
    key: {
      get() {
        return this.pieceForm.real_key;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_KEY", value);
      },
    },
    metre: {
      get() {
        return this.pieceForm.meter;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_METRE", value);
      },
    },
    tempo: {
      get() {
        return this.pieceForm.tempo;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_TEMPO", value);
      },
    },
    contributor() {
      return this.pieceForm.contributorp_role;
    },
    creator() {
      return this.pieceForm.creatorp_role;
    },
    date() {
      return this.pieceForm.datep;
    },
    instrument: {
      get() {
        return this.pieceForm.instruments;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_INSTRUMENT", value);
      },
    },
    genre: {
      get() {
        return this.pieceForm.genre;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_GENRE", value);
      },
    },
    altTitle: {
      get() {
        return this.pieceForm.alt_title;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_ALTTITLE", value);
      },
    },
    mode: {
      get() {
        return this.pieceForm.mode;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_MODE", value);
      },
    },
    description: {
      get() {
        return this.pieceForm.descp;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_DESCRIPTION", value);
      },
    },
    type: {
      get() {
        return this.pieceForm.type_piece;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_TYPE", value);
      },
    },
    format: {
      get() {
        return this.pieceForm.formattingp;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_FORMAT", value);
      },
    },
    subject: {
      get() {
        return this.pieceForm.subject;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_SUBJECT", value);
      },
    },
    language: {
      get() {
        return this.pieceForm.language;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_LANGUAGE", value);
      },
    },
    relation: {
      get() {
        return this.pieceForm.relationp;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_RELATION", value);
      },
    },
    hasVersion: {
      get() {
        return this.pieceForm.hasVersion;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_HASVERSION", value);
      },
    },
    isVersionOf: {
      get() {
        return this.pieceForm.isVersionOf;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_ISVERSIONOF", value);
      },
    },
    coverage: {
      get() {
        return this.pieceForm.coverage;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_COVERAGE", value);
      },
    },
    spatialCountry: {
      get() {
        return this.pieceForm.spatial.country;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_SPATIALCOUNTRY", value);
      },
    },
    spatialState: {
      get() {
        return this.pieceForm.spatial.state;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_SPATIALSTATE", value);
      },
    },
    spatialLocation: {
      get() {
        return this.pieceForm.spatial.location;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_SPATIALLOCATION", value);
      },
    },
    temporalCentury: {
      get() {
        return this.pieceForm.temporal.century;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_TEMPORALCENTURY", value);
      },
    },
    temporalDecade: {
      get() {
        return this.pieceForm.temporal.decade;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_TEMPORALDECADE", value);
      },
    },
    temporalYear: {
      get() {
        return this.pieceForm.temporal.year;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_TEMPORALYEAR", value);
      },
    },
    xml: {
      get() {
        return this.pieceForm.xml;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_XML", value);
      },
    },
    mei: {
      get() {
        return this.pieceForm.mei;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_MEI", value);
      },
    },
    midi: {
      get() {
        return this.pieceForm.midi;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_MIDI", value);
      },
    },
    audio: {
      get() {
        return this.pieceForm.audio;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_AUDIO", value);
      },
    },
    video: {
      get() {
        return this.pieceForm.video;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_VIDEO", value);
      },
    },
    col_id: {
      get() {
        return this.pieceForm.col_id;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_COLID", value);
      },
    },
  },
  methods: {
    ...mapActions([
      "saveDataPiece",
      "addContributor",
      "addCreator",
      "removeContributor",
      "removeCreator",
      "formatAndSaveDate",
      "resetPieceForm",
      "importDataFromExcel",
      "importDataFromMEI",
    ]),
    saveData() {
      if (this.right !== "" && this.creator.length > 0 && this.date !== "" &&
        this.pieceForm.title !== "" && this.pieceForm.rights !== "" && this.pieceForm.creator !== "" && this.pieceForm.date !== "") {
        this.saveDataPiece();
      } else {
        alert("You must fill the required fields");
      }
    },
    importFile() {
      this.$refs.fileInput.click();
    },
    handleFileChange(event) {
      const file = event.target.files[0];
      if (file && file.name.endsWith(".xlsx")) {
        const reader = new FileReader();
        reader.onload = async (e) => {
          if(window.confirm("Do you want to upload the corresponding XML File for this piece?"))
            var xml = await this.readFileContents()
          if(window.confirm("Do you want to upload the corresponding MEI File for this piece?"))
            var mei = await this.readFileContents()
          this.importDataFromExcel({ file: e.target.result, xml: xml ? xml : '', mei: mei ? mei : '' });
        };
        reader.readAsText(file);
      } else if (file && file.name.endsWith(".mei")) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.importDataFromMEI({ file: e.target.result });
        };
        reader.readAsText(file);
      }
      console.log("Archivo seleccionado:", file);
    },
    async readFileContents() {
      console.log("")
      try {
        console.log("Reading file...")
        const fileHandle = await window.showOpenFilePicker();
        const file = await fileHandle[0].getFile();
        const contents = await file.text();
        return contents;
      } catch (error) {
        console.error("Error al leer el archivo:", error);
        return '';
      }
    },
    addFields() {
      this.addContributor("Sheet");
      this.contribuidores.push({ name: "", role: "" });
    },
    addFieldsCreators() {
      this.addCreator("Sheet");
      this.creadores.push({ name: "", role: "", gender: "" });
    },
    removeField(index) {
      this.removeContributor({ index: index, form: "Sheet" });
      this.contribuidores.splice(index, 1);
    },
    removeFieldCreator(index) {
      this.removeCreator({ index: index, form: "Sheet" });
      this.creadores.splice(index, 1);
    },
    updateContributor() {
      this.$store.commit("UPDATE_SHEET_CONTRIBUTOR", this.contribuidores);
    },
    updateCreator() {
      this.$store.commit("UPDATE_SHEET_CREATOR", this.creadores);
    },
    formatDate() {
      if (this.selectedDate.length > 0) {
        this.formatAndSaveDate({ date: this.selectedDate, form: "Sheet" });
      } else {
        alert("You must select a date");
      }
    },
  },

  created() {
    this.contribuidores = structuredClone(this.contributor);
    this.creadores = structuredClone(this.creator);
  },
};
</script>
