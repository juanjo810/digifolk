/**
 * @module Getters
 * @description En este fichero se muestran los diferentes getters que se tienen del estado local del sistema.
 */
export default{
    getItemsByType: (state) => (typeId) => {
      return state.defaultSelections.items.filter(item => item.type_item === typeId)
    },
    getItemsNameByType: (state) => (typeId) => {
      const items = state.defaultSelections.items.filter(item => item.type_item === typeId)
      return items.map(item => item.name)
    },
    getMaxItemIdInType: (state) => (typeId) => {
      const filteredItems = state.defaultSelections.items.filter(item => item.type_item === typeId);
      const maxId = filteredItems.reduce((max, item) => (item.id > max ? item.id : max), 0);
      return maxId;
    },
    getImageById: (state) => (id) => { return state.images.find(image => image.id === id) },
    getImagesByUser: (state) => (email) => {
      return state.images.filter(image => image.owner[0] === email)
    },
    getUser: (state) => { return state.user },
    getPosts: (state) => {
      return state.images.filter(image => image.esPublico === true)
    },
    getPostsFollowing: (state) => {
      return state.images.filter(image => state.user.data.siguiendo.includes(image.owner[0]) && image.esPublico)
    },
    getPostsNotFollowing: (state) => {
      return state.images.filter(image => !state.user.data.siguiendo.includes(image.owner[0]) && image.esPublico)
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
    },
    getReports: (state) => {
      return state.images.filter(image => image.esReportada === true)
    },
    getPostsByUser: (state) => (id) => {
      return state.images.filter(image => image.esPublico === true && image.owner[4] === id)
    }
}
