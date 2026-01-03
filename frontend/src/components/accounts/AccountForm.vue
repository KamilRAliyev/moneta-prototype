<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { Button } from "@/components/ui/button";
import { useAccountMeta } from "../../composables/useAccountMeta";
import DateLockField from "./DateLockField.vue";
import type {
  Account,
  AccountCreateRequest,
  AccountUpdateRequest,
} from "../../types/accounts";

interface Props {
  account?: Account | null;
  isLoading?: boolean;
  error?: string | null;
}

interface Emits {
  (e: "submit", payload: AccountCreateRequest | AccountUpdateRequest): void;
  (e: "cancel"): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const { fetchMeta, isLoading: isLoadingMeta } = useAccountMeta();

// Form state
const name = ref("");
const institution = ref("");
const currency = ref("");
const accountType = ref("");
const economicArea = ref<string | null>(null);
const datelockFrom = ref<string | null>(null);
const datelockTo = ref<string | null>(null);

// Meta options
const accountTypes = ref<Array<{ value: string; label: string }>>([]);
const economicAreas = ref<Array<{ value: string; label: string }>>([]);
const currencies = ref<Array<{ code: string; name: string; digits: number }>>(
  [],
);

// Form errors
const errors = ref<Record<string, string>>({});

// Load meta options
onMounted(async () => {
  try {
    const meta = await fetchMeta();
    accountTypes.value = meta.account_types;
    economicAreas.value = meta.economic_areas;
    currencies.value = meta.currencies;
  } catch (err) {
    console.error("Failed to load meta options:", err);
  }

  // Pre-fill form if editing
  if (props.account) {
    name.value = props.account.name;
    institution.value = props.account.institution;
    currency.value = props.account.currency;
    accountType.value = props.account.account_type;
    economicArea.value = props.account.economic_area;
    datelockFrom.value = props.account.datelock_from;
    datelockTo.value = props.account.datelock_to;
  }
});

const isEditMode = computed(() => !!props.account);

const validate = (): boolean => {
  errors.value = {};

  if (!name.value.trim()) {
    errors.value.name = "Account name is required";
  }

  if (!institution.value.trim()) {
    errors.value.institution = "Institution is required";
  }

  if (!currency.value) {
    errors.value.currency = "Currency is required";
  }

  if (!accountType.value) {
    errors.value.accountType = "Account type is required";
  }

  // Validate date lock range
  if (datelockFrom.value && datelockTo.value) {
    if (new Date(datelockFrom.value) > new Date(datelockTo.value)) {
      errors.value.datelock = "From date must be less than or equal to To date";
    }
  }

  return Object.keys(errors.value).length === 0;
};

const handleSubmit = () => {
  if (!validate()) {
    return;
  }

  const payload: AccountCreateRequest | AccountUpdateRequest = {
    name: name.value.trim(),
    institution: institution.value.trim(),
    currency: currency.value,
    account_type: accountType.value,
    economic_area: economicArea.value || null,
    datelock_from: datelockFrom.value || null,
    datelock_to: datelockTo.value || null,
  };

  emit("submit", payload);
};

const handleCancel = () => {
  emit("cancel");
};
</script>

<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <!-- Name -->
    <div>
      <label for="name" class="block text-sm font-medium text-foreground">
        Account Name <span class="text-red-500">*</span>
      </label>
      <input
        id="name"
        v-model="name"
        type="text"
        required
        class="mt-1 block w-full px-3 py-2 border border-input rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-ring focus:border-ring bg-background text-foreground"
        :class="{ 'border-destructive': errors.name }"
      />
      <p v-if="errors.name" class="mt-1 text-sm text-destructive">
        {{ errors.name }}
      </p>
    </div>

    <!-- Institution -->
    <div>
      <label
        for="institution"
        class="block text-sm font-medium text-foreground"
      >
        Institution <span class="text-red-500">*</span>
      </label>
      <input
        id="institution"
        v-model="institution"
        type="text"
        required
        class="mt-1 block w-full px-3 py-2 border border-input rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-ring focus:border-ring bg-background text-foreground"
        :class="{ 'border-red-500': errors.institution }"
      />
      <p
        v-if="errors.institution"
        class="mt-1 text-sm text-red-600 dark:text-red-400"
      >
        {{ errors.institution }}
      </p>
    </div>

    <!-- Currency -->
    <div>
      <label for="currency" class="block text-sm font-medium text-foreground">
        Currency <span class="text-red-500">*</span>
      </label>
      <select
        id="currency"
        v-model="currency"
        required
        class="mt-1 block w-full px-3 py-2 border border-input rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-ring focus:border-ring bg-background text-foreground"
        :class="{ 'border-red-500': errors.currency }"
        :disabled="isLoadingMeta"
      >
        <option value="">Select currency...</option>
        <option v-for="curr in currencies" :key="curr.code" :value="curr.code">
          {{ curr.code }} - {{ curr.name }}
        </option>
      </select>
      <p
        v-if="errors.currency"
        class="mt-1 text-sm text-red-600 dark:text-red-400"
      >
        {{ errors.currency }}
      </p>
    </div>

    <!-- Account Type -->
    <div>
      <label
        for="accountType"
        class="block text-sm font-medium text-foreground"
      >
        Account Type <span class="text-red-500">*</span>
      </label>
      <select
        id="accountType"
        v-model="accountType"
        required
        class="mt-1 block w-full px-3 py-2 border border-input rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-ring focus:border-ring bg-background text-foreground"
        :class="{ 'border-red-500': errors.accountType }"
        :disabled="isLoadingMeta"
      >
        <option value="">Select account type...</option>
        <option
          v-for="type in accountTypes"
          :key="type.value"
          :value="type.value"
        >
          {{ type.label }}
        </option>
      </select>
      <p
        v-if="errors.accountType"
        class="mt-1 text-sm text-red-600 dark:text-red-400"
      >
        {{ errors.accountType }}
      </p>
    </div>

    <!-- Economic Area -->
    <div>
      <label
        for="economicArea"
        class="block text-sm font-medium text-foreground"
      >
        Economic Area
      </label>
      <select
        id="economicArea"
        v-model="economicArea"
        class="mt-1 block w-full px-3 py-2 border border-input rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-ring focus:border-ring bg-background text-foreground"
        :disabled="isLoadingMeta"
      >
        <option :value="null">None</option>
        <option
          v-for="area in economicAreas"
          :key="area.value"
          :value="area.value"
        >
          {{ area.label }}
        </option>
      </select>
    </div>

    <!-- Date Lock -->
    <DateLockField
      :datelock-from="datelockFrom"
      :datelock-to="datelockTo"
      :error="errors.datelock"
      @update:datelock-from="datelockFrom = $event"
      @update:datelock-to="datelockTo = $event"
    />

    <!-- Error Message -->
    <div
      v-if="props.error"
      class="p-4 bg-destructive/10 border border-destructive/20 rounded-md"
    >
      <p class="text-sm text-destructive">
        {{ props.error }}
      </p>
    </div>

    <!-- Actions -->
    <div
      class="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700"
    >
      <Button type="button" @click="handleCancel" variant="outline">
        Cancel
      </Button>
      <Button type="submit" :disabled="props.isLoading || isLoadingMeta">
        {{
          props.isLoading
            ? "Saving..."
            : isEditMode
              ? "Save Changes"
              : "Create Account"
        }}
      </Button>
    </div>
  </form>
</template>
