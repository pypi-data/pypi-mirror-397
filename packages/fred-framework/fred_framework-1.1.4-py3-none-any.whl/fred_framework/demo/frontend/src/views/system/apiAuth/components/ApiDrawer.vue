<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="450px" :title="`${drawerProps.title}API信息`">
    <el-form
      ref="ruleFormRef"
      label-width="100px"
      label-suffix=" :"
      :rules="rules"
      :disabled="drawerProps.isView"
      :model="drawerProps.row"
      :hide-required-asterisk="drawerProps.isView"
    >
      <el-form-item label="API名字" prop="name">
        <el-select
          v-model="drawerProps.row.name"
          placeholder="请选择API名字"
          clearable
          filterable
          style="width: 100%"
          :disabled="drawerProps.isView"
        >
          <el-option v-for="item in blueprintNames" :key="item" :label="item" :value="item" />
        </el-select>
      </el-form-item>
      <el-form-item label="说明" prop="desc">
        <el-input
          v-model="drawerProps.row.desc"
          type="textarea"
          :rows="3"
          placeholder="请输入说明"
          clearable
          maxlength="255"
          show-word-limit
        ></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="drawerVisible = false">取消</el-button>
      <el-button v-show="!drawerProps.isView" type="primary" @click="handleSubmit">确定</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, FormInstance } from "element-plus";
import type { ApiInfo, ApiInfoSaveParams } from "@/api/model/apiAuthModel";
import { getBlueprintNames } from "@/api/modules/apiAuth";

const rules = reactive({
  name: [{ required: true, message: "请选择API名字", trigger: "change" }]
});

interface DrawerProps {
  title: string;
  isView: boolean;
  row: Partial<ApiInfo>;
  api?: (params: ApiInfoSaveParams) => Promise<any>;
  getTableList?: () => void;
}

const drawerVisible = ref(false);
const drawerProps = ref<DrawerProps>({
  isView: false,
  title: "",
  row: {}
});
const blueprintNames = ref<string[]>([]);

// 加载蓝图名字列表
const loadBlueprintNames = async () => {
  try {
    const response = await getBlueprintNames();
    blueprintNames.value = response.data || [];
  } catch {
    console.error("获取蓝图名字失败:", error);
    blueprintNames.value = [];
  }
};

onMounted(() => {
  loadBlueprintNames();
});

const acceptParams = (params: DrawerProps) => {
  drawerProps.value = params;
  drawerVisible.value = true;
};

const ruleFormRef = ref<FormInstance>();
const handleSubmit = () => {
  ruleFormRef.value!.validate(async valid => {
    if (!valid) return;
    try {
      const submitData: ApiInfoSaveParams = {
        name: drawerProps.value.row.name!,
        desc: drawerProps.value.row.desc,
        api_pre: drawerProps.value.row.name!
      };

      await drawerProps.value.api!(submitData);
      ElMessage.success({ message: `${drawerProps.value.title}API信息成功！` });
      if (drawerProps.value.getTableList) {
        drawerProps.value.getTableList();
      }
      drawerVisible.value = false;
    } catch {}
  });
};

defineExpose({
  acceptParams
});
</script>

<style scoped lang="scss"></style>
