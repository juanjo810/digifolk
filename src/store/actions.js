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
        commit(types.REGISTER_USER_FAILURE, { error: "Passwords don't match" })
        reject()
      } else {
        API.register(email, name, surname, username, password, institution)
          .then(() => {
            commit(types.REGISTER_USER_SUCCESS)
            resolve()
          })
          .catch(() => {
            commit(types.REGISTER_USER_FAILURE, {error: 'Register error'})
            reject()
          })
      }
    })
  },

  changeUserPassword ({commit}, {id, currentPassword, newPassword}) {
    API.changePassword(id, newPassword, currentPassword)
      .then(() => {
        commit(types.CHANGE_PASSWORD_SUCCESS)
      })
      .catch(error => {
          commit(types.CHANGE_PASSWORD_FAILURE, { error })
      })
  },

  removeAccount ({commit, state}, {password, email}) {
    return new Promise((resolve, reject) => {
      API.logIn(email, password)
      .then(() => {
        API.deleteAccount(email, state.user.userInfo.user_id, state.user.userInfo.username)
          .then(() => {
            debugger
            commit(types.DELETE_ACCOUNT_SUCCESS)
            
            resolve()
          })
          .catch((error) => { 
            debugger
            commit(types.DELETE_ACCOUNT_FAILURE, {error: error}) 
            reject()
          })
      })
      .catch(() => {
        debugger
        commit(types.DELETE_ACCOUNT_FAILURE, { error: 'Incorrect password' })
        reject()
      })
    })
  },

  logOut({commit}) {
    return new Promise((resolve) => {
      commit(types.LOG_OUT_SUCCESS)
      resolve()
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
  
  async saveDataPiece ({state, commit, getters}) {
    var combinedForm = utils.parsePieceToJSON(state.pieceForm, state.separator, state.defaultSelections.itemsIDs, getters.getItemId)
    combinedForm.xml = await utils.parseFileToString(state.pieceForm.xml[0])
    combinedForm.mei = await utils.parseFileToString(state.pieceForm.mei[0])
    combinedForm.midi = await utils.parseFileToBinaryString(state.pieceForm.midi[0])
    combinedForm.user_id = state.user.userInfo.user_id
    combinedForm.review = false
    combinedForm.user_id = state.user.userInfo.user_id
    var temp = 0
    try {
      temp = parseInt(state.pieceForm.col_id.split(state.separator)[0])
    } catch (error) {
      temp = 0
    }
    combinedForm.col_id = temp
    if(state.user.userInfo.is_admin === true) {
      combinedForm.review = true
    } else {
      combinedForm.review = false
    }
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

  async editPiece ({commit, getters, state}) {
    debugger
    var combinedForm = await utils.parsePieceToJSON(state.pieceForm, state.separator, state.defaultSelections.itemsIDs, getters.getItemId)
    combinedForm.xml = await utils.parseFileToString(state.pieceForm.xml[0])
    combinedForm.mei = await utils.parseFileToString(state.pieceForm.mei[0])
    combinedForm.midi = await utils.parseFileToString(state.pieceForm.midi[0])
    combinedForm.midi_obj = combinedForm.midi
    combinedForm.user_id = state.user.userInfo.user_id
    combinedForm.review = false
    return new Promise((resolve, reject) => {
      commit(types.EDIT_PIECE_REQUEST)
      API.editPiece(combinedForm)
        .then(() => {
          commit(types.EDIT_PIECE_SUCCESS, {piece: combinedForm, id: combinedForm.music_id})
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
    console.log(collectionTemp)
    const json = JSON.stringify(collectionTemp);
    console.log(json);
    return new Promise((resolve, reject) => {
      commit(types.EDIT_COLLECTION_REQUEST)
      API.editCollection(collectionTemp)
        .then(() => {
          commit(types.EDIT_COLLECTION_SUCCESS, {collection: state.collectionForm, id: collectionTemp.col_id})
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
    return new Promise((resolve, reject) => {
      API.getPiece(piece[0])
      .then((res) => {
        var final = utils.parseJSONToPiece(res, state.separator, state.defaultSelections.items, state.collections, creadores, contribuidores, contribuidoresp)
        final.mei = utils.parseStringToFile(final.mei, 'MeiFile', )
        final.xml = utils.parseStringToFile(final.xml, 'XMLFile', 'text/xml')
        final.midi = utils.parseStringToFile(final.midi, 'MidiFile', 'audio/mid')
        commit(types.GET_PIECE_SUCCESS, final)
        resolve()
      })
      .catch((err) => {
        commit(types.GET_PIECE_FAILURE, err)
        reject()
      })
    })
  },

  getReviewPiece({state}, piece) {
    return new Promise((resolve, reject) => {
      API.getPiece(piece.music_id)
      .then((res) => {
        var final = utils.parseJSONToPiece(res, state.separator, state.defaultSelections.items, state.collections)
        final.mei = utils.parseStringToFile(final.mei, 'MeiFile', )
        final.xml = utils.parseStringToFile(final.xml, 'XMLFile', 'text/xml')
        final.midi = utils.parseStringToFile(final.midi, 'MidiFile', 'audio/mid')
        resolve(final)
      })
      .catch((err) => {
        reject(err)
      })
    })
  },


  getCollectionInfo({commit, state}, {collection, creadores, contribuidores}) {
    API.getCollection(collection[0])
    .then((res) => {
      var final = utils.parseJSONToCollection(res[0], state.separator, state.defaultSelections.items, creadores, contribuidores)
      commit(types.GET_COLLECTION_SUCCESS, final)
    })
    .catch((err) => {
      commit(types.GET_COLLECTION_FAILURE, err)
    })
  },

  getReviewCollection({state}, collection) {
    return new Promise((resolve, reject) => {
      API.getCollection(collection)
      .then((res) => {
        var final = utils.parseJSONToCollection(res[0], state.separator, state.defaultSelections.items)
        resolve(final)
      })
      .catch((err) => {
        reject(err)
      })
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
      commit(types.EDIT_USER_SUCCESS, user)
    })
    .catch((err) => {
      commit(types.EDIT_USER_FAILURE, err)
    })
  },

  async validatePiece({commit, state, getters}, piece) {
    var combinedForm = utils.parsePieceToJSON(piece, state.separator, state.defaultSelections.itemsIDs, getters.getItemId)
    combinedForm.xml = await utils.parseFileToString(piece.xml)
    combinedForm.mei = await utils.parseFileToString(piece.mei)
    combinedForm.midi = await utils.parseFileToBinaryString(piece.midi)
    combinedForm.user_id = state.user.userInfo.user_id
    combinedForm.review = true
    return new Promise((resolve, reject) => {
      commit(types.EDIT_PIECE_REQUEST)
      API.editPiece(combinedForm)
        .then(() => {
          commit(types.EDIT_PIECE_SUCCESS, {piece: piece, id: piece.music_id})
          resolve()
        })
        .catch((error) => {
          commit(types.EDIT_PIECE_FAILURE, error.msg)
          reject()
        })
    })
  },

  deletePiece({commit}, id) {
    API.removePiece(id)
    .then(() => {
      commit(types.REMOVE_PIECE_SUCCESS, id)
    })
    .catch((err) => {
      commit(types.REMOVE_PIECE_FAILURE, err)
    })
  },

  validateCollection({commit, state, getters}, collection) {
    var collectionTemp = utils.parseCollectionToJSON(collection, state.separator, state.defaultSelections.itemsIDs, getters.getItemId)
    return new Promise((resolve, reject) => {
      commit(types.EDIT_COLLECTION_REQUEST)
      API.editCollection(collectionTemp)
        .then(() => {
          commit(types.EDIT_COLLECTION_SUCCESS, {collection: collection, id: collectionTemp.col_id})
          resolve()
        })
        .catch((error) => {
          commit(types.EDIT_COLLECTION_FAILURE, error.msg)
          reject()
        })
    })
  },  

  deleteCollection({commit}, id) {
    API.removeCollection(id)
    .then(() => {
      commit(types.REMOVE_COLLECTION_SUCCESS, id)
    })
    .catch((err) => {
      commit(types.REMOVE_COLLECTION_FAILURE, err)
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
