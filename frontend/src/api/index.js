import axios from 'axios'

export default {
  logIn(user, password) {
    const data = new URLSearchParams();
    data.append('username', user);
    data.append('password', password);

    return new Promise((resolve, reject) => {
      //resolve([{user_id: 1, first_name:'Juanjo', last_name:'Navarro', email:'juanjo@juanjo.com', username:'juanjo', is_admin: true, institution:'USAL'},"token"])
      axios.post('http://digifolk.usal.es/api/auth/token', data, {
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
      "is_admin": false,
      "institution": institution,
      "piece": [],
      "password": password
    }
    const param = JSON.stringify(objectTemp)

    return new Promise((resolve, reject) => {
      axios.post('http://digifolk.usal.es/api/createUser', param, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          axios.post('http://digifolk.usal.es/api/sendEmail', {
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
      axios.get('http://digifolk.usal.es/api/getAuth', {
        headers: {
          'Access-Control-Allow-Origin': '*',
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
    return new Promise((resolve, reject) => {
      axios.post('http://digifolk.usal.es/api/editPassword', param, {
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
      axios.delete('http://digifolk.usal.es/api/removeUser', {
        params: {
          email: email,
          id: id,
          username: username
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
  uploadCollection(json) {
    return new Promise((resolve, reject) => {
      console.log(json)
      axios.post('http://digifolk.usal.es/api/createCol', json, {
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
      axios.post('http://digifolk.usal.es/api/createPiece', json, {
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
      id: collection
    }
    return new Promise((resolve, reject) => {
      axios.get('http://digifolk.usal.es/api/getCol', {
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

  getPiecesCollection(collection) {
    const obj = {
      id: collection
    }
    return new Promise((resolve, reject) => {
      axios.get('http://digifolk.usal.es/api/getPiecesFromCol', {
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
      axios.post('http://digifolk.usal.es/api/editPiece', json, {
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
  editCollection(json) {
    return new Promise((resolve, reject) => {
      const query = 'http://digifolk.usal.es/api/editCol'
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
      axios.post('http://digifolk.usal.es/api/createItem', param, {
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
      axios.delete('http://digifolk.usal.es/api/removeItem', {
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
      axios.delete('http://digifolk.usal.es/api/removePiece', {
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
    return new Promise((resolve, reject) => {
      axios.delete('http://digifolk.usal.es/api/removeCol', {
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
  editOneItem(id, id_type, newName) {
    const obj = {
      "id": id,
      "type_item": id_type,
      "name": newName
    }
    const param = JSON.stringify(obj)
    return new Promise((resolve, reject) => {
      axios.post('http://digifolk.usal.es/api/editItem', param, {
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
      axios.get('http://digifolk.usal.es/api/getListItems')
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
      axios.get('http://digifolk.usal.es/api/getListOfPieces')
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
      axios.get('http://digifolk.usal.es/api/getListOfCols')
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
      axios.get('http://digifolk.usal.es/api/getListOfUsers')
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
      axios.get('http://digifolk.usal.es/api/getPiece', {
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
  advancedSearchPieces(query) {
    const obj = {
      ...query,
      xml: '',
      mei: '',
      midi: '',
      audio: '',
      video: '',
      user_id: query.user_id ? query.user_id : 0,
      review: false
    }
    console.log(JSON.stringify(obj))
    return new Promise((resolve, reject) => {
      axios.post('http://digifolk.usal.es/api/getPieceFromFilters', obj, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Content-Type': 'application/json'
        }
      })
        .then(response => {
          debugger
          resolve(response.data);
        }
        )
        .catch(error => {
          debugger
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
          debugger
          resolve(response.data);
        }
        )
        .catch(error => {
          debugger
          reject(error);
        }
        );
    });
  },

  importPieceFromExcel(file, id, xml, mei) {
    return new Promise((resolve, reject) => {
      axios.post('http://digifolk.usal.es/api/ExcelToPiece', 
      {
        xml: xml,
        mei: mei,
        user_id: id,
        file: file
      }, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
        .then(() => {
          resolve();
        })
        .catch(error => {
          reject(error);
        });
    });
  },

  importColFromExcel(file) {
    return new Promise((resolve, reject) => {
      axios.post('http://digifolk.usal.es/api/ExcelToCol', 
      {
        file: file
      }, {
        headers: {
          'Content-Type': 'multipart/form-data'
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
    });
  },

  importDataFromMEI(user_id, meiFile) {
    debugger
    const formData = new FormData();
    formData.append('mei', meiFile);
    return new Promise((resolve, reject) => {
      axios.post(`http://digifolk.usal.es/api/MeiToCsv?user_id=${user_id}`, 
        formData
        , {
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

  importDataFromXML(user_id, xmlFile) {
    debugger
    const formData = new FormData();
    formData.append('xml', xmlFile);
    return new Promise((resolve, reject) => {
      axios.post(`http://digifolk.usal.es/api/XMLToCsv?user_id=${user_id}`, 
        formData
        , {
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

  importMultipleFiles(excel, xml, mei, user_id) {
    debugger
    const formData = new FormData();
    formData.append('file', excel);
    if (mei.lenght == 0)
      formData.append('mei', '');
    else
      mei.forEach((file) => {
        formData.append(`mei`, file);
      });
    xml.forEach((file) => {
      formData.append(`xml`, file);
    });
    formData.append('user_id', user_id);
      return new Promise((resolve, reject) => {
      axios.post(`http://digifolk.usal.es/api/ExcelController?user_id=${user_id}`, 
      formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
        .then(() => {
          resolve();
        })
        .catch(error => {
          reject(error);
        });
    });
  },

  editUser(user, oldMail) {
    return new Promise((resolve, reject) => {
      const query = `http://digifolk.usal.es/api/editUser?email_old=${oldMail}`
      axios.post(query, user
      )
        .then((response) => {
          resolve(response.data);
        })
        .catch((error) => {
          reject(error);
        });
    });
  },

  exportPieceToExcel(id) {
    return new Promise((resolve, reject) => {
      axios.post(`http://digifolk.usal.es/api/piecesToCsv?piece_id=${id}`, {
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
    })
  }  
}
