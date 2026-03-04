<script setup>
import { computed, ref } from "vue";

const props = defineProps({
  time: Number,
  rate: Number,
  overridden: Boolean,
});

const emit = defineEmits(["publish"]);

const editingTime = ref(false);
const timeInput = ref("");
const rateInput = ref("");

const formattedTime = computed(() => {
  const totalMinutes = Math.floor(props.time);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
});

const progressPercent = computed(() => (props.time / 1440) * 100);

function togglePause() {
  if (props.overridden) {
    emit("publish", "time/overridden/set", "false");
  } else {
    emit("publish", "time/set", String(props.time));
  }
}

function startEditTime() {
  editingTime.value = true;
  const totalMinutes = Math.floor(props.time);
  const hours = Math.floor(totalMinutes / 60);
  const minutes = totalMinutes % 60;
  timeInput.value = `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
}

function submitTime() {
  const parts = timeInput.value.split(":");
  if (parts.length === 2) {
    const minutes = parseInt(parts[0]) * 60 + parseInt(parts[1]);
    if (minutes >= 0 && minutes < 1440) {
      emit("publish", "time/set", String(minutes));
    }
  }
  editingTime.value = false;
}

function setRate() {
  const val = parseFloat(rateInput.value);
  if (!isNaN(val) && val >= 0) {
    emit("publish", "time/rate/set", String(val));
  }
  rateInput.value = "";
}
</script>

<template>
  <div class="time-control">
    <div class="time-display-row">
      <div class="time-display" v-if="!editingTime" @click="startEditTime">
        {{ formattedTime }}
      </div>
      <form v-else @submit.prevent="submitTime" class="time-edit">
        <input
          v-model="timeInput"
          type="time"
          class="time-input"
          autofocus
          @blur="editingTime = false"
        />
      </form>

      <button class="pause-btn" :class="{ paused: overridden }" @click="togglePause">
        <span v-if="overridden">&#9654;</span>
        <span v-else>&#9646;&#9646;</span>
      </button>
    </div>

    <div class="progress-bar">
      <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
      <div class="progress-labels">
        <span>00:00</span>
        <span>06:00</span>
        <span>12:00</span>
        <span>18:00</span>
        <span>24:00</span>
      </div>
    </div>

    <div class="rate-row">
      <label>Rate:</label>
      <input
        type="range"
        min="0"
        max="60"
        step="0.5"
        :value="rate"
        @input="emit('publish', 'time/rate/set', $event.target.value)"
      />
      <span class="rate-value">{{ rate.toFixed(1) }}x</span>
      <form @submit.prevent="setRate" class="rate-manual">
        <input v-model="rateInput" type="number" step="0.1" min="0" placeholder="set" />
      </form>
    </div>
  </div>
</template>

<style scoped>
.time-control {
  background: #1a2332;
  border: 1px solid #2a3a4a;
  border-radius: 8px;
  padding: 16px;
}

.time-display-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.time-display {
  font-family: "Courier New", monospace;
  font-size: 3rem;
  font-weight: bold;
  color: #00ff88;
  cursor: pointer;
  letter-spacing: 4px;
}

.time-display:hover {
  color: #00ffaa;
}

.time-edit {
  display: inline;
}

.time-input {
  font-family: "Courier New", monospace;
  font-size: 2.5rem;
  background: #0d1520;
  border: 1px solid #00ff88;
  color: #00ff88;
  padding: 4px 8px;
  border-radius: 4px;
  width: 180px;
}

.pause-btn {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 3px solid #ff4444;
  background: rgba(255, 68, 68, 0.15);
  color: #ff4444;
  font-size: 1.5rem;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  margin-left: auto;
}

.pause-btn:hover {
  background: rgba(255, 68, 68, 0.3);
}

.pause-btn.paused {
  border-color: #00ff88;
  background: rgba(0, 255, 136, 0.15);
  color: #00ff88;
}

.pause-btn.paused:hover {
  background: rgba(0, 255, 136, 0.3);
}

.progress-bar {
  position: relative;
  height: 8px;
  background: #0d1520;
  border-radius: 4px;
  margin-bottom: 16px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #003366, #00aaff, #ffaa00, #ff6600, #003366);
  border-radius: 4px;
  transition: width 0.5s linear;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  position: absolute;
  top: 12px;
  left: 0;
  right: 0;
  font-size: 0.65rem;
  color: #556677;
}

.rate-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.rate-row label {
  color: #8899aa;
  font-size: 0.85rem;
}

.rate-row input[type="range"] {
  flex: 1;
  accent-color: #00aaff;
}

.rate-value {
  font-family: "Courier New", monospace;
  color: #00aaff;
  min-width: 50px;
  font-size: 0.9rem;
}

.rate-manual input {
  width: 60px;
  background: #0d1520;
  border: 1px solid #2a3a4a;
  color: #aabbcc;
  padding: 4px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
}
</style>
