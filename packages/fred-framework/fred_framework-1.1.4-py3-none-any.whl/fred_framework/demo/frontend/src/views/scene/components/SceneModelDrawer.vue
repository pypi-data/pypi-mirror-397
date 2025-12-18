<template>
  <el-drawer v-model="dialogVisible" :title="`${sceneName} - 模型管理`" size="1200px" :destroy-on-close="true" direction="rtl">
    <div class="scene-model-management">
      <!-- 场景信息 -->
      <div class="scene-info" v-if="sceneInfo">
        <el-card class="info-card">
          <div class="info-content">
            <div class="info-item">
              <span class="label">场景名称：</span>
              <span class="value">{{ sceneInfo.name }}</span>
            </div>
            <div class="info-item">
              <span class="label">场景描述：</span>
              <span class="value">{{ sceneInfo.description || "暂无描述" }}</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 模型管理区域 -->
      <div class="model-management">
        <div class="tab-content">
          <div class="section-header">
            <h4>已绑定的模型列表</h4>
            <div class="header-actions">
              <el-button type="primary" size="small" @click="refreshBoundList">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </div>

          <ProTable
            ref="boundProTable"
            :columns="boundColumns"
            :request-api="getBoundModelList"
            :init-param="initParam"
            :data-callback="boundDataCallback"
            :pagination="boundPagination"
          >
            <!-- 空状态插槽 -->
            <template #empty>
              <div class="empty-state">
                <el-empty description="该场景暂无绑定的模型">
                  <el-button type="primary" @click="goToModelManage">去模型管理添加模型</el-button>
                </el-empty>
              </div>
            </template>

            <!-- 操作列 -->
            <template #operation="scope">
              <el-button type="danger" link :icon="Delete" @click="handleUnbind(scope.row)"> 解绑 </el-button>
            </template>
          </ProTable>
        </div>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="tsx">
import { ref, reactive, nextTick } from "vue";
import { useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import { Refresh, Delete } from "@element-plus/icons-vue";
import ProTable from "@/components/ProTable/index.vue";
import { ColumnProps, ProTableInstance } from "@/components/ProTable/interface";
import { getSceneModelList, unbindSceneModel } from "@/api/modules/scene";

interface SceneInfo {
  id: number;
  name: string;
  description: string;
  status: number;
}

interface BoundModel {
  id: number;
  model_id: number;
  scene_id: number;
  model_name: string;
  model_desc: string;
  created: string;
}

// 路由
const router = useRouter();

// 抽屉显示状态
const dialogVisible = ref(false);

// 场景信息
const sceneInfo = ref<SceneInfo | null>(null);
const sceneName = ref<string>("");

// ProTable 实例
const boundProTable = ref<ProTableInstance>();

// 初始化参数
const initParam = reactive<{
  scene_id?: number;
  name?: string;
}>({});

// 已绑定模型的数据回调
const boundDataCallback = (data: any) => {
  const records = data.records || [];
  const total = data.total || 0;

  // 根据数据是否为空来控制分页组件显示
  boundPagination.value = total > 0;

  return {
    records: records,
    total: total
  };
};

// 控制分页组件显示
const boundPagination = ref(true);

// 已绑定模型表格列配置
const boundColumns = reactive<ColumnProps<BoundModel>[]>([
  {
    prop: "id",
    label: "ID",
    width: 80
  },
  {
    prop: "model_name",
    label: "模型名称",
    width: 200,
    search: {
      el: "input",
      props: { placeholder: "请输入模型名称" }
    }
  },
  {
    prop: "model_desc",
    label: "模型简介",
    minWidth: 200,
    showOverflowTooltip: true
  },
  {
    prop: "created",
    label: "绑定时间",
    width: 200
  },
  { prop: "operation", label: "操作", fixed: "right", width: 120 }
]);

// 获取已绑定模型列表
const getBoundModelList = (params: any) => {
  const requestParams = {
    ...params,
    scene_id: initParam.scene_id
  };

  return getSceneModelList(requestParams);
};

// 刷新已绑定列表
const refreshBoundList = () => {
  boundProTable.value?.getTableList();
};

// 解绑模型
const handleUnbind = async (relation: BoundModel) => {
  try {
    await ElMessageBox.confirm(`确定要解绑模型"${relation.model_name}"吗？`, "提示", { type: "warning" });

    await unbindSceneModel({
      relation_id: relation.id
    });

    ElMessage.success("解绑成功");
    nextTick(() => {
      boundProTable.value?.getTableList(); // 重新加载已绑定列表
    });
  } catch {
    // 用户取消操作
  }
};

// 打开抽屉
const openDrawer = (scene: SceneInfo) => {
  sceneInfo.value = scene;
  sceneName.value = scene.name;

  // 设置查询参数
  Object.assign(initParam, {
    scene_id: scene.id,
    name: ""
  });

  dialogVisible.value = true;

  // 重置分页组件显示状态
  boundPagination.value = true;

  // 使用 nextTick 确保组件完全渲染后再调用
  nextTick(() => {
    // 延迟一点时间，确保 ProTable 组件完全初始化
    setTimeout(() => {
      if (boundProTable.value) {
        boundProTable.value.getTableList();
      }
    }, 100);
  });
};

// 跳转到模型管理页面
const goToModelManage = () => {
  if (sceneInfo.value) {
    router.push({
      path: "/modelManage/list",
      query: { sceneId: sceneInfo.value.id, sceneName: sceneInfo.value.name }
    });
  } else {
    router.push("/modelManage/list");
  }
};

// 暴露方法给父组件
defineExpose({
  openDrawer
});
</script>

<style scoped lang="scss">
.scene-model-management {
  .scene-info {
    margin-bottom: 20px;

    .info-card {
      .info-content {
        .info-item {
          display: flex;
          align-items: center;
          margin-bottom: 12px;

          &:last-child {
            margin-bottom: 0;
          }

          .label {
            font-weight: 500;
            color: #606266;
            min-width: 80px;
          }

          .value {
            color: #303133;
            flex: 1;
          }
        }
      }
    }
  }

  .model-management {
    .tab-content {
      min-height: 500px;

      .section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;

        h4 {
          margin: 0;
          color: #303133;
          font-size: 16px;
          font-weight: 500;
        }

        .header-actions {
          display: flex;
          gap: 8px;
        }
      }
    }
  }
}

