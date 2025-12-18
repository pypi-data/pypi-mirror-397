<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="500px" :title="`${drawerProps.title}模型`">
    <el-form
      ref="ruleFormRef"
      label-width="100px"
      label-suffix=" :"
      :rules="rules"
      :disabled="drawerProps.isView"
      :model="drawerProps.row"
      :hide-required-asterisk="drawerProps.isView"
    >
      <el-form-item :label="t('model.name')" prop="name">
        <el-input v-model="drawerProps.row!.name" :placeholder="t('model.enterModelName')" clearable></el-input>
      </el-form-item>
      <el-form-item :label="t('model.description')" prop="desc">
        <el-input
          v-model="drawerProps.row!.desc"
          :placeholder="t('model.enterModelDesc')"
          clearable
          type="textarea"
          :autosize="{ minRows: 3, maxRows: 6 }"
        ></el-input>
      </el-form-item>
      <el-form-item :label="t('model.filePath')" prop="file_path">
        <el-input v-model="drawerProps.row!.file_path" :placeholder="t('model.enterModelFilePath')" clearable></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="drawerVisible = false">{{ t("common.cancel") }}</el-button>
      <el-button v-if="!drawerProps.isView" type="primary" @click="handleSubmit">{{ t("common.confirm") }}</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts" name="ModelDrawer">
import { ref, reactive, nextTick } from "vue";
import { useI18n } from "vue-i18n";
import { ElMessage, FormInstance } from "element-plus";

// 国际化
const { t } = useI18n();

const rules = reactive({
  name: [
    { required: true, message: "请填写模型名称", trigger: "blur" },
    { min: 1, max: 50, message: "模型名称长度必须在1-50个字符之间", trigger: "blur" }
  ],
  desc: [{ max: 255, message: "模型简介长度不能超过255个字符", trigger: "blur" }],
  file_path: [{ max: 255, message: "模型文件路径长度不能超过255个字符", trigger: "blur" }]
});

interface DrawerProps {
  title: string;
  isView: boolean;
  row: Partial<any>;
  api?: (params: any) => Promise<any>;
  getTableList?: () => void;
}

const drawerVisible = ref(false);
const drawerProps = ref<DrawerProps>({
  isView: false,
  title: "",
  row: {}
});

// 接收父组件传过来的参数
const acceptParams = (params: DrawerProps) => {
  drawerProps.value = params;

  // 如果是新增模式，清空表单数据
  if (params.title === "新增") {
    drawerProps.value.row = {
      name: "",
      desc: "",
      file_path: ""
    };
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

    try {
      // 准备提交的数据
      const submitData: any = {
        name: drawerProps.value.row.name?.trim(),
        desc: drawerProps.value.row.desc?.trim() || "",
        file_path: drawerProps.value.row.file_path?.trim() || ""
      };

      // 如果是编辑模式，添加ID
      if (drawerProps.value.title === "编辑" && drawerProps.value.row.id) {
        submitData.id = drawerProps.value.row.id;
      }

      await drawerProps.value.api!(submitData);
      ElMessage.success(`${drawerProps.value.title}模型成功！`);
      drawerProps.value.getTableList!();
      drawerVisible.value = false;
    } catch (error: any) {
      ElMessage.error(error.response?.data?.message || `${drawerProps.value.title}模型失败！`);
    }
  });
};

defineExpose({
  acceptParams
});
</script>
