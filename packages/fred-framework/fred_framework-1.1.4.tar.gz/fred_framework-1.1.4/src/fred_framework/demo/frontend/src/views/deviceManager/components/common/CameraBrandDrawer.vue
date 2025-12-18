<template>
  <el-drawer
    v-model="drawerVisible"
    :title="drawerTitle"
    :width="drawerWidth"
    :close-on-click-modal="false"
    :destroy-on-close="true"
    class="camera-brand-drawer"
  >
    <div class="drawer-content">
      <!-- 搜索区域 -->
      <div class="search-section">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索品牌名称"
          :prefix-icon="Search"
          clearable
          @input="handleSearch"
          class="search-input"
        />
        <el-button type="primary" :icon="Plus" @click="openAddDialog">新增品牌</el-button>
      </div>

      <!-- 品牌列表 -->
      <div class="brand-list">
        <div v-if="filteredBrands.length === 0" class="no-data">
          <el-empty description="暂无品牌数据" />
        </div>
        <div v-else class="brand-items">
          <div v-for="brand in filteredBrands" :key="brand.id" class="brand-item">
            <div class="brand-info">
              <div class="brand-name">{{ brand.name }}</div>
            </div>
            <div class="brand-actions">
              <el-button type="primary" link :icon="Edit" @click="openEditDialog(brand)" size="small"> 编辑 </el-button>
              <el-button type="danger" link :icon="Delete" @click="handleDelete(brand)" size="small"> 删除 </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增/编辑品牌弹框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      :width="dialogWidth"
      :close-on-click-modal="false"
      :destroy-on-close="true"
      :center="false"
      :align-center="true"
      class="brand-dialog"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px" class="brand-form">
        <el-form-item label="品牌名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入品牌名称" maxlength="255" show-word-limit clearable />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          {{ isEdit ? "更新" : "保存" }}
        </el-button>
      </template>
    </el-dialog>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from "vue";
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from "element-plus";
import { Search, Plus, Edit, Delete } from "@element-plus/icons-vue";
import {
  getCameraBrandList,
  saveCameraBrand,
  updateCameraBrand,
  deleteCameraBrand,
  type CameraBrandInfo,
  type CameraBrandSaveParams
} from "@/api/modules/cameraBrand";

// 响应式数据
const drawerVisible = ref(false);
const drawerTitle = ref("品牌管理");
const searchKeyword = ref("");
const brandList = ref<CameraBrandInfo[]>([]);
const filteredBrands = ref<CameraBrandInfo[]>([]);

// 弹框相关
const dialogVisible = ref(false);
const dialogTitle = ref("新增品牌");
const isEdit = ref(false);
const currentBrand = ref<CameraBrandInfo>({} as CameraBrandInfo);
const submitLoading = ref(false);

// 表单相关
const formRef = ref<FormInstance>();
const formData = ref<CameraBrandSaveParams>({
  name: ""
});

// 表单验证规则
const formRules: FormRules = {
  name: [
    { required: true, message: "请输入品牌名称", trigger: "blur" },
    { min: 1, max: 255, message: "品牌名称长度在1到255个字符", trigger: "blur" }
  ]
};

// 计算弹框宽度 - 自适应
const drawerWidth = computed(() => {
  const windowWidth = window.innerWidth;
  if (windowWidth <= 768) {
    return "90%";
  } else if (windowWidth <= 1024) {
    return "60%";
  } else {
    return "500px";
  }
});

const dialogWidth = computed(() => {
  const windowWidth = window.innerWidth;
  if (windowWidth <= 768) {
    return "90%";
  } else {
    return "500px";
  }
});

// 搜索防抖定时器
const searchTimeout = ref<ReturnType<typeof setTimeout> | null>(null);

// 加载品牌列表
const loadBrandList = async () => {
  try {
    const response = await getCameraBrandList({ page: 1, limit: 1000 });
    brandList.value = response.data.records || [];
    filteredBrands.value = [...brandList.value];
  } catch (error) {
    ElMessage.error("加载品牌列表失败");
    console.error("加载品牌列表失败:", error);
  }
};

// 处理搜索
const handleSearch = () => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value);
  }

  searchTimeout.value = setTimeout(() => {
    if (!searchKeyword.value.trim()) {
      filteredBrands.value = [...brandList.value];
    } else {
      filteredBrands.value = brandList.value.filter(brand =>
        brand.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
      );
    }
  }, 300);
};