.operation-buttons {
  display: flex;
  gap: 4px;
  align-items: center;
}

.file-path {
  .no-path {
    color: #c0c4cc;
    font-size: 12px;
  }
}

:deep(.el-drawer__header) {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

:deep(.el-card) {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

:deep(.el-button--link) {
  padding: 4px 8px;
  margin: 0 2px;
}

:deep(.el-tabs__content) {
  padding-top: 16px;
}

// 确保ProTable在空数据时有足够的高度
:deep(.pro-table) {
  .el-table__empty-block {
    min-height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }

  .el-table__empty-text {
    width: 100%;
  }
}

// 确保表格容器有足够高度
:deep(.el-table) {
  .el-table__body-wrapper {
    min-height: 300px;
  }

  .el-table__empty-block {
    min-height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
  }
}

// 空状态样式 - 参考ProTable的table-empty样式
.empty-state {
  padding: 40px 20px;
  text-align: center;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  :deep(.el-empty) {
    width: 100%;

    .el-empty__image {
      margin-bottom: 16px;
      width: 80px;
      height: 80px;
    }

    .el-empty__description {
      margin-bottom: 16px;
      color: #909399;
      font-size: 14px;
      line-height: 1.5;
    }

    .el-empty__bottom {
      margin-top: 16px;
    }
  }
}

// 确保表格空状态正确显示
:deep(.el-table__empty-block) {
  height: 300px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;

  .table-empty {
    line-height: 30px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 200px;

    img {
      display: inline-flex;
      width: 80px;
      height: 80px;
      margin-bottom: 16px;
    }

    div {
      color: #909399;
      font-size: 14px;
    }
  }
}

// 强制设置表格容器高度
:deep(.el-table__body-wrapper) {
  min-height: 300px !important;
}

// 确保ProTable容器有足够高度
:deep(.pro-table) {
  .table-main {
    min-height: 400px;
  }
}
</style>
