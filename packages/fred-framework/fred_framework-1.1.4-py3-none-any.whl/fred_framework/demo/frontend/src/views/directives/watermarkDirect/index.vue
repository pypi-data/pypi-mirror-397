<template>
  <div v-waterMarker="{ text: 'Geeker Admin', textColor: 'rgba(180, 180, 180, 0.6)' }" class="card content-box">
    <span class="text">水印指令 🍇🍇🍇🍓🍓🍓</span>
  </div>
</template>

<script setup lang="ts" name="watermarkDirect"></script>

<style scoped lang="scss">
.card {
  padding: 20px;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);

  .text {
    font-size: 16px;
    color: #333;
  }
}
</style>
