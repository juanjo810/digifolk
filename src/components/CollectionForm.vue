<template>
    <v-container>
        <v-row>
            <v-col>
                <h1>Information about the source of the musical piece</h1>
                <div>
                    <template>
                        <v-progress-linear color="deep-purple" height="10" indeterminate></v-progress-linear>
                    </template>
                    <v-card-text>
                        <v-row>
                            <v-col cols="6">
                                <v-text-field v-model="title" label="Title" :rules="rules" hint="Use ' : ', i.e. space colon space, to separate title and subtitle
Use ' = ' i.e. space equals space, where a title is available in different languages" ></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-select v-model="right" label="Rights" :items="rights"></v-select>
                            </v-col>

                            <v-col cols="6">
                                <v-date-picker
                                v-model="this.selectedDate"
                                @update:modelValue="formatDate"
                                ></v-date-picker>
                            </v-col>
                            <v-col cols="6">
                                <h2>Fecha seleccionada: {{ this.date }}</h2>
                            </v-col>

                            <v-col cols="12">
                                <label>Creator</label>
                            </v-col>
                            <v-col cols="6">
                                <v-text-field v-model="creatorName" label="Name or URI" :rules="rules" hint="URI example in http://www.dib.ie" persistent-hint></v-text-field>
                            </v-col>
                            <v-col cols="6">
                                <v-select v-model="creatorRole" label="Role" :items="roles" :rules="rules"></v-select>
                            </v-col>

                            <v-col cols="6  ">
                                <h2>Contributors</h2>
                            </v-col>
                            <v-col cols="6">
                                <v-btn @click="addFields()">Add contributor</v-btn>
                            </v-col>
                            <v-container v-for="(c,index) in contribuidores" :key="index">
                                <v-row>
                                    <v-col cols="6">
                                        <v-text-field v-model="c.name" @input="updateContributor()" label="Name or URI" :rules="rules" hint="URI example in http://www.dib.ie" persistent-hint></v-text-field>
                                    </v-col>
                                    <v-col cols="5">
                                        <v-select  v-model="c.role" @update:modelValue="updateContributor()" label="Role" :items="['Editor', 'Arranger']" :rules="rules"></v-select>
                                    </v-col>
                                    <v-col cols="1">
                                        <v-btn @click="removeField(index)">
                                            <v-icon>mdi-close</v-icon>
                                        </v-btn>
                                    </v-col>
                                </v-row>
                            </v-container>
                            
                            <v-col cols="6">
                                <v-select v-model="type" label="Type" :items="types"></v-select>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="source" label="Source" :rules="rules"></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="description" label="Description" :rules="rules"></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="format" label="Format" :rules="rules"></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="extent" label="Extent" :rules="rules"></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="publisher" label="Publisher" :rules="rules"></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="bibliographic" label="Bibliographic citation" :rules="rules"></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="subject" label="Subject" :rules="rules" hint="You can check the subject in https://www.vwml.org/song-subject-index. Multiple subjects must be separated by '|'" persistent-hint></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="language" label="Language code" :rules="rules" hint="You can check the code in https://www.loc.gov/standards/iso639-2/php/code_list.php" persistent-hint></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="relation" label="Relation" :rules="rules" hint=" Multiple subjects must be separated by '|'" persistent-hint=""></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="coverage" label="Coverage" :rules="rules"></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="spatial" label="Spatial" :rules="rules"></v-text-field>
                            </v-col>

                            <v-col cols="12">
                                <h2>Temporal</h2>
                            </v-col>
                            <v-col cols="4">
                                <v-text-field v-model="temporalCentury" label="Century" :rules="rules"></v-text-field>
                            </v-col>
                            <v-col cols="4">
                                <v-text-field v-model="temporalDecade" label="Decade" :rules="rules"></v-text-field>
                            </v-col>
                            <v-col cols="4">
                                <v-text-field v-model="temporalYear" label="Year" :rules="rules"></v-text-field>
                            </v-col>

                            <v-col cols="12">
                                <v-text-field v-model="rightsHolder" label="RightsHolder" :rules="rules"></v-text-field>
                            </v-col>
                        </v-row>



                    </v-card-text>

                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn color="deep-purple lighten-2" text @click="saveData()">
                            Save data
                        </v-btn>
                        <v-btn color="deep-purple lighten-2" text @click="importFile()">
                            Import File
                        </v-btn>
                        <input type="file" ref="fileInput" class="d-none" accept=".xlsx, .xls, .mei, .mxml" @change="handleFileChange">
                    </v-card-actions>
                </div>
            </v-col>
        </v-row>

    </v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex'
import { VDatePicker } from 'vuetify/labs/VDatePicker'

