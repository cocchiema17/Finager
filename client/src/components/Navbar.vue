<template>
  <nav id="navbar" class="navbar body-tertiary border-bottom">
    <div class="container-fluid">
      <router-link :to="user ? '/home' : '/'" class="navbar-brand mb-0 h3 text-primary text-decoration-none">
        <img
          src="@/assets/trasparent-logo.png"
          height="30"
          width="35"
          class="me-1"
        />Finager
      </router-link>
      <ul class="nav nav-pills nav-fill align-items-center">

        <li class="nav-item" v-if="!user">
          <router-link to="/login" class="nav-link">Accedi</router-link>
        </li>

        <li class="nav-item" v-if="!user">
          <router-link to="/register" class="nav-link">Registrati</router-link>
        </li>

        <li class="nav-item" v-if="user && this.$route.name != 'Home'">
          <router-link to="/home" class="nav-link d-flex align-items-center gap-1">
            <i class="bi bi-house-door"></i>
            <span>Home</span>
          </router-link>
        </li>

        <li class="nav-item" v-if="user">
          <router-link
            to="/chat"
            class="nav-link d-flex align-items-center gap-1"
            :class="{ active: $route.name === 'Chat' }"
            title="Assistente Finanziario AI"
          >
            <i class="bi bi-robot fs-5"></i>
            <span class="d-none d-sm-inline">Finager AI</span>
          </router-link>
        </li>

        <li class="nav-item" v-if="user">
          <a @click="onLogout" href="javascript:void(0)" class="nav-link text-danger">
            Logout
          </a>
        </li>
      </ul>
    </div>
  </nav>
</template>

<script>
import { logout } from "../api";
import { mapGetters } from "vuex";

export default {
  name: "NavbarComp",
  computed: {
    ...mapGetters(["user"]),
  },
  methods: {
    async onLogout() {
      await logout();
      this.$store.dispatch("isLogged", false);
      this.$store.dispatch("user", null);
      this.$router.push("/");
    },
  },
};
</script>
