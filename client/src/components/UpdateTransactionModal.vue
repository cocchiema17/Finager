<template>
  <div
    class="modal fade"
    tabindex="-1"
    aria-hidden="true"
    data-bs-backdrop="static"
    data-bs-keyboard="false"
    id="updateTransactionModal"
  >
    <div class="modal-dialog modal-dialog-centered">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5 text-center">Update Transaction</h1>
        </div>
        <div class="modal-body">
          <form
            ref="upForm"
            novalidate
            :class="{ 'was-validated': formValidated }"
          >
            <div class="mb-3">
              <label class="form-label">Title</label>
              <input
                class="form-control"
                id="title"
                v-model="title"
                required
                minlength="3"
                maxlength="40"
              />
            </div>

            <div class="mb-3">
              <label class="form-label">Description</label>
              <input
                class="form-control"
                type="text"
                v-model="description"
                maxlength="200"
              />
            </div>

            <div class="mb-3">
              <label class="form-label">Date</label>
              <input
                class="form-control"
                type="date"
                v-model="date"
                required
                :max="new Date().toISOString().split('T')[0]"
              />
            </div>

            <div class="mb-3">
              <label for="amount" class="form-label">Amount</label>
              <MoneyInput v-model="value" required />
            </div>
          </form>
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-secondary"
            data-bs-dismiss="modal"
            @click.prevent="onClose"
            ref="upCloseBtn"
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
import { updateTransaction } from "../api";
import MoneyInput from "./MoneyInput";
import { TYPE } from "vue-toastification";

export default {
  name: "UpdateTransactionModalComp",
  computed: {
    ...mapGetters(["spaces", "categories"]),
  },
  components: { MoneyInput },
  data() {
    return {
      title: "",
      description: "",
      date: "",
      value: null,
      formValidated: false,
      txId: null,
    };
  },
  methods: {
    async onSave() {
      console.log("saving");
      const form = this.$refs.upForm;
      const closeBtn = this.$refs.upCloseBtn;

      if (form.checkValidity()) {
        try {
          await updateTransaction(this.txId, {
            title: this.title,
            description: this.description,
            date: this.date,
            value: this.value,
          });

          this.formValidated = false;
          this.$emit("tx-updated");
          closeBtn.click();
          this.newToast("Transaction updated", TYPE.SUCCESS);
        } catch (err) {
          this.newToast("Transaction update failed", TYPE.ERROR);
        }
      } else {
        this.formValidated = true;
      }
    },
    setTx(tx) {
      this.txId = tx.id;
      this.title = tx.title;
      this.description = tx.description;
      this.date = tx.transactionDate,
      this.value = tx.value;
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
