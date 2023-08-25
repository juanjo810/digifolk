/**
 * @module Actions
 * @description Este fichero muestra las diferentes acciones que realiza el sistema para proporcionar su funcionalidad.
 * En todas las funciones se utiliza el objeto contexto recibido automáticamente como primer parámetro. En concreto se utiliza
 * la propiedad commit para realizar las mutaciones del sistema.
 */

import * as types from './mutations-types'
import API from '@/api'
import { format } from 'date-fns'
import utils from '@/utils/utils'

export default{
  
  loginUser ({ commit }, { user, password }) {
      return new Promise((resolve, reject)=>{
        commit(types.LOGIN_USER_REQUEST)
        API.logIn(user, password)
          .then((res)=>{
            if (Array.isArray(res)) {
              commit(types.LOGIN_USER_SUCCESS, {userInfo: res[0], token: res[1]})
            } else {
              commit(types.LOGIN_USER_FAILURE, { error: 'Wrong user or password.'})
            }
            resolve()
          })
          .catch((err) => {
            console.log(err)
            commit(types.LOGIN_USER_FAILURE, { error: 'Failed connection with server.'})
            reject()
          })
      } 
    )},

  
  registerUser ({ commit }, { email, password, name, surname, username, password2, institution }) {
    return new Promise((resolve, reject) => {
      commit(types.REGISTER_USER_REQUEST)
      if (password !== password2) {
        commit(types.REGISTER_USER_FAILURE, { error: 'Las contraseñas no coinciden' })
        reject()
      } else {
        API.register(email, name, surname, username, password, institution)
          .then(() => {
            commit(types.REGISTER_USER_SUCCESS)
            resolve()
          })
          .catch(() => {
            commit(types.REGISTER_USER_FAILURE, {error: 'Error de registro'})
            reject()
          })
      }
    })
  },

  saveDataCollection ({state, commit, getters}) {
    const collectionTemp = utils.parseCollectionToJSON(state.collectionForm, state.separator, state.defaultSelections.itemsIDs, getters.getItemId)
    collectionTemp.user_id = state.user.userInfo.user_id
    const json = JSON.stringify(collectionTemp)
    return new Promise((resolve, reject) => {
      commit(types.UPLOAD_COLLECTION_REQUEST)
      API.uploadCollection(json)
        .then((res) => {
          commit(types.UPLOAD_COLLECTION_SUCCESS, res)
          resolve()
        })
        .catch((error) => {
          commit(types.UPLOAD_COLLECTION_FAILURE, {error: error.msg})
          reject()
        })
    })
  },
  
  saveDataPiece ({state, commit, getters}) {
    var combinedForm = utils.parsePieceToJSON(state.pieceForm, state.separator, state.defaultSelections.itemsIDs, getters.getItemId)
    combinedForm.xml = utils.parseFileToString(state.xml)
    combinedForm.mei = utils.parseFileToString(state.mei)
    combinedForm.midi = utils.parseFileToBinaryString(state.midi)
    combinedForm.user_id = state.user.userInfo.user_id
    combinedForm.col_id = parseInt(state.pieceForm.col_id.split(state.separator)[0])
    const json = JSON.stringify(combinedForm)
    return new Promise((resolve, reject) => {
      commit(types.UPLOAD_PIECE_REQUEST)
      API.uploadPiece(json)
        .then(() => {
          commit(types.UPLOAD_PIECE_SUCCESS)
          resolve()
        })
        .catch((error) => {
          commit(types.UPLOAD_PIECE_FAILURE, {error: error.msg})
          reject()
        })
    })  
  },

  editPiece ({commit, getters, state}) {
    var combinedForm = utils.parsePieceToJSON(state.pieceForm, state.separator, state.defaultSelections.itemsIDs, getters.getItemId)
    combinedForm.xml = utils.parseFileToString(state.xml)
    combinedForm.mei = utils.parseFileToString(state.mei)
    combinedForm.midi = utils.parseFileToBinaryString(state.midi)
    combinedForm.user_id = state.user.userInfo.user_id
    combinedForm.col_id = parseInt(state.pieceForm.col_id.split(state.separator)[0])
    const json = JSON.stringify(combinedForm)
    return new Promise((resolve, reject) => {
      commit(types.EDIT_PIECE_REQUEST)
      API.editPiece(json)
        .then(() => {
          commit(types.EDIT_PIECE_SUCCESS)
          resolve()
        })
        .catch((error) => {
          commit(types.EDIT_PIECE_FAILURE, error.msg)
          reject()
        })
    })  
  },

  // Function called editCollection which is used to edit a collection. The process is similar to editPiece, but using the fields of the collection form, which can be found in the state.
  editCollection ({commit, getters, state}) {
    var collectionTemp = utils.parseCollectionToJSON(state.collectionForm, state.separator, state.defaultSelections.itemsIDs, getters.getItemId)
    const id = collectionTemp.col_id
    collectionTemp = {
      ...collectionTemp,
      piece_col: []
    }
    delete collectionTemp.col_id
    console.log(collectionTemp)
    const json = JSON.stringify(collectionTemp);
    console.log(json);
    return new Promise((resolve, reject) => {
      commit(types.EDIT_COLLECTION_REQUEST)
      API.editCollection(collectionTemp, id)
        .then(() => {
          commit(types.EDIT_COLLECTION_SUCCESS, id)
          resolve()
        })
        .catch((error) => {
          commit(types.EDIT_COLLECTION_FAILURE, error.msg)
          reject()
        })
    })
  },
  
  addContributor ({ commit }, form){
    switch (form) {
      case 'User':
        commit(types.ADD_USER_CONTRIBUTOR)
        break
      case 'Sheet':
        commit(types.ADD_SHEET_CONTRIBUTOR)
        break
      case 'Collection':
        commit(types.ADD_COLLECTION_CONTRIBUTOR)
        break
      default:
        return
    }
  },

  addCreator ({ commit }, form){
    switch (form) {
      case 'Sheet':
        commit(types.ADD_SHEET_CREATOR)
        break
      case 'Collection':
        commit(types.ADD_COLLECTION_CREATOR)
        break
      default:
        return
    }
  },

  removeContributor ({ commit }, {index, form}){
    switch (form) {
      case 'User':
        commit(types.REMOVE_USER_CONTRIBUTOR, index)
        break
      case 'Sheet':
        commit(types.REMOVE_SHEET_CONTRIBUTOR, index)
        break
      case 'Collection':
        commit(types.REMOVE_COLLECTION_CONTRIBUTOR, index)
        break
      default:
        return
    }
  },

  removeCreator ({ commit }, {index, form}){
    switch (form) {
      case 'Sheet':
        commit(types.REMOVE_SHEET_CREATOR, index)
        break
      case 'Collection':
        commit(types.REMOVE_COLLECTION_CREATOR, index)
        break
      default:
        return
    }
  },

  formatAndSaveDate ({commit}, {date, form}) {
    const formattedDate = format(date[0], 'd MMMM yyyy')
    switch (form) {
      case 'User':
        commit(types.SAVE_USER_DATE, formattedDate)
        break
      case 'Sheet':
        commit(types.SAVE_SHEET_DATE, formattedDate)
        break
      case 'Collection':
        commit(types.SAVE_COLLECTION_DATE, formattedDate)
        break
      default:
        return
    }
  },

  addNewItem ({commit}, {id, id_type, newItem}) {
    return new Promise((resolve, reject) => {
      API.addItem(id, id_type, newItem)
      .then((res) => {
        commit(types.ADD_NEW_ITEM_SUCCESS, res)
        resolve()
      })
      .catch((err) => {
        commit(types.ADD_NEW_ITEM_FAILURE, err)
        reject()
      })
    })
  },

  removeOneItem ({commit}, {item, id_type}) {
    API.removeItem(item.id, id_type)
    .then(() => {
      commit(types.REMOVE_ITEM_SUCCESS, item)
    })
    .catch((err) => {
      commit(types.REMOVE_ITEM_FAILURE, err)
    })
  },

  editItem ({commit}, {id, id_type, newName}) {
    API.editOneItem(id, id_type, newName)
    .then(() => {
      commit(types.EDIT_ITEM_SUCCESS, {id: id, id_type: id_type, newName: newName})
    })
    .catch((err) => {
      commit(types.EDIT_ITEM_FAILURE, err)
    })
  },

  fetchItems({commit}) {
    API.fetchAllItems()
    .then((res)=>{
      commit(types.FETCH_ITEMS, res)
    })
  },

  fetchPieces({commit}) {
    API.fetchAllPieces()
    .then((res)=>{
      commit(types.FETCH_PIECES, res)
    })
  },

  fetchCollections({commit}) {
    API.fetchAllCollections()
    .then((res)=>{
      commit(types.FETCH_COLLECTIONS, res)
    })
  },

  getPieceInfo({commit, state}, {piece, creadores, contribuidores, contribuidoresp}) {
    //API.getPiece(piece)
    //.then((res) => {
      // const res = state.pieces.find(p => p.id === parseInt(piece[0]))
      console.log(state, piece)
      const res = {
        title: ["Titulo"],
        rights: 17,
        creator: "Creator",
        date: "5 August 2023",
        type_file: 74,
        publisher: "Publisher",
        contributor_role: [
          {
            name: "Contributor",
            role: 22
          }
        ],
        desc: "Description",
        rightsp: 111,
        creatorp_role: [
          {
            name: "Creador1",
            role: 34
          }
        ],
        datep: "5 August 2023",
        real_key: "D",
        meter: "9/8",
        tempo: "Fast",
        instruments: ["Banjo", "5-String Banjo", "Irish Bouzouki"],
        genre: ["Work piece", "Sons"],
        contributorp_role: [
          {
            name: "Contributor",
            role: 42
          }
        ],
        alt_title: "AltTitle",
        mode: "Mode",
        descp: "Decription",
        type_piece: 75,
        formattingp: "Format",
        subject: ["Subject"],
        language: "IE",
        relationp: ["Relation1", "Relation2"],
        hasVersion: ["Version"],
        isVersionOf: ["Is", "2"],
        coverage: "Coverage",
        spatial: {
          country: "Ireland",
          state: "Dublin",
          location: "Dublin"
        },
        temporal: {
          century: "20th",
          decade: "10s",
          year: "1914"
        },
        xml: "",
        mei: "",
        midi: "",
        audio: "Audio1",
        video: "Video1",
        user_id: 1,
        col_id: 1
      }
    var final = structuredClone(res)
    final.title = final.title.join('|')
    var item = state.defaultSelections.items.find(i => i.id === parseInt(final.rights))
    final.rights = item.name
    var type_file = state.defaultSelections.items.find(i => i.id === parseInt(final.type_file))
    final.type_file = type_file.name
    final.contributor_role = final.contributor_role.map((c) => {
      var item = state.defaultSelections.items.find(i => i.id === parseInt(c.role))
      const temp = {
        name: c.name,
        role: item.name
      }
      contribuidores.push(temp)
      return temp
    })
    final.rightsp = state.defaultSelections.items.find(i => i.id === parseInt(final.rightsp)).name
    final.creatorp_role = final.creatorp_role.map((c) => {
      var item = state.defaultSelections.items.find(i => i.id === parseInt(c.role))
      const temp = {
        name: c.name,
        role: item.name
      }
      creadores.push(temp)
      return temp
    })
    final.contributorp_role = final.contributorp_role.map((c) => {
      var item = state.defaultSelections.items.find(i => i.id === parseInt(c.role))
      const temp = {
        name: c.name,
        role: item.name
      }
      contribuidoresp.push(temp)
      return temp
    })
    final.subject = final.subject.join('|')
    final.relationp = final.relationp.join('|')
    final.hasVersion = final.hasVersion.join('|')
    final.isVersionOf = final.isVersionOf.join('|')

      commit(types.GET_PIECE_SUCCESS, final)
    //})
    //.catch((err) => {
    //  commit(types.GET_PIECE_FAILURE, err)
    //})
  },

  getCollectionInfo({commit, state}, {collection, creadores, contribuidores}) {
    API.getCollection(collection)
    .then((res) => {
      /*const res = {
          col_id: 1,
          title: ["Collection1"],
          rights: 17,
          date: "8 August 2023",
          creator_role: [
            {
              name: "Creator1",
              role: 51
            }
          ],
          contributor_role: [
            {
              name: "Contributor1",
              role: 61
            }
          ],
          source_type: 71,
          source: "Source",
          description: "Description",
          formatting: "Format",
          extent: "Extent",
          publisher: "Publisher",
          subject: ["Subject"],
          language: "es",
          relation: ["Relation1", "Relation2"],
          coverage: "Coverage",
          spatial: {
            country: "Ireland",
            state: "Ireland",
            location: "Dublin"
          },
          temporal: {
            century: "19th",
            decade: "10s",
            year: "1814"
          },
          rightsHolder: "RightsHolder",
          piece_col: []
        }*/
      var final = structuredClone(res[0])
      final.title = final.title.join('|')
      var item = state.defaultSelections.items.find(i => i.id === parseInt(final.rights))
      final.rights = item.name
      final.source_type = state.defaultSelections.items.find(i => i.id === parseInt(final.source_type)).name
      final.creator_role = final.creator_role.map((c) => {
        var item = state.defaultSelections.items.find(i => i.id === parseInt(c.role))
        const temp = {
          name: c.name,
          role: item.name
        }
        creadores.push(temp)
        return temp
      })
      final.contributor_role = final.contributor_role.map((c) => {
        var item = state.defaultSelections.items.find(i => i.id === parseInt(c.role))
        const temp = {
          name: c.name,
          role: item.name
        }
        contribuidores.push(temp)
        return temp
      })
      final.subject = final.subject.join('|')
      final.relation = final.relation.join('|')

      commit(types.GET_COLLECTION_SUCCESS, final)
    })
    .catch((err) => {
      commit(types.GET_COLLECTION_FAILURE, err)
    })
  },

  resetPieceForm({commit}) {
    commit(types.RESET_PIECE_FORM)
  },

  resetCollectionForm({commit}) {
    commit(types.RESET_COLLECTION_FORM)
  },

  advancedSearch({commit, state, getters}, {query, type}) {
    return new Promise((resolve, reject) => {
      if (type === 'pieces') {
        var pieceQuery = utils.parsePieceToJSON(query, state.separator, state.defaultSelections.itemsIDs, getters.getItemId)
        API.advancedSearchPieces(pieceQuery)
        .then((res) => {
          resolve(res)
        })
        .catch((err) => {
          commit(types.ADVANCED_SEARCH_FAILURE, err)
          reject()
        })
      } else if (type === 'collections') {
        var collectionQuery = utils.parseCollectionToJSON(query, state.separator, state.defaultSelections.itemsIDs, getters.getItemId)
        API.advancedSearchCollections(collectionQuery)
        .then((res) => {
          resolve(res)
        })
        .catch((err) => {
          commit(types.ADVANCED_SEARCH_FAILURE, err)
          reject()
        })
      }
    })
  },

  importDataFromExcel({commit}, {file}) {
    API.importDataFromExcel(file)
    .then((res) => {
      commit(types.IMPORT_DATA_SUCCESS, res)
    })
    .catch((err) => {
      commit(types.IMPORT_DATA_FAILURE, err)
    })
  },

  importDataFromMEI({commit}, {file}) {
    API.importDataFromMEI(file)
    .then((res) => {
      commit(types.IMPORT_DATA_SUCCESS, res)
    })
    .catch((err) => {
      commit(types.IMPORT_DATA_FAILURE, err)
    })
  },

  fetchUsers({commit}) {
    API.fetchAllUsers()
    .then((res) => {
      commit(types.FETCH_USERS, res)
    })
  },

  editUserInfo({commit}, {user, oldMail}) {
    API.editUser(user, oldMail)
    .then(() => {
      commit(types.EDIT_USER_SUCCESS, {user, oldMail})
    })
    .catch((err) => {
      commit(types.EDIT_USER_FAILURE, err)
    })
  },
  
  /**
   * Función para restablecer la contraseña del usuario.
   * Se llama a la función de la API para que envíe un email de restablecimiento
   * de contraseña al usuario.
   * @param {string} email email del usuario
   */
  // resetPassword ({ commit }, email) {
  //   return new Promise((resolve) => {
  //     commit(types.RESET_PASSWORD_REQUEST)
  //     API.resetPass(email)
  //       .then(() => {
  //         commit(types.RESET_PASSWORD_SUCCESS)
  //         resolve()
  //       })
  //       .catch(error => commit(types.RESET_PASSWORD_FAILURE, { error }))
  //   })
  // },

  /**
   * Función para cambiar la contraseña del usuario.
   * Se actualiza la contraseña del usuario llamando a la función 
   * correspondiente de la API.
   * Se comprueba que el usuario ha introducido correctamente su contraseña actual
   * realizando de nuevo el login y si es correcta se cambia por la nueva.
   * @param {Object} usuario datos del usuario
   * @prop {string} usuario.email email del usuario
   * @prop {string} usuario.currentPassword contraseña actual del usuario
   * @prop {string} usuario.newPassword nueva contraseña del usuario
   * @prop {string} usuario.repeatedPassword repetición de la nueva contraseña
   */
  // changePassword ({commit}, {email, currentPassword, newPassword, repeatedPassword}) {
  //   if (newPassword !== repeatedPassword) {
  //     commit(types.CHANGE_PASSWORD_FAILURE, { error: 'Las contraseñas no coinciden' })
  //   } else {
  //     API.login(email, currentPassword)
  //       .then(() => {
  //         API.changeUserPassword(newPassword)
  //           .then(() => {
  //             commit(types.CHANGE_PASSWORD_SUCCESS)
  //           })
  //           .catch(error => {
  //             if (error.code === 'auth/weak-password') {
  //               commit(types.CHANGE_PASSWORD_FAILURE, { error: 'La contraseña debe contener 6 caracteres o más' })
  //             } else {
  //               commit(types.CHANGE_PASSWORD_FAILURE, { error })
  //             }
  //           })
  //       })
  //       .catch(() => commit(types.CHANGE_PASSWORD_FAILURE, { error: 'La contraseña actual es incorrecta' }))
  //   }
  // },

 
  /**
   * Función para el borrado de cuenta
   * Se comprueban las credenciales del usuario para asegurar que realmente
   * desea eliminar su cuenta. Después se borran todos los elementos de la base
   * de datos del usuario y se elimina la cuenta del usuario.
   * @param {Object} usuario datos del usuario
   * @prop {array} usuario.images imagenes subidas por el usuario 
   * @prop {string} usuario.email email del usuario
   * @prop {string} usuario.password contraseña del usuario 
   */
  // deleteAccount ({commit}, {images, email, password}) {
  //   return new Promise((resolve) => {
  //     commit(types.DELETE_ACCOUNT_REQUEST)
  //     API.login(email, password)
  //     .then(async () => {
  //       for (const element of images) {
  //         await API.removePostById(element.id, element.esPublico)
  //           .catch((error) => { commit(types.DELETE_ACCOUNT_FAILURE, {error: error}) })
  //       }
  //       API.deleteUserAccount()
  //         .then(() => {
  //           commit(types.DELETE_ACCOUNT_SUCCESS)
  //           resolve()
  //         })
  //         .catch((error) => { commit(types.DELETE_ACCOUNT_FAILURE, {error: error}) })
  //     })
  //     .catch(() => commit(types.DELETE_ACCOUNT_FAILURE, { error: 'Credenciales introducidas incorrectas' }))
  //   })
  // },

 
  /**
   * Función que recupera los 20 reportes más recientes del sistema
   * empezando por la imagen con id 'start'
   * Si start está vacío se empieza desde el principio
   * @param {start} id de la imagen reportada por la que queremos empezar
   */
  //  getReportes ({ commit }, start) {
  //   commit(types.FETCH_IMAGES_REQUEST, start)
  //   API.getReportss(start)
  //     .then((images) => {
  //       commit(types.FETCH_IMAGES_SUCCESS, images)
  //     })
  //     .catch ((error) => {
  //       commit(types.FETCH_IMAGES_FAILURE, error)
  //     })
  // },

  /**
   * Función que recupera las 20 publicaciones más recientes del sistema
   * empezando por la imagen con id 'start'
   * Si start está vacío se empieza desde el principio
   * @param {start} id de la publicación por la que queremos empezar
   */
  

  /**
   * Función utilizada para el cierre de sesión del usuario
   * Se llama a la función de la API correspondiente.
   */
  // signOut ({commit}) {
  //   return new Promise((resolve, reject) => {})

  // }
}
