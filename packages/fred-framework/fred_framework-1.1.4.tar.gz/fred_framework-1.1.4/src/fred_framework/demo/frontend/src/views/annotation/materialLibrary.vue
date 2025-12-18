<template>
  <div class="table-box">
    <ProTable
      ref="proTable"
      :columns="currentColumns"
      :request-api="getMaterialLibraryList"
      :init-param="initParam"
      :data-callback="dataCallback"
    >
      <!-- 表格 header 按钮 -->
      <template #tableHeader="scope">
        <el-button type="primary" :icon="CirclePlus" @click="openDrawer('新增')">{{
          t("materialLibrary.addMaterial")
        }}</el-button>
        <el-button type="danger" :icon="Delete" plain :disabled="!scope.isSelected" @click="batchDelete(scope.selectedListIds)">
          {{ t("materialLibrary.batchDelete") }}
        </el-button>
      </template>

      <!-- 表格操作 -->
      <template #operation="scope">
        <el-button type="primary" link :icon="View" @click="openDrawer('查看', scope.row)">{{
          t("materialLibrary.view")
        }}</el-button>
        <el-button type="primary" link :icon="EditPen" @click="openDrawer('编辑', scope.row)">{{
          t("materialLibrary.edit")
        }}</el-button>
        <el-button type="info" link :icon="Picture" @click="viewMaterialImages(scope.row)">{{
          t("materialLibrary.viewImages")
        }}</el-button>
        <el-button type="warning" link @click="syncMaterialLibrary(scope.row)">{{ t("materialLibrary.update") }}</el-button>
        <el-button type="success" link @click="openTeamDrawer(scope.row)">{{ t("materialLibrary.teams") }}</el-button>
        <el-button type="danger" link :icon="Delete" @click="deleteMaterialLibrary(scope.row)">{{
          t("materialLibrary.delete")
        }}</el-button>
      </template>
    </ProTable>

    <!-- 新增/编辑抽屉 -->
    <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="500px" :title="drawerTitle">
      <el-form
        ref="ruleFormRef"
        label-width="100px"
        label-suffix=" :"
        :rules="rules"
        :disabled="isView"
        :model="formData"
        :hide-required-asterisk="isView"
      >
        <el-form-item :label="t('materialLibrary.name')" prop="name">
          <el-input v-model="formData.name" :placeholder="t('materialLibrary.inputName')" clearable></el-input>
        </el-form-item>
        <el-form-item :label="t('materialLibrary.path')" prop="path">
          <el-select
            v-model="formData.path"
            :placeholder="t('materialLibrary.selectFolder')"
            filterable
            :loading="folderLoading"
            :disabled="drawerTitleKey === '编辑' || isView"
            style="width: 100%"
          >
            <el-option
              v-for="(folder, index) in folderList"
              :key="`${folder.path}-${index}`"
              :label="folder.name"
              :value="folder.path"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="drawerVisible = false">{{ t("common.cancel") }}</el-button>
        <el-button v-if="!isView" type="primary" @click="handleSubmit">{{ t("common.confirm") }}</el-button>
      </template>
    </el-drawer>

    <!-- 所属团队抽屉 -->
    <MaterialTeamDrawer
      v-model:visible="teamDrawerVisible"
      :material-id="currentMaterialId"
      :material-name="currentMaterialName"
      @close="handleTeamDrawerClose"
    />
  </div>
</template>

<script setup lang="tsx">
import { reactive, ref, computed, nextTick } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { useHandleData } from "@/hooks/useHandleData";
import ProTable from "@/components/ProTable/index.vue";
import { ColumnProps, ProTableInstance } from "@/components/ProTable/interface";
import { CirclePlus, Delete, EditPen, View, Picture } from "@element-plus/icons-vue";
import { ElMessage, FormInstance } from "element-plus";
import MaterialTeamDrawer from "./components/dialogs/MaterialTeamDrawer.vue";

// 国际化
const { t } = useI18n();
const router = useRouter();
import {
  getMaterialLibraryListApi,
  deleteMaterialLibraryApi,
  createMaterialLibraryApi,
  updateMaterialLibraryApi,
  syncMaterialLibraryApi
} from "@/api/modules/materialLibrary";
import { getUploadFolders } from "@/api/modules/annotation";
import type { UploadFolderInfo } from "@/api/model/materialLibraryModel";