export default {
    components: {
        VDatePicker,
    },
    data() {
        return {
            roles:['Collector', 'Writer'],
            rolesCont:['Sound engineer', 'Videographer', 'Typesetter'],
            types:['Collection', 'Dataset', 'Event', 'Image', 'InteractiveResource', 'MovingImage', 'PhysicalObject', 'Service', 'Software', 'Sound', 'StillImage', 'Text'],
            rights:['Rights statements', 'In copyright', 'In copyright – EU Orphan Work', 'In copyright - Educational Use Permitted', 'In copyright - Non-commercial Use Permitted', 'In Copyright – Rights Holder(s) Unlocatable or Unidentifiable', 'No Copyright – Contractual Restrictions', 'No Copyright – Non-commercial Use Only', 'No Copyright – Other Known Legal Restrictions', 'CC-BY (Creative Commons – Attribution', 'CC-BY-SA (Creative Commons – Attribution – Share Alike)', 'CC-BY-NC (Creative Commons – Attribution – Non-commercial)', 'CC-BY-NC-SA (Creative Commons – Attribution – Non-commercial – Share Alike)', 'CC-BY-ND (Creative Commons – Attribution – No Derivatives)', 'CC-BY-NC-ND (Creative Commons – Attribution – Non-commercial – No Derivatives)', 'CC-0 (CC Zero)', 'Public domain mark'],
            contribuidores: [],
            selectedDate: null,
            rules: [
                value => !!value || 'Required.'
            ]
        }
    },
    computed: {
        ...mapState([
            'error',
            'collectionForm'
        ]),
        title: {
            get () {
                return this.collectionForm.title
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_TITLE', value)
            }
        },
        right: {
            get () {
                return this.collectionForm.right
            },
            set (value) {
                this.$store.commit('UPDATE_COLLECTION_RIGHT', value)
            }
        },
        creatorName: {
            get () {
                return this.collectionForm.creator.name
            },
            set (value) {
                this.$store.commit('UPDATE_COLLECTION_CREATORNAME', value)
            }
        },
        creatorRole: {
            get () {
                return this.collectionForm.creator.role
            },
            set (value) {
                this.$store.commit('UPDATE_COLLECTION_CREATORROLE', value)
            }
        },
        contributor () {
            return this.collectionForm.contributor
        },
        date () {
            return this.collectionForm.date
        },
        description: {
            get () {
                return this.collectionForm.description
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_DESCRIPTION', value)
            }
        },
        type: {
            get () {
                return this.collectionForm.type
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_TYPE', value)
            }
        },
        format: {
            get () {
                return this.collectionForm.format
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_FORMAT', value)
            }
        },
        subject: {
            get () {
                return this.collectionForm.subject
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_SUBJECT', value)
            }
        },
        language: {
            get () {
                return this.collectionForm.language
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_LANGUAGE', value)
            }
        },
        relation: {
            get () {
                return this.collectionForm.relation
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_RELATION', value)
            }
        },
        coverage: {
            get () {
                return this.collectionForm.coverage
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_COVERAGE', value)
            }
        },
        spatial: {
            get () {
                return this.collectionForm.spatial
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_SPATIAL', value)
            }
        },
        temporalCentury: {
            get () {
                return this.collectionForm.temporal.century
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_TEMPORALCENTURY', value)
            }
        },
        temporalDecade: {
            get () {
                return this.collectionForm.temporal.decade
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_TEMPORALDECADE', value)
            }
        },
        temporalYear: {
            get () {
                return this.collectionForm.temporal.year
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_TEMPORALYEAR', value)
            }
        },
        source: {
            get () {
                return this.collectionForm.source
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_SOURCE', value)
            }
        },
        extent: {
            get () {
                return this.collectionForm.extent
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_EXTENT', value)
            }
        },
        publisher: {
            get () {
                return this.collectionForm.publisher
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_PUBLISHER', value)
            }
        },
        bibliographic: {
            get () {
                return this.collectionForm.bibliographic
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_BIBLIOGRAPHIC', value)
            }
        },
        rightsHolder: {
            get () {
                return this.collectionForm.rightsHolder
            },
            set (value) {   
                this.$store.commit('UPDATE_COLLECTION_RIGHTSHOLDER', value)
            }
        },
    },
    methods: {
        ...mapActions([
            'saveDataUserForm',
            'addContributor',
            'formatAndSaveDate',
            'removeContributor'
        ]),
        saveData () {
            this.saveDataUserForm(this.userFormData)
        },
        importFile () {
            this.$refs.fileInput.click();
        },
        handleFileChange(event) {
            const file = event.target.files[0];
            console.log('Archivo seleccionado:', file);
        },
        addFields ()  {
            this.addContributor('Collection')
            this.contribuidores.push({name: '', role: ''})
        },
        removeField (index) {
            this.removeContributor({index:index, form: 'Collection'})
            this.contribuidores.splice(index, 1)
        },
        updateContributor() {
            this.$store.commit('UPDATE_COLLECTION_CONTRIBUTOR', this.contribuidores);
        },
        formatDate() {
            if (this.selectedDate) {   
                this.formatAndSaveDate( {date: this.selectedDate, form: 'Collection'})
            }
        },
    },
    
    created () {
        this.contribuidores = structuredClone(this.contributor)
    }
}
</script>
