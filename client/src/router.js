
import { createRouter, createWebHistory } from 'vue-router';

import Intro from "./views/Intro";
import Home from "./views/Home";
import Chat from "./views/Chat";
import Login from "./views/Login";
import Register from "./views/Register";
import NotFound from "./views/NotFound";

import { getCurrentUser } from "./api";
import vuex from "./vuex";

const routes = [
  {
    path: "/",
    name: "Intro",
    component: Intro
  },
  {
    path: "/home",
    name: "Home",
    component: Home,
    meta: {
      requiresAuth: true
    },
  },
  {
    path: "/chat",
    name: "Chat",
    component: Chat,
    meta: {
      requiresAuth: true
    }
  },
  {
    path: "/login",
    name: "Login",
    component: Login,
    meta: {
      requiresGuest: true
    },
  },
  {
    path: "/register",
    name: "Register",
    component: Register,
    meta: {
      requiresGuest: true
    },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach(async (to, from, next) => {
  const requiresAuth = to.matched.some((x) => x.meta.requiresAuth);
  const requiresGuest = to.matched.some((x) => x.meta.requiresGuest);

  let logged = vuex.getters.isLogged;

  if (!logged) {
    try {
      const user = await getCurrentUser();
      if (Object.keys(user).length > 0) {
        vuex.commit('user', user);
        vuex.commit('isLogged', true);
        logged = true;
      } else {
        vuex.commit('isLogged', false);
        logged = false;
      }
    } catch (err) {
      logged = false;
    }
  }

  if (requiresAuth && !logged) {
    next("/login");
  } else if (requiresGuest && logged) {
    next("/home");
  } else {
    next();
  }
});

export default router;