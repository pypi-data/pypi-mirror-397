<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="450px" :title="`${drawerProps.title}Token`">
    <el-form
      ref="ruleFormRef"
      label-width="100px"
      label-suffix=" :"
      :rules="rules"
      :disabled="drawerProps.isView"
      :model="drawerProps.row"
      :hide-required-asterisk="drawerProps.isView"
    >
      <el-form-item label="用户名" prop="username" v-if="!drawerProps.row.id">
        <el-input
          v-model="drawerProps.row.username"
          placeholder="请输入用户名"
          clearable
          maxlength="100"
          show-word-limit
        ></el-input>
      </el-form-item>
      <el-form-item label="到期时间" prop="expiration">
        <el-date-picker
          v-model="drawerProps.row.expiration"
          type="datetime"
          placeholder="请选择到期时间（可选）"
          format="YYYY-MM-DD HH:mm:ss"
          value-format="YYYY-MM-DD HH:mm:ss"
          style="width: 100%"
          clearable
          :disabled-date="disabledDate"
          :disabled-time="disabledTime"
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="drawerVisible = false">取消</el-button>
      <el-button v-show="!drawerProps.isView" type="primary" @click="handleSubmit">确定</el-button>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { ElMessage, FormInstance } from "element-plus";
import type { ApiToken, ApiTokenSaveParams } from "@/api/model/apiAuthModel";

const rules = reactive({
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }]
});

interface DrawerProps {
  title: string;
  isView: boolean;
  row: Partial<ApiToken>;
  api?: (params: ApiTokenSaveParams) => Promise<any>;
  getTableList?: () => void;
}

const drawerVisible = ref(false);
const drawerProps = ref<DrawerProps>({
  isView: false,
  title: "",
  row: {}
});

const acceptParams = (params: DrawerProps) => {
  drawerProps.value = params;
  drawerVisible.value = true;
};

// 禁用今天及之前的日期
const disabledDate = (time: Date) => {
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  return time.getTime() < now.getTime();
};

// 禁用今天已过去的时间
const disabledTime = (date: Date) => {
  const now = new Date();
  const selectedDate = new Date(date);

  // 如果选择的是今天，禁用已过去的时间
  if (
    selectedDate.getFullYear() === now.getFullYear() &&
    selectedDate.getMonth() === now.getMonth() &&
    selectedDate.getDate() === now.getDate()
  ) {
    return {
      disabledHours: () => {
        const hours: number[] = [];
        for (let i = 0; i < now.getHours(); i++) {
          hours.push(i);
        }
        return hours;
      },
      disabledMinutes: (selectedHour: number) => {
        if (selectedHour === now.getHours()) {
          const minutes: number[] = [];
          for (let i = 0; i <= now.getMinutes(); i++) {
            minutes.push(i);
          }
          return minutes;
        }
        return [];
      },
      disabledSeconds: (selectedHour: number, selectedMinute: number) => {
        if (selectedHour === now.getHours() && selectedMinute === now.getMinutes()) {
          const seconds: number[] = [];
          for (let i = 0; i <= now.getSeconds(); i++) {
            seconds.push(i);
          }
          return seconds;
        }
        return [];
      }
    };
  }
  return {};
};

const ruleFormRef = ref<FormInstance>();
const handleSubmit = () => {
  // 验证 username
  const username = drawerProps.value.row.username?.trim();
  if (!username) {
    ElMessage.warning("请输入用户名");
    return;
  }

  ruleFormRef.value!.validate(async valid => {
    if (!valid) return;
    try {
      const submitData: ApiTokenSaveParams = {
        api_id: drawerProps.value.row.api_id!,
        username: username,
        expiration: drawerProps.value.row.expiration
      };

      // 验证到期时间是否为未来时间
      if (submitData.expiration) {
        const expirationDate = new Date(submitData.expiration);
        const now = new Date();
        if (expirationDate <= now) {
          ElMessage.warning("到期时间必须选择未来时间");
          return;
        }
      }

      await drawerProps.value.api!(submitData);
      ElMessage.success({ message: `${drawerProps.value.title}Token成功！` });
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
