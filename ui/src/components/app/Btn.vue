<template>
  <v-btn
    :color="color"
    v-bind="$attrs"
    v-on="$listeners"
  >
    <slot />
  </v-btn>
</template>

<script>
export default {
  name: "AppBtn",

  props: {
    color: {
      type: String,
      default: "primary"
    }
  }
};
</script>
