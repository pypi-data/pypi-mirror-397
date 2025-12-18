<template>
  <div class="search-container">
    <el-card class="search-card" shadow="hover">
      <el-form :model="localSearchForm" class="annotation-search">
        <div class="search-row compact">
          <!-- 标注状态筛选 -->
          <div class="search-group inline-form-item">
            <label class="form-label">{{ t("annotation.annotationStatus") }}</label>
            <el-select v-model="localSearchForm.status" :placeholder="t('annotation.selectStatus')" style="width: 140px">
              <el-option :label="t('annotation.all')" :value="null as any" />
              <el-option :label="t('annotation.unannotated')" :value="0" />
              <el-option :label="t('annotation.annotated')" :value="1" />
            </el-select>
          </div>

          <!-- 删除状态筛选 -->
          <div class="search-group inline-form-item">
            <label class="form-label">{{ t("annotation.deleteStatus") }}</label>
            <el-select v-model="localSearchForm.deleted" :placeholder="t('annotation.selectDeleteStatus')" style="width: 140px">
              <el-option :label="t('annotation.normal')" :value="0" />
              <el-option :label="t('annotation.deleted')" :value="1" />
            </el-select>
          </div>

          <!-- 素材库筛选 -->
          <div class="search-group inline-form-item">
            <label class="form-label">{{ t("annotation.materialLibrary") }}</label>
            <el-select
              v-model="localSearchForm.material_id"
              :placeholder="t('annotation.selectMaterialLibrary')"
              style="width: 280px"
              clearable
              filterable
            >
              <el-option :label="t('annotation.all')" :value="null as any" />
              <el-option v-for="material in materialLibraryList" :key="material.id" :label="material.name" :value="material.id">
                <div style="display: flex; justify-content: space-between; align-items: center">
                  <span>{{ material.name }}</span>
                  <span :style="{ color: '#8492a6', fontSize: '12px', marginLeft: '12px' }">
                    {{ material.total_num || 0 }}{{ t("annotation.imagesCount") }}
                  </span>
                </div>
              </el-option>
            </el-select>
          </div>

          <!-- 标注更新时间范围筛选 -->
          <div class="search-group inline-form-item">
            <label class="form-label">{{ t("annotation.annotationUpdatedTime") }}</label>
            <el-date-picker
              v-model="annotationTimeRange"
              type="datetimerange"
              :range-separator="t('annotation.timeRangeSeparator')"
              :start-placeholder="t('annotation.startTimePlaceholder')"
              :end-placeholder="t('annotation.endTimePlaceholder')"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              style="width: 360px"
              clearable
              @change="handleTimeRangeChange"
            />
          </div>

          <div class="search-group search-actions-inline">
            <el-button type="primary" @click="handleSearch" size="default">
              <el-icon><Search /></el-icon>
              {{ t("annotation.search") }}
            </el-button>
            <el-button @click="handleReset" size="default">
              <el-icon><Refresh /></el-icon>
              {{ t("annotation.reset") }}
            </el-button>
            <!-- 导出标注按钮 -->
            <el-button
              v-auth="'导出标注'"
              type="success"
              @click="handleExportAnnotations"
              size="default"
              :loading="exportLoading"
            >
              <el-icon><Download /></el-icon>
              {{ t("annotation.exportAnnotations") }}
            </el-button>
            <!-- 远程训练按钮 -->
            <el-button v-auth="'远程训练'" type="primary" @click="handleTrainAnnotations" size="default" :loading="trainLoading">
              <el-icon><VideoPlay /></el-icon>
              远程训练
            </el-button>
          </div>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import { Search, Refresh, Download, VideoPlay } from "@element-plus/icons-vue";
import { getUserTeamMaterialsApi } from "@/api/modules/materialLibrary";
import type { MaterialLibraryInfo } from "@/api/model/materialLibraryModel";

const { t } = useI18n();

