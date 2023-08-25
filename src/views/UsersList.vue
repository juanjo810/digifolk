<template>
  <v-container>
    <h1>Lista de Usuarios</h1>
    <user-dropdown
      v-for="(user, index) in users"
      :key="index"
      :user="user"
      :index="index"
    /></v-container>
</template>

<script>
import { mapState, mapActions } from "vuex";
import UserDropdown from "@/components/UserDropdown.vue";

export default {
  components: {
    UserDropdown
  },
  computed: {
    ...mapState(["users"]),
  },
  methods: {
    ...mapActions([
      "getUserInfo",
      "fetchUsers"
    ]),
  },
  mounted() {
    this.fetchUsers();
  }
};
</script>
