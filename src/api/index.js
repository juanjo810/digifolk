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
    console.log(param)

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
    debugger
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
  }
}
