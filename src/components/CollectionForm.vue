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
                            <v-col cols="12">
                                <v-text-field v-model="email" label="Title" :rules="rulesEmail"></v-text-field>
                            </v-col>

                            <v-col cols="12">
                                <v-select v-model="email" label="Rights" :items="rights"></v-select>
                            </v-col>

                            <v-col cols="12">
                                <VDatePicker hide-actions="true"></VDatePicker>
                            </v-col>

                            <v-col cols="12">
                                <label>Creator</label>
                            </v-col>
                            <v-col cols="6">
                                <v-text-field v-model="email" label="Name or URI" :rules="rulesEmail" hint="URI example in http://www.dib.ie" persistent-hint></v-text-field>
                            </v-col>
                            <v-col cols="6">
                                <v-select v-model="email" label="Role" :items="roles" :rules="rulesEmail"></v-select>
                            </v-col>

                            <v-col cols="12">
                                <label>Contributor</label>
                            </v-col>
                            <v-col cols="6">
                                <v-text-field v-model="email" label="Name or URI" :rules="rulesEmail" hint="URI example in http://www.dib.ie. Multiple separated by |" persistent-hint></v-text-field>
                            </v-col>
                            <v-col cols="6">
                                <v-select v-model="email" label="Role" :items="rolesCont" :rules="rulesEmail"></v-select>
                            </v-col>
                            
                            <v-col cols="12">
                                <v-select v-model="email" label="Type" :items="types"></v-select>
                            </v-col>

                            <v-col cols="12">
                                <v-text-field v-model="email" label="Source" :rules="rulesEmail"></v-text-field>
                            </v-col>

                            <v-col cols="12">
                                <v-text-field v-model="email" label="Description" :rules="rulesEmail"></v-text-field>
                            </v-col>
                            
                            <v-col cols="12">
                                <v-select v-model="email" label="Type" :items="types"></v-select>
                            </v-col>

                            <v-col cols="12">
                                <v-text-field v-model="email" label="Format" :rules="rulesEmail"></v-text-field>
                            </v-col>

                            <v-col cols="12">
                                <v-text-field v-model="email" label="Extent" :rules="rulesEmail"></v-text-field>
                            </v-col>

                            <v-col cols="12">
                                <v-text-field v-model="email" label="Publisher" :rules="rulesEmail"></v-text-field>
                            </v-col>

                            <v-col cols="12">
                                <v-text-field v-model="email" label="Bibliographic citation" :rules="rulesEmail"></v-text-field>
                            </v-col>

                            <v-col cols="12">
                                <v-text-field v-model="email" label="Subject" :rules="rulesEmail" hint="You can check the subject in https://www.vwml.org/song-subject-index" persistent-hint></v-text-field>
                            </v-col>

                            <v-col cols="12">
                                <v-text-field v-model="email" label="Language code" :rules="rulesEmail" hint="You can check the code in https://www.loc.gov/standards/iso639-2/php/code_list.php" persistent-hint></v-text-field>
                            </v-col>

                            <v-col cols="12">
                                <v-text-field v-model="email" label="Relation" :rules="rulesEmail"></v-text-field>
                            </v-col>

                            <v-col cols="12">
                                <v-text-field v-model="email" label="Coverage" :rules="rulesEmail"></v-text-field>
                            </v-col>

                            <v-col cols="12">
                                <v-text-field v-model="email" label="Spatial" :rules="rulesEmail"></v-text-field>
                            </v-col>

                            <v-col cols="12">
                                <label>Temporal</label>
                            </v-col>
                            <v-col cols="4">
                                <v-text-field v-model="email" label="Century" :rules="rulesEmail"></v-text-field>
                            </v-col>
                            <v-col cols="4">
                                <v-text-field v-model="email" label="Decade" :rules="rulesEmail"></v-text-field>
                            </v-col>
                            <v-col cols="4">
                                <v-text-field v-model="email" label="Year" :rules="rulesEmail"></v-text-field>
                            </v-col>

                            <v-col cols="12">
                                <v-select v-model="email" label="Rights" :items="rights"></v-select>
                            </v-col>

                            <v-col cols="12">
                                <v-text-field v-model="email" label="RightsHolder" :rules="rulesEmail"></v-text-field>
                            </v-col>
                        </v-row>



                    </v-card-text>

                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn color="deep-purple lighten-2" text @click="register()" v-if="!fetchingUser">
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
            name: '',
            surname: '',
            email: '',
            profilePhoto: '',
            password: '',
            password2: '',
            visible1: false,
            visible2: false,
            visibility: false,
            rulesEmail: [
                value => !!value || 'Required.',
                value => {
                    const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
                    return pattern.test(value) || 'Invalid e-mail.'
                },
            ],
            rules: [
                value => !!value || 'Required.'
            ]
        }
    },
    computed: {
        ...mapState([
            'fetchingUser',
            'error'
        ])
    },
    methods: {
        ...mapActions([
            'registerUser'
        ]),
        register() {
            if (this.name !== '' && this.surname !== '' && this.email !== '' && this.password !== '' && this.password2 !== '') {
                this.registerUser({ email: this.email, password: this.password, name: this.name, surname: this.surname, password2: this.password2, profilePhoto: this.profilePhoto })
                    .then(() => {
                        if (this.error === '') {
                            this.name = ''
                            this.surname = ''
                            this.email = ''
                            this.profilePhoto = ''
                            this.password = ''
                            this.password2 = ''
                            this.visibility = true
                        }
                    })
            }
        },
        continuar() {
            this.visibility = false
            this.$router.push({ name: 'login' })
        }
    }
}
</script>
