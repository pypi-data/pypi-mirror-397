<template>
  <div class="table-view-container">
    <template v-if="imageList.length > 0">
      <ProTable ref="proTable" :columns="columns" :data="imageList" :pagination="false" row-key="id" class="full-width-table">
        <template #file_preview="{ row }">
          <div class="image-preview-cell" @click="handleImageClick(row)">
            <img :src="getImageUrl(row.file_path)" :alt="row?.file_name" class="preview-image" />
          </div>
        </template>

        <template #annotation_count="{ row }: { row: AnnotationItem }">
          <el-tag :type="row.annotation_count > 0 ? 'success' : 'info'">
            {{ row.annotation_count }}
          </el-tag>
        </template>

        <template #created_at="{ row }: { row: AnnotationItem }">
          {{ formatDate(row.created_at) || "-" }}
        </template>

        <template #operation="{ row }">
          <div class="operation-buttons">
            <el-button type="success" link :icon="Edit" @click.stop="handleImageClick(row)">
              {{ t("annotation.imageDetails") }}
            </el-button>
            <el-button v-if="row.deleted === 1" type="success" link :icon="RefreshRight" @click.stop="handleMarkDeleted(row)">
              {{ t("annotation.restore") }}
            </el-button>
            <el-button v-else type="danger" link :icon="Delete" @click.stop="handleMarkDeleted(row)">
              {{ t("annotation.delete") }}
            </el-button>
          </div>
        </template>
      </ProTable>
    </template>
    <template v-else>
      <div class="empty-state table-empty-state">
        <el-empty description="暂无数据">
          <template #image>
            <el-icon :size="60" color="#c0c4cc">
              <Document />
            </el-icon>
          </template>
        </el-empty>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from "vue";
import { useI18n } from "vue-i18n";
import { Edit, Document, Delete, RefreshRight } from "@element-plus/icons-vue";
import ProTable from "@/components/ProTable/index.vue";
import type { ColumnProps } from "@/components/ProTable/interface";

const { t } = useI18n();

interface AnnotationItem {
  id: number | null;
  file_name: string;
  file_path: string;
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
}

defineProps<Props>();

const emit = defineEmits<{
  imageClick: [item: AnnotationItem];
  markDeleted: [item: AnnotationItem];
  selectionChange: [selectedItems: AnnotationItem[]];
}>();

const proTable = ref<InstanceType<typeof ProTable>>();

// 监听 ProTable 的 selectedList 变化
watch(
  () => proTable.value?.selectedList,
  newList => {
    if (newList) {
      emit("selectionChange", newList as AnnotationItem[]);
    }
  },
  { deep: true, immediate: true }
);

const handleImageClick = (item: AnnotationItem) => {
  emit("imageClick", item);
};

const handleMarkDeleted = (item: AnnotationItem) => {
  emit("markDeleted", item);
};

// 表格列配置
const columns = computed<ColumnProps<AnnotationItem>[]>(() => [
  { type: "selection", width: 55, fixed: "left" },
  { prop: "id", label: "ID", width: 80 },
  {
    prop: "file_preview",
    label: t("annotation.imagePreview"),
    width: 120,
    isShow: true
  },
  { prop: "file_name", label: t("annotation.fileName"), width: 200, isShow: true },
  {
    prop: "creator_name",
    label: t("annotation.uploader"),
    width: 120,
    isShow: true,
    render: (scope: { row: AnnotationItem }) => {
      return scope.row.creator_name || t("annotation.system");
    }
  },
  {
    prop: "annotation_count",
    label: t("annotation.annotationCount"),
    width: 100,
    isShow: true
  },
  {
    prop: "created_at",
    label: t("annotation.createdAt"),
    width: 180,
    isShow: true
  },
  { prop: "operation", label: t("annotation.operation"), fixed: "right", isShow: true }
]);
</script>

<style lang="scss" scoped>
.table-view-container {
  .full-width-table {
    width: 100%;
  }

  .image-preview-cell {
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    padding: 4px;

    .preview-image {
      width: 60px;
      height: 60px;
      object-fit: cover;
      border-radius: 4px;
      border: 1px solid #e4e7ed;
      transition: transform 0.2s ease;

      &:hover {
        transform: scale(1.05);
      }
    }
  }

  .operation-buttons {
    display: flex;
    gap: 8px;
  }

  .empty-state {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 300px;

    &.table-empty-state {
      min-height: 400px;
    }
  }
}
</style>
