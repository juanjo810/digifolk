const utils = {
  methods: {
    parseFileToString(file) {
      return new Promise((resolve, reject) => {
        if (file) {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result);
          reader.onerror = reject;
          reader.readAsDataURL(file);          
        } else {
          resolve('');
        }
      });
    },
    parseFileToBinaryString(file) {
      return new Promise((resolve, reject) => {
        if (file) {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result);
          reader.onerror = reject;
          reader.readAsBinaryString(file);          
        } else {
          resolve('');
        }
      });
    }
  }
}

export default utils;