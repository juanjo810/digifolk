import axios from 'axios'

export default {
  logIn(user, password) {
    const data = new URLSearchParams();
    data.append('username', user);
    data.append('password', password);

    return new Promise((resolve, reject) => {
      //resolve([{user_id: 1, first_name:'Juanjo', last_name:'Navarro', email:'juanjo@juanjo.com', username:'juanjo', is_admin: true, institution:'USAL'},"token"])
      axios.post('http://100.127.151.18:8000/auth/token', data, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
        .then(response => {
          debugger
          resolve(response.data);
        })
        .catch(error => {
          debugger
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
      "is_admin": false,
      "institution": institution,
      "piece": [],
      "password": password
    }
    const param = JSON.stringify(objectTemp)

    return new Promise((resolve, reject) => {
      axios.post('http://100.127.151.18:8000/createUser', param, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          axios.post('http://100.127.151.18:8000/sendEmail', {
            "receiver_email": email,
          },
          {
            headers: {
              'Access-Control-Allow-Origin': '*',
              'Content-Type': 'application/json'
            }
          })
          .then(() => {
            resolve(response.data);
          })
          .catch(error => {
            reject(error);
          })
        })
        .catch(error => {
          reject(error);
        });
    });
  },
  isAutenticated(token) {
    return new Promise((resolve, reject) => {
      axios.get('http://100.127.151.18:8000/getAuth', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
        .then((response) => {
          resolve(response.data);
        })
        .catch((error) => {
          reject(error);
        })
    })
  },
  changePassword(id, newPassword, currentPassword) {
    const param = {
      "old_password": currentPassword,
      "new_password": newPassword,
      "user_id": id
    }
    debugger
    return new Promise((resolve, reject) => {
      axios.post('http://100.127.151.18:8000/editPassword', param, {
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
  deleteAccount(email, id, username) {
    return new Promise((resolve, reject) => {
      axios.delete('http://100.127.151.18:8000/removeUser', {
        params: {
          email: email,
          id: id,
          username: username
        }
      })
      .then(() => {
        debugger
        resolve();
      })
      .catch(error => {
        debugger
        reject(error);
      });
    })
  },
  uploadCollection(json) {
    return new Promise((resolve, reject) => {
      console.log(json)
      axios.post('http://100.127.151.18:8000/createCol', json, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          resolve(response.data);
        })
        .catch(error => {
          debugger
          reject(error);
        });
    });
  },
  uploadPiece(json) {
    return new Promise((resolve, reject) => {
      axios.post('http://100.127.151.18:8000/createPiece', json, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          debugger
          resolve(response.data);
        })
        .catch(error => {
          debugger
          reject(error);
        });
    });
  },

  getCollection(collection) {
    const obj = {
      id: collection
    }
    return new Promise((resolve, reject) => {
      axios.get('http://100.127.151.18:8000/getCol', {
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
    console.log(json)
    return new Promise((resolve, reject) => {
      axios.post('http://100.127.151.18:8000/editPiece', json, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          debugger
          resolve(response.data);
        })
        .catch(error => {
          debugger
          reject(error);
        });
    });
  },
  editCollection(json) {
    return new Promise((resolve, reject) => {
      const query = 'http://100.127.151.18:8000/editCol'
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
      axios.post('http://100.127.151.18:8000/createItem', param, {
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
      axios.delete('http://100.127.151.18:8000/removeItem', {
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
  removePiece(id) {
    return new Promise((resolve,reject) => {
      axios.delete('http://100.127.151.18:8000/removePiece', {
        params: {
          id: id
        }})
      .then(() => {
        resolve();
      })
      .catch(error => {
        reject(error);
      });
    })
  },
  removeCollection(id) {
    return new Promise((resolve,reject) => {
      axios.delete('http://100.127.151.18:8000/removeCol', {
        params: {
          id: id
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
      axios.post('http://100.127.151.18:8000/editItem', param, {
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
      axios.get('http://100.127.151.18:8000/getListItems')
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
      axios.get('http://100.127.151.18:8000/getListOfPieces')
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
      axios.get('http://100.127.151.18:8000/getListOfCols')
      .then(response => {
        resolve(response.data);
      })
      .catch(error => {
        reject(error);
      });
    })
  },
  fetchAllUsers() {
    return new Promise((resolve, reject) => {
      axios.get('http://100.127.151.18:8000/getListOfUsers')
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
      "id": piece
    }
    return new Promise((resolve, reject) => {
      axios.get('http://100.127.151.18:8000/getPiece', {
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
      axios.get('http://100.127.151.18:8000/advancedSearchPiece', {
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
      axios.get('http://1000.127.151.18:8000/advancedSearchCol', {
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
      axios.post('http://100.127.151.18:8000/mapFromExcel', formData, {
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
      axios.post('http://100.127.151.18:8000/meitocsv', json, {
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

  editUser(user, oldMail) {
    return new Promise((resolve, reject) => {
      const query = `http://100.127.151.18:8000/editUser?email_old=${oldMail}`
      console.log(user)
      axios.post(query, user
      )
        .then((response) => {
          resolve(response.data);
        })
        .catch((error) => {
          reject(error);
        });
    });
  }
  
}
