<template>
  <div class="card content-box">
    <span class="text">长按指令 🍇🍇🍇🍓🍓🍓</span>
    <el-button v-longpress="longpress" type="primary"> 长按2秒触发事件 </el-button>
  </div>
</template>

<script setup lang="ts" name="longpressDirect">
import { ElMessage } from "element-plus";
const longpress = () => {
  ElMessage.success("长按事件触发成功 🎉🎉🎉");
};
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
}
</style>
