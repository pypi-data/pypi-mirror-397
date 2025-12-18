<template>
  <div class="image-grid">
    <template v-if="imageList.length > 0">
      <div
        v-for="item in imageList"
        :key="item.id"
        class="image-card"
        :class="{ selected: isSelected(item) }"
        @click="handleImageClick(item)"
      >
        <div class="image-wrapper">
          <img :src="getImageUrl(item.file_path)" :alt="item?.file_name" class="grid-image" />
          <div class="image-overlay">
            <div class="overlay-content">
              <div class="image-info">
                <h4>{{ item.file_name }}</h4>
                <p>{{ item.project_name }}</p>
              </div>
            </div>
          </div>
        </div>
        <div class="card-footer">
          <div class="file-info">
            <div class="info-row">
              <span class="creator">{{ item.creator_name }}</span>
              <span class="date">{{ formatDate(item.created_at) }}</span>
            </div>
            <div class="annotation-info">
              <el-checkbox
                :model-value="isSelected(item)"
                @change="handleToggleSelection(item)"
                @click.stop
                class="large-checkbox"
              />
              <el-tag :type="item.annotation_count > 0 ? 'success' : 'info'" size="small">
                {{ item.annotation_count }} 标注
              </el-tag>
            </div>
          </div>
          <div class="card-actions">
            <el-button type="success" text :icon="Edit" @click.stop="handleImageClick(item)">详情</el-button>
          </div>
        </div>
      </div>
    </template>
    <template v-else>
      <div class="empty-state">
        <el-empty description="暂无数据">
          <template #image>
            <el-icon :size="60" color="#c0c4cc">
              <Picture />
            </el-icon>
          </template>
        </el-empty>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { Edit, Picture } from "@element-plus/icons-vue";

interface AnnotationItem {
  id: number | null;
  file_name: string;
  file_path: string;
  project_name: string;
  creator_name: string;
  created_at: string;
  annotation_count: number;
  width?: number;
  height?: number;
  deleted?: number; // 删除状态：0-正常，1-已删除
}

interface Props {
  imageList: AnnotationItem[];
  getImageUrl: (filePath: string) => string;
  formatDate: (dateString: string) => string;
  selectedItems?: AnnotationItem[];
}

const props = withDefaults(defineProps<Props>(), {
  selectedItems: () => []
});

const emit = defineEmits<{
  imageClick: [item: AnnotationItem];
  selectionChange: [selectedItems: AnnotationItem[]];
}>();

const localSelectedItems = ref<AnnotationItem[]>([]);

// 监听props变化
watch(
  () => props.selectedItems,
  newItems => {
    localSelectedItems.value = [...newItems];
  },
  { immediate: true, deep: true }
);

const isSelected = (item: AnnotationItem) => {
  return localSelectedItems.value.some(selected => selected.id === item.id);
};

const handleToggleSelection = (item: AnnotationItem) => {
  const index = localSelectedItems.value.findIndex(selected => selected.id === item.id);
  if (index > -1) {
    localSelectedItems.value.splice(index, 1);
  } else {
    localSelectedItems.value.push(item);
  }
  emit("selectionChange", [...localSelectedItems.value]);
};

const handleImageClick = (item: AnnotationItem) => {
  emit("imageClick", item);
};
</script>

<style lang="scss" scoped>
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  padding: 16px 0;
}

.image-card {
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;

  &.selected {
    border: 2px solid #409eff;
    box-shadow: 0 4px 16px rgba(64, 158, 255, 0.3);
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  }

  .image-wrapper {
    position: relative;
    width: 100%;
    height: 200px;
    overflow: hidden;

    .grid-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.3s ease;
    }

    .image-overlay {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(to bottom, transparent 0%, rgba(0, 0, 0, 0.7) 100%);
      opacity: 0;
      transition: opacity 0.3s ease;
      display: flex;
      align-items: flex-end;
      padding: 16px;

      .overlay-content {
        width: 100%;
        color: white;

        .image-info {
          h4 {
            margin: 0 0 4px 0;
            font-size: 16px;
            font-weight: 500;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }

          p {
            margin: 0;
            font-size: 12px;
            opacity: 0.8;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
        }
      }
    }

    &:hover .image-overlay {
      opacity: 1;
    }

    &:hover .grid-image {
      transform: scale(1.05);
    }
  }

  .card-footer {
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #fafafa;

    .file-info {
      display: flex;
      flex-direction: column;
      gap: 6px;

      .info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 8px;

        .creator {
          font-size: 12px;
          color: #666;
          font-weight: 500;
        }

        .date {
          font-size: 11px;
          color: #999;
        }
      }

      .annotation-info {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        gap: 8px;

        .large-checkbox {
          transform: scale(2);
          margin-right: 8px;
        }
      }
    }

    .card-actions {
      .el-button {
        padding: 4px 8px;
        font-size: 12px;
      }
    }
  }
}

.empty-state {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}
</style>