// ProTable 实例
const proTable = ref<ProTableInstance>();

// 初始化参数
const initParam = reactive({});

// dataCallback 是对于返回的表格数据做处理
const dataCallback = (data: any) => {
  const records = Array.isArray(data.records) ? data.records : [];
  const total = data.total || 0;

  return {
    records: records,
    total: total
  };
};

// 获取素材库列表
const getMaterialLibraryList = (params: any) => {
  return getMaterialLibraryListApi(params);
};

// 表格配置项
const columns = computed<ColumnProps<any>[]>(() => [
  {
    type: "selection",
    fixed: "left",
    width: 70
  },
  {
    prop: "id",
    label: t("materialLibrary.id"),
    width: 80
  },
  {
    prop: "name",
    label: t("materialLibrary.name"),
    width: 200,
    search: {
      el: "input",
      props: { placeholder: t("materialLibrary.inputName") }
    }
  },
  {
    prop: "path",
    label: t("materialLibrary.path"),
    search: {
      el: "input",
      props: { placeholder: t("materialLibrary.inputPath") }
    }
  },
  {
    prop: "total_num",
    label: t("materialLibrary.totalNum"),
    width: 120
  },
  {
    prop: "created",
    label: t("materialLibrary.created"),
    width: 200
  },
  { prop: "operation", label: t("materialLibrary.operation"), fixed: "right", width: 420 }
]);

// 当前表格列配置
const currentColumns = columns;

// 删除素材库
const deleteMaterialLibrary = async (params: any) => {
  await useHandleData(
    deleteMaterialLibraryApi,
    { id: params.id },
    t("materialLibrary.deleteConfirm", { name: params.name }),
    "warning",
    t
  );
  proTable.value?.getTableList();
};

// 同步素材库目录中的图片到数据库
const syncMaterialLibrary = async (params: any) => {
  try {
    await useHandleData(
      syncMaterialLibraryApi,
      { id: params.id },
      t("materialLibrary.syncConfirm", { name: params.name }),
      "warning",
      t
    );
    proTable.value?.getTableList();
  } catch {
    // useHandleData 已经处理了成功和失败的消息提示，这里只需要处理取消操作的情况
  }
};

// 批量删除素材库
const batchDelete = async (ids: (string | number)[]) => {
  if (ids.length === 0) {
    ElMessage.warning(t("materialLibrary.batchDeleteConfirm"));
    return;
  }

  try {
    for (const id of ids) {
      const numericId = typeof id === "string" ? parseInt(id, 10) : id;
      await useHandleData(deleteMaterialLibraryApi, { id: numericId }, t("materialLibrary.batchDeleteConfirm"), "warning", t);
    }
    proTable.value?.clearSelection();
    proTable.value?.getTableList();
    ElMessage.success(t("materialLibrary.batchDeleteSuccess", { count: ids.length }));
  } catch {
    ElMessage.error(t("materialLibrary.batchDeleteFailed"));
  }
};

// 抽屉相关状态
const drawerVisible = ref(false);
const drawerTitle = ref("");
const drawerTitleKey = ref(""); // 保存原始title key用于判断
const isView = ref(false);
const formData = reactive({
  id: undefined as number | undefined,
  name: "",
  path: ""
});
const currentApi = ref<((params: any) => Promise<any>) | undefined>(undefined);

// 表单验证规则
const rules = computed(() => {
  const baseRules: any = {
    name: [
      { required: true, message: "请填写名称", trigger: "blur" },
      { min: 1, max: 255, message: "名称长度必须在1-255个字符之间", trigger: "blur" }
    ]
  };

  // 只有新增模式才需要验证路径
  if (drawerTitleKey.value !== "编辑") {
    baseRules.path = [{ required: true, message: "请选择素材路径", trigger: "change" }];
  }

  return baseRules;
});

// 文件夹列表
const folderList = ref<UploadFolderInfo[]>([]);
const folderLoading = ref(false);

// 所属团队抽屉
const teamDrawerVisible = ref(false);
const currentMaterialName = ref("");
const currentMaterialId = ref<number>(0);

