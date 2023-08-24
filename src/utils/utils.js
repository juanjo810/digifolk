const utils = {
  parseFileToString(file) {
    return new Promise((resolve, reject) => {
      if (file) {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      } else {
        resolve('');
      }
    });
  },
  parseFileToBinaryString(file) {
    return new Promise((resolve, reject) => {
      if (file) {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsBinaryString(file);
      } else {
        resolve('');
      }
    });
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
    }));
    return pieceTemp
  }
}

export default utils;
