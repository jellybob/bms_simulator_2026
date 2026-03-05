import { reactive, ref } from "vue";
import mqtt from "mqtt";

const BASE_TOPIC = "bms_sim/";

export function useMqtt() {
  const state = reactive({
    time: 0,
    timeRate: 1,
    timeOverridden: false,
    oat: 0,
    oatOverridden: false,
    temperature: 0,
    temperatureOverridden: false,
    occupancy: false,
    occupancyOverridden: false,
    exteriorLightLevel: 0,
    exteriorLightLevelOverridden: false,
    interiorLightLevel: 0,
    interiorLightLevelOverridden: false,
    // Actuators
    heat: false,
    airCon: false,
    lights: false,
    // Power tracking
    powerUsage: 0,
    cumulativePowerUsage: 0,
  });

  const connected = ref(false);

  // Use wss:// if the page is served over https://, otherwise use ws://
  // Connect to /mqtt path which is proxied by nginx to the broker
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const brokerUrl = `${protocol}//${window.location.host}/mqtt`;
  const client = mqtt.connect(brokerUrl);

  client.on("connect", () => {
    connected.value = true;
    client.subscribe(`${BASE_TOPIC}#`);
  });

  client.on("close", () => {
    connected.value = false;
  });

  const topicMap = {
    [`${BASE_TOPIC}time`]: (v) => (state.time = parseFloat(v)),
    [`${BASE_TOPIC}time/rate`]: (v) => (state.timeRate = parseFloat(v)),
    [`${BASE_TOPIC}time/overridden`]: (v) =>
      (state.timeOverridden = v === "true"),
    [`${BASE_TOPIC}oat`]: (v) => (state.oat = parseFloat(v)),
    [`${BASE_TOPIC}oat/overridden`]: (v) =>
      (state.oatOverridden = v === "true"),
    [`${BASE_TOPIC}temperature`]: (v) => (state.temperature = parseFloat(v)),
    [`${BASE_TOPIC}temperature/overridden`]: (v) =>
      (state.temperatureOverridden = v === "true"),
    [`${BASE_TOPIC}occupancy`]: (v) => (state.occupancy = v === "true"),
    [`${BASE_TOPIC}occupancy/overridden`]: (v) =>
      (state.occupancyOverridden = v === "true"),
    [`${BASE_TOPIC}exterior_light_level`]: (v) =>
      (state.exteriorLightLevel = parseFloat(v)),
    [`${BASE_TOPIC}exterior_light_level/overridden`]: (v) =>
      (state.exteriorLightLevelOverridden = v === "true"),
    [`${BASE_TOPIC}interior_light_level`]: (v) =>
      (state.interiorLightLevel = parseFloat(v)),
    [`${BASE_TOPIC}interior_light_level/overridden`]: (v) =>
      (state.interiorLightLevelOverridden = v === "true"),
    // Actuators
    [`${BASE_TOPIC}heat`]: (v) => (state.heat = v === "true"),
    [`${BASE_TOPIC}air_con`]: (v) => (state.airCon = v === "true"),
    [`${BASE_TOPIC}lights`]: (v) => (state.lights = v === "true"),
    // Power tracking
    [`${BASE_TOPIC}power_usage`]: (v) => (state.powerUsage = parseFloat(v)),
    [`${BASE_TOPIC}cumulative_power_usage`]: (v) =>
      (state.cumulativePowerUsage = parseFloat(v)),
  };

  client.on("message", (topic, message) => {
    const handler = topicMap[topic];
    if (handler) {
      handler(message.toString());
    }
  });

  function publish(topicSuffix, value) {
    client.publish(`${BASE_TOPIC}${topicSuffix}`, String(value));
  }

  return { state, connected, publish };
}
