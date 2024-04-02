<template>
    <div class="home">
        <!-- Header section -->
        <HomeBar />

        <!-- First section -->
        <section>
            <v-img src="@/assets/logoCuadrado.png" alt="Static Image" cover max-height="500" />
        </section>
        <!-- Second section -->
        <section>
            <v-container>
                <v-row>
                    <v-spacer></v-spacer>
                    <div class="follow-us">
                        <v-card-title class="d-flex align-center justify-center">Follow us:</v-card-title>
                        <div class="social-media-buttons">
                        <v-btn
                            v-for="s in social"
                            :key="s.icon"
                            :icon="s.icon"
                            :href="s.link"
                            class="mx-2"
                            variant="text"
                        ></v-btn>
                        </div>
                    </div>
                    <v-spacer></v-spacer>
                </v-row>
            </v-container>
            <v-divider></v-divider>
            <v-container>
                <v-row>
                    <v-col cols="6" class="d-flex align-center justify-center">
                        <v-card class="v-col-5">
                            <iframe src="https://www.facebook.com/plugins/page.php?href=https%3A%2F%2Fwww.facebook.com%2FcopoemE&tabs=timeline&width=340&height=500&small_header=false&adapt_container_width=true&hide_cover=false&show_facepile=true&appId" width="340" height="500" style="border:none;overflow:hidden" scrolling="no" frameborder="0" allowfullscreen="true" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe>
                        </v-card>
                    </v-col>
                    <v-divider vertical></v-divider>
                    <v-col cols="6">
                        <h2>Digifolk</h2>
                        <p>{{this.resume}}</p>
                    </v-col>
                </v-row>
            </v-container>
        </section>
        <v-divider></v-divider>
        <!-- Third section -->
        <section>
            <v-container align="center">
                <v-card max-width="50%">
                    <v-row>
                        <v-col cols="3">
                            <v-list variant="tonal">
                                <v-list-item link title="Our goals" @click="showText(0)"></v-list-item>
                                <v-list-item link title="Research Fields" @click="showText(1)"></v-list-item>
                                <v-list-item link title="Methodology" @click="showText(2)"></v-list-item>
                                <v-list-item link title="Activities" @click="showText(3)"></v-list-item>
                            </v-list>
                        </v-col>
                        <v-col>
                            <v-container align="left" v-html="this.selectedText"></v-container>
                        </v-col>
                    </v-row>
                </v-card>
            </v-container>
        </section>
        <v-divider></v-divider>
        <!-- Fourth section -->
        <section>
            <v-container>
                <v-row class="partnership d-flex align-center justify-center">
                    <h2>Partnership</h2>
                </v-row> 
                <v-row class="partnership d-flex align-center justify-center">
                    <!-- Logos of the enterprises -->
                    <v-img src="@/assets/logo1.png" max-width="10%" alt="University of Salamanca (USAL)" class="mr-2" />
                    <v-img src="@/assets/logo2.png" max-width="7%" alt="University Complutense of Madrid (UCM)" class="mr-2" />
                    <v-img src="@/assets/logo3.png" max-width="10%" alt="PTNera" class="mr-2" />
                    <v-img src="@/assets/logo4.png" max-width="10%" alt="Institute of Engineering (INESC)" class="mr-2" />
                    <v-img src="@/assets/logo5.png" max-width="5%" alt="University of Coimbra (UC)" class="mr-2" />
                    <v-img src="@/assets/logo6.jpg" max-width="5%" alt="Irish Traditional Music Archive (ITMA)" class="mr-2" />
                    <v-img src="@/assets/logo7.png" max-width="5%" alt="National Autonomous University of Mexico (UNAM)" class="mr-2" />
                </v-row>
            </v-container>
        </section>

        <v-footer class="bg-indigo-lighten-1 text-center d-flex flex-column">
            <v-row>
                <v-col class="d-flex justify-center align-center">
                    <v-img src="@/assets/SEPIE_erasmus_plus.gif" max-width="400"/>
                </v-col>
                <v-col class="d-flex align-center justify-end">
                    <div>
                        {{this.disclaimer }}
                    </div>
                </v-col>
            </v-row>

            <v-divider></v-divider>
        </v-footer>
    </div>
</template>

<script>
import HomeBar from '@/components/HomeBar.vue';

