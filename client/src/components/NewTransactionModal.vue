<template>
  <div
    class="modal fade"
    :id="name"
    tabindex="-1"
    aria-hidden="true"
    data-bs-backdrop="static"
    data-bs-keyboard="false"
  >
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5 text-center">Add Transaction</h1>
        </div>
        <div class="modal-body">
          <form
            ref="txForm"
            novalidate
            :class="{ 'was-validated': formValidated }"
          >
            <div class="mb-3">
              <label for="title" class="form-label">Title</label>
              <input
                class="form-control"
                type="text"
                id="title"
                v-model="title"
                required
                minlength="3"
                maxlength="40"
              />
            </div>

            <div class="mb-3">
              <label for="description" class="form-label">Description</label>
              <input
                class="form-control"
                type="text"
                id="description"
                v-model="description"
                maxlength="200"
              />
            </div>

            <div class="mb-3">
              <label for="date" class="form-label">Date</label>
              <input
                class="form-control"
                type="date"
                id="date"
                v-model="date"
                required
                :max="new Date().toISOString().split('T')[0]"
              />
            </div>

            <div class="row g-3">
              <div class="col">
                <label for="category" class="form-label">Category</label>
                <input
                  class="form-control"
                  v-model="categoryName"
                  id="category"
                  list="categoriesSuggest"
                  @change="onChangeCategory"
                  required
                />
                <datalist id="categoriesSuggest">
                  <option v-for="c in categories" :key="c.id">
                    {{ c.name }}
                  </option>
                </datalist>
              </div>
              <div class="col">
                <label class="form-label" for="color"> Color </label>
                <input
                  class="form-control"
                  style="height: 38px"
                  type="color"
                  v-model="color"
                  id="color"
                  :disabled="!this.colorPickerEnabled"
                />
              </div>
            </div>

            <div class="row g-3 mt-1 mb-2">
              <div class="col">
                <label for="space" class="form-label">Space</label>
                <select
                  class="form-control"
                  v-model="spaceIdx"
                  id="space"
                  required
                >
                  <option v-for="(s, idx) in spaces" :key="idx" :value="idx">
                    {{ s.name }}
                  </option>
                </select>
              </div>
              <div class="col">
                <label for="amount" class="form-label">Amount</label>
                <MoneyInput v-model="value" required />
              </div>
            </div>
          </form>
        </div>

        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
            ref="closeBtn"
            @click.prevent="resetData"
          >
            Close
          </button>
          <button @click.prevent="onSave" type="button" class="btn btn-primary">
            Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from "vuex";
import { createTransaction } from "../api";
import MoneyInput from "./MoneyInput";
import { TYPE } from "vue-toastification";
import randomColor from "randomcolor";

export default {
  name: "NewTransactionModalComp",
  computed: {
    ...mapGetters(["spaces", "categories"]),
  },
  components: { MoneyInput },
  props: ["name"],
  data() {
    return {
      title: "",
      description: "",
      date: "",
      categoryName: "",
      spaceIdx: 0,
      color: randomColor({ format: "hex" }),
      value: null,
      formValidated: false,
      colorPickerEnabled: true,
    };
  },
  methods: {
    async onSave() {
      const form = this.$refs.txForm;
      const closeBtn = this.$refs.closeBtn;

      if (form.checkValidity()) {
        try {
          const tx = await createTransaction({
            title: this.title,
            description: this.description,
            date: this.date,
            categoryName: this.categoryName,
            color: this.color,
            spaceId: this.spaces[this.spaceIdx].id,
            value: this.value,
          });

          (tx.spaceName = this.spaces[this.spaceIdx].name),
            (this.formValidated = false);

          this.$emit("new-tx", tx);
          closeBtn.click();
          this.newToast("Transaction added", TYPE.SUCCESS);
          this.resetData();
        } catch (err) {
          console.log(err);
          this.newToast("Transaction creation failed", TYPE.ERROR);
        }
      } else {
        this.formValidated = true;
      }
    },
    onChangeCategory() {
      const selectedCategory = this.categories.find(
        (c) => c.name == this.categoryName
      );
      if (selectedCategory) {
        this.color = selectedCategory.color;
        this.colorPickerEnabled = false;
      } else {
        this.color = randomColor({ format: "hex" });
        this.colorPickerEnabled = true;
      }
    },
    resetData() {
      this.title = "";
      this.description = "";
      this.date = "";
      this.categoryName = "";
      this.color = "";
    },
  },
};
</script>

<style scoped>
.form-control.no-validate:valid {
  border-color: #ced4da;
  padding-right: 0.75rem;
  background: none;
}
</style>
