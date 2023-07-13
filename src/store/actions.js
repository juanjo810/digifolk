/**
 * @module Actions
 * @description Este fichero muestra las diferentes acciones que realiza el sistema para proporcionar su funcionalidad.
 * En todas las funciones se utiliza el objeto contexto recibido automáticamente como primer parámetro. En concreto se utiliza
 * la propiedad commit para realizar las mutaciones del sistema.
 */

import * as types from './mutations-types'
import API from '@/api'
import { format } from 'date-fns';

export default{
  
  loginUser ({ commit }, { user, password }) {
      return new Promise((resolve, reject)=>{
        commit(types.LOGIN_USER_REQUEST)
        API.logIn(user, password)
          .then((res)=>{
            commit(types.LOGIN_USER_SUCCESS, res)
            resolve()
          })
          .catch((err) => {
            console.log(err)
            commit(types.LOGIN_USER_FAILURE, { error: 'Usuario o contraseña incorrectos'})
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

  saveDataCollection ({state, commit}) {
    var collectionTemp = structuredClone(state.collectionForm)
    collectionTemp.relation = state.collectionForm.relation.split(state.separator)
    collectionTemp.subject = state.collectionForm.subject.split(state.separator)
    collectionTemp.title = state.collectionForm.title.split(state.separator)
    collectionTemp.rights = state.defaultSelections.rightsMapping[state.collectionForm.rights]
    collectionTemp.source_type = state.defaultSelections.typesMapping[state.collectionForm.source_type]
    collectionTemp.contributor_role = collectionTemp.contributor_role.map(contributor => ({
      name: contributor.name,
      role: state.defaultSelections.cont_rolessMapping[contributor.role]
    }));
    collectionTemp.creator_role = collectionTemp.creator_role.map(creator => ({
      name: creator.name,
      role: state.defaultSelections.creator_rolessMapping[creator.role]
    }));
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

  saveDataPiece ({state, commit}) {
    var userTemp = structuredClone(state.userForm)
    var sheetTemp = structuredClone(state.sheetForm)
    const combinedForm = {
      ...userTemp,
      ...sheetTemp
    };
    
    combinedForm.title = userTemp.title.split(state.separator)
    combinedForm.subject = sheetTemp.subject.split(state.separator)
    combinedForm.relationp = sheetTemp.relationp.split(state.separator)
    combinedForm.hasVersion = sheetTemp.hasVersion.split(state.separator)
    combinedForm.isVersionOf = sheetTemp.isVersionOf.split(state.separator)
    combinedForm.rights = state.defaultSelections.rightsMapping[state.userForm.rights]
    combinedForm.type_file = state.defaultSelections.typesMapping[state.userForm.type_file]
    combinedForm.rightsp = state.defaultSelections.rightsMapping[state.sheetForm.rightsp]
    combinedForm.type_piece = state.defaultSelections.typesMapping[state.sheetForm.type_piece]
    combinedForm.contributor_role = combinedForm.contributor_role.map(contributor => ({
      name: contributor.name,
      role: state.defaultSelections.cont_rolesXMLMapping[contributor.role]
    }));
    combinedForm.creatorp_role = combinedForm.creatorp_role.map(creator => ({
      name: creator.name,
      role: state.defaultSelections.creator_rolespMapping[creator.role]
    }));
    combinedForm.contributorp_role = combinedForm.contributorp_role.map(contributor => ({
      name: contributor.name,
      role: state.defaultSelections.cont_rolespMapping[contributor.role]
    }));
    const json = JSON.stringify(combinedForm);
    console.log(json);
    return new Promise((resolve, reject) => {
      commit(types.UPLOAD_PIECE_REQUEST)
      API.uploadCollection(json)
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
    var formattedDate = format(date[0], 'd MMMM yyyy')
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
  }

  
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
