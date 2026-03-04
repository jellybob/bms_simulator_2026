<script setup>
import { ref } from "vue";

const props = defineProps({
  label: String,
  value: [Number, Boolean],
  unit: String,
  topic: String,
  overridden: Boolean,
  type: { type: String, default: "number" },
  icon: { type: String, default: "" },
});

const emit = defineEmits(["publish"]);
const editing = ref(false);
const inputValue = ref("");

function startEdit() {
  editing.value = true;
  if (props.type === "boolean") {
    inputValue.value = props.value ? "true" : "false";
  } else {
    inputValue.value = String(props.value);
  }
}

function submit() {
  if (props.type === "boolean") {
    emit("publish", `${props.topic}/set`, inputValue.value);
  } else {
    const val = parseFloat(inputValue.value);
    if (!isNaN(val)) {
      emit("publish", `${props.topic}/set`, String(val));
    }
  }
  editing.value = false;
}

function releaseOverride() {
  emit("publish", `${props.topic}/overridden/set`, "false");
}

function displayValue() {
  if (props.type === "boolean") {
    return props.value ? "OCCUPIED" : "VACANT";
  }
  if (typeof props.value === "number") {
    return props.value.toFixed(1);
  }
  return String(props.value);
}
</script>

<template>
  <div class="sensor-card" :class="{ overridden }">
    <div class="sensor-header">
      <span class="sensor-icon">{{ icon }}</span>
      <span class="sensor-label">{{ label }}</span>
      <span v-if="overridden" class="override-badge">OVR</span>
    </div>

    <div class="sensor-value" @click="startEdit">
      <template v-if="!editing">
        <span class="value">{{ displayValue() }}</span>
        <span class="unit" v-if="unit && type !== 'boolean'">{{ unit }}</span>
      </template>
      <form v-else @submit.prevent="submit" class="edit-form" @click.stop>
        <template v-if="type === 'boolean'">
          <select v-model="inputValue" autofocus>
            <option value="true">Occupied</option>
            <option value="false">Vacant</option>
          </select>
          <button type="submit">Set</button>
          <button type="button" @click="editing = false">Cancel</button>
        </template>
        <template v-else>
          <input
            v-model="inputValue"
            type="number"
            step="0.1"
            autofocus
            @keydown.escape="editing = false"
          />
          <button type="submit">Set</button>
          <button type="button" @click="editing = false">Cancel</button>
        </template>
      </form>
    </div>

    <button v-if="overridden" class="release-btn" @click="releaseOverride">
      Release Override
    </button>
  </div>
</template>

<style scoped>
.sensor-card {
  background: #1a2332;
  border: 1px solid #2a3a4a;
  border-radius: 8px;
  padding: 14px;
  transition: border-color 0.3s;
}

.sensor-card.overridden {
  border-color: #ffaa00;
}

.sensor-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.sensor-icon {
  font-size: 1.2rem;
}

.sensor-label {
  color: #8899aa;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.override-badge {
  margin-left: auto;
  background: #ffaa00;
  color: #1a2332;
  font-size: 0.6rem;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 3px;
  letter-spacing: 1px;
}

.sensor-value {
  cursor: pointer;
  min-height: 40px;
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.value {
  font-family: "Courier New", monospace;
  font-size: 1.8rem;
  font-weight: bold;
  color: #e0e8f0;
}

.unit {
  color: #556677;
  font-size: 0.9rem;
}

.edit-form {
  display: flex;
  gap: 6px;
  align-items: center;
}

.edit-form input,
.edit-form select {
  width: 100px;
  background: #0d1520;
  border: 1px solid #00aaff;
  color: #e0e8f0;
  padding: 6px 8px;
  border-radius: 4px;
  font-size: 1rem;
  font-family: "Courier New", monospace;
}

.edit-form button {
  background: #00aaff;
  color: #0d1520;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  font-size: 0.8rem;
}

.release-btn {
  margin-top: 8px;
  width: 100%;
  background: transparent;
  border: 1px solid #ffaa00;
  color: #ffaa00;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: background 0.2s;
}

.release-btn:hover {
  background: rgba(255, 170, 0, 0.15);
}
</style>
