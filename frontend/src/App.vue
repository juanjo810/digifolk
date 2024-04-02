<template>
  <v-app>
    <v-main style="background-color: #F4E0CA">
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
import { mapState, mapActions } from "vuex";
import utils from '@/utils/utils.js'

export default {
  name: "App",

  data: () => ({
    //
  }),
  computed: {
    ...mapState(["error", "user"]),
    otroError: {
      get() {
        return this.error;
      },
      set(value) {
        this.$store.commit("RESET_ERROR", value);
      },
    },
  },
  methods: {
    ...mapActions(["logOut", "resetPieceForm", "resetCollectionForm", "isAutenticated", "importMultipleFiles"]),
    logout() {
      this.logOut().then(() => {
        this.$router.push({ name: "login" });
      });
    },
    goToCollectionForm() {
      this.resetCollectionForm();
      this.$router.push({ name: "collectionForm" });
    },
    goToPieceForm() {
      this.resetPieceForm();
      this.$router.push({ name: "uploadPiece" });
    },
    async importMultipleData() {
      var extensions = [
        {
          description: 'Archivos Excel',
          accept: {
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
            'application/vnd.ms-excel': ['.xls']
          }
        }
      ]
      var excelFile = await utils.readFileContents(extensions)
      if (excelFile !== '') {
        if(window.confirm('Do you want to import XML Files?')){
          extensions = [
            {
              description: 'Archivos XML y MXML',
              accept: {
                'text/xml': ['.xml', '.mxml', '.musicxml']
              }
            }
          ]
          var xmlFiles = await utils.readFileContents(extensions, true)
        }
        if(window.confirm('Do you want to import MEI Files?')) {
          extensions = [
            {
              description: 'Archivos MEI',
              accept: {
                'text/mei': ['.mei']
              }
            }
          ]
          var meiFiles = await utils.readFileContents(extensions, true)
        }
        this.importMultipleFiles({excelFile: excelFile, xmlFiles: xmlFiles, meiFiles: meiFiles})
      }
    }
  },
};
</script>
