<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="800px" :title="`${drawerProps.title}场景`">
    <!-- 步骤条 -->
    <div class="steps-container" v-if="!drawerProps.isView && drawerProps.title === '新增'">
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="基本信息" description="填写场景基本信息" />
        <el-step title="绑定模型" description="选择要绑定的模型" />
        <el-step title="完成" description="保存场景配置" />
      </el-steps>
    </div>

    <!-- 步骤1：基本信息 -->
    <div v-if="currentStep === 0 || drawerProps.isView || drawerProps.title !== '新增'">
      <el-form
        ref="ruleFormRef"
        label-width="100px"
        label-suffix=" :"
        :rules="rules"
        :disabled="drawerProps.isView"
        :model="drawerProps.row"
        :hide-required-asterisk="drawerProps.isView"
      >
        <el-form-item :label="t('scene.sceneName')" prop="name">
          <el-input
            v-model="drawerProps.row.name"
            :placeholder="t('scene.enterSceneName')"
            maxlength="100"
            show-word-limit
            clearable
          />
        </el-form-item>

        <el-form-item :label="t('scene.sceneDescription')" prop="description">
          <el-input
            v-model="drawerProps.row.description"
            type="textarea"
            :rows="3"
            :placeholder="t('scene.enterSceneDescription')"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item :label="t('scene.executionFrequency')" prop="hz">
          <div class="frequency-selection">
            <el-radio-group v-model="drawerProps.row.hz" :disabled="drawerProps.isView" class="frequency-group">
              <div class="frequency-grid">
                <el-radio v-for="freq in executionFrequencies" :key="freq.value" :value="freq.value" class="frequency-radio">
                  <div class="frequency-option">
                    <span class="frequency-label">{{ freq.label }}</span>
                    <el-tooltip v-if="freq.description" :content="freq.description" placement="top" effect="dark">
                      <el-icon class="frequency-info-icon"><InfoFilled /></el-icon>
                    </el-tooltip>
                  </div>
                </el-radio>
              </div>
            </el-radio-group>
            <div class="frequency-tip">
              <el-icon><InfoFilled /></el-icon>
              <span>选择场景的执行频率，系统将按此频率运行场景任务</span>
            </div>
          </div>
        </el-form-item>

        <el-form-item :label="t('scene.sortOrder')" prop="sort_order">
          <el-input-number v-model="drawerProps.row.sort_order" :min="0" :max="999" :disabled="drawerProps.isView" />
        </el-form-item>

        <el-form-item :label="t('scene.status')" prop="status">
          <el-radio-group v-model="drawerProps.row.status" :disabled="drawerProps.isView">
            <el-radio :value="1">{{ t("scene.enabled") }}</el-radio>
            <el-radio :value="0">{{ t("scene.disabled") }}</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </div>

    <!-- 步骤2：绑定模型 -->
    <div v-if="currentStep === 1 && !drawerProps.isView && drawerProps.title === '新增'">
      <div class="model-selection">
        <h4>选择要绑定的模型</h4>
        <p class="step-description">
          <el-icon><Warning /></el-icon>
          请选择要绑定到此场景的模型，可以多选。<strong>必须至少选择一个模型才能继续下一步。</strong>
        </p>
        <div v-if="selectedModels.length > 0" class="selected-count">
          <el-tag type="success" size="large">
            <el-icon><Check /></el-icon>
            已选择 {{ selectedModels.length }} 个模型
          </el-tag>
        </div>

        <ProTable
          ref="modelProTable"
          :columns="modelColumns"
          :request-api="getModelList"
          :init-param="modelInitParam"
          :data-callback="modelDataCallback"
          :pagination="true"
          @row-click="handleRowClick"
          :row-class-name="getRowClassName"
        >
          <template #empty>
            <div class="empty-state">
              <el-empty description="暂无可绑定的模型">
                <el-button type="primary" @click="goToModelManage">去模型管理添加模型</el-button>
              </el-empty>
            </div>
          </template>
        </ProTable>
      </div>
    </div>

    <!-- 步骤3：完成 -->
    <div v-if="currentStep === 2 && !drawerProps.isView && drawerProps.title === '新增'">
      <div class="completion-step">
        <el-result icon="success" title="配置完成" sub-title="场景信息已配置完成，点击保存即可创建场景">
          <template #extra>
            <div class="summary-info">
              <h4>场景信息摘要：</h4>
              <p><strong>场景名称：</strong>{{ drawerProps.row.name }}</p>
              <p><strong>场景描述：</strong>{{ drawerProps.row.description || "无" }}</p>
              <p><strong>执行频率：</strong>{{ drawerProps.row.hz ? `${drawerProps.row.hz}秒` : "未设置" }}</p>
              <p><strong>状态：</strong>{{ drawerProps.row.status === 1 ? "启用" : "禁用" }}</p>
              <p><strong>已选择模型：</strong>{{ selectedModels.length }} 个</p>
              <div v-if="selectedModels.length > 0" class="selected-models">
                <el-tag v-for="model in selectedModels" :key="model.id" class="model-tag">
                  {{ model.name }}
                </el-tag>
              </div>
            </div>
          </template>
        </el-result>
      </div>
    </div>

    <template #footer>
      <div class="footer-buttons">
        <el-button @click="drawerVisible = false">{{ t("common.cancel") }}</el-button>

        <!-- 编辑模式或查看模式 -->
        <template v-if="drawerProps.isView || drawerProps.title !== '新增'">
          <el-button v-show="!drawerProps.isView" type="primary" :loading="submitting" @click="handleSubmit">
            {{ t("common.confirm") }}
          </el-button>
        </template>

        <!-- 新增模式分步骤 -->
        <template v-else>
          <el-button v-if="currentStep > 0" @click="prevStep">上一步</el-button>
          <el-button v-if="currentStep < 2" type="primary" @click="nextStep">下一步</el-button>
          <el-button v-if="currentStep === 2" type="primary" :loading="submitting" @click="handleSubmit"> 保存场景 </el-button>
        </template>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, reactive } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";
