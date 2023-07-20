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
                                  <template v-if="editingIndex === index">
                                    <v-list-item-content>
                                      <v-text-field v-model="nameEditing" @blur="endEditing(item)"></v-text-field>
                                    </v-list-item-content>
                                  </template>
                                  <template v-else>
                                    <v-list-item-content @dblclick="startEditing(index, item.name)">
                                      {{ item.name }}
                                    </v-list-item-content>
                                  </template>
                                    <v-list-item-action>
                                    <v-icon @click="removeItem(item)">mdi-close</v-icon>
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
import { mapActions, mapState, mapGetters } from 'vuex'

export default {
    data () {
        return{
            idItem: null,
            newItemName: '',
            editingIndex: -1,
            nameEditing: ''
        }
    },
    computed: {
        ...mapState([
            'defaultSelections'
        ]),
        ...mapGetters([
          'getItemsByType',
          'getMaxItemIdInType'
        ]),
        itemsIDs() {
            return this.defaultSelections.itemsIDs
        },
        filteredItems() {
            switch (this.idItem) {
                case '1-Rights':
                    return this.getItemsByType(1)
                case '2-XML Contributor Roles':
                    return this.getItemsByType(2)
                case '3-Creator Pieces Roles':
                    return this.getItemsByType(3)
                case '4-Contributor Pieces Roles':
                    return this.getItemsByType(4)
                case '5-Creator Sources Roles':
                    return this.getItemsByType(5)
                case '6-Contributor Sources Roles':
                    return this.getItemsByType(6)
                case '7-Types':
                    return this.getItemsByType(7)
            }
            return ['No data']
        }
    },
    methods: {
        ...mapActions([
            'saveDataPiece',
            'addContributor',
            'formatAndSaveDate',
            'addNewItem',
            'removeOneItem',
            'fetchItems',
            'editItem'
        ]),
        addItem() {
            const firstCharacter = this.idItem.charAt(0);
            const id_type = parseInt(firstCharacter, 10);
            const id = this.getMaxItemIdInType(id_type)
            this.addNewItem({id: id+1, id_type: id_type, newItem: this.newItemName})
            this.newItemName = ''
        },
        removeItem(item) {
            const firstCharacter = this.idItem.charAt();
            const id_type = parseInt(firstCharacter, 10);
            this.removeOneItem({item: item, id_type: id_type})
        },
        startEditing(index, name) {
          this.editingIndex = index
          this.nameEditing = name
        },
        endEditing(item) {
          const firstCharacter = this.idItem.charAt();
          const id_type = parseInt(firstCharacter, 10);
          this.editItem({id: item.id, id_type: id_type, newName: this.nameEditing})
          this.editingIndex = -1
        }
    },
    created () {
      this.fetchItems()
    }
}
</script>
