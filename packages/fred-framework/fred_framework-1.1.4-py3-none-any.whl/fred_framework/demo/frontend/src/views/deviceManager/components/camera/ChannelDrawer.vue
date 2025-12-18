<template>
  <el-drawer
    v-model="drawerVisible"
    :title="drawerTitle"
    :size="drawerSize"
    :close-on-click-modal="false"
    :destroy-on-close="true"
    class="channel-drawer"
  >
    <div class="channel-drawer-content">
      <!-- 摄像头信息展示 -->
      <el-card class="camera-info-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>摄像头信息</span>
          </div>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="IP地址">{{ componentProps?.cameraInfo?.ip || "-" }}</el-descriptions-item>
          <el-descriptions-item label="账号">{{ componentProps?.cameraInfo?.user || "-" }}</el-descriptions-item>
          <el-descriptions-item label="品牌">{{ componentProps?.cameraInfo?.brand_name || "-" }}</el-descriptions-item>
          <el-descriptions-item label="类型">
            <el-tag :type="componentProps?.cameraInfo?.type === 'nvr' ? 'success' : 'primary'">
              {{ componentProps?.cameraInfo?.type === "nvr" ? "NVR" : "摄像头" }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="所属门店" :span="2">{{
            componentProps?.cameraInfo?.store_name || "-"
          }}</el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 通道管理 -->
      <el-card class="channels-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>通道管理</span>
            <span class="channel-tip">
              {{ componentProps?.cameraInfo?.type === "nvr" ? "NVR支持多个通道" : "摄像头只能有一个通道" }}
            </span>
          </div>
        </template>

        <!-- 空状态提示 -->
        <div v-if="form.channels.length === 0" class="empty-channels">
          <el-empty :image-size="80" description="暂无通道数据">
            <template #description>
              <p>该设备还没有配置通道</p>
              <p class="empty-tip">
                {{ componentProps?.cameraInfo?.type === "nvr" ? "请点击下方按钮添加通道" : "请点击下方按钮添加通道" }}
              </p>
            </template>
          </el-empty>
        </div>

        <!-- 通道方块列表 -->
        <div class="channels-grid">
          <div v-for="(channel, index) in form.channels" :key="index" class="channel-card-item">
            <el-card class="channel-card" shadow="hover">
              <template #header>
                <div class="channel-header">
                  <span class="channel-title">通道 {{ index + 1 }}</span>
                  <el-button
                    v-if="componentProps?.cameraInfo?.type === 'nvr' && form.channels.length > 1"
                    type="danger"
                    link
                    size="small"
                    @click="removeChannel(index)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </template>

              <div class="channel-content">
                <!-- 通道编号 -->
                <div class="channel-field">
                  <label class="field-label">通道编号</label>
                  <el-input v-model="channel.channel_id" placeholder="通道编号" size="small" class="channel-id-input" />
                </div>

                <!-- 通道状态 -->
                <div class="channel-field channel-field-inline">
                  <div class="field-row">
                    <label class="field-label">状态</label>
                    <el-switch
                      v-model="channel.status"
                      :active-value="1"
                      :inactive-value="0"
                      active-text="可用"
                      inactive-text="不可用"
                      inline-prompt
                      size="small"
                    />
                  </div>
                </div>

                <!-- 通道截图 -->
                <div v-if="channel.image" class="channel-field">
                  <label class="field-label">通道截图</label>
                  <div class="channel-image-preview">
                    <img :src="channel.image" alt="通道截图" @error="handleImageError" />
                  </div>
                </div>
              </div>
            </el-card>
          </div>

          <!-- 添加通道按钮 -->
          <div
            class="add-channel-item"
            :class="{ disabled: componentProps?.cameraInfo?.type === 'camera' && form.channels.length >= 1 }"
          >
            <el-card
              class="add-channel-card"
              shadow="hover"
              @click="addChannel"
              :class="{ disabled: componentProps?.cameraInfo?.type === 'camera' && form.channels.length >= 1 }"
            >
              <div class="add-channel-content">
                <el-icon class="add-icon" :size="24">
                  <CirclePlus />
                </el-icon>
                <span class="add-text">添加通道</span>
              </div>
            </el-card>
          </div>
        </div>
      </el-card>
    </div>

    <template #footer>
      <div class="drawer-footer">
        <el-button @click="drawerVisible = false" :disabled="submitLoading">
          <el-icon><Close /></el-icon>
          取消
        </el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit" :disabled="submitLoading">
          <el-icon v-if="!submitLoading"><Check /></el-icon>
          {{ submitLoading ? "保存中..." : "确定" }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from "vue";
import { ElMessage } from "element-plus";
import { CirclePlus, Close, Check, Delete } from "@element-plus/icons-vue";
import type { CameraInfo, CameraChannelInfo } from "@/api/modules/camera";
import { updateCameraChannels } from "@/api/modules/camera";

// 组件属性
interface Props {
  cameraInfo: CameraInfo;
  getTableList: () => Promise<void>;
}

// 响应式数据
const drawerVisible = ref(false);
const submitLoading = ref(false);
const drawerTitle = ref("通道管理");

// 组件属性
let componentProps: Props;

// 表单数据
const form = reactive<{ channels: CameraChannelInfo[] }>({
  channels: []
});

// 计算属性
const drawerSize = computed(() => {
  const windowWidth = window.innerWidth;
  if (windowWidth <= 768) {
    return "100%";
  } else if (windowWidth <= 1024) {
    return "80%";
  } else {
    return "60%";
  }
});

// 添加通道
const addChannel = () => {
  // NVR类型可以添加多个通道，摄像头类型只能添加一个通道
  if (
    componentProps?.cameraInfo?.type === "nvr" ||
    (componentProps?.cameraInfo?.type === "camera" && form.channels.length === 0)
  ) {
    const nextChannelId = form.channels.length + 1;
    form.channels.push({ channel_id: String(nextChannelId), status: 1, image: "" });
  }
};

// 删除通道
const removeChannel = (index: number) => {
  if (componentProps?.cameraInfo?.type === "nvr" && form.channels.length > 1) {
    form.channels.splice(index, 1);
  }
};

// 处理图片加载错误
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  img.style.display = "none";
};

// 统一错误处理
const handleError = (error: any, defaultMessage: string = "操作失败") => {
  const errorMessage = error?.response?.data?.message || error?.message || defaultMessage;
  ElMessage.error(errorMessage);
};

// 重置表单
const resetForm = () => {
  // 如果设备有通道数据，则使用现有通道；否则初始化为空数组
  form.channels =
    componentProps?.cameraInfo?.channels && componentProps.cameraInfo.channels.length > 0
      ? componentProps.cameraInfo.channels.map(ch => ({ ...ch }))
      : [];
};

// 提交表单
const handleSubmit = async () => {
  try {
    // 验证通道数据
    if (componentProps?.cameraInfo?.type === "camera" && form.channels.length !== 1) {
      ElMessage.error("摄像头类型只能有一个通道");
      return;
    }

    if (form.channels.length === 0) {
      ElMessage.error("至少需要一个通道");
      return;
    }

    submitLoading.value = true;

    // 准备提交数据
    const submitData = {
      camera_id: componentProps?.cameraInfo?.id,
      channels: form.channels.map(channel => ({
        id: channel.id || undefined, // 通道ID，存在表示修改，不存在表示新增
        channel_id: String(channel.channel_id).trim(),
        status: Number(channel.status),
        image: channel.image || ""
      }))
    };

    await updateCameraChannels(submitData);

    ElMessage.success("通道更新成功");
    drawerVisible.value = false;

    // 刷新表格数据
    await componentProps?.getTableList();
  } catch (error) {
    handleError(error, "更新通道失败");
  } finally {
    submitLoading.value = false;
  }
};

// 接受参数
const acceptParams = (params: Props) => {
  componentProps = params;
  drawerTitle.value = `通道管理 - ${params.cameraInfo?.ip || "未知IP"}`;

  // 重置表单
  resetForm();

  // 显示抽屉
  drawerVisible.value = true;
};

// 暴露方法
defineExpose({
  acceptParams
});
</script>

<style scoped lang="scss">
.channel-drawer {
  :deep(.el-drawer__body) {
    padding: 16px;
    overflow-y: auto;
  }
}

.channel-drawer-content {
  .camera-info-card,
  .channels-card {
    margin-bottom: 16px;
    border: 1px solid #e4e7ed;
    border-radius: 8px;

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
      color: #303133;
      padding: 12px 16px;

      .channel-tip {
        font-size: 12px;
        color: #909399;
        font-weight: normal;
      }
    }

    :deep(.el-card__body) {
      padding: 16px;
    }
  }

  .channels-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
    margin: 0;

    .channel-card-item {
      .channel-card {
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        :deep(.el-card__body) {
          padding: 8px;
        }

        :deep(.el-card__header) {
          padding: 8px 12px;
        }

        .channel-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-weight: 600;
          color: #303133;
          padding: 8px 0;

          .channel-title {
            font-size: 13px;
          }
        }

        .channel-content {
          .channel-field {
            margin-bottom: 10px;

            &:last-child {
              margin-bottom: 0;
            }

            .field-label {
              display: block;
              font-size: 11px;
              color: #606266;
              margin-bottom: 4px;
              font-weight: 500;
            }

            .channel-id-input {
              width: 100%;
            }

            .channel-image-preview {
              img {
                width: 100%;
                height: 60px;
                object-fit: cover;
                border-radius: 4px;
                border: 1px solid #e4e7ed;
              }
            }

            // 行内布局样式
            &.channel-field-inline {
              .field-row {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 8px;

                .field-label {
                  margin-bottom: 0;
                  flex-shrink: 0;
                  font-size: 11px;
                  color: #606266;
                  font-weight: 500;
                }
              }
            }
          }
        }
      }
    }
  }

  .empty-channels {
    text-align: center;
    padding: 30px 20px;
    margin: 0;

    .empty-tip {
      margin-top: 8px;
      font-size: 14px;
      color: #909399;
    }
  }

  .add-channel-item {
    // 确保添加通道按钮与其他通道卡片尺寸一致
    min-width: 200px;
    max-width: 200px;

    .add-channel-card {
      height: 100%;
      min-height: 130px; // 设置最小高度，确保与其他卡片高度一致
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.3s ease;
      border: 2px dashed #d9d9d9;
      background-color: #fafafa;

      &:hover:not(.disabled) {
        border-color: #409eff;
        background-color: #f0f9ff;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
      }

      &.disabled {
        cursor: not-allowed;
        opacity: 0.5;
        border-color: #e4e7ed;
        background-color: #f5f7fa;
      }

      :deep(.el-card__body) {
        padding: 0;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .add-channel-content {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 8px;
        color: #909399;

        .add-icon {
          color: #409eff;
        }

        .add-text {
          font-size: 12px;
          font-weight: 500;
        }
      }

      &:hover:not(.disabled) .add-channel-content {
        color: #409eff;

        .add-icon {
          color: #409eff;
        }
      }

      &.disabled .add-channel-content {
        color: #c0c4cc;

        .add-icon {
          color: #c0c4cc;
        }
      }
    }
  }
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px;
  border-top: 1px solid #e4e7ed;
  background-color: #fafafa;

  .el-button {
    min-width: 80px;

    .el-icon {
      margin-right: 4px;
    }
  }
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .channels-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 10px;
  }

  .add-channel-item {
    min-width: 180px;
    max-width: 180px;
  }
}

@media (max-width: 768px) {
  .channel-drawer {
    :deep(.el-drawer) {
      width: 100% !important;
    }

    :deep(.el-drawer__body) {
      padding: 12px;
    }
  }

  .channel-drawer-content {
    .camera-info-card,
    .channels-card {
      margin-bottom: 12px;

      .card-header {
        padding: 10px 12px;
      }

      :deep(.el-card__body) {
        padding: 12px;
      }
    }

    .channels-grid {
      grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
      gap: 8px;
    }

    .add-channel-item {
      min-width: 150px;
      max-width: 150px;

      .add-channel-card {
        min-height: 150px;

        .add-channel-content {
          .add-icon {
            font-size: 20px;
          }

          .add-text {
            font-size: 11px;
          }
        }
      }
    }
  }

  .drawer-footer {
    padding: 15px;
    flex-direction: column;

    .el-button {
      width: 100%;
    }
  }
}
</style>
