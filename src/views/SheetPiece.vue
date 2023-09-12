<template>
  <div>
    <div ref="osmdContainer"></div>
    <input type="file" @change="onFileChange" />
  </div>
</template>

<script>
import * as opensheetmusicdisplay from 'opensheetmusicdisplay'; // Importa la biblioteca

export default {
  data() {
    return {
      osmd: null,
    };
  },
  methods: {
    onFileChange(e) {
      var reader = new FileReader();
      reader.onload = () => {
        this.osmd.load(reader.result).then(
          () => {
            this.osmd.render();
          },
          function (e) {
            console.log('error loading ' + e);
          }
        );
      };
      reader.readAsText(e.target.files[0]);
    },
  },
  mounted() {
    this.osmd = new opensheetmusicdisplay.OpenSheetMusicDisplay(this.$refs.osmdContainer);
    this.osmd.setOptions({
      backend: 'svg',
      drawTitle: true,
      // drawingParameters: 'compacttight' // Opciones adicionales si es necesario
    });
  }
};
</script>

<style scoped>
/* Estilos específicos para este componente si es necesario */
</style>
