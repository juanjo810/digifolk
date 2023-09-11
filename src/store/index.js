/**
 * @module Store
 * 
 * @description En este fichero se realiza la definición de la Store del sistema
 */

import { createLogger, createStore } from 'vuex'

import state from './state'
import mutations from './mutations'
import actions from './actions'
import getters from './getters'
import createPersistedState from "vuex-plugin-persistedstate";

const debug = process.env.NODE_ENV !== 'production'

export default createStore({
  strict: debug,
  plugins: debug ? [createLogger(), createPersistedState()] : [createPersistedState()],
  state,
  getters,
  actions,
  mutations
})
