<template>
  <v-container>
    <v-row>
      <v-col>
        <h1>Information about the MusicXML file</h1>
        <div>
          <template>
            <v-progress-linear
              color="deep-purple"
              height="10"
              indeterminate
            ></v-progress-linear>
          </template>
          <v-card-text>
            <v-row>

              <v-col cols="4">
                <v-text-field
                  v-model="this.title"
                  label="Title*"
                  :rules="rules"
                  hint="Use ' | ', i.e. space colon space, to separate title and subtitle. Use ' = ' i.e. space equals space, where a title is available in different languages"
                  persistent-hint
                ></v-text-field>
              </v-col>

              <v-col cols="4">
                <v-select
                  v-model="this.right"
                  label="Rights*"
                  :items="getItemsNameByType(1)"
                ></v-select>
              </v-col>

              <v-col cols="4">
                <v-text-field
                  v-model="this.creator"
                  label="Creator*"
                  :rules="rules"
                ></v-text-field>
              </v-col>

              <v-col cols="6">
                <v-date-picker
                  v-model="this.selectedDate"
                  @update:modelValue="formatDate"
                ></v-date-picker>
              </v-col>
              <v-col cols="6">
                <h2>Selected date*: {{ this.date }}</h2>
              </v-col>

              <v-col cols="6">
                <v-select
                  v-model="this.type"
                  label="Type"
                  :items="getItemsNameByType(7)"
                  :rules="rules"
                ></v-select>
              </v-col>

              <v-col cols="6">
                <v-text-field
                  v-model="this.publisher"
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
                      persistent-hint
                    ></v-text-field>
                    <span>
                      <a href="http://www.dib.ie" target="_blank">URI examples</a>
                    </span>
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
                <v-text-field
                  v-model="this.description"
                  label="Description"
                ></v-text-field>
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
import { mapActions, mapGetters, mapState } from "vuex";
import { VDatePicker } from "vuetify/labs/VDatePicker";

export default {
  components: {
    VDatePicker,
  },
  data() {
    return {
      rules: [(value) => !!value || "Required."],
      contribuidores: [],
      selectedDate: null,
      id: "XX-XXXX-XX-XX-X",
    };
  },
  computed: {
    ...mapState(["error", "pieceForm", "defaultSelections"]),
    ...mapGetters(["getItemsNameByType"]),
    /*id: {
      get() {
        return this.pieceForm.identifier;
      },
      set(value) {
        this.$store.commit("UPDATE_USER_ID", value);
      },
    },*/
    title: {
      get() {
        return this.pieceForm.title;
      },
      set(value) {
        this.$store.commit("UPDATE_USER_TITLE", value);
      },
    },
    right: {
      get() {
        return this.pieceForm.rights;
      },
      set(value) {
        this.$store.commit("UPDATE_USER_RIGHT", value);
      },
    },
    creator: {
      get() {
        return this.pieceForm.creator;
      },
      set(value) {
        this.$store.commit("UPDATE_USER_CREATOR", value);
      },
    },
    date() {
      return this.pieceForm.date;
    },
    type: {
      get() {
        return this.pieceForm.type_file;
      },
      set(value) {
        this.$store.commit("UPDATE_USER_TYPE", value);
      },
    },
    publisher: {
      get() {
        return this.pieceForm.publisher;
      },
      set(value) {
        this.$store.commit("UPDATE_USER_PUBLISHER", value);
      },
    },
    contributor() {
      return this.pieceForm.contributor_role;
    },
    description: {
      get() {
        return this.pieceForm.desc;
      },
      set(value) {
        this.$store.commit("UPDATE_USER_DESCRIPTION", value);
      },
    },
  },
  methods: {
    ...mapActions([
      "saveDataPiece",
      "addContributor",
      "formatAndSaveDate",
      "removeContributor",
      "resetPieceForm",
      "importDataFromExcel",
      "importDataFromMEI",
    ]),
    saveData() {
      if (this.pieceForm.rightsp !== "" && this.pieceForm.creatorp_role.length > 0 && this.pieceForm.datep !== "" &&
        this.title !== "" && this.rights !== "" && this.creator !== "" && this.date !== "") {
        this.saveDataPiece();
      } else {
        alert("Please fill in all the required fields");
      }
    },
    addFields() {
      this.addContributor("User");
      this.contribuidores.push({ name: "", role: "" });
    },
    removeField(index) {
      this.removeContributor({ index: index, form: "User" });
      this.contribuidores.splice(index, 1);
    },
    updateContributor() {
      this.$store.commit("UPDATE_USER_CONTRIBUTOR", this.contribuidores);
    },
    formatDate() {
      if (this.selectedDate.length > 0) {
        this.formatAndSaveDate({ date: this.selectedDate, form: "User" });
      } else {
        alert("Please select a date");
      }
    },
  },
  created() {
    this.contribuidores = structuredClone(this.contributor);
  },
};
</script>
