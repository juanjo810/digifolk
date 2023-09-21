import axios from 'axios'

export default {
  logIn(user, password) {
    const data = new URLSearchParams();
    data.append('username', user);
    data.append('password', password);

    return new Promise((resolve, reject) => {
      //resolve([{user_id: 1, first_name:'Juanjo', last_name:'Navarro', email:'juanjo@juanjo.com', username:'juanjo', is_admin: true, institution:'USAL'},"token"])
      axios.post('http://100.127.151.18:8000/api/auth/token', data, {
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
      axios.post('http://100.127.151.18:8000/api/createUser', param, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          axios.post('http://100.127.151.18:8000/api/sendEmail', {
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
      axios.get('http://100.127.151.18:8000/api/getAuth', {
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
      axios.post('http://100.127.151.18:8000/api/editPassword', param, {
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
      axios.delete('http://100.127.151.18:8000/api/removeUser', {
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
      axios.post('http://100.127.151.18:8000/api/createCol', json, {
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
  uploadPiece(json) {
    return new Promise((resolve, reject) => {
      axios.post('http://100.127.151.18:8000/api/createPiece', json, {
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
    console.log(json)
    return new Promise((resolve, reject) => {
      axios.post('http://100.127.151.18:8000/api/editPiece', json, {
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
      const query = 'http://100.127.151.18:8000/api/editCol'
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

  addItem(id, typeId, newItem) {
    const obj = {
      "id": id,
      "type_item": typeId,
      "name": newItem
    }
    const param = JSON.stringify(obj)
    return new Promise((resolve, reject) => {
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
  removeItem(id, typeId) {
    return new Promise((resolve, reject) => {
      axios.delete('http://100.127.151.18:8000/api/removeItem', {
        params: {
          id: id,
          type_item: typeId
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
  removePiece(id) {
    return new Promise((resolve, reject) => {
      axios.delete('http://100.127.151.18:8000/api/removePiece', {
        params: {
          id: id
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
  removeCollection(id) {
    debugger
    return new Promise((resolve, reject) => {
      axios.delete('http://100.127.151.18:8000/api/removeCol', {
        params: {
          id: id
        }
      })
        .then(() => {
          debugger
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
    return new Promise((resolve, reject) => {
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
  fetchAllUsers() {
    return new Promise((resolve, reject) => {
      axios.get('http://100.127.151.18:8000/api/getListOfUsers')
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
    return new Promise((resolve, reject) => {
      axios.post('http://100.127.151.18:8000/api/PieceFromExcel', 
      {
        file: file
      }, {
        headers: {
          'Content-Type': 'multipart/form-data'
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

  editUser(user, oldMail) {
    return new Promise((resolve, reject) => {
      const query = `http://100.127.151.18:8000/api/editUser?email_old=${oldMail}`
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
