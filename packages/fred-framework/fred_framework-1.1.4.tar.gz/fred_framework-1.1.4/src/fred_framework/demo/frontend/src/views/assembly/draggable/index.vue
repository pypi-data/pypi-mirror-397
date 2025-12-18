<template>
  <draggable
    v-model="gridList"
    class="card grid-container"
    item-key="id"
    animation="300"
    chosen-class="chosen"
    force-fallback="true"
  >
    <template #item="{ element }">
      <div :class="'item' + ' ' + 'item-' + element.num">
        {{ element.num }}
      </div>
    </template>
  </draggable>
</template>

<script setup lang="ts" name="draggable">
import { ref } from "vue";
import draggable from "vuedraggable";

let gridList = ref([
  { id: 1, num: 1 },
  { id: 2, num: 2 },
  { id: 3, num: 3 },
  { id: 4, num: 4 },
  { id: 5, num: 5 },
  { id: 6, num: 6 },
  { id: 7, num: 7 },
  { id: 8, num: 8 },
  { id: 9, num: 9 }
]);
</script>

<style scoped lang="scss">
.card {
  padding: 20px;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  padding: 20px;
}

.item {
  height: 100px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 24px;
  font-weight: bold;
  cursor: move;
  transition: all 0.3s ease;
  user-select: none;

  &:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  }

  &.chosen {
    transform: scale(1.1);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
  }
}

.item-1 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
.item-2 {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}
.item-3 {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}
.item-4 {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}
.item-5 {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}
.item-6 {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}
.item-7 {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}
.item-8 {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
}
.item-9 {
  background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
}
</style>
