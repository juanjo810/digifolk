<template>
  <div>
    <v-row>
      <v-col>
        <v-toolbar dense floating>
          <v-text-field
            hide-details
            prepend-icon="mdi-magnify"
            single-line
            v-model="searchQuery"
            clearable
          ></v-text-field>
        </v-toolbar>
      </v-col>
      <v-col>
        <v-btn @click="showAdvancedSearch">Advanced search</v-btn>
      </v-col>
    </v-row>
    <v-row>
      <v-list v-if="searchQuery">
        <v-list-item
          v-for="piece in filteredPieces"
          :key="piece.id"
          @click="getInfo(piece.id)"
        >
          <v-list-item-title>{{ piece.title }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-row>
    <v-dialog v-model="visible1" persistent width="1024">
      <v-card>
        <v-card-title>
          <span class="text-h5">Piece Filters</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <h1>Information about the MusicXML file</h1>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="title"
                  label="Title"
                  :rules="rules"
                  hint="Use ' | ', i.e. space colon space, to separate title and subtitle
                  Use ' = ' i.e. space equals space, where a title is available in different languages"
                  persistent-hint
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="right"
                  label="Rights"
                  :items="getItemsNameByType(1)"
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="creator"
                  label="Creator"
                  :rules="rules"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="type"
                  label="Type"
                  :items="getItemsNameByType(7)"
                  :rules="rules"
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="publisher"
                  label="Publisher"
                  :rules="rules"
                ></v-text-field>
              </v-col>

              <v-col cols="6  ">
                <h2>Contributors</h2>
              </v-col>
              <v-col cols="6">
                <v-btn @click="addFields()">Add contributor</v-btn>
              </v-col>
              <v-container v-for="(c, index) in contribuidores" :key="index">
                <v-row>
                  <v-col cols="6">
                    <v-text-field
                      v-model="c.name"
                      @input="updateContributor()"
                      label="Name or URI"
                      :rules="rules"
                      hint="URI example in http://www.dib.ie"
                      persistent-hint
                    ></v-text-field>
                  </v-col>
                  <v-col cols="5">
                    <v-select
                      v-model="c.role"
                      @update:modelValue="updateContributor()"
                      label="Role"
                      :items="getItemsNameByType(2)"
                      :rules="rules"
                    ></v-select>
                  </v-col>
                  <v-col cols="1">
                    <v-btn @click="removeField(index)">
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>

              <v-col cols="12">
                <v-text-field v-model="desc" label="Description"></v-text-field>
              </v-col>
            </v-row>
            <h1>Information about the piece</h1>
            <v-row>
              <v-col cols="12">
                <v-select
                  v-model="rightsp"
                  label="Rights"
                  :items="getItemsNameByType(1)"
                  :rules="rules"
                ></v-select>
              </v-col>

              <v-col cols="6  ">
                <h2>Creators</h2>
              </v-col>
              <v-col cols="6">
                <v-btn @click="addFieldsCreators()">Add creator</v-btn>
              </v-col>

              <v-container v-for="(c, index) in creadores" :key="index">
                <v-row>
                  <v-col cols="4">
                    <v-text-field
                      v-model="c.name"
                      @input="updateCreator()"
                      label="Name or URI"
                      :rules="rules"
                      hint="URI example in http://www.dib.ie"
                      persistent-hint
                    ></v-text-field>
                  </v-col>
                  <v-col cols="4">
                    <v-select
                      v-model="c.role"
                      @update:modelValue="updateCreator()"
                      label="Role"
                      :items="getItemsNameByType(3)"
                      :rules="rules"
                    ></v-select>
                  </v-col>
                  <v-col cols="3">
                    <v-select
                      v-model="c.gender"
                      @update:modelValue="updateCreator()"
                      label="Gender"
                      :items="getItemsNameByType(13)"
                    ></v-select>
                  </v-col>
                  <v-col cols="1">
                    <v-btn @click="removeFieldCreator(index)">
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>

              <v-col>
                <v-select
                  v-model="real_key"
                  label="Key"
                  :items="getItemsNameByType(8)"
                  :rules="rules"
                ></v-select>
              </v-col>

              <v-col cols="4">
                <v-select
                  v-model="meter"
                  label="Metre"
                  :items="getItemsNameByType(9)"
                  :rules="rules"
                ></v-select>
              </v-col>

              <v-col cols="4">
                <v-select
                  v-model="tempo"
                  label="Tempo"
                  :items="getItemsNameByType(10)"
                  :rules="rules"
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="instruments"
                  label="Instruments"
                  :items="getItemsNameByType(11)"
                  multiple
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="genre"
                  label="Genre"
                  :items="getItemsNameByType(12)"
                  :rules="rules"
                  multiple
                ></v-select>
              </v-col>

              <v-col cols="6">
                <h2>Contributors</h2>
              </v-col>
              <v-col cols="6">
                <v-btn @click="addFieldsp()"> Add contributor </v-btn>
              </v-col>
              <v-container v-for="(c, index) in contribuidoresp" :key="index">
                <v-row>
                  <v-col cols="6">
                    <v-text-field
                      v-model="c.name"
                      @input="updateContributor()"
                      label="Name or URI"
                      :rules="rules"
                      hint="URI example in http://www.dib.ie"
                      persistent-hint
                    ></v-text-field>
                  </v-col>
                  <v-col cols="5">
                    <v-select
                      v-model="c.role"
                      @update:modelValue="updateContributor()"
                      label="Role"
                      :items="getItemsNameByType(4)"
                      :rules="rules"
                    ></v-select>
                  </v-col>
                  <v-col cols="1">
                    <v-btn @click="removeFieldp(index)">
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>

              <v-col cols="12">
                <v-text-field
                  v-model="altTitle"
                  label="Alternative title"
                ></v-text-field>
              </v-col>

              <v-col cols="12">
                <v-text-field
                  v-model="descp"
                  label="Description"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="type_piece"
                  label="Type"
                  :items="getItemsNameByType(7)"
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="formattingp"
                  label="Format"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="subject"
                  label="Subject"
                  hint="You can check the subject in https://www.vwml.org/song-subject-index. Multiple subjects must be separated by '|'"
                  persistent-hint
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="language"
                  label="Language code"
                  hint="You can check the code in https://www.loc.gov/standards/iso639-2/php/code_list.php"
                  persistent-hint
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="relation"
                  label="Relation"
                  hint="Multiple relations must be separated by ':'"
                  persistent-hint
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="hasVersion"
                  label="HasVersion"
                  hint="Multiple versions must be separated by ':'"
                  persistent-hint
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="isVersionOf"
                  label="IsVersionOf"
                  hint="Multiple versions must be separated by ':'"
                  persistent-hint
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="coverage"
                  label="Coverage"
                ></v-text-field>
              </v-col>

              <v-col cols="12">
                <h2>Spatial</h2>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="spatialCountry"
                  label="Country"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="spatialState"
                  label="State"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="spatialLocation"
                  label="Location"
                ></v-text-field>
              </v-col>

              <v-col cols="12">
                <h2>Temporal</h2>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="temporalCentury"
                  label="Century"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="temporalDecade"
                  label="Decade"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="temporalYear"
                  label="Year"
                ></v-text-field>
              </v-col>

              <v-col cols="4">
                <v-select
                  label="Select collection"
                  :items="this.getNameCollections"
                  v-model="this.col_id"
                ></v-select>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue-darken-1" variant="text" @click="visible1 = false">
            Close
          </v-btn>
          <v-btn color="blue-darken-1" variant="text" @click="searchFilter()">
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="visible2" persistent width="1024">
      <v-card>
        <v-card-title>
          <span class="text-h5">Collection Filters</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model="title"
                  label="Title"
                  :rules="rules"
                  hint="Use ' | ', i.e. space colon space, to separate title and subtitle
Use ' = ' i.e. space equals space, where a title is available in different languages"
                  persistent-hint
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="right"
                  label="Rights"
                  :items="this.getItemsNameByType(1)"
                  :rules="rules"
                ></v-select>
              </v-col>
              <v-col cols="6">
                <h2>Fecha seleccionada: {{ date }}</h2>
              </v-col>

              <v-col cols="6">
                <h2>Creators</h2>
              </v-col>
              <v-col cols="6">
                <v-btn @click="addFieldsCreators()">Add creator</v-btn>
              </v-col>

              <v-container v-for="(c, index) in creadores" :key="index">
                <v-row>
                  <v-col cols="6">
                    <v-text-field
                      v-model="c.name"
                      label="Name or URI"
                      :rules="rules"
                      hint="URI example in http://www.dib.ie"
                      persistent-hint
                    ></v-text-field>
                  </v-col>
                  <v-col cols="5">
                    <v-select
                      v-model="c.role"
                      label="Role"
                      :items="getItemsNameByType(5)"
                      :rules="rules"
                    ></v-select>
                  </v-col>
                  <v-col cols="1">
                    <v-btn @click="removeFieldCreator(index)">
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>

              <v-col cols="6">
                <h2>Contributors</h2>
              </v-col>
              <v-col cols="6">
                <v-btn @click="addFields()">Add contributor</v-btn>
              </v-col>
              <v-container v-for="(c, index) in contribuidores" :key="index">
                <v-row>
                  <v-col cols="6">
                    <v-text-field
                      v-model="c.name"
                      label="Name or URI"
                      hint="URI example in http://www.dib.ie"
                      persistent-hint
                    ></v-text-field>
                  </v-col>
                  <v-col cols="5">
                    <v-select
                      v-model="c.role"
                      label="Role"
                      :items="getItemsNameByType(6)"
                    ></v-select>
                  </v-col>
                  <v-col cols="1">
                    <v-btn @click="removeField(index)">
                      <v-icon>mdi-close</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>

              <v-col cols="6">
                <v-select
                  v-model="type"
                  label="Type"
                  :items="getItemsNameByType(7)"
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-text-field v-model="source" label="Source"></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="description"
                  label="Description"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field v-model="format" label="Format"></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field v-model="extent" label="Extent"></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="publisher"
                  label="Publisher"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="subject"
                  label="Subject"
                  hint="You can check the subject in https://www.vwml.org/song-subject-index. Multiple subjects must be separated by '|'"
                  persistent-hint
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="language"
                  label="Language code"
                  hint="You can check the code in https://www.loc.gov/standards/iso639-2/php/code_list.php"
                  persistent-hint
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="relation"
                  label="Relation"
                  hint=" Multiple subjects must be separated by '|'"
                  persistent-hint
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="coverage"
                  label="Coverage"
                ></v-text-field>
              </v-col>

              <v-col cols="12">
                <h2>Spatial</h2>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="spatialCountry"
                  label="Country"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="spatialState"
                  label="State"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="spatialLocation"
                  label="Location"
                ></v-text-field>
              </v-col>

              <v-col cols="12">
                <h2>Temporal</h2>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="temporalCentury"
                  label="Century"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="temporalDecade"
                  label="Decade"
                ></v-text-field>
              </v-col>
              <v-col cols="4">
                <v-text-field
                  v-model="temporalYear"
                  label="Year"
                ></v-text-field>
              </v-col>

              <v-col cols="12">
                <v-text-field
                  v-model="rights_holder"
                  label="rights_holder"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue-darken-1" variant="text" @click="visible2 = false">
            Close
          </v-btn>
          <v-btn color="blue-darken-1" variant="text" @click="searchFilter()">
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from "vuex";
import { format } from "date-fns";

export default {
  components: {},
  data() {
    return {
      searchQuery: "",
      visible1: false,
      visible2: false,
      title: "",
      right: "",
      selectedDate: "",
      selectedDatep: "",
      datep: "",
      date: "",
      creadores: [],
      contribuidores: [],
      contribuidoresp: [],
      type: "",
      source: "",
      description: "",
      format: "",
      extent: "",
      publisher: "",
      subject: "",
      language: "",
      relation: "",
      coverage: "",
      spatialCountry: "",
      spatialState: "",
      spatialLocation: "",
      temporalCentury: "",
      temporalDecade: "",
      temporalYear: "",
      rights_holder: "",
      advancedSearch: false,
      advancedSearchResult: null,
      creator: "",
      type_file: "",
      desc: "",
      rightsp: "",
      real_key: "",
      meter: "",
      tempo: "",
      instruments: [],
      genre: [],
      alt_title: "",
      mode: "",
      descp: "",
      type_piece: "",
      formattingp: "",
      relationp: "",
      hasVersion: "",
      isVersionOf: "",
      col_id: "",
    };
  },
  props: {
    objects: {
      type: Array,
      required: true,
    },
    typeObject: {
      type: String,
      required: true,
    },
    getInfo: {
      type: Function,
      required: true,
    },
  },
  computed: {
    ...mapState(["pieces", "collections"]),
    ...mapGetters(["getItemsNameByType", "getNameCollections"]),
    filteredPieces() {
      if (this.searchQuery === "Advanced search") {
        return this.advancedSearchResult;
      } else {
        return this.objects.filter((piece) => {
          return piece.title.toLowerCase().includes(this.searchQuery.toLowerCase());
        });
      }
    },
  },
  methods: {
    ...mapActions(["advancedSearch"]),
    showAdvancedSearch() {
      if (this.typeObject === "pieces") {
        this.visible1 = true;
      } else if (this.typeObject === "collections") {
        this.visible2 = true;
      }
    },

    addFields() {
      this.contribuidores.push({ name: "", role: "" });
    },
    addFieldsp() {
      this.contribuidoresp.push({ name: "", role: "" });
    },
    addFieldsCreators() {
      this.creadores.push({ name: "", role: "" });
    },
    removeField(index) {
      this.contribuidores.splice(index, 1);
    },
    removeFieldp(index) {
      this.contribuidoresp.splice(index, 1);
    },
    removeFieldCreator(index) {
      this.creadores.splice(index, 1);
    },
    formatDate() {
      this.date = format(this.selectedDate[0], "d MMMM yyyy");
    },
    formatDatep() {
      this.datep = format(this.selectedDatep[0], "d MMMM yyyy");
    },
    searchFilter() {
      if (this.typeObject === "collections") {
        const query = {
          title: this.title,
          rights: this.right,
          date: this.date,
          creator_role: structuredClone(this.creadores),
          contributor_role: structuredClone(this.contribuidores),
          source_type: this.type,
          source: this.source,
          description: this.description,
          formatting: this.format,
          extent: this.extent,
          publisher: this.publisher,
          subject: this.subject,
          language: this.language,
          relation: this.relation,
          coverage: this.coverage,
          spatial: {
            country: this.spatialCountry,
            state: this.spatialState,
            location: this.spatialLocation,
          },
          temporal: {
            century: this.temporalCentury,
            decade: this.temporalDecade,
            year: this.temporalYear,
          },
          rights_holder: this.rights_holder,
        };
        this.advancedSearch({ query: query, type: this.typeObject }).then(
          (res) => {
            this.advancedSearchResult = res;
            this.searchQuery = "Advanced search";
            this.visible1 = this.visible2 = false;
          }
        );
      } else if (this.typeObject === "pieces") {
        const query = {
          title: this.title,
          rights: this.right,
          creator: this.creator,
          date: this.date,
          type_file: this.type_file,
          publisher: this.publisher,
          contributor_role: structuredClone(this.contribuidores),
          desc: this.desc,
          rightsp: this.rightsp,
          creatorp_role: structuredClone(this.creadores),
          datep: this.datep,
          real_key: this.real_key,
          meter: this.meter,
          tempo: this.tempo,
          instruments: structuredClone(this.instruments),
          genre: structuredClone(this.genre),
          contributorp_role: structuredClone(this.contribuidoresp),
          alt_title: this.alt_title,
          mode: this.mode,
          descp: this.descp,
          type_piece: this.type_piece,
          formattingp: this.formattingp,
          subject: this.subject,
          language: this.language,
          relationp: this.relationp,
          hasVersion: this.hasVersion,
          isVersionOf: this.isVersionOf,
          coverage: this.coverage,
          spatial: {
            country: this.spatialCountry,
            state: this.spatialState,
            location: this.spatialLocation,
          },
          temporal: {
            century: this.temporalCentury,
            decade: this.temporalDecade,
            year: this.temporalYear,
          },
          col_id: this.col_id,
        };
        this.advancedSearch({ query: query, type: this.typeObject }).then(
          (res) => {
            this.advancedSearchResult = res;
            this.searchQuery = "Advanced search";
            this.visible1 = this.visible2 = false;
          }
        );
      }
    },
  },
};
</script>