// 加载上传文件夹列表
const loadUploadFolders = async () => {
  // 如果正在加载中，避免重复请求
  if (folderLoading.value) {
    return;
  }

  folderLoading.value = true;
  try {
    const res = await getUploadFolders();
    // 处理响应数据，兼容不同的响应结构
    if (res && res.data && Array.isArray(res.data)) {
      folderList.value = res.data.map((item: any) => {
        // 如果item是字符串，转换为对象格式（兼容旧格式）
        if (typeof item === "string") {
          return {
            name: item,
            path: `/upload/up_img/${item}`
          };
        }
        // 后端返回的name和path已经保持一致，都包含配置目录前缀
        return {
          name: item.name || item.path || "",
          path: item.path || item.name || ""
        };
      });
    } else if (Array.isArray(res)) {
      folderList.value = res.map((item: any) => {
        // 如果item是字符串，转换为对象格式（兼容旧格式）
        if (typeof item === "string") {
          return {
            name: item,
            path: `/upload/up_img/${item}`
          };
        }
        // 后端返回的name和path已经保持一致，都包含配置目录前缀
        return {
          name: item.name || item.path || "",
          path: item.path || item.name || ""
        };
      });
    } else {
      folderList.value = [];
    }
  } catch {
    ElMessage.error("加载文件夹列表失败");
  } finally {
    folderLoading.value = false;
  }
};

// 打开 drawer(新增、查看、编辑)
const openDrawer = (title: string, row: Partial<any> = {}) => {
  const titleMap: Record<string, string> = {
    新增: t("materialLibrary.addMaterial"),
    编辑: t("materialLibrary.edit"),
    查看: t("materialLibrary.view")
  };
  drawerTitle.value = titleMap[title] || title;
  drawerTitleKey.value = title; // 保存原始title用于后续判断
  isView.value = title === "查看";

  if (title === "新增") {
    currentApi.value = createMaterialLibraryApi;
    formData.id = undefined;
    formData.name = "";
    formData.path = "";
    // 新增时自动加载文件夹列表
    loadUploadFolders();
  } else if (title === "编辑") {
    currentApi.value = updateMaterialLibraryApi;
    formData.id = row.id;
    formData.name = row.name || "";
    formData.path = row.path || "";
  } else {
    // 查看
    currentApi.value = undefined;
    formData.id = row.id;
    formData.name = row.name || "";
    formData.path = row.path || "";
  }

  drawerVisible.value = true;

  // 重置表单验证状态
  nextTick(() => {
    ruleFormRef.value?.clearValidate();
  });
};

// 提交数据（新增/编辑）
const ruleFormRef = ref<FormInstance>();
const handleSubmit = () => {
  ruleFormRef.value!.validate(async valid => {
    if (!valid) return;

    if (!currentApi.value) return;

    try {
      // 准备提交的数据
      const submitData: any = {
        name: formData.name?.trim()
      };

      // 如果是编辑模式，添加ID，但不发送路径
      if (drawerTitleKey.value === "编辑" && formData.id) {
        submitData.id = formData.id;
      } else {
        // 新增模式才发送路径
        submitData.path = formData.path?.trim();
      }

      await currentApi.value(submitData);
      ElMessage.success(t("common.operateSuccess", { message: drawerTitle.value }));
      proTable.value?.getTableList();
      drawerVisible.value = false;
    } catch (error: any) {
      ElMessage.error(error.response?.data?.message || t("common.operateSuccess", { message: drawerTitle.value }) + "失败");
    }
  });
};

// 打开所属团队抽屉
const openTeamDrawer = (row: any) => {
  currentMaterialName.value = row.name || "";
  currentMaterialId.value = row.id || 0;
  teamDrawerVisible.value = true;
};

// 关闭团队抽屉
const handleTeamDrawerClose = () => {
  teamDrawerVisible.value = false;
};

// 查看素材图片
const viewMaterialImages = (row: any) => {
  router.push({
    path: "/annotation/material-images",
    query: {
      id: row.id,
      name: row.name
    }
  });
};
</script>

<style scoped lang="scss">
@import "@/styles/table-optimization.scss";

.table-box {
  @extend .table-box;
}

// 避免在没有数据的情况下出现滚动条
:deep(.el-table) {
  .el-table__body-wrapper {
    // 当表格为空时，隐藏滚动条
    &:has(.el-table__empty-block) {
      overflow: hidden !important;
    }
  }

  .el-table__empty-block {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }
}

:deep(.el-table__header) {
  background-color: #f5f7fa;
}

:deep(.el-button--link) {
  padding: 4px 8px;
  margin: 0 2px;
}
</style>
