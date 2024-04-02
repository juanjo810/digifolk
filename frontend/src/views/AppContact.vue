<template>
    <div>
        <HomeBar />
        <section class="contact-info">
            <div class="gmap-area">
                <v-container class="container">
                    <v-row class="row">
                        <v-col class="d-flex align-center justify-center" cols="7">
                            <div class="circle">
                                <div class="iframe-container">
                                    <iframe frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://maps.google.com/maps?width=100%&amp;height=600&amp;hl=en&amp;q=Facultad%20de%20ciencias%2C%20salamanca%2C%20espa%C3%B1a+(Facultad%20de%20ciencias)&amp;ie=UTF8&amp;t=&amp;z=14&amp;iwloc=B&amp;output=embed"></iframe>
                                </div>
                            </div>
                        </v-col>

                        <v-col class="d-flex align-center justify-center" cols="2">
                            <ul class="list">
                                <li class="col-sm-6">
                                    <address>
                                        <h3>María Navarro Cáceres</h3>

                                        <p>Address:<br>
                                            Facultad de Ciencias <br>
                                            Plaza de los caídos s/n
                                            <br>37008, Salamanca, Spain</p>
                                        <p>Phone:+34-923294500 <br>
                                            Email: maria90@usal.es</p>
                                    </address>
                                </li>
                            </ul>
                        </v-col>
                    </v-row>
                </v-container>
            </div>
        </section>
    </div>
</template>

<script>
import HomeBar from '@/components/HomeBar.vue';

export default {
    name: 'AppContact',
    components: {
        HomeBar
    }
};
</script>

<style scoped>
    .gmap-area{
        background-image: url('@/assets/mapa.png');
        background-color: rgba(0, 0, 0, 0.5);
        background-size: cover;
    }
    .circle {
    width: 300px; /* ajusta el tamaño del círculo según sea necesario */
    height: 300px;
    border-radius: 50%; /* establece el borde redondeado para crear un círculo */
    overflow: hidden; /* oculta cualquier contenido que se salga del círculo */
    }
    
    .iframe-container {
    width: 100%;
    height: 100%;
    }

    .iframe-container iframe {
    width: 100%;
    height: 100%;
    border: 0; /* elimina cualquier borde del iframe */
    }
    .list{
        list-style-type: none;
    }
</style>