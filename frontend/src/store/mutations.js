import * as types from './mutations-types'

/**
 * @module Mutations
 * 
 * @description En este fichero se detalla cada una de las mutaciones que se producen del estado del sistema.
 */

export default {
  [types.LOGIN_USER_REQUEST](state) {
    state.fetchingUser = true
    state.error = ''
  },

  [types.LOGIN_USER_SUCCESS](state, { userInfo, token }) {
    state.fetchingUser = false
    state.user.tokenSession = token
    state.user.userInfo = userInfo
    state.error = ''
  },

  [types.LOGIN_USER_FAILURE](state, { error }) {
    state.fetchingUser = false
    state.error = error
  },

  [types.REGISTER_USER_REQUEST](state) {
    state.fetchingUser = true
    state.error = ''
  },

  [types.REGISTER_USER_SUCCESS](state) {
    state.fetchingUser = false
    state.error = ''
  },

  [types.REGISTER_USER_FAILURE](state, { error }) {
    state.fetchingUser = false
    state.error = error
  },

  [types.RESET_PASSWORD_REQUEST](state) {
    state.error = ''
    state.changingPass = true
  },

  [types.RESET_PASSWORD_SUCCESS](state) {
    state.error = ''
    state.changingPass = false
  },

  [types.RESET_PASSWORD_FAILURE](state, { error }) {
    state.error = error
    state.changingPass = false
  },

  [types.CHANGE_PASSWORD_SUCCESS](state) {
    state.error = ''
  },

  [types.CHANGE_PASSWORD_FAILURE](state, error) {
    state.error = error
  },

  [types.LOG_OUT_SUCCESS](state) {
    state.user.tokenSession = ''
    state.user.userInfo = null
  },

  [types.DELETE_ACCOUNT_REQUEST](state) {
    state.error = ''
  },

  [types.DELETE_ACCOUNT_FAILURE](state, { error }) {
    state.error = error
  },

  [types.DELETE_ACCOUNT_SUCCESS](state) {
    state.pieces = []
    state.collection = []
    state.user.tokenSession = ''
    state.user.userInfo = null
  },

  ['REMOVE_TOKEN_SESSION'](state) {
    state.user.tokenSession = ''
    state.user.userInfo = null
  },

  ['REFRESH_TOKEN_SESSION'](state, token) {
    state.user.tokenSession = token
  },

  [types.FETCH_IMAGES_REQUEST](state, start) {
    if (start === '')
      state.images = []
    state.error = ''
    state.fetchingImages = true
  },

  [types.FETCH_IMAGES_SUCCESS](state, images) {
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

  [types.FETCH_IMAGES_FAILURE](state, error) {
    state.error = error
    state.fetchingImages = false
  },

  [types.FETCH_COMMENTS_REQUEST](state, start) {
    state.error = ''
    if (start === '')
      state.comments = []
  },

  [types.FETCH_COMMENTS_SUCCESS](state, comments) {
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

  [types.FETCH_COMMENTS_FAILURE](state, { error }) {
    state.error = error
    state.fetchingImages = false
  },

  [types.GEN_SOUNDSCAPE_REQUEST](state) {
    state.generatingSoundscape = true
    state.soundscapeGenerated = false
    state.error = ''
  },

  [types.GEN_SOUNDSCAPE_SUCCESS](state, { url, id }) {
    state.generatingSoundscape = false
    state.error = ''
    state.soundscapeGenerated = true
    var element = state.images.find(image => image.id === id)
    element.esPublico = true
    element.soundscape = url
  },

  [types.GEN_SOUNDSCAPE_FAILURE](state, { error }) {
    state.generatingSoundscape = false
    state.error = error
  },

  [types.ADD_USER_CONTRIBUTOR](state) {
    state.pieceForm.contributor_role.push({ name: '', role: '' })
  },

  [types.ADD_SHEET_CONTRIBUTOR](state) {
    state.pieceForm.contributorp_role.push({ name: '', role: '' })
  },

  [types.ADD_COLLECTION_CONTRIBUTOR](state) {
    state.collectionForm.contributor_role.push({ name: '', role: '' })
  },

  [types.ADD_SHEET_CREATOR](state) {
    state.pieceForm.creatorp_role.push({ name: '', role: '', gender: '' })
  },

  [types.ADD_COLLECTION_CREATOR](state) {
    state.collectionForm.creator_role.push({ name: '', role: '' })
  },

  [types.REMOVE_USER_CONTRIBUTOR](state, index) {
    state.pieceForm.contributor_role.splice(index, 1)
  },

  [types.REMOVE_COLLECTION_CREATOR](state, index) {
    state.collectionForm.creator_role.splice(index, 1)
  },

  [types.REMOVE_SHEET_CONTRIBUTOR](state, index) {
    state.pieceForm.contributorp_role.splice(index, 1)
  },

  [types.REMOVE_COLLECTION_CONTRIBUTOR](state, index) {
    state.collectionForm.contributor_role.splice(index, 1)
  },

  [types.REMOVE_SHEET_CREATOR](state, index) {
    state.pieceForm.creatorp_role.splice(index, 1)
  },

  [types.SAVE_COLLECTION_DATE](state, date) {
    state.collectionForm.date = date
  },

  /**
   * UPDATE OF USER FORM FIELDS
   * 
   * Each following method update the corresponding field of the user form in the vuex state
   */

  ['UPDATE_USER_TITLE'](state, title) {
    state.pieceForm.title = title
  },

  ['UPDATE_USER_RIGHT'](state, right) {
    state.pieceForm.rights = right
  },

  ['UPDATE_USER_CREATOR'](state, creator) {
    state.pieceForm.creator = creator
  },

  [types.SAVE_USER_DATE](state, date) {
    state.pieceForm.date = date
  },

  ['UPDATE_USER_TYPE'](state, type) {
    state.pieceForm.type_file = type
  },

  ['UPDATE_USER_PUBLISHER'](state, publisher) {
    state.pieceForm.publisher = publisher
  },

  ['UPDATE_USER_CONTRIBUTOR'](state, contribuidores) {
    state.pieceForm.contributor_role = structuredClone(contribuidores)
  },

  ['UPDATE_USER_DESCRIPTION'](state, description) {
    state.pieceForm.desc = description
  },

  /**
   * UPDATE OF SHEET FORM FIELDS
   * 
   * Each following method update the corresponding field of the sheet form in the vuex state
   */

  ['UPDATE_SHEET_RIGHT'](state, right) {
    state.pieceForm.rightsp = right
  },

  ['UPDATE_SHEET_CREATOR'](state, creators) {
    state.pieceForm.creatorp_role = structuredClone(creators)
  },

  [types.SAVE_SHEET_DATE](state, date) {
    state.pieceForm.datep = date
  },

  ['UPDATE_SHEET_KEY'](state, key) {
    state.pieceForm.real_key = key
  },

  ['UPDATE_SHEET_METRE'](state, metre) {
    state.pieceForm.meter = metre
  },

  ['UPDATE_SHEET_TEMPO'](state, tempo) {
    state.pieceForm.tempo = tempo
  },

  ['UPDATE_SHEET_INSTRUMENT'](state, instrument) {
    state.pieceForm.instruments = instrument
  },

  ['UPDATE_SHEET_GENRE'](state, genre) {
    state.pieceForm.genre = genre
  },

  ['UPDATE_SHEET_CONTRIBUTOR'](state, contributors) {
    state.pieceForm.contributorp_role = structuredClone(contributors)
  },

  ['UPDATE_SHEET_ALTTITLE'](state, altTitle) {
    state.pieceForm.alt_title = altTitle
  },

  ['UPDATE_SHEET_MODE'](state, mode) {
    state.pieceForm.mode = mode
  },

  ['UPDATE_SHEET_DESCRIPTION'](state, description) {
    state.pieceForm.descp = description
  },

  ['UPDATE_SHEET_TYPE'](state, type) {
    state.pieceForm.type_piece = type
  },

  ['UPDATE_SHEET_FORMAT'](state, format) {
    state.pieceForm.formattingp = format
  },

  ['UPDATE_SHEET_SUBJECT'](state, subject) {
    state.pieceForm.subject = subject
  },

  ['UPDATE_SHEET_LANGUAGE'](state, language) {
    state.pieceForm.language = language
  },

  ['UPDATE_SHEET_RELATION'](state, relation) {
    state.pieceForm.relationp = relation
  },

  ['UPDATE_SHEET_HASVERSION'](state, hasVersion) {
    state.pieceForm.hasVersion = hasVersion
  },

  ['UPDATE_SHEET_ISVERSIONOF'](state, isVersionOf) {
    state.pieceForm.isVersionOf = isVersionOf
  },

  ['UPDATE_SHEET_COVERAGE'](state, coverage) {
    state.pieceForm.coverage = coverage
  },

  ['UPDATE_SHEET_SPATIALCOUNTRY'](state, country) {
    state.pieceForm.spatial.country = country
  },

  ['UPDATE_SHEET_SPATIALSTATE'](state, state2) {
    state.pieceForm.spatial.state = state2
  },

  ['UPDATE_SHEET_SPATIALLOCATION'](state, location) {
    state.pieceForm.spatial.location = location
  },

  ['UPDATE_SHEET_TEMPORALCENTURY'](state, century) {
    state.pieceForm.temporal.century = century
  },

  ['UPDATE_SHEET_TEMPORALDECADE'](state, decade) {
    state.pieceForm.temporal.decade = decade
  },

  ['UPDATE_SHEET_TEMPORALYEAR'](state, year) {
    state.pieceForm.temporal.year = year
  },

  ['UPDATE_SHEET_XML'](state, xml) {
    state.pieceForm.xml = xml
  },

  ['UPDATE_SHEET_MEI'](state, mei) {
    state.pieceForm.mei = mei
  },

  ['UPDATE_SHEET_MIDI'](state, midi) {
    state.pieceForm.midi = midi
  },

  ['UPDATE_SHEET_AUDIO'](state, audio) {
    state.pieceForm.audio = audio
  },

  ['UPDATE_SHEET_VIDEO'](state, video) {
    state.pieceForm.video = video
  },

  ['UPDATE_SHEET_COLID'](state, col_id) {
    state.pieceForm.col_id = col_id
  },

  /**
   * UPDATE OF COLLECTION FORM FIELDS
   * 
   * Each following method update the corresponding field of the collection form in the vuex state
   */

  ['UPDATE_COLLECTION_TITLE'](state, title) {
    state.collectionForm.title = title
  },

  ['UPDATE_COLLECTION_RIGHT'](state, right) {
    state.collectionForm.rights = right
  },

  ['UPDATE_COLLECTION_CREATOR'](state, creators) {
    state.collectionForm.creator_role = structuredClone(creators)
  },

  [types.SAVE_COLLECTION_DATE](state, date) {
    state.collectionForm.date = date
  },

  ['UPDATE_COLLECTION_CONTRIBUTOR'](state, contributors) {
    state.collectionForm.contributor_role = structuredClone(contributors)
  },

  ['UPDATE_COLLECTION_EXTENT'](state, extent) {
    state.collectionForm.extent = extent
  },

  ['UPDATE_COLLECTION_DESCRIPTION'](state, description) {
    state.collectionForm.description = description
  },

  ['UPDATE_COLLECTION_TYPE'](state, type) {
    state.collectionForm.source_type = type
  },

  ['UPDATE_COLLECTION_FORMAT'](state, formatting) {
    state.collectionForm.formatting = formatting
  },

  ['UPDATE_COLLECTION_SUBJECT'](state, subject) {
    state.collectionForm.subject = subject
  },

  ['UPDATE_COLLECTION_LANGUAGE'](state, language) {
    state.collectionForm.language = language
  },

  ['UPDATE_COLLECTION_RELATION'](state, relation) {
    state.collectionForm.relation = relation
  },

  ['UPDATE_COLLECTION_PUBLISHER'](state, publisher) {
    state.collectionForm.publisher = publisher
  },

  ['UPDATE_COLLECTION_COVERAGE'](state, coverage) {
    state.collectionForm.coverage = coverage
  },

  ['UPDATE_COLLECTION_SPATIALCOUNTRY'](state, country) {
    state.collectionForm.spatial.country = country
  },

  ['UPDATE_COLLECTION_SPATIALSTATE'](state, state2) {
    state.collectionForm.spatial.state = state2
  },

  ['UPDATE_COLLECTION_SPATIALLOCATION'](state, location) {
    state.collectionForm.spatial.location = location
  },

  ['UPDATE_COLLECTION_TEMPORALCENTURY'](state, century) {
    state.collectionForm.temporal.century = century
  },

  ['UPDATE_COLLECTION_TEMPORALDECADE'](state, decade) {
    state.collectionForm.temporal.decade = decade
  },

  ['UPDATE_COLLECTION_TEMPORALYEAR'](state, year) {
    state.collectionForm.temporal.year = year
  },

  ['UPDATE_COLLECTION_SOURCE'](state, source) {
    state.collectionForm.source = source
  },

  ['UPDATE_COLLECTION_rights_holder'](state, rights_holder) {
    state.collectionForm.rights_holder = rights_holder
  },


  ['RESET_ERROR'](state, error) {
    state.error = error
  },

  ['SET_OBJECTFROMLIST'](state, object) {
    state.objectFromList = object
  },

  /**
   * Uploading data mutations: piece and collections
   */

  [types.UPLOAD_COLLECTION_REQUEST](state) {
    state.fetchingCollection = true
  },

  [types.UPLOAD_COLLECTION_SUCCESS](state) {
    state.fetchingCollection = false
  },

  [types.UPLOAD_COLLECTION_FAILURE](state, error) {
    state.fetchingCollection = false
    state.error = error
  },

  [types.EDIT_COLLECTION_REQUEST](state) {
    state.fetchingCollection = true
  },

  [types.EDIT_COLLECTION_SUCCESS](state, { collection, id }) {
    const indexToDelete = state.collections.findIndex(item => item.col_id === id);
    state.collections.splice(indexToDelete, 1);
    const newCol = {
      col_id: id,
      title: collection.title.split('|'),
    }
    state.collections.push(newCol)
    state.fetchingCollection = false
  },

  [types.EDIT_COLLECTION_FAILURE](state, error) {
    state.fetchingCollection = false
    state.error = error
  },

  [types.REMOVE_COLLECTION_REQUEST](state) {
    state.fetchingCollection = true
  },

  [types.REMOVE_COLLECTION_SUCCESS](state, id) {
    const indexToDelete = state.collections.findIndex(item => item.col_id === id);
    state.collections.splice(indexToDelete, 1);
    state.fetchingCollection = false
  },

  [types.REMOVE_COLLECTION_FAILURE](state, error) {
    state.fetchingCollection = false
    state.error = error
  },

  [types.UPLOAD_PIECE_REQUEST](state) {
    state.fetchingPiece = true
  },

  [types.UPLOAD_PIECE_SUCCESS](state) {
    state.fetchingPiece = false
  },

  [types.UPLOAD_PIECE_FAILURE](state, error) {
    state.fetchingPiece = false
    state.error = error
  },

  [types.EDIT_PIECE_REQUEST](state) {
    state.fetchingPiece = true
  },

  [types.EDIT_PIECE_SUCCESS](state, { piece, id }) {
    const indexToDelete = state.pieces.findIndex(item => item.music_id === id);
    state.pieces.splice(indexToDelete, 1);
    const newPiece = {
      music_id: id,
      title: piece.title,
      review: piece.review,
    }
    state.pieces.push(newPiece)
    state.fetchingPiece = false
  },

  [types.EDIT_PIECE_FAILURE](state, error) {
    state.fetchingPiece = false
    state.error = error
  },

  [types.REMOVE_PIECE_REQUEST](state) {
    state.fetchingPiece = true
  },

  [types.REMOVE_PIECE_SUCCESS](state, id) {
    const indexToDelete = state.pieces.findIndex(item => item.music_id === id);
    state.pieces.splice(indexToDelete, 1);
    state.fetchingPiece = false
  },

  [types.REMOVE_PIECE_FAILURE](state, error) {
    state.fetchingPiece = false
    state.error = error
  },

  /**
   * ADD AND REMOVE ITEMS MUTATIONS
   */

  [types.ADD_NEW_ITEM_SUCCESS](state, item) {
    state.defaultSelections.items.push(item)
  },

  [types.ADD_NEW_ITEM_FAILURE](state, error) {
    state.error = error
  },

  [types.REMOVE_ITEM_SUCCESS](state, item) {
    state.defaultSelections.items = state.defaultSelections.items.filter(it => it !== item);
  },

  [types.REMOVE_ITEM_FAILURE](state, error) {
    state.error = error
  },

  [types.EDIT_ITEM_SUCCESS](state, { id, id_type, newName }) {
    const editedItemIndex = state.defaultSelections.items.findIndex(
      (item) =>
        item.id === id && item.type_item === id_type
    )
    state.defaultSelections.items[editedItemIndex].name = newName
  },

  [types.EDIT_ITEM_FAILURE](state, error) {
    state.error = error
  },

  [types.FETCH_ITEMS](state, items) {
    state.defaultSelections.items = items
  },

  [types.FETCH_COLLECTIONS](state, colls) {
    state.collections = colls
  },

  [types.FETCH_PIECES](state, pieces) {
    state.pieces = pieces
  },

  [types.FETCH_USERS](state, users) {
    state.users = users.users
  },

  [types.GET_PIECE_SUCCESS](state, piece) {
    state.pieceForm = piece
  },

  [types.GET_PIECE_FAILURE](state, err) {
    state.error = err
  },

  [types.GET_COLLECTION_SUCCESS](state, collection) {
    state.collectionForm = collection
  },

  [types.GET_COLLECTION_FAILURE](state, err) {
    state.error = err
  },

  [types.GET_PIECES_COLLECTION_SUCCESS](state, pieces) {
    state.collectionForm.pieces = pieces
  },

  [types.GET_PIECES_COLLECTION_FAILURE](state, err) {
    state.error = err
  },

  [types.RESET_PIECE_FORM](state) {
    state.pieceForm = {
      title: '',
      rights: '',
      creator: '',
      date: null,
      type_file: '',
      publisher: '',
      contributor_role: [],
      desc: '',
      rightsp: '', //rightsp
      creatorp_role: [],
      datep: null, // datep
      real_key: '', // real_key
      meter: '', // meter
      tempo: '',
      instruments: [], // instruments
      genre: [],
      contributorp_role: [], // contributorp_role
      alt_title: '', // alt_title
      mode: '',
      descp: '', // descp
      type_piece: '', // type_piece
      formattingp: '', // formattingp
      subject: '',
      language: '',
      relationp: '', // relationp
      hasVersion: '',
      isVersionOf: '',
      coverage: '',
      spatial: {
        country: '',
        state: '',
        location: ''
      },
      temporal: {
        century: '',
        decade: '',
        year: ''
      },
      // Estos se mandan como un flujo de bytes
      xml: '',
      mei: '',
      midi: '',
      // Estos se mandan como URL a youtube, drive, ...
      audio: '',
      video: '',
      user_id: '',
      col_id: '' // ID de la colección. Por tanto, primero tiene que crear la colección y después meter los otros formularios.
    }
  },

  [types.RESET_COLLECTION_FORM](state) {
    state.collectionForm = {
      title: '',
      rights: '', // rights
      date: null,
      creator_role: [],
      contributor_role: [], // contributor_role
      source_type: '', // source_type
      source: '',
      description: '',
      formatting: '', // formatting
      extent: '',
      publisher: '',
      subject: '',
      language: '',
      relation: '',
      coverage: '',
      spatial: {
        country: '',
        state: '',
        location: ''
      },
      temporal: {
        century: '',
        decade: '',
        year: ''
      },
      rights_holder: '',
      piece_col: []
    }
  },

  [types.ADVANCED_SEARCH_FAILURE](state, error) {
    state.error = error
  },

  [types.IMPORT_DATA_SUCCESS](state, res) {
    state.pieceForm = res
  },

  [types.IMPORT_DATA_FAILURE](state, error) {
    state.error = error
  },

  [types.EDIT_USER_SUCCESS](state, user) {
    var userIndex = state.users.findIndex(u => u.user_id === user.user_id)
    state.users.splice(userIndex, 1)
    state.users.push(user)
  },

  [types.EDIT_USER_FAILURE](state, error) {
    state.error = error
  }

}
