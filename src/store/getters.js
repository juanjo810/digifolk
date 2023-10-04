/**
 * @module Getters
 * @description En este fichero se muestran los diferentes getters que se tienen del estado local del sistema.
 */
import utils from '@/utils/utils.js'

export default {
  getItemsByType: (state) => (typeId) => {
    return state.defaultSelections.items.filter(item => item.type_item === typeId)
  },
  getItemsNameByType: (state) => (typeId) => {
    const items = state.defaultSelections.items.filter(item => item.type_item === typeId)
    return items.map(item => item.name)
  },
  getMaxItemIdInType: (state) => (typeId) => {
    const cifras = Math.abs(typeId).toString().length
    const filteredItems = state.defaultSelections.items.filter(item => item.type_item === typeId)
    if (filteredItems.length === 0)
      return 0
    const maxId = filteredItems.reduce((max, item) => (item.id > max ? item.id : max), 0)
    return parseInt(maxId.toString().slice(cifras))
  },
  getItemId: (state) => (typeId, name) => {
    const filteredItems = state.defaultSelections.items.filter(item => item.type_item === typeId)
    const tmp = filteredItems.find(item => item.name === name)
    if (tmp)
      return tmp.id
    else
      return -1
  },
  getNamePieces: (state) => {
    return state.pieces.map(piece => {
      const title = piece.title.join('|')
      return {
        id: piece.music_id,
        title: title
      }
    })
  },
  getMei: (state) => {
    return utils.parseFileToString(state.pieceForm.mei[0])
  },
  getMidi: (state) => {
    return utils.parseFileToString(state.pieceForm.midi[0])
  },
  getNameCollections: (state) => {
    return state.collections.map(collection => {
      const title = collection.title.join('|')
      return {
        id: collection.col_id,
        title: title
      }
    })
  },
  getUserName: () => (user) => {
    return `${user.user_id}-${user.username}`
  },
  getReviewPieces: (state) => {
    return state.pieces.map(piece => {
      if (!piece.review) {
        const title = piece.title.join('|')
        return {
          id: piece.music_id,
          title: title
        }
      }
    })
  },
  getReviewCollections: (state) => {
    return state.collections.map(collection => {
      if (!collection.review) {
        const title = collection.title.join('|')
        return {
          id: collection.col_id,
          title: title
        }
      }
    })
  },
  getFivePosts: (state) => {
    var count = 0
    return state.images.filter((image) => {
      if (count < 5 && image.esPublico === true) {
        count++
        return true
      }
      return false
    }).sort(function (x, y) {
      return y.fecha.seconds - x.fecha.seconds
    })
  }
}
