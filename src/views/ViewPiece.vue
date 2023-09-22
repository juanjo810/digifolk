<template>
  <v-container>
    <!-- Information about the MusicXML file -->
    <v-row>
      <v-col>
        <v-row>
          <v-col cols="4">
            <h1>View piece</h1>
          </v-col>
          <v-col cols="8">
            <SearchBar
              :objects="this.getNamePieces"
              :getInfo="this.loadPieceInfo"
              typeObject="pieces"
            ></SearchBar>
          </v-col>
        </v-row>
        <h1>Information about the MusicXML file</h1>
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
                  v-model="id"
                  label="Identifier"
                  readonly
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="title"
                  label="Title"
                  :rules="rules"
                  hint="Use ' | ', i.e. space colon space, to separate title and subtitle"
                  persistent-hint
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="right"
                  label="Rights"
                  :items="getItemsNameByType(1)"
                  :disabled="!editing"
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="creator"
                  label="Creator"
                  :rules="rules"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-date-picker
                  v-model="selectedDate"
                  @update:modelValue="formatDate"
                  :disabled="!editing"
                ></v-date-picker>
              </v-col>
              <v-col cols="6">
                <h2>Selected date: {{ date }}</h2>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="type"
                  label="Type"
                  :items="getItemsNameByType(7)"
                  :rules="rules"
                  :disabled="!editing"
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="publisher"
                  label="Publisher"
                  :rules="rules"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="6  ">
                <h2>Contributors</h2>
              </v-col>
              <v-col cols="6">
                <v-btn @click="addFields()" :disabled="!editing"
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
                      :rules="rules"
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
                      :items="getItemsNameByType(2)"
                      :rules="rules"
                      :disabled="!editing"
                    ></v-select>
                  </v-col>
                  <v-col cols="1">
                    <v-btn @click="removeField(index)" :disabled="!editing">
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>

              <v-col cols="12">
                <v-text-field
                  v-model="description"
                  label="Description"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-card-text>
        </div>
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
                  v-model="rightsp"
                  label="Rights"
                  :items="getItemsNameByType(1)"
                  :rules="rules"
                  :disabled="!editing"
                ></v-select>
              </v-col>

              <v-col cols="6  ">
                <h2>Creators</h2>
              </v-col>
              <v-col cols="6">
                <v-btn @click="addFieldsCreators()" :disabled="!editing"
                  >Add creator</v-btn
                >
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
                      :disabled="!editing"
                    ></v-text-field>
                  </v-col>
                  <v-col cols="4">
                    <v-select
                      v-model="c.role"
                      @update:modelValue="updateCreator()"
                      label="Role"
                      :items="getItemsNameByType(3)"
                      :rules="rules"
                      :disabled="!editing"
                    ></v-select>
                  </v-col>
                  <v-col cols="3">
                    <v-select
                      v-model="c.gender"
                      @update:modelValue="updateCreator()"
                      label="Gender"
                      :items="getItemsNameByType(13)"
                      :disabled="!editing"
                    ></v-select>
                  </v-col>
                  <v-col cols="1">
                    <v-btn
                      @click="removeFieldCreator(index)"
                      :disabled="!editing"
                    >
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>

              <v-col cols="6">
                <v-date-picker
                  v-model="selectedDatep"
                  @update:modelValue="formatDate"
                  :disabled="!editing"
                ></v-date-picker>
              </v-col>
              <v-col cols="6">
                <h2>Selected date: {{ date }}</h2>
              </v-col>

              <v-col>
                <v-select
                  v-model="key"
                  label="Key"
                  :items="getItemsNameByType(8)"
                  :rules="rules"
                  :disabled="!editing"
                ></v-select>
              </v-col>

              <v-col cols="4">
                <v-select
                  v-model="metre"
                  label="Metre"
                  :items="getItemsNameByType(9)"
                  :rules="rules"
                  :disabled="!editing"
                ></v-select>
              </v-col>

              <v-col cols="4">
                <v-select
                  v-model="tempo"
                  label="Tempo"
                  :items="getItemsNameByType(10)"
                  :rules="rules"
                  :disabled="!editing"
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="instrument"
                  label="Instruments"
                  :items="getItemsNameByType(11)"
                  multiple
                  :disabled="!editing"
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="genre"
                  label="Genre"
                  :items="getItemsNameByType(12)"
                  :rules="rules"
                  multiple
                  :disabled="!editing"
                ></v-select>
              </v-col>

              <v-col cols="6">
                <h2>Contributors</h2>
              </v-col>
              <v-col cols="6">
                <v-btn @click="addFieldsp()" :disabled="!editing">
                  Add contributor
                </v-btn>
              </v-col>
              <v-container v-for="(c, index) in contribuidoresp" :key="index">
                <v-row>
                  <v-col cols="6">
                    <v-text-field
                      v-model="c.name"
                      @input="updateContributor()"
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
                      @update:modelValue="updateContributor()"
                      label="Role"
                      :items="getItemsNameByType(4)"
                      :rules="rules"
                      :disabled="!editing"
                    ></v-select>
                  </v-col>
                  <v-col cols="1">
                    <v-btn @click="removeFieldp(index)" :disabled="!editing">
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>

              <v-col cols="12">
                <v-text-field
                  v-model="altTitle"
                  label="Alternative title"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="12">
                <v-text-field
                  v-model="description"
                  label="Description"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="type"
                  label="Type"
                  :items="defaultSelections.types"
                  :disabled="!editing"
                ></v-select>
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
                  hint="Multiple relations must be separated by ':'"
                  persistent-hint
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="hasVersion"
                  label="HasVersion"
                  hint="Multiple versions must be separated by ''"
                  persistent-hint
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="isVersionOf"
                  label="IsVersionOf"
                  hint="Multiple versions must be separated by ':'"
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
                <h2>Spatial</h2>
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
                <h2>Temporal</h2>
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

              <v-col cols="4">
                <v-file-input
                  accept=".xml"
                  v-model="xml"
                  label="XML File"
                  :disabled="!editing"
                ></v-file-input>
              </v-col>

              <v-col cols="4">
                <v-file-input
                  accept=".mei"
                  v-model="mei"
                  label="MEI File"
                  :disabled="!editing"
                ></v-file-input>
              </v-col>

              <v-col cols="4">
                <v-file-input
                  accept=".mid"
                  v-model="midi"
                  label="MIDI File"
                  :disabled="!editing"
                ></v-file-input>
              </v-col>

              <v-col cols="4">
                <v-text-field
                  v-model="audio"
                  label="Audio URL"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="4">
                <v-text-field
                  v-model="video"
                  label="Video URL"
                  :disabled="!editing"
                ></v-text-field>
              </v-col>

              <v-col cols="4">
                <v-select
                  label="Select collection"
                  :items="this.getNameCollections"
                  v-model="this.col_id"
                  :disabled="!editing"
                ></v-select>
              </v-col>
            </v-row>
          </v-card-text>
          <v-card-actions>

            <v-spacer></v-spacer>
            <div
              v-if="
                pieceSelected &&
                this.pieceForm.user_id === this.user.userInfo.user_id
              "
            >
              <v-btn
                color="deep-purple lighten-2"
                text
                @click="saveFields"
                v-if="editing"
              >
                Save piece
              </v-btn>
              <v-btn
                color="deep-purple lighten-2"
                text
                @click="editFields"
                v-else
              >
                Edit fields
              </v-btn>
              <v-btn
                color="deep-purple lighten-2"
                text
                @click="this.delete"
                v-if="!editing"
              >
                Delete piece
              </v-btn>
            </div>
            <v-btn
              color="deep-purple lighten-2"
              text
              @click="this.exportExcel"
            >
              Export Excel
            </v-btn>
          </v-card-actions>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapActions, mapGetters, mapState } from "vuex";
