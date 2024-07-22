<template>
  <v-container>
    <v-row justify="center">
      <v-card max-width="1000" width="100%">
        <v-bottom-navigation>
          <v-btn value="excel" @click="$router.push({ name: 'userForm' })">
            <span>XML user data</span>
            <v-icon>mdi-account</v-icon>
          </v-btn>

          <v-btn value="xml" @click="$router.push({ name: 'sheetForm' })">
            <span>Music sheet data</span>
            <v-icon>mdi-file-music</v-icon>
          </v-btn>

          <v-btn value="import" @click="importFile()">
            <span>Import from file</span>
            <v-icon>mdi-file</v-icon>
          </v-btn>
          <input type="file" ref="fileInput" class="d-none" accept=".xlsx, .xls, .mei, .mxml"
            @change="handleFileChange" />
        </v-bottom-navigation>

        <router-view></router-view>
      </v-card>
    </v-row>
  </v-container>
</template>

<script>
import { mapActions } from 'vuex';
import utils from '@/utils/utils.js';
export default {
  methods: {
    ...mapActions(['resetPieceForm',
      'importDataFromExcel',
      'importDataFromXML',
      'importDataFromMEI']),
    importFile() {
      this.$refs.fileInput.click();
    },
    handleFileChange(event) {
      const file = event.target.files[0];
      if (file && file.name.endsWith(".xlsx")) {
        const reader = new FileReader();
        reader.onload = async () => {
          if (window.confirm("Do you want to upload the corresponding XML File for this piece?"))
            var xml = await utils.readFileContents(".xml, .mxml, .musicxml")
          if (window.confirm("Do you want to upload the corresponding MEI File for this piece?"))
            var mei = await utils.readFileContents(".mei")
          this.importDataFromExcel({ file: file, xml: xml ? xml : '', mei: mei ? mei : '' });
        };
        reader.readAsText(file);
      } else if (file && file.name.endsWith(".mei")) {
        this.importDataFromMEI({ file: file });
      } else if (file && (file.name.endsWith(".xml") || file.name.endsWith(".mxml") || file.name.endsWith(".musicxml"))) {
        const reader = new FileReader();
        reader.onload = (e) => {
          this.importDataFromXML({ file: e.target.result });
        };
        reader.readAsText(file);
      }
      console.log("Archivo seleccionado:", file);
    },
  },
  created() {
    this.resetPieceForm();
  },
};
</script>