import { ElMessage, FormInstance } from "element-plus";
import { InfoFilled, Warning, Check } from "@element-plus/icons-vue";
import ProTable from "@/components/ProTable/index.vue";
import { ColumnProps, ProTableInstance } from "@/components/ProTable/interface";
import { saveScene, getSceneFrequencyOptions } from "@/api/modules/scene";
import { getModelListApi } from "@/api/modules/model";

interface Scene {
  id?: number;
  name: string;
  description: string;
  status: number;
  sort_order: number;
  hz?: number;
}

interface Model {
  id: number;
  name: string;
  desc: string;
  created: string;
}

interface DrawerProps {
  title: string;
  isView: boolean;
  row: Scene;
  api?: (params: any) => Promise<any>;
  getTableList?: () => void;
}

// 国际化
const { t } = useI18n();
const router = useRouter();

// 步骤控制
const currentStep = ref(0);

// 模型选择相关
const selectedModels = ref<Model[]>([]);
const modelProTable = ref<ProTableInstance>();

// 执行频率选项
const executionFrequencies = ref<Array<{ label: string; value: number; description?: string }>>([]);

// 模型表格列配置
const modelColumns = reactive<ColumnProps<Model>[]>([
  {
    prop: "id",
    label: "ID",
    width: 80
  },
  {
    prop: "name",
    label: "模型名称",
    width: 200,
    search: {
      el: "input",
      props: { placeholder: "请输入模型名称" }
    }
  },
  {
    prop: "desc",
    label: "模型描述",
    minWidth: 200,
    showOverflowTooltip: true
  },
  {
    prop: "created",
    label: "创建时间",
    width: 200
  }
]);

// 模型查询参数
const modelInitParam = reactive<{
  name?: string;
}>({});

// 模型数据回调
const modelDataCallback = (data: any) => {
  return {
    records: data.records || [],
    total: data.total || 0
  };
};

const rules = computed(() => ({
  name: [
    { required: true, message: t("scene.nameRequired"), trigger: "blur" },
    { min: 2, max: 100, message: t("scene.nameLength"), trigger: "blur" },
    {
      validator: (rule: any, value: string, callback: (error?: Error) => void) => {
        if (value && value.trim().length === 0) {
          callback(new Error(t("scene.nameRequired")));
        } else {
          callback();
        }
      },
      trigger: "blur"
    }
  ],
  description: [{ max: 500, message: t("scene.descriptionLength"), trigger: "blur" }],
  status: [{ required: true, message: t("scene.statusRequired"), trigger: "change" }],
  sort_order: [
    {
      validator: (rule: any, value: number, callback: (error?: Error) => void) => {
        if (value !== undefined && (value < 0 || value > 999)) {
          callback(new Error("排序值必须在0-999之间"));
        } else {
          callback();
        }
      },
      trigger: "blur"
    }
  ],
  hz: [
    { required: true, message: "请选择执行频率", trigger: "change" },
    {
      validator: (rule: any, value: number, callback: (error?: Error) => void) => {
        if (value !== undefined && value !== null) {
          const validValues = [0.5, 1, 2, 4, 6, 8, 10];
          if (!validValues.includes(value)) {
            callback(new Error("执行频率只能选择0.5、1、2、4、6、8、10秒"));
          } else {
            callback();
          }
        } else {
          callback(new Error("请选择执行频率"));
        }
      },
      trigger: "change"
    }
  ]
}));