export default {
    data() {
        return {
            selectedText: '',
            social: [
                {
                    icon: 'mdi-facebook',
                    link: 'https://www.facebook.com/p/EA-Digifolk-100095030644127/?wtsid=rdr_0twLwdqJ62I424ZDF',
                },
                {
                    icon: 'mdi-instagram',
                    link: 'https://www.instagram.com/eadigifolk?igsh=c2N2aTFpemw0cDY0',
                },
            ],
            text: [
                '<ol> <li>Create a new paradigm to make the musical and ethnomusicological analysis easier for the community. In this pillar, our specific goals are: <ul> <li>Propose a standardised methodology to collect folk music.</li> <li>Propose a standard model that allows a uniform analysis of the repertoire collected.</li> <li>Create a corpus as a case study to show the possibilities that the platform offers, and that reflect the idiosyncrasies of the cultures involved.</li> </ul> </li> <li>Show knowledge discovery through the application of new technologies in the platform: EA-DIGIFOLK is intended as a computing platform that joins musical knowledge with computational techniques. Our specific goals in this pillar are: <ul> <li>To review in detail and design new algorithms related to Musical Information Retrieval (MIR) techniques adapted to the specific properties of folk music. This includes the study, definition and development of models that allows the extraction of knowledge to compare different popular music, highlighting the differences and similarities that makes us European folk.</li> <li>To review in detail and design new algorithms related to Natural Language Processing (NLP) adapted to the languages involved, namely Spanish, Portuguese and English. This includes the study, definition and development of models that allows the extraction of knowledge to compare lyrics in folk music, highlighting the differences and similarities.</li> <li>To develop a visual grammar to show the dataset (scores, audio files) and analysis outcomes (patterns, lyrics information, etc).</li> <li>To technically design and create a collaborative section for any user that aims to discuss the materials uploaded or that intends to submit new materials to expand the investigations.</li> </ul> </li> <li>Bring folk music to educational and public environments: We aim to take folk music to educational institutions, such as schools, music academies and conservatoires. Our specific goals are: <ul> <li>To design a plan that makes the incorporation of such repertoires in educational institutions easier</li> <li>To help teachers to show their students folk music through the proposal and dissemination of training activities specifically designed.</li> <li>To attract students and young people to this repertoire as a way to understand their cultures and heritage.</li> <li>To incorporate public participation through the creation and design of a collaborative section in the platform which allows to upload folk material, discuss about the repertoires and collaborate with the edition or correction of the material published. This activity will always be monitored by an administrator that supervises the material uploaded to the platform.</li> </ul> </li> </ol>',
                '<ul> <li>Music Education</li> <li>Musicology</li> <li>Computer Science</li></ul>',
                '<ol> <li>Analyse and to evaluate published/developed proposals</li> <li>Recognize the computational and musical requirements (digital formats, computing technologies, programming languages, hardware requirements, server configuration, etc.)</li> <li>Implement a solution-generation process</li> <li>Iteratively develop a solution prototype</li> <li>Integrate a solution with what has been developed in other work packages.</li> <li>Validate results.</li> </ol>',
                '<ol> <li>Coordination/Management</li> <li>Corpus design and creation</li> <li>Design and music analysis</li> <li>Multimodal folk music</li> <li>Text analysis</li> <li>Data visualization</li> <li>Education Plans</li> <li>Communication/Dissemination</li> </ol>'
            ],
            resume: 'Music is an element that is present in our daily lives. There are different styles of music, including classical, jazz, pop, rock, etc. There is a kind of music, folk music, which is of great interest due to its peculiar characteristics and the social context it represents or has represented. This music is a form of social and cultural identification that allows us to twin and recognize ourselves as folks, and also to promote cultural diversity through knowledge of other music. This project proposes creating a platform that contains and presents information about folk music from European and Iber-American culture. The main goal is to create a whole paradigm in which folk music can be understandable from a ethnomusicological, musical and educative point of view. Furthermore, we aim to bring folk music closer to the public creating an interactive and attractive platform that incorporate multimedia information (audio files, scores, visual information about patterns and similarities, etc.). As the platform will be open to the common public, all people that might be interested in folk music can get access, enjoy the resources or even submit their own materials. Our goal is aligned with three main pillars: i) Create a new paradigm to make the musical and ethnomusicological analysis easier for the community; ii) Show knowledge discovery through the application of new technologies in the platform; iii) Bring folk music to educative and public environments. Our project complies with the digitalization pillars proposed in the strategic plan of MSCA, through the inclusion of computer sciences technologies to get a new vision in music analysis. It also helps to create a more resilient, inclusive and democratic European society and includes actions that are also mentioned in the cluster “Culture, Creative and Inclusive Society”, through the inclusion of folk repertoires that reflect cultural issues from different European and Iber-American regions.',
            disclaimer: 'DISCLAIMER: This project has been funded with support from the European Commission. This publication reflects the views only of the author, and the Commission cannot be held responsible for any use which may be made of the information contained therein.'
        };
    },
    components: {
        HomeBar
    },
    methods: {
        showText(index) {
            this.selectedText = this.text[index];
        }
    }
};
</script>

<style scoped>
    .home {
        background-color: white;
    }
</style>