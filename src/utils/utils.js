import API from '@/api'

const utils = {
  parseFileToString(file) {
    return new Promise((resolve) => {
      if (file && file !== '') {
        const reader = new FileReader();
        reader.onload = () => { resolve(reader.result) }
        reader.onerror = () => { resolve('') }
        reader.readAsText(file);
      } else {
        resolve('');
      }
    })
  },
  parseFileToBase64(file) {
    debugger
    return new Promise((resolve) => {
      if (file && file !== '') {
        const reader = new FileReader();
        reader.onload = () => { 
          debugger
          const base64 = btoa(reader.result)
          resolve(base64)
        }
        reader.onerror = () => { resolve('') }
        reader.readAsBinaryString(file);
      } else {
        resolve('')
      }
    })
  },
  parseStringToFile(stringContent, fileName, mimeType) {
    if (stringContent && stringContent !== '') {
      const blob = new Blob([stringContent], { type: mimeType });
      const file = new File([blob], fileName, { type: mimeType });
      return [file]
    } else {
      return ""
    }
  },
  parseBase64ToFile(base64, fileName, mimeType) {
    if (base64 && base64 !== '') {
      const stringContent = atob(base64)
      const blob = new Blob([stringContent], { type: mimeType });
      const file = new File([blob], fileName, { type: mimeType });
      return [file]
    } else {
      return ""
    }
  },
  parseCollectionToJSON(fields, separator, itemsIDs, getItemId) {
    var collectionTemp = structuredClone(fields)
    collectionTemp.relation = fields.relation.split(separator)
    collectionTemp.subject = fields.subject.split(separator)
    collectionTemp.title = fields.title.split(separator)
    var type = itemsIDs["Rights"]
    collectionTemp.rights = getItemId(type, fields.rights)
    type = itemsIDs["Types"]
    collectionTemp.source_type = getItemId(type, fields.source_type)
    type = itemsIDs["Contributor Sources Roles"]
    collectionTemp.contributor_role = collectionTemp.contributor_role.map(contributor => ({
      name: contributor.name,
      role: getItemId(type, contributor.role)
    }));
    type = itemsIDs["Creator Sources Roles"]
    collectionTemp.creator_role = collectionTemp.creator_role.map(creator => ({
      name: creator.name,
      role: getItemId(type, creator.role)
    }));
    collectionTemp.code = collectionTemp.code ? collectionTemp.code : collectionTemp.col_id
    return collectionTemp
  },
  parsePieceToJSON(fields, separator, itemsIDs, getItemId) {
    const pieceTemp = structuredClone(fields)
    pieceTemp.title = pieceTemp.title.split(separator)
    pieceTemp.subject = pieceTemp.subject.split(separator)
    pieceTemp.relationp = pieceTemp.relationp.split(separator)
    pieceTemp.hasVersion = pieceTemp.hasVersion.split(separator)
    pieceTemp.isVersionOf = pieceTemp.isVersionOf.split(separator)
    var type = itemsIDs["Rights"]
    pieceTemp.rights = getItemId(type, fields.rights)
    type = itemsIDs["Types"]
    pieceTemp.type_file = getItemId(type, fields.type_file)
    type = itemsIDs["Rights"]
    pieceTemp.rightsp = getItemId(type, fields.rightsp)
    type = itemsIDs["Types"]
    pieceTemp.type_piece = getItemId(type, fields.type_piece)
    type = itemsIDs["Mode"]
    pieceTemp.mode = getItemId(type, fields.mode)
    type = itemsIDs["XML Contributor Roles"]
    pieceTemp.contributor_role = pieceTemp.contributor_role.map(contributor => ({
      name: contributor.name,
      role: getItemId(type, contributor.role)
    }));
    type = itemsIDs["Creator Pieces Roles"]
    pieceTemp.creatorp_role = pieceTemp.creatorp_role.map(creator => ({
      name: creator.name,
      role: getItemId(type, creator.role)
    }));
    type = itemsIDs["Contributor Pieces Roles"]
    pieceTemp.contributorp_role = pieceTemp.contributorp_role.map(contributor => ({
      name: contributor.name,
      role: getItemId(type, contributor.role)
    }))
    if (pieceTemp.col_id) {
      const temp = pieceTemp.col_id.split('-')
      pieceTemp.col_id = temp ? parseInt(temp[0]) : null
    } else {
      pieceTemp.col_id = null
    }
    return pieceTemp
  },

  parseJSONToPiece(fields, separator, itemsIDs, collections, creadores, contribuidores, contribuidoresp) {
    var final = structuredClone(fields)
    final.title = final.title.join(separator)
    var temp = itemsIDs.find(i => i.id === parseInt(final.rights))
    if (temp)
      final.rights = temp.name
    else
      final.rights = ''
    temp = itemsIDs.find(i => i.id === parseInt(final.type_file))
    if (temp)
      final.type_file = temp.name
    else
      final.type_file = ''
    final.contributor_role = final.contributor_role.map((c) => {
      var item = itemsIDs.find(i => i.id === parseInt(c.role))
      const temp = {
        name: c.name,
        role: item ? item.name : ''
      }
      if (contribuidores) contribuidores.push(structuredClone(temp))
      return temp
    })
    temp = itemsIDs.find(i => i.id === parseInt(final.rightsp)).name
    if (temp)
      final.rightsp = temp
    else
      final.rightsp = ''
    final.creatorp_role = final.creatorp_role.map((c) => {
      var item = itemsIDs.find(i => i.id === parseInt(c.role))
      const temp = {
        name: c.name,
        role: item ? item.name : ''
      }
      if (creadores) creadores.push(structuredClone(temp))
      return temp
    })
    final.contributorp_role = final.contributorp_role.map((c) => {
      var item = itemsIDs.find(i => i.id === parseInt(c.role))
      const temp = {
        name: c.name,
        role: item ? item.name : ''
      }
      if (contribuidoresp) contribuidoresp.push(structuredClone(temp))
      return temp
    })
    final.subject = final.subject.join(separator)
    final.relationp = final.relationp.join(separator)
    final.hasVersion = final.hasVersion.join(separator)
    final.isVersionOf = final.isVersionOf.join(separator)
    if (!final.spatial) {
      final.spatial = {
        country: '',
        state: '',
        location: ''
      }
    }
    if (!final.temporal) {
      final.temporal = {
        century: '',
        year: '',
        decade: ''
      }
    }
    temp = itemsIDs.find(i => i.id === parseInt(final.mode))
    if (temp)
      final.mode = temp
    else
      final.mode = ''
    temp = collections.find(c => c.col_id === parseInt(final.col_id))
    if (temp)
      final.col_id = `${temp.col_id}-${temp.title}`
    else
      final.col_id = ''
    return final
  },

  parseJSONToCollection(fields, separator, itemsIDs, creadores, contribuidores) {
    debugger
    var final = structuredClone(fields)
    final.title = final ? final.title.join(separator) : ''
    var item = itemsIDs.find(i => i.id === parseInt(final.rights))
    final.rights = item ? item.name : ''
    item = itemsIDs.find(i => i.id === parseInt(final.source_type))
    final.source_type = item ? item.name : ''
    final.creator_role = final.creator_role.map((c) => {
      var item = itemsIDs.find(i => i.id === parseInt(c.role))
      const temp = {
        name: c.name,
        role: item ? item.name : ''
      }
      if (creadores) creadores.push(structuredClone(temp))
      return temp
    })
    final.contributor_role = final.contributor_role.map((c) => {
      var item = itemsIDs.find(i => i.id === parseInt(c.role))
      const temp = {
        name: c.name,
        role: item ? item.name : ''
      }
      if (contribuidores) contribuidores.push(structuredClone(temp))
      return temp
    })
    final.subject = final.subject.join(separator)
    final.relation = final.relation.join(separator)
    return final
  },

  authenticated(token) {
    return new Promise((resolve) => {
      API.isAutenticated(token)
        .then((res) => {
          resolve(res)
        })
        .catch(() => {
          resolve(false)
        })
    })
  }
}

export default utils;