const drawerVisible = ref(false);
const submitting = ref(false);

const drawerProps = ref<DrawerProps>({
  isView: false,
  title: "",
  row: {
    name: "",
    description: "",
    status: 1,
    sort_order: 0,
    hz: undefined
  }
});

// 步骤控制方法
const nextStep = () => {
  if (currentStep.value === 0) {
    // 验证基本信息
    ruleFormRef.value?.validate(valid => {
      if (valid) {
        // 额外验证执行频率
        if (drawerProps.value.row.hz === undefined || drawerProps.value.row.hz === null) {
          ElMessage.warning("请选择执行频率");
          return;
        }

        currentStep.value++;
        // 加载模型列表
        nextTick(() => {
          modelProTable.value?.getTableList();
        });
      } else {
        ElMessage.warning("请完善基本信息");
      }
    });
  } else if (currentStep.value === 1) {
    // 验证是否选择了模型
    if (selectedModels.value.length === 0) {
      ElMessage.warning("请至少选择一个模型进行绑定");
      return;
    }
    // 进入完成步骤
    currentStep.value++;
  }
};

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--;
  }
};

// 模型选择相关方法
const getModelList = async (params: any) => {
  try {
    const response = await getModelListApi(params);
    return response;
  } catch {
    return {
      code: 200,
      data: {
        records: [],
        total: 0
      }
    };
  }
};

// 处理行点击事件
const handleRowClick = (row: Model) => {
  // 切换该行的选中状态
  const currentSelection = selectedModels.value;
  const isSelected = currentSelection.some(model => model.id === row.id);

  if (isSelected) {
    // 如果已选中，则取消选中
    selectedModels.value = currentSelection.filter(model => model.id !== row.id);
  } else {
    // 如果未选中，则选中
    selectedModels.value = [...currentSelection, row];
  }
};

// 获取行样式类名
const getRowClassName = ({ row }: { row: Model }) => {
  const isSelected = selectedModels.value.some(model => model.id === row.id);
  return isSelected ? "selected-row" : "";
};

const goToModelManage = () => {
  router.push("/modelManage/list");
};

// 获取执行频率选项
const loadFrequencyOptions = async () => {
  try {
    const response = await getSceneFrequencyOptions();
    if (response && response.code === 200 && response.data) {
      executionFrequencies.value = response.data as Array<{ label: string; value: number; description?: string }>;
    } else {
      // 使用默认选项作为后备
      executionFrequencies.value = [
        { label: "0.5秒", value: 0.5, description: "高频执行，适合实时性要求高的场景" },
        { label: "1秒", value: 1, description: "标准频率，适合大多数场景" },
        { label: "2秒", value: 2, description: "中等频率，适合一般监控场景" },
        { label: "4秒", value: 4, description: "低频执行，适合资源敏感场景" },
        { label: "6秒", value: 6, description: "较低频率，适合非关键场景" },
        { label: "8秒", value: 8, description: "低频率，适合后台处理场景" },
        { label: "10秒", value: 10, description: "最低频率，适合批量处理场景" }
      ];
    }
  } catch {
    // 使用默认选项作为后备
    executionFrequencies.value = [
      { label: "0.5秒", value: 0.5, description: "高频执行，适合实时性要求高的场景" },
      { label: "1秒", value: 1, description: "标准频率，适合大多数场景" },
      { label: "2秒", value: 2, description: "中等频率，适合一般监控场景" },
      { label: "4秒", value: 4, description: "低频执行，适合资源敏感场景" },
      { label: "6秒", value: 6, description: "较低频率，适合非关键场景" },
      { label: "8秒", value: 8, description: "低频率，适合后台处理场景" },
      { label: "10秒", value: 10, description: "最低频率，适合批量处理场景" }
    ];
  }
};

