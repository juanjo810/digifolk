import axios from 'axios'

export default {
  logIn(user, password) {
    const data = new URLSearchParams();
    data.append('username', user);
    data.append('password', password);

    return new Promise((resolve, reject) => {
      axios.post('http://100.127.151.18:8000/api/auth/token', data, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
        .then(response => {
          resolve(response.data);
        })
        .catch(error => {
          reject(error);
        })
    })
  },
  register(email, name, surname, username, password, institution) {
    const objectTemp = {
      "first_name": name,
      "last_name": surname,
      "email": email,
      "username": username,
      "is_admin": true,
      "institution": institution,
      "piece": [],
      "password": password
    }
    const param = JSON.stringify(objectTemp)

    return new Promise((resolve, reject) => {
      axios.post('http://100.127.151.18:8000/api/createUser', param, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          resolve(response.data);
        })
        .catch(error => {
          reject(error);
        });
    });
  },
  uploadCollection(json) {
    return new Promise((resolve, reject) => {
      console.log(json)
      axios.post('http://100.127.151.18:8000/api/createCol', json, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          resolve(response.data);
        })
        .catch(error => {
          reject(error);
        });
    });
  },
  uploadPiece(json) {
    return new Promise((resolve, reject) => {
      axios.post('http://100.127.151.18:8000/api/createPiece', json, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          resolve(response.data);
        })
        .catch(error => {
          reject(error);
        });
    });
  },

  getCollection(collection) {
    const obj = {
      id: collection[0],
      title: collection[1]
    }
    return new Promise((resolve, reject) => {
      axios.get('http://100.127.151.18:8000/api/getCol', {
        params: obj
      })
      .then(response => {
        resolve(response.data);
      })
      .catch(error => {
        reject(error);
      });
    });
  },

  editPiece(json) {
    return new Promise((resolve, reject) => {
      axios.post('http://100.127.151.18:8000/api/editPiece', json, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          resolve(response.data);
        })
        .catch(error => {
          reject(error);
        });
    });
  },
  editCollection(json, id) {
    return new Promise((resolve, reject) => {
      const query = `http://100.127.151.18:8000/api/editCol?id=${id}`
      console.log(query)
      axios.post(query, json
      )
        .then((response) => {
          resolve(response.data);
        })
        .catch((error) => {
          reject(error);
        });
    });
  },

  addItem(id,typeId, newItem) {
    const obj = {
      "id": id,
      "type_item": typeId,
      "name": newItem
    }
    const param = JSON.stringify(obj)
    return new Promise((resolve,reject) => {
      axios.post('http://100.127.151.18:8000/api/createItem', param, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        }
      })
      .then(() => {
        resolve(obj);
      })
      .catch(error => {
        reject(error);
      });
    })
  },
  removeItem(id,typeId) {
    return new Promise((resolve,reject) => {
      axios.delete('http://100.127.151.18:8000/api/removeItem', {
        params: {
          id: id,
          type_item: typeId
        }})        
      .then(() => {
        resolve();
      })
      .catch(error => {
        reject(error);
      });
    })
  },
  editOneItem(id, id_type, newName) {
    const obj = {
      "id": id,
      "type_item": id_type,
      "name": newName
    }
    const param = JSON.stringify(obj)
    return new Promise((resolve,reject) => {
      axios.post('http://100.127.151.18:8000/api/editItem', param, {
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then(() => {
        resolve();
      })
      .catch(error => {
        reject(error);
      });
    })
  },
  fetchAllItems() {
    return new Promise((resolve, reject) => {
      axios.get('http://100.127.151.18:8000/api/getListItems')
      .then(response => {
        resolve(response.data);
      })
      .catch(error => {
        reject(error);
      });
    });
  },
  fetchAllPieces() {
    return new Promise((resolve, reject) => {
      axios.get('http://100.127.151.18:8000/api/getListOfPieces')
      .then(response => {
        resolve(response.data);
      })
      .catch(error => {
        reject(error);
      });
    });
  },
  fetchAllCollections() {
    return new Promise((resolve, reject) => {
      axios.get('http://100.127.151.18:8000/api/getListOfCols')
      .then(response => {
        resolve(response.data);
      })
      .catch(error => {
        reject(error);
      });
    })
  },
  getPiece(piece) {
    const obj = {
      "id": piece[0],
      "title": piece[1]
    }
    return new Promise((resolve, reject) => {
      axios.get('http://100.127.151.18:8000/api/getPiece', {
        params: obj
      })
      .then(response => {
        resolve(response.data);
      })
      .catch(error => {
        reject(error);
      });
    });
  },
  advancedSearchPiece(query) {
    return new Promise((resolve, reject) => {
      axios.get('http://100.127.151.18:8000/api/advancedSearchPiece', {
        params: query
      })
      .then(response => {
        resolve(response.data);
      }
      )
      .catch(error => {
        reject(error);
      }
      );
    });
  },
  advancedSearchCollection(query) {
    return new Promise((resolve, reject) => {
      axios.get('http://1000.127.151.18:8000/api/advancedSearchCol', {
        params: query
      })
      .then(response => {
        resolve(response.data);
      }
      )
      .catch(error => {
        reject(error);
      }
      );
    });
  },

  importDataFromExcel(file) {
    const fileBlob = new Blob([file], { type: 'application/octet-stream' });
    const formData = new FormData();
    formData.append('file', fileBlob);
    console.log(formData)
    return new Promise((resolve, reject) => {
      axios.post('http://100.127.151.18:8000/api/mapFromExcel', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      .then(response => {
        resolve(response.data);
      })
      .catch(error => {
        reject(error);
      });
    });
  },

  importDataFromMEI(json) {
    return new Promise((resolve, reject) => {
      axios.post('http://100.127.151.18:8000/api/meitocsv', json, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        }
      })
      .then(response => {
        resolve(response.data);
      })
      .catch(error => {
        reject(error);
      });
    });
  },
  
}
