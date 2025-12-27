import { createRouter, createWebHistory } from "vue-router";
import AppShell from "../layouts/AppShell.vue";
import Home from "../views/Home.vue";
import AccountsList from "../views/accounts/AccountsList.vue";
import AccountCreate from "../views/accounts/AccountCreate.vue";
import AccountDetail from "../views/accounts/AccountDetail.vue";
import Statements from "../views/statements/Statements.vue";
import Transactions from "../views/transactions/Transactions.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      component: AppShell,
      children: [
        {
          path: "",
          name: "home",
          component: Home,
        },
        {
          path: "accounts",
          name: "accounts",
          component: AccountsList,
        },
        {
          path: "accounts/new",
          name: "account-create",
          component: AccountCreate,
        },
        {
          path: "accounts/:id",
          name: "account-detail",
          component: AccountDetail,
        },
        {
          path: "statements",
          name: "statements",
          component: Statements,
        },
        {
          path: "transactions",
          name: "transactions",
          component: Transactions,
        },
      ],
    },
  ],
});

export default router;