// 接收父组件传过来的参数
const acceptParams = (params: DrawerProps) => {
  // 深拷贝参数，避免直接修改原始数据
  drawerProps.value = {
    ...params,
    row: { ...params.row }
  };

  // 重置步骤
  currentStep.value = 0;
  selectedModels.value = [];

  // 设置默认值（仅在新增时设置，编辑时保持原有值）
  if (drawerProps.value.title === "新增") {
    if (drawerProps.value.row.sort_order === undefined || drawerProps.value.row.sort_order === null) {
      drawerProps.value.row.sort_order = 0;
    }
    if (drawerProps.value.row.status === undefined || drawerProps.value.row.status === null) {
      drawerProps.value.row.status = 1;
    }
    if (drawerProps.value.row.hz === undefined || drawerProps.value.row.hz === null) {
      drawerProps.value.row.hz = undefined;
    }
  } else {
    // 编辑时，确保数值类型正确，但不覆盖现有值
    if (drawerProps.value.row.sort_order !== undefined && drawerProps.value.row.sort_order !== null) {
      drawerProps.value.row.sort_order = Number(drawerProps.value.row.sort_order);
    }
    if (drawerProps.value.row.status !== undefined && drawerProps.value.row.status !== null) {
      drawerProps.value.row.status = Number(drawerProps.value.row.status);
    }
    if (drawerProps.value.row.hz !== undefined && drawerProps.value.row.hz !== null) {
      drawerProps.value.row.hz = Number(drawerProps.value.row.hz);
    }
  }

  // 确保字符串字段不为null
  drawerProps.value.row.name = drawerProps.value.row.name || "";
  drawerProps.value.row.description = drawerProps.value.row.description || "";

  drawerVisible.value = true;

  // 加载执行频率选项
  loadFrequencyOptions();

  // 如果是编辑模式，重置表单验证状态
  if (drawerProps.value.title === "编辑" && ruleFormRef.value) {
    nextTick(() => {
      ruleFormRef.value?.clearValidate();
    });
  }
};

// 提交数据（新增/编辑）
const ruleFormRef = ref<FormInstance>();
const handleSubmit = async () => {
  // 如果是新增模式且不是最后一步，先验证基本信息
  if (drawerProps.value.title === "新增" && currentStep.value < 2) {
    ruleFormRef.value?.validate(valid => {
      if (valid) {
        nextStep();
      } else {
        ElMessage.warning("请完善基本信息");
      }
    });
    return;
  }

  // 如果是新增模式的第三步，跳过表单验证直接保存
  if (drawerProps.value.title === "新增" && currentStep.value === 2) {
    await performSave();
    return;
  }

  // 验证表单
  if (!ruleFormRef.value) {
    ElMessage.error("表单未正确初始化，请重试");
    return;
  }

  ruleFormRef.value.validate(async valid => {
    if (!valid) {
      ElMessage.warning("请检查表单填写是否完整");
      return;
    }
    await performSave();
  });
};

// 执行保存操作
const performSave = async () => {
  try {
    submitting.value = true;

    // 只取表单字段并清理数据
    const { id, name, description, status, sort_order, hz } = drawerProps.value.row;

    // 组装提交数据，确保数据类型正确
    const submitData: any = {
      name: name?.trim() || "",
      description: description?.trim() || "",
      status: status !== undefined && status !== null ? Number(status) : 1,
      sort_order: sort_order !== undefined && sort_order !== null ? Number(sort_order) : 0,
      hz: hz !== undefined && hz !== null ? Number(hz) : undefined
    };

    // 如果是新增模式且选择了模型，添加模型ID列表
    if (drawerProps.value.title === "新增" && selectedModels.value.length > 0) {
      submitData.model_ids = selectedModels.value.map(model => model.id);
    }

    // 编辑时需要包含id
    if (id) {
      submitData.id = Number(id);
    }

    // 使用传入的API或默认的saveScene
    const api = drawerProps.value.api || saveScene;
    const response = await api(submitData);

    // 检查响应状态
    if (response && (response.code === 200 || response.code === "200")) {
      // 根据操作类型显示不同的成功消息
      const successMessage =
        drawerProps.value.title === "新增"
          ? t("scene.addSuccess")
          : drawerProps.value.title === "编辑"
            ? t("scene.editSuccess")
            : `${drawerProps.value.title}场景成功！`;

      ElMessage.success(successMessage);

      // 刷新表格数据
      if (drawerProps.value.getTableList) {
        drawerProps.value.getTableList();
      }

      // 关闭抽屉
      drawerVisible.value = false;
    } else {
      // API返回错误
      const errorMessage =
        response?.message || (drawerProps.value.title === "新增" ? t("scene.addFailed") : t("scene.editFailed"));
      ElMessage.error(errorMessage);
    }
  } catch (error: any) {
    // 处理不同类型的错误
    let errorMessage = "操作失败";
    if (error?.response?.data?.message) {
      errorMessage = error.response.data.message;
    } else if (error?.message) {
      errorMessage = error.message;
    } else if (drawerProps.value.title === "新增") {
      errorMessage = t("scene.addFailed");
    } else if (drawerProps.value.title === "编辑") {
      errorMessage = t("scene.editFailed");
    }

    ElMessage.error(errorMessage);
  } finally {
    submitting.value = false;
  }
};

