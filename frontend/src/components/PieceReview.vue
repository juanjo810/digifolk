<template>
  <v-card>
    <v-container>
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
                v-model="this.pieceForm.title_xml"
                label="Identifier"
              ></v-text-field>
            </v-col>

            <v-col cols="6">
              <v-text-field
                v-model="this.pieceForm.title"
                label="Title"
              ></v-text-field>
            </v-col>

            <v-col cols="6">
              <v-select
                v-model="this.pieceForm.rights"
                label="Rights"
                :items="getItemsNameByType(1)"
              ></v-select>
            </v-col>

            <v-col cols="6">
              <v-text-field
                v-model="this.pieceForm.creator"
                label="Creator"
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <h2>Selected date: {{ this.pieceForm.date }}</h2>
            </v-col>

            <v-col cols="6">
              <v-select
                v-model="this.pieceForm.type_file"
                label="Type"
                :items="getItemsNameByType(7)"
              ></v-select>
            </v-col>

            <v-col cols="6">
              <v-text-field
                v-model="this.pieceForm.publisher"
                label="Publisher"
              ></v-text-field>
            </v-col>

            <v-col cols="6  ">
              <h2>Contributors</h2>
            </v-col>
            <v-container v-for="(c, index) in contribuidores" :key="index">
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    v-model="c.name"
                    label="Name or URI"
                  ></v-text-field>
                </v-col>
                <v-col cols="5">
                  <v-select
                    v-model="c.role"
                    label="Role"
                    :items="getItemsNameByType(2)"
                  ></v-select>
                </v-col>
              </v-row>
            </v-container>

            <v-col cols="12">
              <v-text-field
                v-model="this.pieceForm.desc"
                label="Description"
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
                v-model="this.pieceForm.rightsp"
                label="Rights"
                :items="getItemsNameByType(1)"
              ></v-select>
            </v-col>

            <v-col cols="6  ">
              <h2>Creators</h2>
            </v-col>

            <v-container v-for="(c, index) in creadores" :key="index">
              <v-row>
                <v-col cols="4">
                  <v-text-field
                    v-model="c.name"
                    label="Name or URI"
                  ></v-text-field>
                </v-col>
                <v-col cols="4">
                  <v-select
                    v-model="c.role"
                    label="Role"
                    :items="getItemsNameByType(3)"
                  ></v-select>
                </v-col>
                <v-col cols="3">
                  <v-select
                    v-model="c.gender"
                    label="Gender"
                    :items="getItemsNameByType(13)"
                  ></v-select>
                </v-col>
              </v-row>
            </v-container>
            <v-col cols="12">
              <h2>Selected date: {{ this.pieceForm.datep }}</h2>
            </v-col>

            <v-col>
              <v-select
                v-model="this.pieceForm.real_key"
                label="Key"
                :items="getItemsNameByType(8)"
              ></v-select>
            </v-col>

            <v-col cols="4">
              <v-select
                v-model="this.pieceForm.meter"
                label="Meter"
                :items="getItemsNameByType(9)"
              ></v-select>
            </v-col>

            <v-col cols="4">
              <v-select
                v-model="this.pieceForm.tempo"
                label="Tempo"
                :items="getItemsNameByType(10)"
              ></v-select>
            </v-col>

            <v-col cols="6">
              <v-select
                v-model="this.pieceForm.instruments"
                label="Instruments"
                :items="getItemsNameByType(11)"
                multiple
              ></v-select>
            </v-col>

            <v-col cols="6">
              <v-select
                v-model="this.pieceForm.genre"
                label="Genre"
                :items="getItemsNameByType(12)"
                multiple
              ></v-select>
            </v-col>

            <v-col cols="6">
              <h2>Contributors</h2>
            </v-col>
            <v-col cols="6"> </v-col>
            <v-container v-for="(c, index) in contribuidoresp" :key="index">
              <v-row>
                <v-col cols="6">
                  <v-text-field
                    v-model="c.name"
                    label="Name or URI"
                    persistent-hint
                  ></v-text-field>
                </v-col>
                <v-col cols="5">
                  <v-select
                    v-model="c.role"
                    label="Role"
                    :items="getItemsNameByType(4)"
                  ></v-select>
                </v-col>
              </v-row>
            </v-container>

            <v-col cols="6">
              <v-text-field
                v-model="this.pieceForm.alt_title"
                label="Alternative title"
              ></v-text-field>
            </v-col>

            <v-col cols="6">
              <v-text-field
                v-model="this.pieceForm.mode"
                label="Mode"
              ></v-text-field>
            </v-col>

            <v-col cols="12">
              <v-text-field
                v-model="this.pieceForm.descp"
                label="Description"
              ></v-text-field>
            </v-col>

            <v-col cols="6">
              <v-select
                v-model="this.pieceForm.type_piece"
                label="Type"
                :items="getItemsNameByType(7)"
              ></v-select>
            </v-col>

            <v-col cols="6">
              <v-text-field
                v-model="this.pieceForm.formattingp"
                label="Format"
              ></v-text-field>
            </v-col>

            <v-col cols="6">
              <v-text-field
                v-model="this.pieceForm.subject"
                label="Subject"
                hint="You can check the subject in https://www.vwml.org/song-subject-index. Multiple subjects must be separated by '|'"
                persistent-hint
              ></v-text-field>
            </v-col>

            <v-col cols="6">
              <v-text-field
                v-model="this.pieceForm.language"
                label="Language code"
                hint="You can check the code in https://www.loc.gov/standards/iso639-2/php/code_list.php"
                persistent-hint
              ></v-text-field>
            </v-col>

            <v-col cols="6">
              <v-text-field
                v-model="relation"
                label="Relation"
                hint="Multiple relations must be separated by ':'"
                persistent-hint
              ></v-text-field>
            </v-col>

            <v-col cols="6">
              <v-text-field
                v-model="this.pieceForm.hasVersion"
                label="HasVersion"
                hint="Multiple versions must be separated by ':'"
                persistent-hint
              ></v-text-field>
            </v-col>

            <v-col cols="6">
              <v-text-field
                v-model="this.pieceForm.isVersionOf"
                label="IsVersionOf"
                hint="Multiple versions must be separated by ':'"
                persistent-hint
              ></v-text-field>
            </v-col>

            <v-col cols="6">
              <v-text-field
                v-model="this.pieceForm.coverage"
                label="Coverage"
              ></v-text-field>
            </v-col>

            <v-col cols="12">
              <h2>Spatial</h2>
            </v-col>
            <v-col cols="4">
              <v-text-field
                v-model="this.pieceForm.spatial.country"
                label="Country"
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <v-text-field
                v-model="this.pieceForm.spatial.state"
                label="State"
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <v-text-field
                v-model="this.pieceForm.spatial.location"
                label="Location"
              ></v-text-field>
            </v-col>

            <v-col cols="12">
              <h2>Temporal</h2>
            </v-col>
            <v-col cols="4">
              <v-text-field
                v-model="this.pieceForm.temporal.century"
                label="Century"
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <v-text-field
                v-model="this.pieceForm.temporal.decade"
                label="Decade"
              ></v-text-field>
            </v-col>
            <v-col cols="4">
              <v-text-field
                v-model="this.pieceForm.temporal.year"
                label="Year"
              ></v-text-field>
            </v-col>

            <v-col cols="4">
              <v-file-input
                accept=".xml"
                v-model="this.pieceForm.xml"
                label="XML File"
              ></v-file-input>
              <v-btn @click="saveXMLFile" :disabled="this.xml == ''">Download</v-btn>
            </v-col>

            <v-col cols="4">
              <v-file-input
                accept=".mei"
                v-model="this.pieceForm.mei"
                label="MEI File"
              ></v-file-input>
              <v-btn @click="saveMEIFile" :disabled="this.mei == ''">Download</v-btn>
            </v-col>

            <v-col cols="4">
              <v-file-input
                accept=".midi"
                v-model="this.pieceForm.midi"
                label="MIDI File"
              ></v-file-input>
              <v-btn @click="saveMIDIFile" :disabled="this.midi == ''">Download</v-btn>
            </v-col>

            <v-col cols="4">
              <v-text-field v-model="this.pieceForm.audio"></v-text-field>
            </v-col>

            <v-col cols="4">
              <v-text-field
                v-model="this.pieceForm.video"
                label="Video URL"
              ></v-text-field>
            </v-col>

            <v-col cols="4">
              <v-select
                label="Select collection"
                :items="this.getNameCollections"
                v-model="this.pieceForm.col_id"
                :disabled="!editing"
              ></v-select>
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
      </div>
    </v-container>
  </v-card>
