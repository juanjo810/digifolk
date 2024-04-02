<template>
    <header>
        <v-app-bar app color="blue" dark>
            <div class="d-flex align-center">
                <v-img alt="Digifolk Logo" class="shrink mr-2" contain src="@/assets/logo.png"
                    transition="scale-transition" width="60" style="cursor: pointer" />
                <v-img alt="UE Financiado" class="shrink mr-2" contain src="@/assets/ue.png" transition="scale-transition"
                    width="100" style="cursor: pointer" />
            </div>
            <v-list-item @click="$router.push({ name: 'home' })">
                <v-app-bar-title>Home</v-app-bar-title>
            </v-list-item>
            <v-list-item @click="$router.push({ name: 'contact' })">
                <v-app-bar-title>Contact</v-app-bar-title>
            </v-list-item>
            <v-spacer></v-spacer>
            <v-spacer></v-spacer>
            <v-spacer></v-spacer>
            <v-list-item @click="$router.push({ name: 'login' })">
                <v-app-bar-title>Login</v-app-bar-title>
            </v-list-item>
        </v-app-bar>
    </header>
</template>

<script>
export default {
    name: 'HomeBar',
}
</script>
