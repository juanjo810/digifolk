export default{
  error: '',
  userForm: {
    identifier: 'XX-XXXX-XX-XX-X',
    title: '', 
    rights: '',
    creator: '',
    date: null,
    type: 'MusicXML', //type_file
    publisher: '',
    contributor: [], //contributor_role
    description:'' // desc
  },
  sheetForm: {
    right: '', //rightsp
    creator: { // creatorp_role
      name: '',
      role: '',
      gender: ''
    },
    date: null, // datep
    key: '', // real_key
    metre: '', // meter
    tempo: '',
    instrument: '', // instruments
    genre: '', 
    contributor: [], // contributorp_role
    altTitle: '', // alt_title
    description: '', // descp
    type: '', // type_piece
    format: '', // formattingp
    subject: '', 
    language: '', 
    relation: '', // relationp
    hasVersion: '', 
    isVersionOf: '',
    coverage: '',
    spatial: '',/**
    {
      country: '',
      state: '',
      location: ''
    }, */
    temporal: {
      century: '',
      decade: '',
      year: ''
    },
    source: '', // Borrar campo
    // Estos se mandan como un flujo de bytes
    xml: '',
    mei: '',
    midi: '',
    // Estos se mandan como URL a youtube, drive, ...
    audio: '',
    video: '',
    col_id: '' // ID de la colección. Por tanto, primero tiene que crear la colección y después meter los otros formularios.
  },
  collectionForm: {
    title: '',
    right: '', // rights
    date: null, 
    creator: { // creator_role
      name: '',
      role: ''
    },
    contributor: [], // contributor_role
    type: '', // source_type
    source: '',
    description: '',
    format: '', // formatting
    extent: '', 
    publisher: '', 
    bibliographic: '', // Borrar campo
    subject: '', 
    language: '',
    relation: '',
    coverage: '',
    spatial: '',/**
    {
      country: '',
      state: '',
      location: ''
    }, */
    temporal: {
      century: '',
      decade: '',
      year: ''
    },
    rightsHolder: ''
  }
}
