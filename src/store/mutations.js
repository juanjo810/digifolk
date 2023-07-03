import * as types from './mutations-types'

/**
 * @module Mutations
 * 
 * @description En este fichero se detalla cada una de las mutaciones que se producen del estado del sistema.
 */

export default{
  [types.LOGIN_USER_REQUEST] (state) {
    state.fetchingUser = true
    state.error = ''
  },

  [types.LOGIN_USER_SUCCESS] (state) {
    state.fetchingUser = false
    state.error = ''
  },

  [types.LOGIN_USER_FAILURE] (state, { error }) {
    state.fetchingUser = false
    state.error = error
  },

  [types.REPORT_POST_SUCCESS] (state, {id, report}) {
    state.images.find(image => {
      if (image.id === id) {
        image.reporte = report
        image.esReportado = true
      }
    })
  },

  [types.REPORT_POST_FAILURE] (state, error) {
    state.error = error
  },

  [types.DECLINE_REPORT_SUCCESS] (state, id) {
    state.images.find(image => {
      if (image.id === id) {
        image.reporte = []
        image.esReportado = false
      }
    })
  },

  [types.DECLINE_REPORT_FAILURE] (state, error) {
    state.error = error
  },

  [types.GIVE_LIKE_SUCCESS] (state, {id, likes}) {
    state.images.find(image => {
      if (image.id === id) {
        image.likes = likes
        image.numLikes++
      }
    })
  },

  [types.GIVE_LIKE_FAILURE] (state, error) {
    state.error = error
  },

  [types.REMOVE_LIKE_SUCCESS] (state, {id, likes}) {
    state.images.find(image => {
      if (image.id === id) {
        image.likes = likes
        image.numLikes--
      }
    })
  },

  [types.REMOVE_LIKE_FAILURE] (state, error) {
    state.error = error
  },

  [types.REMOVE_SOUND_SUCCESS] (state, id) {
    state.images.find(image => {
      if (image.id === id) {
        image.esPublico = false
        image.soundscape = ''
      }
    })
  },

  [types.REMOVE_SOUND_FAILURE] (state, error) {
    state.error = error
  },

  [types.REMOVE_COMMENT_SUCCESS] (state, id) {
    state.comments = state.comments.filter(comment => comment.id !== id)
  },

  [types.REMOVE_COMMENT_FAILURE] (state, error) {
    state.error = error
  },

  [types.CONFIRM_REPORT_SUCCESS] (state, id) {
    state.images = state.images.filter(image => image.id !== id)
  },

  [types.CONFIRM_REPORT_FAILURE] (state, error) {
    state.error = error
  },

  [types.FOLLOW_USER_SUCCESS] (state, email) {
    state.user.data.siguiendo.push(email)
    // Vue.set(state.user.data.siguiendo, state.data.siguiendo.lenght - 1, email)
  },

  [types.FOLLOW_USER_FAILURE] (state, error) {
    state.error = error
  },

  [types.STOP_FOLLOW_SUCCESS] (state, email) {
    state.user.data.siguiendo = state.user.data.siguiendo.filter(user => user !== email)
  },

  [types.STOP_FOLLOW_FAILURE] (state, error) {
    state.error = error
  },

  [types.EDIT_DESCRIPTION_SUCCESS] (state, {id, descripcion}) {
    state.images.find(image => {
      if (image.id === id) {
        image.descripcion = descripcion
      }
    })
  },

  [types.EDIT_DESCRIPTION_FAILURE] (state, error) {
    state.error = error
  },

  [types.REGISTER_USER_REQUEST] (state) {
    state.fetchingUser = true
    state.error = ''
  },

  [types.REGISTER_USER_SUCCESS] (state) {
    state.fetchingUser = false
    state.error = ''
  },

  [types.REGISTER_USER_FAILURE] (state, { error }) {
    state.fetchingUser = false
    state.error = error
  },

  [types.RESET_PASSWORD_REQUEST] (state) {
    state.error = ''
    state.changingPass = true
  },

  [types.RESET_PASSWORD_SUCCESS] (state) {
    state.error = ''
    state.changingPass = false
  },

  [types.RESET_PASSWORD_FAILURE] (state, { error }) {
    state.error = error
    state.changingPass = false
  },

  [types.CHANGE_PASSWORD_SUCCESS] (state) {
    state.changingPass = false
    state.error = ''
  },

  [types.CHANGE_PASSWORD_FAILURE] (state, { error }) {
    state.changingPass = false
    state.error = error
  },

  [types.CHANGE_INFO_SUCCESS] (state, {user, descripcion}) {
    state.changingPass = false
    state.user.data.email = user.email
    state.user.data.displayName = user.displayName
    state.user.data.photoURL = user.photoURL
    state.user.data.descripcion = descripcion
    state.error = ''
  },

  [types.CHANGE_INFO_FAILURE] (state, { error }) {
    state.changingPass = false
    state.error = error
  },

  [types.LOG_OUT_FAILURE] (state, {error}) {
    state.error = error
  },

  [types.LOG_OUT_SUCCESS] (state) {
    state.user.loggedIn = false
    state.user.data = null
    state.images = []
  },

  [types.DELETE_ACCOUNT_REQUEST] (state) {
    state.error = ''
    state.deletingAccount = true
  },

  [types.DELETE_ACCOUNT_FAILURE] (state, {error}) {
    state.error = error
    state.deletingAccount = false
  },

  [types.DELETE_ACCOUNT_SUCCESS] (state) {
    state.user.loggedIn = false
    state.user.data = null
    state.images = []
    state.deletingAccount = false
  },

  [types.FETCH_IMAGES_REQUEST] (state, start) {
    if (start === '')
      state.images = []
    state.error = ''
    state.fetchingImages = true
  },

  [types.FETCH_IMAGES_SUCCESS] (state, images) {
    state.fetchingImages = false
    state.error = ''
    if (images.length) {
      if (!state.images.length) {
        state.images = images
      } else {
        state.images.push(...images)
      }
      if (images.length < 20) {
        state.noImages = false  
      } else {
        state.noImages = true
      }
    } else {
      state.noImages = false
    }
  },

  [types.FETCH_IMAGES_FAILURE] (state, error) {
    state.error = error
    state.fetchingImages = false
  },

  [types.FETCH_COMMENTS_REQUEST] (state, start) {
    state.error = ''
    if (start === '')
      state.comments = []
  },

  [types.FETCH_COMMENTS_SUCCESS] (state, comments) {
    state.fetchingImages = false
    state.error = ''
    if (comments.length) {
      if (!state.comments.length) {
        state.comments = comments
      } else {
        state.comments.push(...comments)
      }
      if (comments.length < 10) {
        state.noComments = false  
      } else {
        state.noComments = true
      }
    } else {
      state.noComments = false
    }
  },

  [types.FETCH_COMMENTS_FAILURE] (state, { error }) {
    state.error = error
    state.fetchingImages = false
  },

  [types.ADD_PHOTO_SUCCESS] (state, img) {
    var temp = [img, ...state.images]
    state.images = temp
  },

  [types.ADD_PHOTO_FAILURE] (state, error) {
    state.error = error
  },

  [types.ADD_COMMENT_SUCCESS] (state, com) {
    com = {
      autor: [state.user.data.email, state.user.data.displayName, state.user.data.photoURL, state.user.data.descripcion],
      ...com
    }
    state.comments.push(com)
    // Vue.set(state.comments, state.comments.lenght - 1, com)
  },

  [types.REMOVE_POST_SUCCESS] (state, id) {
    state.fetchingImages = false
    state.error = ''
    var element = state.images.find(image => image.id === id)
    var index = state.images.indexOf(element)
    state.images.splice(index, 1)
  },

  [types.REMOVE_POST_FAILURE] (state, error) {
    state.error = error
  },

  [types.GEN_SOUNDSCAPE_REQUEST] (state) {
    state.generatingSoundscape = true
    state.soundscapeGenerated = false
    state.error = ''
  },

  [types.GEN_SOUNDSCAPE_SUCCESS] (state, {url, id}) {
    state.generatingSoundscape = false
    state.error = ''
    state.soundscapeGenerated = true
    var element = state.images.find(image => image.id === id)
    element.esPublico = true
    element.soundscape = url
  },

  [types.GEN_SOUNDSCAPE_FAILURE] (state, {error}) {
    state.generatingSoundscape = false
    state.error = error
  },

  [types.GET_OTHERUSER_SUCCESS] (state, user) {
    state.otherUser = user
  },

  [types.GET_OTHERUSER_FAILURE] (state, error) {
    state.error = error
  },

  [types.ADD_USER_CONTRIBUTOR] (state) {
    state.userForm.contributor.push({name: '', role: ''})
  },

  ['UPDATE_USER_ID'] (state, id) {
    state.userForm.identifier = id
  },

  ['UPDATE_USER_TITLE'] (state, title) {
    state.userForm.title = title
  },

  ['UPDATE_USER_RIGHT'] (state, right) {
    state.userForm.right = right
  },

  ['UPDATE_USER_CREATOR'] (state, creator) {
    state.userForm.creator = creator
  },

  ['UPDATE_USER_DATE'] (state, date) {
    state.userForm.date = date
  },

  ['UPDATE_USER_TYPE'] (state, type) {
    state.userForm.type = type
  },

  ['UPDATE_USER_PUBLISHER'] (state, publisher) {
    state.userForm.publisher = publisher
  },

  ['UPDATE_USER_CONTRIBUTOR'] (state, {value, index}) {
    if (index < state.userForm.contributor.length)
      state.userForm.contributor[index].name = value
  },

  ['UPDATE_USER_DESCRIPTION'] (state, description) {
    state.userForm.description = description
  }
}