import { VDatePicker } from "vuetify/labs/VDatePicker";
import SearchBar from "../components/SearchBar.vue";

export default {
  components: {
    VDatePicker,
    SearchBar,
  },
  data() {
    return {
      items: ["Piece1", "Piece2"],
      contribuidores: [],
      contribuidoresp: [],
      creadores: [],
      selectedDate: null,
      selectedDatep: null,
      rules: [(value) => !!value || "Required."],
      editing: false,
      pieceSelected: false,
    };
  },
  computed: {
    ...mapState([
      "error",
      "defaultSelections",
      "pieces",
      "pieceSelected",
      "pieceForm",
      "user",
    ]),
    ...mapGetters([
      "getItemsNameByType",
      "getNamePieces",
      "getNameCollections",
    ]),
    id: {
      get() {
        return this.pieceForm.identifier;
      },
      set(value) {
        this.$store.commit("UPDATE_USER_ID", value);
      },
    },
    title: {
      get() {
        return this.pieceForm.title;
      },
      set(value) {
        this.$store.commit("UPDATE_USER_TITLE", value);
      },
    },
    right: {
      get() {
        return this.pieceForm.rights;
      },
      set(value) {
        this.$store.commit("UPDATE_USER_RIGHT", value);
      },
    },
    rightsp: {
      get() {
        return this.pieceForm.rightsp;
      },
      set(value) {
        this.$store.commit("UPDATE_USER_RIGHT", value);
      },
    },
    creator: {
      get() {
        return this.pieceForm.creator;
      },
      set(value) {
        this.$store.commit("UPDATE_USER_CREATOR", value);
      },
    },
    date() {
      return this.pieceForm.date;
    },
    type: {
      get() {
        return this.pieceForm.type_file;
      },
      set(value) {
        this.$store.commit("UPDATE_USER_TYPE", value);
      },
    },
    publisher: {
      get() {
        return this.pieceForm.publisher;
      },
      set(value) {
        this.$store.commit("UPDATE_USER_PUBLISHER", value);
      },
    },
    contributor() {
      return this.pieceForm.contributor_role;
    },
    contributorp() {
      return this.pieceForm.contributorp_role;
    },
    description: {
      get() {
        return this.pieceForm.desc;
      },
      set(value) {
        this.$store.commit("UPDATE_USER_DESCRIPTION", value);
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
    creatorSheet() {
      return this.pieceForm.creatorp_role;
    },
    dateSheet() {
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
    descriptionSheet: {
      get() {
        return this.pieceForm.descp;
      },
      set(value) {
        this.$store.commit("UPDATE_SHEET_DESCRIPTION", value);
      },
    },
    typeSheet: {
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
        debugger;
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
      "fetchPieces",
      "getPieceInfo",
      "editPiece",
      "resetPieceForm",
      "deletePiece",
      "exportPieceToExcel",
    ]),
    importFile() {
      this.$refs.fileInput.click();
    },
    handleFileChange(event) {
      const file = event.target.files[0];
      console.log("Archivo seleccionado:", file);
    },
    addFields() {
      this.addContributor("User");
      this.contribuidores.push({ name: "", role: "" });
    },
    addFieldsp() {
      this.addContributor("Sheet");
      this.contribuidoresp.push({ name: "", role: "" });
    },
    addFieldsCreators() {
      this.addCreator("Sheet");
      this.creadores.push({ name: "", role: "", gender: "" });
    },
    removeField(index) {
      this.removeContributor({ index: index, form: "User" });
      this.contribuidores.splice(index, 1);
    },
    removeFieldp(index) {
      this.removeContributor({ index: index, form: "Sheet" });
      this.contribuidoresp.splice(index, 1);
    },
    removeFieldCreator(index) {
      this.removeCreator({ index: index, form: "Sheet" });
      this.creadores.splice(index, 1);
    },
    updateContributor() {
      this.$store.commit("UPDATE_USER_CONTRIBUTOR", this.contribuidores);
    },
    updateContributorp() {
      this.$store.commit("UPDATE_SHEET_CONTRIBUTOR", this.contribuidoresp);
    },
    updateCreator() {
      this.$store.commit("UPDATE_SHEET_CREATOR", this.creadores);
    },
    formatDate() {
      if (this.selectedDate) {
        this.formatAndSaveDate({ date: this.selectedDate, form: "Sheet" });
      }
    },
    formatDatep() {
      if (this.selectedDatep) {
        this.formatAndSaveDate({ date: this.selectedDatep, form: "Sheet" });
      }
    },
    editFields() {
      this.editing = true;
    },
    saveFields() {
      this.editPiece();
      this.editing = false;
    },
    async loadPieceInfo(selectedPiece) {
      await this.getPieceInfo({
        piece: selectedPiece,
        creadores: this.creadores,
        contribuidores: this.contribuidores,
        contribuidoresp: this.contribuidoresp,
      });
      this.pieceSelected = true;
    },
    delete() {
      this.deletePiece(this.pieceForm.music_id);
      this.resetPieceForm();
    },
    exportExcel() {
      this.exportPieceToExcel(this.pieceForm.music_id);
    }
  },
  created() {
    this.resetPieceForm();
    this.contribuidores = structuredClone(this.contributor);
    this.contribuidoresp = structuredClone(this.contributorp);
    this.creadores = structuredClone(this.creatorSheet);
    this.fetchPieces();
  },
};
</script>
