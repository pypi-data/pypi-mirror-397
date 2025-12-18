<template>
  <el-dialog
    v-model="dialogVisible"
    :title="`模型图片关联管理 - ${modelName}`"
    width="80%"
    :before-close="handleClose"
    destroy-on-close
  >
    <div class="image-relation-container">
      <!-- 操作区域 -->
      <div class="operation-area">
        <div class="left-actions">
          <el-button type="primary" @click="openAddDialog">
            <el-icon><Plus /></el-icon>
            添加图片路径
          </el-button>
          <el-button type="danger" :disabled="!hasSelection" @click="batchRemove">
            <el-icon><Delete /></el-icon>
            批量删除
          </el-button>
        </div>
        <div class="right-actions">
          <el-input v-model="searchKeyword" placeholder="搜索图片路径" style="width: 200px" clearable @input="handleSearch">
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button @click="refreshList">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </div>

      <!-- 图片关联列表 -->
      <el-table
        ref="tableRef"
        v-loading="loading"
        :data="imageList"
        @selection-change="handleSelectionChange"
        style="margin-top: 16px"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="image_path" label="图片路径" min-width="300" show-overflow-tooltip />
        <el-table-column prop="created" label="关联时间" width="180" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="danger" link @click="removeImage(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>

    <!-- 添加图片路径对话框 -->
    <el-dialog v-model="addDialogVisible" title="添加图片路径" width="600px" :before-close="handleAddDialogClose">
      <div class="add-image-form">
        <el-form :model="addForm" label-width="100px">
          <el-form-item label="图片路径">
            <el-input v-model="imagePathInput" type="textarea" :rows="4" placeholder="请输入图片路径，多个路径用换行分隔" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleAddDialogClose">取消</el-button>
          <el-button type="primary" @click="confirmAdd" :loading="addLoading"> 确定 </el-button>
        </div>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup lang="tsx">
import { ref, reactive, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus, Delete, Search, Refresh } from "@element-plus/icons-vue";
import { getModelImageRelations, addModelImageRelations, removeModelImageRelations } from "@/api/modules/model";

interface ImageRelation {
  id: number;
  model_id: number;
  image_path: string;
  created: string;
}

// 对话框显示状态
const dialogVisible = ref(false);
const addDialogVisible = ref(false);

// 模型信息
const modelId = ref<number>(0);
const modelName = ref<string>("");

// 列表数据
const imageList = ref<ImageRelation[]>([]);
const loading = ref(false);
const searchKeyword = ref("");

// 分页
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

// 选择
const selectedRows = ref<ImageRelation[]>([]);
const hasSelection = computed(() => selectedRows.value.length > 0);

// 添加表单
const addForm = reactive({
  image_paths: [] as string[]
});
const imagePathInput = ref("");
const addLoading = ref(false);

// 表格引用
const tableRef = ref();

// 打开对话框
const openDialog = (params: { modelId: number; modelName: string }) => {
  modelId.value = params.modelId;
  modelName.value = params.modelName;
  dialogVisible.value = true;
  loadImageList();
};

// 关闭对话框
const handleClose = () => {
  dialogVisible.value = false;
  resetData();
};

// 重置数据
const resetData = () => {
  imageList.value = [];
  searchKeyword.value = "";
  currentPage.value = 1;
  pageSize.value = 10;
  total.value = 0;
  selectedRows.value = [];
};

// 加载图片关联列表
const loadImageList = async () => {
  if (!modelId.value) return;

  loading.value = true;
  try {
    const params = {
      model_id: modelId.value,
      image_path: searchKeyword.value || undefined
    };

    const response = await getModelImageRelations(params);
    // 确保response是数组
    imageList.value = Array.isArray(response) ? response : [];
    total.value = imageList.value.length;
  } catch {
    ElMessage.error("获取图片关联列表失败");
  } finally {
    loading.value = false;
  }
};

// 搜索
const handleSearch = () => {
  currentPage.value = 1;
  loadImageList();
};

// 刷新列表
const refreshList = () => {
  loadImageList();
};

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val;
  currentPage.value = 1;
  loadImageList();
};

const handleCurrentChange = (val: number) => {
  currentPage.value = val;
  loadImageList();
};

// 选择处理
const handleSelectionChange = (selection: ImageRelation[]) => {
  selectedRows.value = selection;
};

// 打开添加对话框
const openAddDialog = () => {
  addDialogVisible.value = true;
  imagePathInput.value = "";
};

// 关闭添加对话框
const handleAddDialogClose = () => {
  addDialogVisible.value = false;
  imagePathInput.value = "";
  addForm.image_paths = [];
};

// 确认添加
const confirmAdd = async () => {
  if (!imagePathInput.value.trim()) {
    ElMessage.warning("请输入图片路径");
    return;
  }

  // 解析图片路径
  const paths = imagePathInput.value
    .split("\n")
    .map(path => path.trim())
    .filter(path => path.length > 0);

  if (paths.length === 0) {
    ElMessage.warning("请输入有效的图片路径");
    return;
  }

  addLoading.value = true;
  try {
    const data = {
      model_id: modelId.value,
      image_paths: paths
    };

    const response = await addModelImageRelations(data);
    ElMessage.success(response || "添加成功");
    handleAddDialogClose();
    loadImageList();
  } catch {
    ElMessage.error("添加图片关联失败");
  } finally {
    addLoading.value = false;
  }
};

// 删除单个图片
const removeImage = async (row: ImageRelation) => {
  try {
    await ElMessageBox.confirm(`确定要删除图片路径 "${row.image_path}" 的关联吗？`, "确认删除", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });

    const data = {
      model_id: modelId.value,
      relation_ids: [row.id]
    };

    const response = await removeModelImageRelations(data);
    ElMessage.success(response || "删除成功");
    loadImageList();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("删除图片关联失败");
    }
  }
};

// 批量删除
const batchRemove = async () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning("请选择要删除的图片");
    return;
  }

  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedRows.value.length} 个图片关联吗？`, "确认批量删除", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });

    const relationIds = selectedRows.value.map(row => row.id);
    const data = {
      model_id: modelId.value,
      relation_ids: relationIds
    };

    const response = await removeModelImageRelations(data);
    ElMessage.success(response || "批量删除成功");
    loadImageList();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("批量删除图片关联失败");
    }
  }
};

// 暴露方法
defineExpose({
  openDialog
});
</script>

<style scoped>
.image-relation-container {
  padding: 0;
}

.operation-area {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.left-actions {
  display: flex;
  gap: 8px;
}

.right-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.pagination-container {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.add-image-form {
  padding: 16px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table__header) {
  background-color: #f5f7fa;
}

:deep(.el-button--link) {
  padding: 4px 8px;
  margin: 0 2px;
}
</style>
