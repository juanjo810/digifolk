<template>
    <v-container>
        <v-row>
            <v-col>
                <h1>Information about the musical piece</h1>
                <div>
                    <template>
                        <v-progress-linear color="deep-purple" height="10" indeterminate></v-progress-linear>
                    </template>
                    <v-card-text>
                        <v-row>
                            <v-col cols="12">
                                <v-select v-model="this.right" label="Rights" :items="rights"></v-select>
                            </v-col>

                            <v-col cols="12">
                                <h2>Creator</h2>
                            </v-col>
                            <v-col cols="4">
                                <v-text-field v-model="this.creatorName" label="Name or URI" :rules="rules" hint="URI example in http://www.dib.ie" persistent-hint></v-text-field>
                            </v-col>
                            <v-col cols="4">
                                <v-select v-model="creatorRole" label="Role" :items="roles" :rules="rules"></v-select>
                            </v-col>
                            <v-col cols="4">
                                <v-select v-model="creatorGender" label="Gender" :items="['Male', 'Female', 'Other']" :rules="rules"></v-select>
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

                            <v-col cols="4">
                                <v-select v-model="key" label="Key" :items="keys"></v-select>
                            </v-col>

                            <v-col cols="4">
                                <v-select v-model="metre" label="Metre" :items="metres"></v-select>
                            </v-col>

                            <v-col cols="4">
                                <v-select v-model="tempo" label="Tempo" :items="tempos"></v-select>
                            </v-col>

                            <v-col cols="6">
                                <v-select v-model="instrument" label="Instrument" :items="instruments" multiple></v-select>
                            </v-col>

                            <v-col cols="6">
                                <v-select v-model="genre" label="Genre" :items="genres"></v-select>
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

                            <v-col cols="12">
                                <v-text-field v-model="altTitle" label="Alternative title" :rules="rules"></v-text-field>
                            </v-col>

                            <v-col cols="12">
                                <v-text-field v-model="description" label="Description" :rules="rules"></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="type" label="Type" :rules="rules"></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="format" label="Format" :rules="rules"></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="subject" label="Subject" :rules="rules" hint="You can check the subject in https://www.vwml.org/song-subject-index. Multiple subjects must be separated by ':'" persistent-hint></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="language" label="Language code" :rules="rules" hint="You can check the code in https://www.loc.gov/standards/iso639-2/php/code_list.php" persistent-hint></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="relation" label="Relation" :rules="rules" hint="Multiple relations must be separated by ':'"></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="hasVersion" label="HasVersion" :rules="rules" hint="Multiple versions must be separated by ':'"></v-text-field>
                            </v-col>

                            <v-col cols="6">
                                <v-text-field v-model="isVersionOf" label="IsVersionOf" :rules="rules" hint="Multiple versions must be separated by ':'"></v-text-field>
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
                                <v-text-field v-model="source" label="Source" :rules="rules"></v-text-field>
                            </v-col>
                        </v-row>



                    </v-card-text>

                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn color="deep-purple lighten-2" text @click="saveData()">
                            Save Data
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
            roles:['Collector', 'Performer', 'Singer', 'Speech', 'Composer'],
            keys:['C', 'G', 'F', 'D', 'Bb', 'Eb', 'A'],
            metres:['2/4', '3/4', '4/4', '6/8', '9/8', '12/8'],
            tempos:['Slow', 'Medium', 'Fast'],
            instruments:['Singer', 'Harmonium', 'Harmonica', 'Banjo', '5-String Banjo', 'Irish Bouzouki', 'Bodhrán', 'Accordion', 'Piano Accordion', 'Bass Clarinet', 'Early Irish Harp', 'Pedal Harp', 'Percussion Instrument', 'Bones', 'Concertina', 'English Concertina', 'Irish Harp', 'Harpsichord', 'Pedal Harp', 'Percussive Dance', 'Bass Guitar', 'Cello', 'Lambeg Drum', 'Low Whistle', 'Flute', 'Tin Whistle', 'Reed Instrument', 'Fiddle', 'Fife', 'Piccolo', 'Metal Flute', 'Drum Set', 'Wind Instrument', 'Woodwind Instrument', 'Guitar', 'Electric Guitar', 'Mandolin', 'Mandola', 'Melodeon', 'Oboe', 'Double Bass', 'Piano', 'Bagpipes', 'War Pipes', 'Pipe Organ', 'Uilleann Pipes', 'Lilting', 'Saxophone', 'Synthesizer', 'Spoons', 'Snare Drum', 'Appalachian Dulcimer', 'Hammered Dulcimer', 'String Instrument', 'Jaw Harp', 'Vocal Instrument', 'Keyboard Instrument', 'Viola'],
            genres:['Sons', 'Children piece', 'Work piece', 'Lullaby piece', 'Pieces of youth', 'Wedding piece', 'Funeral piece', 'Dance', 'Accompanying songs', 'Religious songs'],
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
            'sheetForm'
        ]),
        right: {
            get () {
                return this.sheetForm.right
            },
            set (value) {
                this.$store.commit('UPDATE_SHEET_RIGHT', value)
            }
        },
        creatorName: {
            get () {
                return this.sheetForm.creator.name
            },
            set (value) {
                this.$store.commit('UPDATE_SHEET_CREATORNAME', value)
            }
        },
        creatorRole: {
            get () {
                return this.sheetForm.creator.role
            },
            set (value) {
                this.$store.commit('UPDATE_SHEET_CREATORROLE', value)
            }
        },
        creatorGender: {
            get () {
                return this.sheetForm.creator.gender
            },
            set (value) {
                this.$store.commit('UPDATE_SHEET_CREATORGENDER', value)
            }
        },
        key: {
            get () {
                return this.sheetForm.key
            },
            set (value) {
                this.$store.commit('UPDATE_SHEET_KEY', value)
            }
        },
        metre: {
            get () {
                return this.sheetForm.metre
            },
            set (value) {
                this.$store.commit('UPDATE_SHEET_METRE', value)
            }
        },
        contributor () {
            return this.sheetForm.contributor
        },
        date () {
            return this.sheetForm.date
        },
        instrument: {
            get () {
                return this.sheetForm.instrument
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_INSTRUMENT', value)
            }
        },
        genre: {
            get () {
                return this.sheetForm.genre
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_GENRE', value)
            }
        },
        altTitle: {
            get () {
                return this.sheetForm.altTitle
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_ALTTITLE', value)
            }
        },
        description: {
            get () {
                return this.sheetForm.description
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_DESCRIPTION', value)
            }
        },
        type: {
            get () {
                return this.sheetForm.type
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_TYPE', value)
            }
        },
        format: {
            get () {
                return this.sheetForm.format
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_FORMAT', value)
            }
        },
        subject: {
            get () {
                return this.sheetForm.subject
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_SUBJECT', value)
            }
        },
        language: {
            get () {
                return this.sheetForm.language
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_LANGUAGE', value)
            }
        },
        relation: {
            get () {
                return this.sheetForm.relation
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_RELATION', value)
            }
        },
        hasVersion: {
            get () {
                return this.sheetForm.hasVersion
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_HASVERSION', value)
            }
        },
        isVersionOf: {
            get () {
                return this.sheetForm.isVersionOf
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_ISVERSIONOF', value)
            }
        },
        coverage: {
            get () {
                return this.sheetForm.coverage
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_COVERAGE', value)
            }
        },
        spatial: {
            get () {
                return this.sheetForm.spatial
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_SPATIAL', value)
            }
        },
        temporalCentury: {
            get () {
                return this.sheetForm.temporal.century
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_TEMPORALCENTURY', value)
            }
        },
        temporalDecade: {
            get () {
                return this.sheetForm.temporal.decade
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_TEMPORALDECADE', value)
            }
        },
        temporalYear: {
            get () {
                return this.sheetForm.temporal.year
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_TEMPORALYEAR', value)
            }
        },
        source: {
            get () {
                return this.sheetForm.source
            },
            set (value) {   
                this.$store.commit('UPDATE_SHEET_SOURCE', value)
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
            this.addContributor('Sheet')
            this.contribuidores.push({name: '', role: ''})
        },
        removeField (index) {
            this.removeContributor({index:index, form: 'Sheet'})
            this.contribuidores.splice(index, 1)
        },
        updateContributor() {
            this.$store.commit('UPDATE_SHEET_CONTRIBUTOR', this.contribuidores);
        },
        formatDate() {
            if (this.selectedDate) {   
                this.formatAndSaveDate( {date: this.selectedDate, form: 'Sheet'})
            }
        },
    },
    
    created () {
        this.contribuidores = structuredClone(this.contributor)
    }
}
</script>
