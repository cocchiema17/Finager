<template>
  <div class="centered-form-wrapper container-fluid bg-app">
    <form class="centered-form" @submit.prevent="onSubmit" novalidate>
      <h1 class="display-6 mb-5 text-center">Accedi a Finager!</h1>

      <div class="form-floating mb-3">
        <input
          type="email"
          :class="{ 'form-control': true, 'is-invalid': errors.email }"
          id="email"
          v-model="email"
          placeholder="name@example.com"
        />
        <div v-if="this.errors.email" class="invalid-feedback d-block">
          {{ errors.email }}
        </div>
        <label for="email">Indirizzo email</label>
      </div>
      <div class="form-floating mb-3">
        <input
          type="password"
          :class="{ 'form-control': true, 'is-invalid': errors.password }"
          name="password"
          v-model="password"
          maxlength="50"
          placeholder="Password"
        />
        <div v-if="this.errors.password" class="invalid-feedback d-block">
          {{ errors.password }}
        </div>
        <label for="password">Password</label>
      </div>
      <div class="d-grid gap-2">
        <button
          :disabled="!isSubmitEnabled"
          :class="[
            'btn',
            {
              'btn-primary': !loginFailed,
              'btn-danger': loginFailed,
              shake: loginFailed,
            },
          ]"
        >
          Accedi
        </button>

        <div class="hr-sect mt-3">o</div>

        <router-link class="btn btn-outline-primary mt-3" to="register">
          Registrati
        </router-link>
      </div>
    </form>
  </div>
</template>

<script>
import { AxiosError } from "axios";
import { login } from "../api";
import { TYPE } from "vue-toastification";

export default {
  name: "LoginView",
  data() {
    return {
      email: "",
      password: "",
      errors: {},
      isValid: {
        email: false,
        password: false,
      },
      loginFailed: false
    };
  },
  computed: {
    isSubmitEnabled() {
      return Object.values(this.isValid).every((v) => v === true);
    },
  },
  watch: {
    email(value) {
      const l = this.length(value);
      let msg = null;

      if (l == 0) msg = "Email is required";
      else if (!/^[^@]+@\w+(\.\w+)+\w$/.test(value)) msg = "Not an email";

      this.isValid.email = msg == null;
      this.errors.email = msg;
    },
    password(value) {
      const l = this.length(value);
      let msg = null;

      if (l == 0) msg = "Password is required";
      else if (l < 3) msg = "Password not valid";
      else if (l > 50) msg = "Password not valid";

      this.isValid.password = msg == null;
      this.errors.password = msg;
    },
  },
  methods: {
    length(value) {
      return value && value.length ? value.length : 0;
    },
    async onSubmit() {
      try {
        const data = await login(this.email, this.password);

        this.$store.dispatch("user", data.user || data);
        this.$store.dispatch("isLogged", true);
        this.$router.push("/home");
      } catch (err) {
        if (err instanceof AxiosError) {
          if (err.response.status == 400 || err.response.status == 401) {
            this.newToast("Credenziali non valide", TYPE.ERROR);
          } else {
            this.newToast("Qualcosa è andato storto", TYPE.ERROR);
          }
          this.loginFailed = true;
          setTimeout(() => {
            this.loginFailed = false;
          }, 3000);
        }
      }
    },
  },
};
</script>

<style scoped>
.shake {
  animation: shake 0.8s;
  animation-iteration-count: 1;
}

@keyframes shake {
  0% {
    transform: translateX(0px);
  }
  10% {
    transform: translateX(10px);
  }
  20% {
    transform: translateX(-10px);
  }
  30% {
    transform: translateX(10px);
  }
  40% {
    transform: translateX(-10px);
  }
  50% {
    transform: translateX(10px);
  }
  60% {
    transform: translateX(-10px);
  }
  70% {
    transform: translateX(10px);
  }
  80% {
    transform: translateX(-10px);
  }
  90% {
    transform: translateX(10px);
  }
  100% {
    transform: translateX(-10px);
  }
}

.forgot-password,
.forgot-password a {
  text-align: right;
}

.hr-sect {
  display: flex;
  flex-basis: 100%;
  align-items: center;
  color: grey;
  margin: 8px 0px;
}

.hr-sect:before,
.hr-sect:after {
  content: "";
  flex-grow: 1;
  background: rgba(0, 0, 0, 0.35);
  height: 1px;
  font-size: 0px;
  line-height: 0px;
  margin: 0px 8px;
}
</style>