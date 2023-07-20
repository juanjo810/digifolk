<template>
    <v-container>
        <v-row>
            <v-col>
                <h1>Information about the MusicXML file</h1>
                <div>
                        <template>
                            <v-progress-linear color="deep-purple" height="10" indeterminate></v-progress-linear>
                        </template>
                        <v-card-text>
                            <v-row>
                                <v-col cols="6">
                                    <v-text-field v-model="this.id" label="Identifier" readonly></v-text-field>
                                </v-col>

                                <v-col cols="6">
                                    <v-text-field v-model="this.title" label="Title" :rules="rules" hint="Use ' | ', i.e. space colon space, to separate title and subtitle
Use ' = ' i.e. space equals space, where a title is available in different languages" persistent-hint></v-text-field>
                                </v-col>

                                <v-col cols="6">
                                <v-select v-model="this.right" label="Rights" :items="getItemsNameByType(1)"></v-select>
                            </v-col>

                                <v-col cols="6">
                                    <v-text-field v-model="this.creator" label="Creator" :rules="rules"></v-text-field>
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

                                <v-col cols="6">
                                    <v-select v-model="this.type" label="Type" :items="getItemsNameByType(7)" :rules="rules"></v-select>
                                </v-col>

                                <v-col cols="6">
                                    <v-text-field v-model="this.publisher" label="Publisher" :rules="rules"></v-text-field>
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
                                            <v-select  v-model="c.role" @update:modelValue="updateContributor()" label="Role" :items="getItemsNameByType(2)" :rules="rules"></v-select>
                                        </v-col>
                                        <v-col cols="1">
                                            <v-btn @click="removeField(index)">
                                                <v-icon>mdi-close</v-icon>
                                            </v-btn>
                                        </v-col>
                                    </v-row>
                                </v-container>

                                <v-col cols="12">
                                    <v-text-field v-model="this.description" label="Description"></v-text-field>
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
import { mapActions, mapGetters, mapState } from 'vuex'
import {VDatePicker} from 'vuetify/labs/VDatePicker'

export default {
    components: {
        VDatePicker,
    },
    data() {
        return {
            rules: [
                value => !!value || 'Required.'
            ],
            contribuidores: [],
            selectedDate: null
        }
    },
    computed: {
        ...mapState([
            'error',
            'userForm',
            'defaultSelections'
        ]),
        ...mapGetters([
          'getItemsNameByType'
        ]),
        id: {
            get () {
                return this.userForm.identifier
            },
            set (value) {
                this.$store.commit('UPDATE_USER_ID', value)
            }
        },
        title: {
            get () {
                return this.userForm.title
            },
            set (value) {
                this.$store.commit('UPDATE_USER_TITLE', value)
            }
        },
        right: {
            get () {
                return this.userForm.right
            },
            set (value) {
                this.$store.commit('UPDATE_USER_RIGHT', value)
            }
        },
        creator: {
            get () {
                return this.userForm.creator
            },
            set (value) {
                this.$store.commit('UPDATE_USER_CREATOR', value)
            }
        },
        date () {
            return this.userForm.date
        },
        type: {
            get () {
                return this.userForm.type_file
            },
            set (value) {
                this.$store.commit('UPDATE_USER_TYPE', value)
            }
        },
        publisher: {
            get () {
                return this.userForm.publisher
            },
            set (value) {
                this.$store.commit('UPDATE_USER_PUBLISHER', value)
            }
        },
        contributor () {
            return this.userForm.contributor_role
        },
        description: {
            get () {
                return this.userForm.desc
            },
            set (value) {   
                this.$store.commit('UPDATE_USER_DESCRIPTION', value)
            }
        },
    },
    methods: {
        ...mapActions([
            'saveDataPiece',
            'addContributor',
            'formatAndSaveDate',
            'removeContributor'
        ]),
        saveData () {
            this.saveDataPiece()
        },
        importFile () {
            this.$refs.fileInput.click()
        },
        handleFileChange(event) {
            const file = event.target.files[0]
            console.log('Archivo seleccionado:', file)
        },
        addFields ()  {
            this.addContributor('User')
            this.contribuidores.push({name: '', role: ''})
        },
        removeField (index) {
            this.removeContributor({index:index, form: 'User'})
            this.contribuidores.splice(index, 1)
        },
        updateContributor() {
            this.$store.commit('UPDATE_USER_CONTRIBUTOR', this.contribuidores);
        },
        formatDate() {
            if (this.selectedDate) {   
                this.formatAndSaveDate( {date: this.selectedDate, form: 'User'})
            }
        },
    },
    created () {
        this.contribuidores = structuredClone(this.contributor)
    }
}
</script>
