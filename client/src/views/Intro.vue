<template>
  <main>
    <div class="container">
      <div id="chiSiamo">
        <img src="@/assets/finager-titolo.png" id="titolo" />
      </div>

      <p>
        Finager &egrave; una applicazione che ti permette di gestire e visualizzare le
        tue finanze.
        <br />
        Fai click su Accedi o Registrati in alto a destra per accedere alla tua
        area personale!
      </p>

      <div id="funzionalita">
        <h2><strong> Funzionalit&agrave; </strong></h2>
        <div>
          <div class="text-image-conteiner">
            <div
              class="div-image"
              :style="{
                backgroundImage: 'url(' + require('@/assets/space.png') + ')',
              }"
            ></div>

            <div class="text-element">
              <strong>Conti</strong>
              <br />
              <br />
              Crea uno o pi&ugrave; conti per gestire al meglio le tue finanze
            </div>
          </div>
        </div>

        <hr />

        <element ref="ele-1"></element>

        <div>
          <div
            class="text-image-conteiner content hidden inverted"
            ref="content-1"
          >
            <div class="text-element">
              <strong>Categorie</strong>
              <br />
              <br />
              Assegna delle etichette a ciascuna transazione in modo da poterle
              raggruppare ed identificare rapidamente!
            </div>
            <div
              class="div-image"
              :style="{
                backgroundImage:
                  'url(' + require('@/assets/category.png') + ')',
              }"
            ></div>
          </div>
        </div>

        <hr />

        <element ref="ele-2"></element>

        <div>
          <div class="text-image-conteiner content hidden" ref="content-2">
            <div
              class="div-image"
              :style="{
                backgroundImage:
                  'url(' + require('@/assets/exampleTable.png') + ')',
              }"
            ></div>
            <div class="text-element">
              <strong>Transazioni</strong>
              <br />
              <br />
              Una transazione rappresenta una entrata o un uscita all’interno di
              uno conto. Nella tua home avrai accesso ad una tabella dove
              poterle visualizzare, ordinare, filtrare, modificare, cancellare
              ed esportare in formato excel!
            </div>
          </div>
        </div>

        <hr />

        <element ref="ele-3"></element>

        <div>
          <div
            class="text-image-conteiner content hidden inverted"
            ref="content-3"
          >
            <div class="text-element">
              <strong>Grafici</strong>
              <br />
              <br />
              Ottieni una maggiore consapevolezza del tuo conto attraverso tre
              splenditi grafici: renditi conto a quanto ammontano le tue
              entrate e spese mensili, del valore del tuo conto e della
              suddivisione per categorie!
            </div>
            <div
              class="div-image"
              :style="{
                backgroundImage: 'url(' + require('@/assets/grafici.png') + ')',
              }"
            ></div>
          </div>
        </div>

        <hr />

        <element ref="ele-4"></element>

        <div>
          <div class="text-image-conteiner content hidden" ref="content-4">
            <div
              class="div-image"
              :style="{
                backgroundImage:
                  'url(' + require('@/assets/chat.png') + ')',
              }"
            ></div>
            <div class="text-element">
              <strong>Chatbot</strong>
              <br />
              <br />
              Finager IA &egrave; un assistente virtuale che ti aiuta a gestire le tue finanze.
              Puoi chiedere a Finager IA consigli su come gestire le tue finanze in base alle tue entrate e spese.
            </div>
          </div>
        </div>

        <hr />

      </div>
    </div>

    <Footer />
  </main>
</template>

<script>
import { mapGetters } from "vuex";

import Footer from "../components/Footer";
export default {
  name: "IntroPage",
  components: { Footer },
  computed: {
    ...mapGetters(["user"]),
  },
  mounted() {
    const contents = [
      this.$refs["content-1"],
      this.$refs["content-2"],
      this.$refs["content-3"],
      this.$refs["content-4"],
    ];

    const eles = [
      this.$refs["ele-1"],
      this.$refs["ele-2"],
      this.$refs["ele-3"],
      this.$refs["ele-4"],
    ];

    window.addEventListener("scroll", function () {
      for (let i = 0; i < contents.length; i++) {
        const rect = eles[i].getBoundingClientRect();
        const elePosition =
          rect.top + window.scrollY - window.innerHeight / 1.5;

        if (window.pageYOffset > elePosition) {
          contents[i].classList.add("visible");
          contents[i].classList.remove("hidden");
        }
      }
    });
  },
};
</script>

<style scoped>
a.nav-link {
  color: black;
}

.nav-link {
  padding: 16px 8px;
}

#chiSiamo {
  margin-top: 30px;
  padding: 20px;
  padding-top: 60px;
  background-image: url("@/assets/sfondo.jpg");
  background-position: center;
  background-repeat: no-repeat;
  background-size: cover;
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

#titolo {
  background-color: black;
  padding: 10px;
  height: 200px;
  width: 300px;
}

p {
  background-color: #0d6efd;
  color: white;
  font-size: large;
  padding: 0 10px;
  margin-top: 30px;
  margin-bottom: 30px;
  filter: drop-shadow(0px 4px 3px #0d6efd);
}

strong {
  color: #0d6efd;
  font-size: larger;
}

#funzionalita {
  padding: 0 10px;
}

h2 {
  padding: 10px;
}

hr {
  color: #0d6efd;
  visibility: hidden;
}

#logo {
  height: 30px;
  width: 30px;
  border-radius: 8px;
}

a {
  color: #0d6efd;
}

.fa {
  padding: 15px;
  font-size: 20px;
  width: 10px;
  height: 10px;
  text-align: center;
  text-decoration: none;
  margin: 2px 2px;
  border-radius: 50%;
  color: #0d6efd;
}

.fa:hover {
  opacity: 0.7;
}

.text-image-conteiner {
  display: flex;
  padding-bottom: 30px;
}

.text-image-conteiner > div:nth-child(2) {
  margin-left: 10px;
}

.text-image-conteiner > div {
  border-radius: 20px;
  width: calc(50% - 5px);
}

.div-image {
  background-position: center;
  background-repeat: no-repeat;
  background-size: contain;
}

.text-element {
  padding: 10px;
}

/* ModalitÃ  mobile */
@media screen and (max-width: 740px) {
  .text-image-conteiner {
    flex-direction: column;
  }

  .div-image {
    height: 300px;
  }

  .text-image-conteiner > div {
    width: 100%;
  }

  .text-image-conteiner > div:nth-child(2) {
    margin-left: 0px;
    margin-top: 10px;
  }

  .text-image-conteiner.inverted > div:nth-child(2) {
    margin-left: 0px;
    margin-top: 0px;
    margin-bottom: 10px;
  }

  .text-image-conteiner.inverted {
    flex-direction: column-reverse;
  }

  hr {
    visibility: visible;
  }
}

.hidden {
  opacity: 0;
  transition: opacity 0.5s ease-in-out;
}

.visible {
  opacity: 1;
  transition: opacity 0.5s ease-in-out;
}
</style>
