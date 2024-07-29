<template>
  <v-container>
    <v-row>
      <v-col>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <SearchBar
                :objects="this.getNamePieces"
                :getInfo="this.loadPieceInfo"
              ></SearchBar>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-card-title class="text-h5" v-if="this.content">{{
                this.pieceForm.title
              }}</v-card-title>
              <v-card-text v-else
                >This piece doesn't contain any MEI file. You can edit the piece
                and upload it.</v-card-text
              >
              <VerovioCanvas
                v-if="this.content"
                :toolkit="toolkit"
                :data="this.content"
                view-mode="vertical"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <v-card-text v-if="!this.midiFilePath"
                >This piece doesn't contain any MIDI file. You can edit the piece and upload it.</v-card-text
              >
              <v-btn v-else @click="this.playMidi = !this.playMidi">
                {{ this.playMidi ? "Stop" : "Play" }}
              </v-btn>
              <MidiAudioPlayer
                :midi="this.midiFilePath"
                :playMidi="this.playMidi"
                @finishedPlaying="this.playMidi = false"
              />
            </v-col>
          </v-row>
        </v-card-text>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
const toolkit = ref(null);
createVerovioModule().then((VerovioModule) => {
  toolkit.value = createAsyncVerovioToolkit(new VerovioToolkit(VerovioModule));
});
</script>

<script>
import { mapActions, mapGetters, mapState } from "vuex";
import "vue-verovio-canvas/style.css";
import { VerovioCanvas, createAsyncVerovioToolkit } from "vue-verovio-canvas";
import { VerovioToolkit } from "verovio/esm";
import createVerovioModule from "verovio/wasm-hum";
import { ref } from "vue";
import MidiAudioPlayer from "@/components/MidiAudioPlayer.vue";
import SearchBar from "@/components/SearchBar.vue";

export default {
  components: {
    VerovioCanvas,
    MidiAudioPlayer,
    SearchBar,
  },
  data() {
    return {
      content: null,
      midiFilePath: null,
      playMidi: false,
    };
  },
  computed: {
    ...mapGetters(["getMei", "getMidi", "getNamePieces"]),
    ...mapState(["pieceForm"]),
  },
  methods: {
    ...mapActions(["getPieceInfo"]),
    handleFileChange2(event) {
      const file = event.target.files[0];
      const reader = new FileReader();
      reader.onload = () => {
        this.midiFilePath = reader.result;
      };
      reader.readAsBinaryString(file);
    },
    async loadMedia() {
      this.content = await this.getMei;
      this.midiFilePath = await this.getMidi;
    },
    async loadPieceInfo(selectedPiece) {
      await this.getPieceInfo({ piece: selectedPiece });
      this.loadMedia();
    },
  },
};
</script>