// 打开新增弹框
const openAddDialog = () => {
  isEdit.value = false;
  dialogTitle.value = "新增品牌";
  formData.value = { name: "" };
  dialogVisible.value = true;

  // 清除表单验证
  if (formRef.value) {
    formRef.value.clearValidate();
  }
};

// 打开编辑弹框
const openEditDialog = (brand: CameraBrandInfo) => {
  isEdit.value = true;
  dialogTitle.value = "编辑品牌";
  currentBrand.value = { ...brand };
  formData.value = { name: brand.name };
  dialogVisible.value = true;

  // 清除表单验证
  if (formRef.value) {
    formRef.value.clearValidate();
  }
};

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;

  try {
    await formRef.value.validate();
    submitLoading.value = true;

    if (isEdit.value) {
      await updateCameraBrand(currentBrand.value.id, formData.value);
      ElMessage.success("更新成功");
    } else {
      await saveCameraBrand(formData.value);
      ElMessage.success("保存成功");
    }

    dialogVisible.value = false;
    await loadBrandList();
  } catch (error) {
    console.error("保存品牌失败:", error);
    ElMessage.error(isEdit.value ? "更新失败" : "保存失败");
  } finally {
    submitLoading.value = false;
  }
};

// 删除品牌
const handleDelete = (brand: CameraBrandInfo) => {
  ElMessageBox.confirm(`确定要删除品牌"${brand.name}"吗？`, "提示", {
    type: "warning"
  })
    .then(async () => {
      try {
        await deleteCameraBrand(brand.id);
        ElMessage.success("删除成功");
        await loadBrandList();
      } catch (error) {
        console.error("删除品牌失败:", error);
        ElMessage.error("删除失败");
      }
    })
    .catch(() => {
      // 用户取消删除
    });
};

// 打开抽屉
const openDrawer = () => {
  drawerVisible.value = true;
  loadBrandList();
};

// 关闭抽屉
const closeDrawer = () => {
  drawerVisible.value = false;
  searchKeyword.value = "";
  filteredBrands.value = [];
};

// 暴露方法给父组件
defineExpose({
  openDrawer,
  closeDrawer
});

// 组件卸载时清理
onUnmounted(() => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value);
  }
});
</script>

<style scoped lang="scss">
.camera-brand-drawer {
  :deep(.el-drawer__body) {
    padding: 0;
    height: 100%;
    display: flex;
    flex-direction: column;
  }
}

.drawer-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.search-section {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-shrink: 0;

  .search-input {
    flex: 1;
  }
}

.brand-list {
  flex: 1;
  overflow-y: auto;
  min-height: 0;

  .no-data {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
  }

  .brand-items {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .brand-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border: 1px solid #e4e7ed;
    border-radius: 8px;
    background-color: #fff;
    transition: all 0.2s ease;

    &:hover {
      border-color: #409eff;
      box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
    }

    .brand-info {
      flex: 1;

      .brand-name {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 4px;
      }
    }

    .brand-actions {
      display: flex;
      gap: 8px;
      flex-shrink: 0;

      .el-button {
        margin: 0;
        padding: 6px 12px;
        font-size: 12px;
        border-radius: 4px;
      }
    }
  }
}

.brand-dialog {
  :deep(.el-dialog) {
    margin: 0 auto;
    max-height: 90vh;
    overflow-y: auto;
  }

  :deep(.el-dialog__body) {
    padding: 20px;
  }

  :deep(.el-dialog__header) {
    padding: 20px 20px 10px 20px;
    border-bottom: 1px solid #e4e7ed;
  }

  :deep(.el-dialog__footer) {
    padding: 10px 20px 20px 20px;
    border-top: 1px solid #e4e7ed;
  }
}

.brand-form {
  .el-form-item {
    margin-bottom: 20px;
  }
}

/* 响应式布局 */
@media (max-width: 768px) {
  .drawer-content {
    padding: 15px;
  }

  .search-section {
    flex-direction: column;
    gap: 8px;

    .search-input {
      width: 100%;
    }
  }

  .brand-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;

    .brand-actions {
      width: 100%;
      justify-content: flex-end;
    }
  }
}
</style>