</template>

<script>
import { mapActions, mapGetters } from "vuex";

export default {
  data() {
    return {
      pieceForm: null,
    };
  },
  props: {
    piece: {
      type: Object,
      required: true,
    },
  },
  computed: {
    ...mapGetters(["getItemsNameByType"]),
    title_xml: {
      get() {
        return this.pieceForm.title_xml;
      }
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
    contribuidores() {
      return this.piece.contributor_role;
    },
    contribuidoresp() {
      return this.piece.contributorp_role;
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
    creadores() {
      return this.piece.creatorp_role;
    },
    datep() {
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
    ...mapActions(["validatePiece",
                   "deletePiece",
                   "saveFile"]),
    validate() {
      this.validatePiece(this.pieceForm);
      this.$emit("hide");
    },
    reject() {
      this.deletePiece(this.pieceForm.music_id);
      this.$emit("hide");
    },
    saveXMLFile() {
      this.saveFile( {content: this.xml[0], extension: ".xml"} )
    },
    saveMEIFile() {
      this.saveFile( {content: this.mei[0], extension: ".mei"} )
    },
    saveMIDIFile() {
      this.saveFile( {content: this.midi[0], extension: ".mid"} )
    },
  },
  created() {
    this.pieceForm = structuredClone(this.piece);
  },
};
</script>