interface SearchForm {
  status: number | null;
  material_id: number | null;
  deleted: number | null;
  annotation_updated_start: string | null;
  annotation_updated_end: string | null;
}

interface Props {
  searchForm: SearchForm;
  exportLoading: boolean;
  trainLoading?: boolean;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  search: [];
  reset: [];
  exportAnnotations: [];
  trainAnnotations: [];
  updateSearchForm: [form: Partial<SearchForm>];
}>();

// 素材库列表
const materialLibraryList = ref<MaterialLibraryInfo[]>([]);

// 标注更新时间范围
const annotationTimeRange = ref<[string, string] | null>(null);

// 创建本地搜索表单数据
const localSearchForm = ref<SearchForm>({
  status: props.searchForm.status,
  material_id: props.searchForm.material_id,
  deleted: props.searchForm.deleted,
  annotation_updated_start: props.searchForm.annotation_updated_start,
  annotation_updated_end: props.searchForm.annotation_updated_end
});

// 加载素材库列表
const loadMaterialLibraryList = async () => {
  try {
    const res = await getUserTeamMaterialsApi();
    if (res && typeof res === "object") {
      const data = res.data || res;
      materialLibraryList.value = Array.isArray(data) ? data : [];
    }
  } catch (error: any) {
    console.error("获取素材库列表失败:", error);
    // 错误处理由拦截器统一处理，这里不需要额外的错误提示
  }
};

// 组件挂载时加载素材库列表
onMounted(() => {
  loadMaterialLibraryList();
});

// 监听 props 变化，同步到本地数据
watch(
  () => props.searchForm,
  newForm => {
    localSearchForm.value = {
      status: newForm.status,
      material_id: newForm.material_id,
      deleted: newForm.deleted,
      annotation_updated_start: newForm.annotation_updated_start,
      annotation_updated_end: newForm.annotation_updated_end
    };
    // 同步时间范围选择器
    if (newForm.annotation_updated_start && newForm.annotation_updated_end) {
      annotationTimeRange.value = [newForm.annotation_updated_start, newForm.annotation_updated_end];
    } else {
      annotationTimeRange.value = null;
    }
  },
  { deep: true }
);

// 监听本地数据变化，向父组件发送更新
watch(
  localSearchForm,
  newForm => {
    emit("updateSearchForm", newForm);
  },
  { deep: true }
);

const handleSearch = () => {
  emit("search");
};

// 处理时间范围变化
const handleTimeRangeChange = (value: [string, string] | null) => {
  if (value && value.length === 2) {
    localSearchForm.value.annotation_updated_start = value[0];
    localSearchForm.value.annotation_updated_end = value[1];
  } else {
    localSearchForm.value.annotation_updated_start = null;
    localSearchForm.value.annotation_updated_end = null;
  }
};

const handleReset = () => {
  localSearchForm.value.status = null;
  localSearchForm.value.material_id = null;
  localSearchForm.value.deleted = 0; // 重置为默认值：正常
  localSearchForm.value.annotation_updated_start = null;
  localSearchForm.value.annotation_updated_end = null;
  annotationTimeRange.value = null;
  emit("reset");
};

const handleExportAnnotations = () => {
  emit("exportAnnotations");
};

const handleTrainAnnotations = () => {
  emit("trainAnnotations");
};
</script>

<style lang="scss" scoped>
.search-container {
  margin-bottom: 16px;
}

.search-card {
  .search-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 500;
  }
}

.annotation-search {
  .search-row {
    display: flex;
    align-items: center;
    gap: 16px;
    flex-wrap: wrap;

    &.compact {
      gap: 12px;
    }
  }

  .search-group {
    display: flex;
    align-items: center;
    gap: 8px;

    &.inline-form-item {
      .form-label {
        font-size: 14px;
        color: #606266;
        white-space: nowrap;
        min-width: 60px;
      }
    }

    &.search-actions-inline {
      margin-left: auto;
      gap: 8px;
    }
  }

  .option-content {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}
</style>
