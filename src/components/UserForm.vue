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
                                <v-col cols="12">
                                    <v-text-field v-model="this.id" label="Identifier" ></v-text-field>
                                </v-col>

                                <v-col cols="12">
                                    <v-text-field v-model="this.title" label="Title" :rules="rules"></v-text-field>
                                </v-col>

                                <v-col cols="12">
                                <v-select v-model="this.right" label="Rights" :items="rights"></v-select>
                            </v-col>

                                <v-col cols="12">
                                    <v-text-field v-model="this.creator" label="Creator" :rules="rules"></v-text-field>
                                </v-col>

                                <v-col cols="12">
                                    <VDatePicker hide-actions="true"></VDatePicker>
                                </v-col>

                                <v-col cols="12">
                                    <v-text-field v-model="this.type" label="Type" :rules="rules"></v-text-field>
                                </v-col>

                                <v-col cols="12">
                                    <v-text-field v-model="this.publisher" label="Publisher" :rules="rules"></v-text-field>
                                </v-col>

                                <v-col cols="6  ">
                                <label>Contributor</label>
                                </v-col>
                                <v-col cols="6">
                                    <v-btn @click="addFields()">Add contributor</v-btn>
                                </v-col>
                                <v-container v-for="(cont, index) in contributor" :key="index">
                                    <v-row>
                                        <v-col cols="6">
                                            <v-text-field v-model="contribuidores[index].name" @input="updateContributorName(contribuidores[index].name, index)" label="Name or URI" :rules="rules" hint="URI example in http://www.dib.ie" persistent-hint></v-text-field>
                                        </v-col>
                                        <v-col cols="6">
                                            <v-select label="Role" :items="['Editor', 'Arranger']" :rules="rules"></v-select>
                                        </v-col>
                                    </v-row>
                                </v-container>

                                <v-col cols="12">
                                    <v-text-field v-model="this.description" label="Description" :rules="rules"></v-text-field>
                                </v-col>
                            </v-row>



                        </v-card-text>

                        <v-card-actions>
                            <v-spacer></v-spacer>
                            <v-btn color="deep-purple lighten-2" text @click="saveData()" v-if="!fetchingUser">
                                Guardar datos
                            </v-btn>
                        </v-card-actions>
                </div>
            </v-col>
        </v-row>

    </v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex'
import {VDatePicker} from 'vuetify/labs/VDatePicker'

export default {
    components: {
        VDatePicker,
    },
    data() {
        return {
            rights:['Rights statements', 'In copyright', 'In copyright - EU Orphan Work', 'In copyright - Educational Use Permitted', 'In copyright - Non-commercial Use Permitted', 'In Copyright – Rights Holder(s) Unlocatable or Unidentifiable', 'No Copyright – Contractual Restrictions', 'No Copyright – Non-commercial Use Only', 'No Copyright – Other Known Legal Restrictions', 'CC-BY (Creative Commons – Attribution', 'CC-BY-SA (Creative Commons – Attribution – Share Alike)', 'CC-BY-NC (Creative Commons – Attribution – Non-commercial)', 'CC-BY-NC-SA (Creative Commons – Attribution – Non-commercial – Share Alike)', 'CC-BY-ND (Creative Commons – Attribution – No Derivatives)', 'CC-BY-NC-ND (Creative Commons – Attribution – Non-commercial – No Derivatives)', 'CC-0 (CC Zero)', 'Public domain mark'],
            rules: [
                value => !!value || 'Required.'
            ],
            contribuidores: []
        }
    },
    computed: {
        ...mapState([
            'error',
            'userForm'
        ]),
        id: {
            get () {
                return this.$store.state.userForm.identifier
            },
            set (value) {
                this.$store.commit('UPDATE_USER_ID', value)
            }
        },
        title: {
            get () {
                return this.$store.state.userForm.title
            },
            set (value) {
                this.$store.commit('UPDATE_USER_TITLE', value)
            }
        },
        right: {
            get () {
                return this.$store.state.userForm.right
            },
            set (value) {
                this.$store.commit('UPDATE_USER_RIGHT', value)
            }
        },
        creator: {
            get () {
                return this.$store.state.userForm.creator
            },
            set (value) {
                this.$store.commit('UPDATE_USER_CREATOR', value)
            }
        },
        date: {
            get () {
                return this.$store.state.userForm.date
            },
            set (value) {
                this.$store.commit('UPDATE_USER_DATE', value)
            }
        },
        type: {
            get () {
                return this.$store.state.userForm.type
            },
            set (value) {
                this.$store.commit('UPDATE_USER_TYPE', value)
            }
        },
        publisher: {
            get () {
                return this.$store.state.userForm.publisher
            },
            set (value) {
                this.$store.commit('UPDATE_USER_PUBLISHER', value)
            }
        },
        contributor () {
            return this.userForm.contributor
        },
        description: {
            get () {
                return this.$store.state.userForm.description
            },
            set (value) {   
                this.$store.commit('UPDATE_USER_DESCRIPTION', value)
            }
        },
    },
    methods: {
        ...mapActions([
            'saveDataUserForm',
            'addUserContributor'
        ]),
        saveData () {
            this.saveDataUserForm(this.userFormData)
        },
        addFields ()  {
            this.addUserContributor()
            this.contribuidores.push({name: '', role: ''})
        },
        updateContributorName(value, index) {
            console.log(value,index) 
            this.$store.commit('UPDATE_USER_CONTRIBUTOR', { value, index });
        }
    },
    created () {
        console.log(this.$store.state)
        debugger
        this.contribuidores = structuredClone(this.userForm.contributor)
    }
}
</script>
