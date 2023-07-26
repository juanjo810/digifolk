export default{
  user:{
    tokenSession: '',
    userInfo: null
  },
  error: '',
  fetchingCollection: false,
  fetchingPiece: false,
  separator: '|',
  defaultSelections: {
    items: [],
    itemsIDs:{
      "Rights": 1,
      "XML Contributor Roles": 2,
      "Creator Pieces Roles": 3,
      "Contributor Pieces Roles": 4,
      "Creator Sources Roles": 5,
      "Contributor Sources Roles": 6,
      "Types": 7,
      "Keys": 8,
      "Meters": 9,
      "Tempos": 10,
      "Instruments": 11,
      "Genres": 12,
      "Genders": 13
    }
    ,
    rights:['Rights statements', 'In copyright', 'In copyright - EU Orphan Work', 'In copyright - Educational Use Permitted', 'In copyright - Non-commercial Use Permitted', 'In Copyright – Rights Holder(s) Unlocatable or Unidentifiable', 'No Copyright – Contractual Restrictions', 'No Copyright – Non-commercial Use Only', 'No Copyright – Other Known Legal Restrictions', 'CC-BY (Creative Commons – Attribution', 'CC-BY-SA (Creative Commons – Attribution – Share Alike)', 'CC-BY-NC (Creative Commons – Attribution – Non-commercial)', 'CC-BY-NC-SA (Creative Commons – Attribution – Non-commercial – Share Alike)', 'CC-BY-ND (Creative Commons – Attribution – No Derivatives)', 'CC-BY-NC-ND (Creative Commons – Attribution – Non-commercial – No Derivatives)', 'CC-0 (CC Zero)', 'Public domain mark'],
    rightsMapping: {
      'Rights statements': 11,
      'In copyright': 12,
      'In copyright - EU Orphan Work': 13,
      'In copyright - Educational Use Permitted': 14,
      'In copyright - Non-commercial Use Permitted': 15,
      'In Copyright – Rights Holder(s) Unlocatable or Unidentifiable': 16,
      'No Copyright – Contractual Restrictions': 17,
      'No Copyright – Non-commercial Use Only': 18,
      'No Copyright – Other Known Legal Restrictions': 19,
      'CC-BY (Creative Commons – Attribution': 110,
      'CC-BY-SA (Creative Commons – Attribution – Share Alike)': 111,
      'CC-BY-NC (Creative Commons – Attribution – Non-commercial)': 112,
      'CC-BY-NC-SA (Creative Commons – Attribution – Non-commercial – Share Alike)': 113,
      'CC-BY-ND (Creative Commons – Attribution – No Derivatives)': 114,
      'CC-BY-NC-ND (Creative Commons – Attribution – Non-commercial – No Derivatives)': 115,
      'CC-0 (CC Zero)': 116,
      'Public domain mark': 117
    },
    cont_rolesXML: ['Editor', 'Quality Control'],
    cont_rolesXMLMapping: {
      'Editor': 21,
      'Quality Control': 22
    },
    creator_rolesp:['Collector', 'Performer', 'Singer', 'Speech', 'Composer'],
    creator_rolespMapping: {
      'Collector': 31,
      'Performer': 32,
      'Singer': 33,
      'Speech': 34,
      'Composer': 35
    },
    cont_rolesp: ['Editor', 'Arranger'],
    cont_rolespMapping: {
      'Editor': 41,
      'Arranger': 42
    },
    creator_roless: ['Writer', 'Collector'],
    creator_rolessMapping: {
      'Writer': 51,
      'Collector': 52
    },
    cont_roless: ['Sound engineer', 'Videographer', 'Typesetter'],
    cont_rolessMapping: {
      'Sound engineer': 61,
      'Videographer': 62,
      'Typesetter': 63
    },
    keys:['C', 'G', 'F', 'D', 'Bb', 'Eb', 'A'],
    metres:['2/4', '3/4', '4/4', '6/8', '9/8', '12/8'],
    tempos:['Slow', 'Medium', 'Fast'],
    instruments:['Singer', 'Harmonium', 'Ha rmonica', 'Banjo', '5-String Banjo', 'Irish Bouzouki', 'Bodhrán', 'Accordion', 'Piano Accordion', 'Bass Clarinet', 'Early Irish Harp', 'Pedal Harp', 'Percussion Instrument', 'Bones', 'Concertina', 'English Concertina', 'Irish Harp', 'Harpsichord', 'Pedal Harp', 'Percussive Dance', 'Bass Guitar', 'Cello', 'Lambeg Drum', 'Low Whistle', 'Flute', 'Tin Whistle', 'Reed Instrument', 'Fiddle', 'Fife', 'Piccolo', 'Metal Flute', 'Drum Set', 'Wind Instrument', 'Woodwind Instrument', 'Guitar', 'Electric Guitar', 'Mandolin', 'Mandola', 'Melodeon', 'Oboe', 'Double Bass', 'Piano', 'Bagpipes', 'War Pipes', 'Pipe Organ', 'Uilleann Pipes', 'Lilting', 'Saxophone', 'Synthesizer', 'Spoons', 'Snare Drum', 'Appalachian Dulcimer', 'Hammered Dulcimer', 'String Instrument', 'Jaw Harp', 'Vocal Instrument', 'Keyboard Instrument', 'Viola'],
    genres:['Sons', 'Children piece', 'Work piece', 'Lullaby piece', 'Pieces of youth', 'Wedding piece', 'Funeral piece', 'Dance', 'Accompanying songs', 'Religious songs'],
    genders: ['Male', 'Female', 'Other'],
    types:['Collection', 'Dataset', 'Event', 'Image', 'InteractiveResource', 'MovingImage', 'PhysicalObject', 'Service', 'Software', 'Sound', 'StillImage', 'Text'],
    typesMapping: {
      'Collection': 71,
      'Dataset': 72,
      'Event': 73,
      'Image': 74,
      'InteractiveResource': 75,
      'MovingImage': 76,
      'PhysicalObject': 77,
      'Service': 78,
      'Software': 79,
      'Sound': 710,
      'StillImage': 711,
      'Text': 712
    },
    collectionsIDs: []
  },
  userForm: {
    identifier: 'XX-XXXX-XX-XX-X',
    title: '', 
    rights: '',
    creator: '',
    date: null,
    type_file: '',
    publisher: '',
    contributor_role: [],
    desc:''
  },
  sheetForm: {
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
  },
  collectionForm: {
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
    rightsHolder: '',
    piece_col: []
  }
}
