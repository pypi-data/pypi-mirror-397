<template>
  <el-drawer v-model="drawerVisible" :title="drawerTitle" size="50%">
    <el-skeleton v-if="loading" :rows="8" animated />
    <div v-else-if="notificationData" class="notification-detail-container">
      <!-- 通知基本信息 -->
      <el-card class="basic-info-card">
        <template #header>
          <div class="card-header">
            <span>{{ t("sceneLog.notificationInfo") }}</span>
          </div>
        </template>
        <el-descriptions :column="1" border>
          <el-descriptions-item :label="t('sceneLog.notificationId')">
            {{ notificationData.id }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('sceneLog.notificationMessage')">
            {{ notificationData.message || "-" }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('sceneLog.notificationStatus')">
            <el-tag :type="getStatusTagType(notificationData.status)">
              {{ getStatusText(notificationData.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="t('sceneLog.acceptUser')">
            {{ notificationData.accept_user || "-" }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('sceneLog.plat')">
            {{ notificationData.plat || "-" }}
          </el-descriptions-item>
          <el-descriptions-item :label="t('sceneLog.created')">
            {{ notificationData.created || "-" }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
    <div v-else class="empty-notification">
      <el-empty :description="t('sceneLog.noNotification')" />
    </div>

    <template #footer>
      <div class="drawer-footer">
        <el-button @click="drawerVisible = false">{{ t("sceneLog.close") }}</el-button>
        <el-button v-if="notificationData" type="primary" :loading="resending" @click="handleResend">
          {{ t("sceneLog.resendNotification") }}
        </el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts" name="notificationDrawer">
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { ElMessage, ElMessageBox } from "element-plus";
import { getNotificationBySceneLog, resendNotification, type NotificationInfo } from "@/api/modules/sceneLog";

const { t } = useI18n();

const drawerVisible = ref(false);
const drawerTitle = ref(t("sceneLog.viewNotification"));
const loading = ref(false);
const resending = ref(false);
const notificationData = ref<NotificationInfo | null>(null);
const currentSceneLogId = ref<number | null>(null);

// 获取状态标签类型
const getStatusTagType = (status?: number) => {
  if (status === 1) return "success";
  if (status === 2) return "info";
  return "warning";
};

// 获取状态文本
const getStatusText = (status?: number) => {
  if (status === 0) return t("sceneLog.notificationStatusPending");
  if (status === 1) return t("sceneLog.notificationStatusSent");
  if (status === 2) return t("sceneLog.notificationStatusReplied");
  return t("sceneLog.notificationStatusUnknown");
};

// 打开抽屉
const openDrawer = async (sceneLogId: number) => {
  currentSceneLogId.value = sceneLogId;
  drawerVisible.value = true;
  loading.value = true;
  notificationData.value = null;

  try {
    const res = await getNotificationBySceneLog({ scene_log_id: sceneLogId });
    if (res && res.data && Object.keys(res.data).length > 0) {
      notificationData.value = res.data;
    } else {
      notificationData.value = null;
    }
  } catch (error: any) {
    console.error("获取通知信息失败:", error);
    // 如果是404或没有数据，不显示错误，只显示空状态
    if (error?.response?.status !== 404) {
      ElMessage.error(t("sceneLog.getNotificationFailed"));
    }
    notificationData.value = null;
  } finally {
    loading.value = false;
  }
};

// 重新发送通知
const handleResend = async () => {
  if (!notificationData.value || !notificationData.value.id) {
    ElMessage.warning(t("sceneLog.noNotificationToResend"));
    return;
  }

  try {
    await ElMessageBox.confirm(t("sceneLog.resendConfirm"), t("sceneLog.resendNotification"), {
      confirmButtonText: t("sceneLog.confirm"),
      cancelButtonText: t("sceneLog.cancel"),
      type: "warning"
    });

    resending.value = true;
    await resendNotification({ notification_id: notificationData.value.id });
    ElMessage.success(t("sceneLog.resendSuccess"));

    // 重新加载通知信息
    if (currentSceneLogId.value) {
      const res = await getNotificationBySceneLog({ scene_log_id: currentSceneLogId.value });
      if (res && res.data) {
        notificationData.value = res.data;
      }
    }
  } catch (error: any) {
    if (error !== "cancel") {
      console.error("重新发送通知失败:", error);
      ElMessage.error(t("sceneLog.resendFailed"));
    }
  } finally {
    resending.value = false;
  }
};

// 暴露给父组件的方法
defineExpose({
  openDrawer
});
</script>

<style scoped lang="scss">
.notification-detail-container {
  padding: 20px;
}

.basic-info-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-notification {
  padding: 40px;
  text-align: center;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
