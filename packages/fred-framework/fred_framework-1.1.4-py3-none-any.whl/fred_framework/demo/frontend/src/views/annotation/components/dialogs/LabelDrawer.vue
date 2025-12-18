<template>
  <el-drawer v-model="drawerVisible" :title="drawerTitle" size="500px" :close-on-click-modal="false">
    <div class="drawer-content">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入标签名称" />
        </el-form-item>
        <el-form-item label="标签颜色" prop="color">
          <div class="color-selection">
            <!-- 当前颜色显示 -->
            <div class="current-color-display">
              <div class="color-preview" :style="{ backgroundColor: form.color }"></div>
              <span>{{ formatColorToHex(form.color) }}</span>
            </div>

            <!-- 预定义颜色选项 -->
            <div class="preset-colors">
              <div
                v-for="presetColor in presetColors"
                :key="presetColor"
                class="preset-color-item"
                :class="{ active: formatColorToHex(form.color) === presetColor }"
                :style="{ backgroundColor: presetColor }"
                @click="handlePresetColorClick(presetColor)"
              ></div>
            </div>
            <!-- 自定义颜色选择器 -->
            <el-color-picker
              v-model="form.color"
              show-alpha
              :predefine="presetColors"
              @change="handleColorChange"
              @active-change="handleColorChange"
            />
          </div>
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <div class="drawer-footer">
        <el-button @click="drawerVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, watch } from "vue";
import { ElMessage, FormInstance, FormRules } from "element-plus";
import { createLabelApi, updateLabelApi } from "@/api/modules/label";
import { rgbToHex } from "@/utils/color";

// 定义暴露给父组件的属性和方法
const drawerVisible = ref(false);
const submitLoading = ref(false);
const drawerTitle = ref("");
const isView = ref(false);
const formRef = ref<FormInstance>();

// 定义获取表格列表的回调函数
let getTableList: (() => void) | null = null;

// 颜色格式化函数：确保颜色值以十六进制格式显示
const formatColorToHex = (color: string): string => {
  // 如果颜色为空或无效，返回默认颜色
  if (!color || typeof color !== "string") {
    return "#409EFF";
  }

  // 去除首尾空格
  const trimmedColor = color.trim();

  // 如果已经是十六进制格式，验证并返回
  if (trimmedColor.startsWith("#")) {
    // 验证十六进制格式是否正确
    const hexMatch = trimmedColor.match(/^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/);
    if (hexMatch) {
      return trimmedColor.toUpperCase();
    }
  }

  // 如果是 rgb 格式，转换为十六进制
  if (trimmedColor.startsWith("rgb")) {
    const match = trimmedColor.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (match) {
      const r = parseInt(match[1]);
      const g = parseInt(match[2]);
      const b = parseInt(match[3]);
      // 验证RGB值是否在有效范围内
      if (r >= 0 && r <= 255 && g >= 0 && g <= 255 && b >= 0 && b <= 255) {
        return rgbToHex(r, g, b);
      }
    }
  }

  // 如果是 rgba 格式，转换为十六进制（忽略透明度）
  if (trimmedColor.startsWith("rgba")) {
    const match = trimmedColor.match(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)/);
    if (match) {
      const r = parseInt(match[1]);
      const g = parseInt(match[2]);
      const b = parseInt(match[3]);
      // 验证RGB值是否在有效范围内
      if (r >= 0 && r <= 255 && g >= 0 && g <= 255 && b >= 0 && b <= 255) {
        return rgbToHex(r, g, b);
      }
    }
  }

  // 如果是其他格式或无效格式，返回默认颜色
  return "#409EFF";
};

// 预定义颜色选项
const presetColors = [
  "#409EFF",
  "#67C23A",
  "#E6A23C",
  "#F56C6C",
  "#909399",
  "#000000",
  "#FFFFFF",
  "#FF0000",
  "#00FF00",
  "#0000FF"
];

// 处理颜色选择器变化
const handleColorChange = (color: string) => {
  if (color) {
    // 立即转换为十六进制格式
    const hexColor = formatColorToHex(color);
    form.color = hexColor;
  } else {
    // 如果颜色为空，设置为默认颜色
    form.color = "#409EFF";
  }
};

// 处理预定义颜色点击
const handlePresetColorClick = (color: string) => {
  const hexColor = formatColorToHex(color);
  form.color = hexColor;
};

// 表单数据
const form = reactive({
  id: 0,
  name: "",
  color: "#409EFF"
});

// 监听颜色变化
watch(
  () => form.color,
  () => {
    // 颜色变化监听
  },
  { immediate: true }
);

// 表单验证规则
const rules = reactive<FormRules>({
  name: [
    { required: true, message: "请输入标签名称", trigger: "blur" },
    { min: 1, max: 50, message: "标签名称长度不能超过50个字符", trigger: "blur" }
  ],
  color: [{ required: true, message: "请选择标签颜色", trigger: "change" }]
});

// 接收父组件传来的参数
const acceptParams = async (params: any) => {
  drawerTitle.value = params.title;
  isView.value = params.isView;
  form.id = params.row?.id || 0;
  form.name = params.row?.name || "";
  // 确保颜色值格式正确，如果为空或无效则使用默认颜色
  form.color = formatColorToHex(params.row?.color || "#409EFF");
  getTableList = params.getTableList || null; // 保存获取表格列表的回调函数

  drawerVisible.value = true;
  nextTick(() => {
    formRef.value?.clearValidate();
  });
};

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async valid => {
    if (!valid) return;

    submitLoading.value = true;
    try {
      // 确保提交的颜色值是十六进制格式
      const hexColor = formatColorToHex(form.color);

      if (form.id === 0) {
        // 创建标签
        await createLabelApi({
          name: form.name,
          color: hexColor
        });
        ElMessage.success("创建成功");
      } else {
        // 更新标签
        await updateLabelApi({
          id: form.id,
          name: form.name,
          color: hexColor
        });
        ElMessage.success("更新成功");
      }

      drawerVisible.value = false;
      // 调用回调函数刷新表格数据
      if (getTableList) {
        getTableList();
      }
    } catch (error: any) {
      ElMessage.error(error.message || (form.id === 0 ? "创建失败" : "更新失败"));
    } finally {
      submitLoading.value = false;
    }
  });
};

// 暴露给父组件的方法
defineExpose({
  acceptParams
});
</script>

<style scoped lang="scss">
.drawer-content {
  padding: 20px;
}
.drawer-footer {
  padding: 20px;
  text-align: right;
}
.color-selection {
  display: flex;
  flex-direction: column;
  gap: 15px;
  .current-color-display {
    display: flex;
    gap: 10px;
    align-items: center;
    .color-preview {
      width: 30px;
      height: 30px;
      border: 1px solid #dddddd;
      border-radius: 4px;
    }
  }
  .preset-colors {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    .preset-color-item {
      width: 30px;
      height: 30px;
      cursor: pointer;
      border: 2px solid transparent;
      border-radius: 4px;
      transition: all 0.2s ease;
      &:hover {
        transform: scale(1.1);
      }
      &.active {
        border-color: #333333;
        transform: scale(1.1);
      }
    }
  }
}
</style>
