<template>
  <div class="card content-box">
    <span class="text">复制指令 🍇🍇🍇🍓🍓🍓</span>
    <div class="box-content">
      <el-input v-model="data" placeholder="请输入内容" style="width: 500px">
        <template #append>
          <el-button v-copy="data"> 复制 </el-button>
        </template>
      </el-input>
    </div>
  </div>
</template>

<script setup lang="ts" name="copyDirect">
import { ref } from "vue";

const data = ref<string>("我是被复制的内容 🍒 🍉 🍊");
</script>

<style scoped lang="scss">
.card {
  padding: 20px;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);

  .text {
    font-size: 16px;
    color: #333;
    margin-bottom: 20px;
  }

  .box-content {
    margin-top: 20px;
  }
}
</style>
