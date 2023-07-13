<template>
    <v-container>
        <v-row>
            <v-col>
                <h1>Modify items</h1>
                <div>
                    <template>
                        <v-progress-linear color="deep-purple" height="10" indeterminate></v-progress-linear>
                    </template>
                    <v-card-text>
                        <v-row>
                            <v-col cols="4">
                                <v-select v-model="this.idItem" label="Item ID" :items="this.itemsIDs"></v-select>
                            </v-col>
                            <v-col cols="8">
                                <v-list v-if="this.idItem">
                                <v-list-item v-for="(item, index) in filteredItems" :key="index">
                                    <v-list-item-content>
                                    {{ item }}
                                    </v-list-item-content>
                                    <v-list-item-action>
                                    <v-icon @click="removeItem(index)">mdi-close</v-icon>
                                    </v-list-item-action>
                                </v-list-item>
                                </v-list> 
                                <v-text-field v-if="this.idItem" v-model="newItemName" label="New item name"></v-text-field>
                                <v-btn v-if="this.idItem" @click="addItem">Add item</v-btn>
                            </v-col>
                        </v-row> 
                    </v-card-text>

                    <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn color="deep-purple lighten-2" text @click="saveData()">
                            Save Data
                        </v-btn>
                    </v-card-actions>
                </div>
            </v-col>
        </v-row>

    </v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex'

export default {
    data () {
        return{
            idItem: null,
            items: [
                { id: 1, name: 'Item 1' },
                { id: 1, name: 'Item 2' },
                { id: 2, name: 'Item 3' },
                { id: 3, name: 'Item 4' }
            ],
            newItemName: ''
        }
    },
    computed: {
        ...mapState([
            'defaultSelections'
        ]),
        itemsIDs() {
            return this.defaultSelections.itemsIDs
        },
        filteredItems() {
            switch (this.idItem) {
                case '1-Rights':
                    return this.defaultSelections.rights
                case '2-XML Contributor Roles':
                    return this.defaultSelections.cont_rolesXML
                case '3-Creator Pieces Roles':
                    return this.defaultSelections.creator_rolesp
                case '4-Contributor Pieces Roles':
                    return this.defaultSelections.cont_rolesp
                case '5-Creator Sources Roles':
                    return this.defaultSelections.creator_roless
                case '6-Contributor Sources Roles':
                    return this.defaultSelections.cont_roless
                case '7-Types':
                    return this.defaultSelections.types
            }
            return ['No data']
        }
    },
    methods: {
        ...mapActions([
            'saveDataPiece',
            'addContributor',
            'formatAndSaveDate',
            'removeContributor'
        ]),
        addItem() {
            this.filteredItems.push(this.newItemName);
        },
        removeItem(index) {
            this.items.splice(index, 1);
        },
        saveData () {
            this.saveDataPiece()
        }
    }
}
</script>
