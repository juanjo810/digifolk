<template>
  <v-container>
    <v-row>
      <v-col>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <input type="file" accept=".mei" @change="handleFileChange" />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <SearchBar :objects="this.getNamePieces" :getInfo="this.loadPieceInfo"></SearchBar>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <VerovioCanvas
                v-if="this.content"
                :toolkit="toolkit"
                :data="this.content"
                view-mode="vertical"
                @change="this.handleFileChanged()"
              />
            </v-col>
          </v-row>
          <v-row>
          <v-row>
            <v-col cols="12">
              <input type="file" accept=".mid" @change="handleFileChange2" />
            </v-col>
          </v-row>
            <v-col cols="12">
              <v-btn @click="this.playMidi = !this.playMidi">
                {{ this.playMidi ? "Stop" : "Play" }}
              </v-btn>
              <MidiAudioPlayer :midi="this.midiFilePath" :playMidi="this.playMidi" />
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
import { mapGetters } from "vuex";
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
    SearchBar
  },
  data() {
    return {
      content: null,
      midiFilePath: '@/assets/ejemplo.mid',
      playMidi: false,
    };
  },
  computed: {
    ...mapGetters([
      "getNamePiecesWithMei",
      "getMei",
      "getNamePieces",
      "getPieceInfo"]),
  },
  methods: {
    handleFileChange(event) {
      const file = event.target.files[0];
      const reader = new FileReader();
      reader.onload = (e) => {
        this.content = e.target.result;
      };
      reader.readAsText(file);
    },
    handleFileChange2(event) {
      const file = event.target.files[0];
      const reader = new FileReader();
      reader.onload = () => {
        this.midiFilePath = reader.result;
      };
      reader.readAsBinaryString(file);
    },
    loadMei() {
      const file = this.getMei(this.selectedPiece); 
      const reader = new FileReader();
      reader.onload = (e) => {
        this.content = e.target.result;
        console.log(this.content);
      };
      debugger;
      reader.readAsText(file);
    },
    loadPieceInfo(selectedPiece) {
      const parts = selectedPiece.split("-")
      this.getPieceInfo({piece: parts, creadores: this.creadores, contribuidores: this.contribuidores, contribuidoresp: this.contribuidoresp})
    }
  },
};
</script>