defineExpose({
  acceptParams
});
</script>

<style scoped lang="scss">
.steps-container {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.model-selection {
  .step-description {
    color: #666;
    margin-bottom: 15px;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 8px;

    .el-icon {
      color: #e6a23c;
      font-size: 16px;
    }

    strong {
      color: #e6a23c;
      font-weight: 600;
    }
  }

  .selected-count {
    margin-bottom: 20px;

    .el-tag {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 14px;
      padding: 8px 16px;
    }
  }
}

.completion-step {
  .summary-info {
    text-align: left;
    background: #f8f9fa;
    padding: 40px;
    border-radius: 12px;
    margin-top: 20px;
    width: 95%;
    margin-left: auto;
    margin-right: auto;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);

    h4 {
      margin: 0 0 25px 0;
      color: #303133;
      font-size: 20px;
      font-weight: 600;
      text-align: center;
      border-bottom: 2px solid #e4e7ed;
      padding-bottom: 15px;
    }

    p {
      margin: 15px 0;
      color: #606266;
      font-size: 16px;
      line-height: 1.8;
      display: flex;
      align-items: center;

      strong {
        color: #303133;
        font-weight: 600;
        min-width: 120px;
        margin-right: 10px;
      }
    }

    .selected-models {
      margin-top: 20px;
      padding-top: 15px;
      border-top: 1px solid #e4e7ed;

      .model-tag {
        margin-right: 12px;
        margin-bottom: 12px;
        padding: 8px 16px;
        font-size: 14px;
        border-radius: 20px;
        background: #e6f7ff;
        color: #409eff;
        border: 1px solid #b3d8ff;
      }
    }
  }
}

.footer-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

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

:deep(.el-drawer__body) {
  padding: 20px;
}

:deep(.el-steps) {
  .el-step__title {
    font-weight: 500;
  }

  .el-step__description {
    font-size: 12px;
    color: #909399;
  }
}

// 执行频率选择区域样式
.frequency-selection {
  .frequency-group {
    margin-bottom: 12px;
  }

  .frequency-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 8px;
  }

  .frequency-radio {
    margin: 0;
    padding: 8px 12px;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    background: #fafafa;
    transition: all 0.3s ease;
    cursor: pointer;
    flex-shrink: 0;

    &:hover {
      border-color: #409eff;
      background: #f0f9ff;
    }

    :deep(.el-radio__input) {
      display: none;
    }

    :deep(.el-radio__label) {
      padding: 0;
      font-size: 13px;
      font-weight: 500;
      color: #606266;
      text-align: center;
      white-space: nowrap;
    }

    &.is-checked {
      border-color: #409eff;
      background: #e6f7ff;

      .frequency-label {
        color: #409eff;
        font-weight: 600;
      }
    }
  }

  .frequency-tip {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    background: #f8f9fa;
    border-radius: 6px;
    font-size: 13px;
    color: #909399;
    border-left: 3px solid #409eff;

    .el-icon {
      color: #409eff;
      font-size: 14px;
    }
  }
}

// 模型表格样式
:deep(.el-table) {
  .selected-row {
    background-color: #e6f7ff !important;

    &:hover {
      background-color: #bae7ff !important;
    }
  }

  tbody tr {
    cursor: pointer;
    transition: background-color 0.2s ease;

    &:hover:not(.selected-row) {
      background-color: #f5f7fa;
    }
  }
}

// 执行频率选项样式优化
.frequency-option {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 6px;

  .frequency-label {
    font-weight: 500;
    color: #606266;
  }

  .frequency-info-icon {
    color: #909399;
    font-size: 14px;
    cursor: help;
    transition: color 0.2s ease;

    &:hover {
      color: #409eff;
    }
  }
}
</style>
