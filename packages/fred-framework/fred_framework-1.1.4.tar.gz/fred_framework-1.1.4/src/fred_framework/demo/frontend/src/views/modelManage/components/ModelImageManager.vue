<template>
  <el-drawer
    v-model="drawerVisible"
    :title="`自动推理路径 - ${modelName}`"
    size="40%"
    :before-close="handleClose"
    destroy-on-close
  >
    <div class="image-manager-container">
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
        <el-table-column prop="image_path" label="自动推理路径" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created" label="关联时间" width="280" />
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
    <el-dialog v-model="addDialogVisible" title="添加图片路径" width="500px" :before-close="handleAddDialogClose">
      <div class="add-image-form">
        <el-form :model="addForm" label-width="100px">
          <el-form-item label="选择文件夹">
            <el-select v-model="selectedFolder" placeholder="请选择文件夹" style="width: 100%" :loading="folderLoading">
              <el-option v-for="folder in folderList" :key="folder.path" :label="folder.name" :value="folder.path" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <div class="folder-info">
              <el-text type="info"> 选择文件夹后，该文件夹下的所有图片路径将自动关联到模型 </el-text>
            </div>
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
  </el-drawer>
</template>

<script setup lang="tsx">
import { ref, reactive, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus, Delete, Refresh } from "@element-plus/icons-vue";
import { getModelImageRelations, addModelImageRelations, removeModelImageRelations } from "@/api/modules/model";
import { getUploadFolders } from "@/api/modules/annotation";

interface ImageRelation {
  id: number;
  model_id: number;
  image_path: string;
  created: string;
}

interface FolderItem {
  name: string;
  path: string;
}

// 抽屉显示状态
const drawerVisible = ref(false);

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

// 添加对话框
const addDialogVisible = ref(false);
const addForm = reactive({
  image_paths: [] as string[]
});
const addLoading = ref(false);

// 文件夹相关
const folderList = ref<FolderItem[]>([]);
const folderLoading = ref(false);
const selectedFolder = ref("");

// 表格引用
const tableRef = ref();

// 打开抽屉
const openDrawer = (params: { modelId: number; modelName: string }) => {
  modelId.value = params.modelId;
  modelName.value = params.modelName;
  drawerVisible.value = true;
  loadImageList();
  loadFolders();
};

// 关闭抽屉
const handleClose = () => {
  drawerVisible.value = false;
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
  selectedFolder.value = "";
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
    // 处理后端返回的数据格式 {code: 200, data: [...]}
    if (response && response.code === 200 && Array.isArray(response.data)) {
      imageList.value = response.data;
    } else if (Array.isArray(response)) {
      // 兼容直接返回数组的情况
      imageList.value = response;
    } else {
      imageList.value = [];
    }
    total.value = imageList.value.length;
  } catch {
    ElMessage.error("获取图片关联列表失败");
  } finally {
    loading.value = false;
  }
};

// 加载文件夹列表
const loadFolders = async () => {
  try {
    folderLoading.value = true;
    const response = await getUploadFolders();
    if (response && response.data && Array.isArray(response.data)) {
      folderList.value = response.data;
    } else {
      ElMessage.warning("获取文件夹列表失败");
    }
  } catch {
    ElMessage.error("获取文件夹列表失败");
  } finally {
    folderLoading.value = false;
  }
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
  selectedFolder.value = "";
};

// 关闭添加对话框
const handleAddDialogClose = () => {
  addDialogVisible.value = false;
  selectedFolder.value = "";
  addForm.image_paths = [];
};

// 确认添加
const confirmAdd = async () => {
  if (!selectedFolder.value) {
    ElMessage.warning("请选择文件夹");
    return;
  }

  addLoading.value = true;
  try {
    const data = {
      model_id: modelId.value,
      image_paths: [selectedFolder.value] // 直接使用文件夹路径
    };

    const response = await addModelImageRelations(data);
    // 处理后端返回的数据格式
    if (response && response.code === 200) {
      ElMessage.success(response.message || "添加成功");
    } else if (typeof response === "string") {
      ElMessage.success(response);
    } else {
      ElMessage.success("添加成功");
    }
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
    // 处理后端返回的数据格式
    if (response && response.code === 200) {
      ElMessage.success(response.message || "删除成功");
    } else if (typeof response === "string") {
      ElMessage.success(response);
    } else {
      ElMessage.success("删除成功");
    }
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
    // 处理后端返回的数据格式
    if (response && response.code === 200) {
      ElMessage.success(response.message || "批量删除成功");
    } else if (typeof response === "string") {
      ElMessage.success(response);
    } else {
      ElMessage.success("批量删除成功");
    }
    loadImageList();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("批量删除图片关联失败");
    }
  }
};

// 暴露方法
defineExpose({
  openDrawer
});
</script>

<style scoped>
.image-manager-container {
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

:deep(.el-drawer__header) {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.folder-info {
  margin-top: 8px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border-left: 4px solid #409eff;
}
</style>
