<template>
  <div class="material-images-container">
    <div class="header">
      <h2>{{ materialName }}</h2>
      <el-button :icon="ArrowLeft" @click="goBack">{{ t("common.back") }}</el-button>
    </div>

    <div class="content">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="8" animated />
      </div>

      <div v-else-if="imageList.length > 0" class="image-grid">
        <template v-for="(item, index) in imageList" :key="item?.id || index">
          <div v-if="item && item.file_path" class="image-card" @click="openPreview(index)">
            <div class="image-wrapper">
              <el-image
                :src="getImageUrl(item?.file_path)"
                :alt="item?.file_name || ''"
                class="grid-image"
                fit="cover"
                :lazy="true"
              >
                <template #error>
                  <div class="image-slot">
                    <el-icon><PictureFilled /></el-icon>
                  </div>
                </template>
              </el-image>
              <div class="image-overlay">
                <div class="overlay-content">
                  <div class="image-info">
                    <h4>{{ item?.file_name || "" }}</h4>
                    <p v-if="item?.width && item?.height">{{ item.width }} × {{ item.height }}</p>
                  </div>
                </div>
              </div>
            </div>
            <div class="card-footer">
              <div class="file-info">
                <span class="file-name">{{ item?.file_name || "" }}</span>
                <span class="date">{{ formatDate(item?.created_at) }}</span>
              </div>
            </div>
          </div>
        </template>
      </div>

      <div v-else class="empty-state">
        <el-empty :description="t('common.noData')">
          <template #image>
            <el-icon :size="60" color="#c0c4cc">
              <Picture />
            </el-icon>
          </template>
        </el-empty>
      </div>

      <!-- 分页 -->
      <div v-if="imageList.length > 0" class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 40, 60, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 图片预览对话框 -->
    <el-dialog
      v-model="previewVisible"
      :title="`${getCurrentImagePosition()} / ${total} - ${currentImage?.file_name || ''}`"
      width="90%"
      top="5vh"
      :close-on-click-modal="false"
      destroy-on-close
      @close="closePreview"
      class="image-preview-dialog"
    >
      <div class="preview-container">
        <div class="preview-image-wrapper" @click="nextImage">
          <img
            v-if="currentImage && currentImage.file_path"
            :src="getImageUrl(currentImage?.file_path)"
            :alt="currentImage?.file_name || ''"
            class="preview-image"
            @error="handleImageError"
            @load="handleImageLoad"
          />
          <div v-else class="preview-placeholder">
            <el-icon :size="60" color="#c0c4cc"><Picture /></el-icon>
            <p>{{ t("materialLibrary.imageLoadFailed") || "图片加载失败" }}</p>
          </div>
        </div>
        <div class="preview-controls">
          <el-button :icon="ArrowLeft" :disabled="!canGoPrev" @click="prevImage">
            {{ t("materialLibrary.prevImage") || "上一张" }} (A)
          </el-button>
          <el-button :icon="ArrowRight" :disabled="!canGoNext" @click="nextImage">
            {{ t("materialLibrary.nextImage") || "下一张" }} (D)
          </el-button>
          <el-button @click="closePreview">{{ t("common.close") || "关闭" }} (ESC)</el-button>
        </div>
        <div class="preview-info">
          <p><strong>文件名:</strong> {{ currentImage?.file_name || "-" }}</p>
          <p v-if="currentImage?.width && currentImage?.height">
            <strong>尺寸:</strong> {{ currentImage.width }} × {{ currentImage.height }}
          </p>
          <p v-if="currentImage?.created_at"><strong>创建时间:</strong> {{ formatDate(currentImage.created_at) }}</p>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { ElMessage } from "element-plus";
import { ArrowLeft, ArrowRight, Picture, PictureFilled } from "@element-plus/icons-vue";
import { getMaterialImagesApi } from "@/api/modules/materialLibrary";
import type { MaterialImageInfo } from "@/api/model/materialLibraryModel";

const route = useRoute();
const router = useRouter();
const { t } = useI18n();

// 素材信息
const materialId = ref<number>(0);
const materialName = ref<string>("");

// 图片列表
const imageList = ref<MaterialImageInfo[]>([]);
const loading = ref(false);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);

// 图片预览相关
const previewVisible = ref(false);
const currentImageIndex = ref(0);
const currentImage = computed(() => {
  if (
    currentImageIndex.value >= 0 &&
    currentImageIndex.value < imageList.value.length &&
    imageList.value[currentImageIndex.value]
  ) {
    const img = imageList.value[currentImageIndex.value];
    // 确保图片有 file_path 属性
    if (img && img.file_path) {
      return img;
    }
  }
  return null;
});

// 计算当前图片的全局位置（跨页）
const getCurrentImagePosition = () => {
  if (currentImageIndex.value < 0 || currentImageIndex.value >= imageList.value.length) {
    return 0;
  }
  return (currentPage.value - 1) * pageSize.value + currentImageIndex.value + 1;
};

// 是否可以上一张
const canGoPrev = computed(() => {
  if (currentImageIndex.value > 0) {
    return true;
  }
  // 当前页第一张，检查是否有上一页
  return currentPage.value > 1;
});

// 是否可以下一张
const canGoNext = computed(() => {
  if (currentImageIndex.value < imageList.value.length - 1) {
    return true;
  }
  // 当前页最后一张，检查是否有下一页
  const totalPages = Math.ceil(total.value / pageSize.value);
  return currentPage.value < totalPages;
});

// 获取图片URL
const getImageUrl = (filePath: string | undefined | null) => {
  // 严格检查，确保 filePath 是有效的字符串
  if (!filePath || typeof filePath !== "string" || filePath.trim() === "") {
    return "";
  }

  try {
    // 如果已经是完整URL，直接返回
    if (filePath.startsWith("http://") || filePath.startsWith("https://")) {
      return filePath;
    }

    // 处理相对路径
    let path = filePath.replace(/\\/g, "/");

    // 移除开头的 ../ 或 ./ 前缀（可能有多层）
    while (path.startsWith("../") || path.startsWith("./")) {
      path = path.replace(/^\.\.?\//, "");
    }

    // 移除开头的斜杠，避免重复
    path = path.replace(/^\/+/, "");

    // 检查路径是否包含 resource/，如果包含则使用 /resource/ 路由
    if (path.includes("resource/")) {
      // 提取 resource/ 之后的部分
      const resourceIndex = path.indexOf("resource/");
      if (resourceIndex >= 0) {
        path = path.substring(resourceIndex + 9); // 9 是 "resource/" 的长度
        // 确保路径以 /resource 开头
        if (!path.startsWith("/")) {
          path = "/resource/" + path;
        } else {
          path = "/resource" + path;
        }
        // 清理路径中的多余斜杠
        path = path.replace(/([^:])\/+/g, "$1/");
        return path;
      }
    }

    // 如果路径包含 upload/，提取 upload/ 之后的部分，使用 /upload/ 路由
    const uploadIndex = path.indexOf("upload/");
    if (uploadIndex >= 0) {
      path = path.substring(uploadIndex + 7); // 7 是 "upload/" 的长度
      // 确保路径以 /upload 开头
      if (!path.startsWith("/")) {
        path = "/upload/" + path;
      } else {
        path = "/upload" + path;
      }
      // 清理路径中的多余斜杠
      path = path.replace(/([^:])\/+/g, "$1/");
      return path;
    }

    // 如果路径不包含 resource/ 或 upload/，默认使用 /upload/ 路由
    if (!path.startsWith("/")) {
      path = "/upload/" + path;
    } else {
      path = "/upload" + path;
    }

    // 清理路径中的多余斜杠
    path = path.replace(/([^:])\/+/g, "$1/");

    // 对于相对路径，直接返回路径（不需要添加API前缀，因为后端有/upload和/resource路由）
    return path;
  } catch {
    return "";
  }
};

// 格式化日期
const formatDate = (dateString: string | undefined) => {
  if (!dateString) return "";
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString("zh-CN", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit"
    });
  } catch {
    return "";
  }
};

// 获取图片列表
const fetchImageList = async () => {
  if (!materialId.value) {
    ElMessage.error(t("materialLibrary.materialIdRequired") || "素材ID不能为空");
    return;
  }

  loading.value = true;
  try {
    const res = await getMaterialImagesApi({
      material_id: materialId.value,
      pageNum: currentPage.value,
      pageSize: pageSize.value
    });

    if (res.code === 200) {
      // 安全地访问响应数据
      const responseData = res.data;
      if (!responseData) {
        ElMessage.error(t("materialLibrary.fetchImageListFailed") || "获取图片列表失败：数据格式错误");
        return;
      }

      // 安全地获取 records 数组
      const records = Array.isArray(responseData.records) ? responseData.records : [];

      // 过滤掉无效的数据，确保每个item都有file_path属性
      imageList.value = records.filter((item: any) => {
        // 严格检查：确保 item 存在，有 id，有 file_path，且 file_path 是字符串
        if (!item || typeof item !== "object") {
          return false;
        }
        if (!item.id || (typeof item.id !== "number" && typeof item.id !== "string")) {
          return false;
        }
        if (!item.file_path || typeof item.file_path !== "string" || item.file_path.trim() === "") {
          return false;
        }
        return true;
      });

      total.value = typeof responseData.total === "number" ? responseData.total : 0;

      // 如果当前索引超出范围，重置为0
      if (currentImageIndex.value >= imageList.value.length) {
        currentImageIndex.value = 0;
      }
    } else {
      ElMessage.error(res.message || t("materialLibrary.fetchImageListFailed") || "获取图片列表失败");
    }
  } catch (error: any) {
    // 错误处理由拦截器统一处理，这里不需要额外的错误提示
    // 只有在非HTTP错误的情况下才显示提示
    if (!error.response) {
      ElMessage.error(error.message || t("materialLibrary.fetchImageListFailed") || "获取图片列表失败");
    }
  } finally {
    loading.value = false;
  }
};

// 分页变化
const handleSizeChange = (size: number) => {
  pageSize.value = size;
  currentPage.value = 1;
  fetchImageList();
};

const handlePageChange = (page: number) => {
  currentPage.value = page;
  fetchImageList();
};

// 打开预览
const openPreview = (index: number) => {
  try {
    if (index >= 0 && index < imageList.value.length) {
      const targetImage = imageList.value[index];
      // 确保目标图片存在且有 file_path
      if (targetImage && targetImage.file_path && typeof targetImage.file_path === "string") {
        currentImageIndex.value = index;
        previewVisible.value = true;
      } else {
        ElMessage.warning(t("materialLibrary.imageLoadFailed") || "图片数据无效，无法预览");
      }
    }
  } catch {
    ElMessage.error(t("materialLibrary.imageLoadFailed") || "打开预览失败");
  }
};

// 关闭预览
const closePreview = () => {
  previewVisible.value = false;
};

// 上一张图片（支持跨页）
const prevImage = async () => {
  if (imageList.value.length === 0) return;

  if (currentImageIndex.value > 0) {
    // 当前页内还有上一张图片
    currentImageIndex.value--;
    // 确保新图片有效
    const targetImage = imageList.value[currentImageIndex.value];
    if (!targetImage || !targetImage.file_path) {
      // 如果当前图片无效，继续向前查找
      while (currentImageIndex.value > 0) {
        currentImageIndex.value--;
        const img = imageList.value[currentImageIndex.value];
        if (img && img.file_path) {
          break;
        }
      }
    }
  } else {
    // 当前页第一张图片，尝试切换到上一页
    if (currentPage.value > 1) {
      currentPage.value--;
      await fetchImageList();
      // 切换到新页面的最后一张图片
      if (imageList.value.length > 0) {
        currentImageIndex.value = imageList.value.length - 1;
        // 确保新图片有效
        const targetImage = imageList.value[currentImageIndex.value];
        if (!targetImage || !targetImage.file_path) {
          // 如果最后一张无效，向前查找
          while (currentImageIndex.value > 0) {
            currentImageIndex.value--;
            const img = imageList.value[currentImageIndex.value];
            if (img && img.file_path) {
              break;
            }
          }
        }
        ElMessage.info(t("materialLibrary.switchedToPage", { page: currentPage.value }) || `已切换到第 ${currentPage.value} 页`);
      }
    } else {
      // 已经是第一页第一张图片
      ElMessage.info(t("materialLibrary.alreadyFirstImage") || "已经是第一张图片");
    }
  }
};

// 下一张图片（支持跨页）
const nextImage = async () => {
  if (imageList.value.length === 0) return;

  if (currentImageIndex.value < imageList.value.length - 1) {
    // 当前页内还有下一张图片
    currentImageIndex.value++;
    // 确保新图片有效
    const targetImage = imageList.value[currentImageIndex.value];
    if (!targetImage || !targetImage.file_path) {
      // 如果当前图片无效，继续向后查找
      while (currentImageIndex.value < imageList.value.length - 1) {
        currentImageIndex.value++;
        const img = imageList.value[currentImageIndex.value];
        if (img && img.file_path) {
          break;
        }
      }
    }
  } else {
    // 当前页最后一张图片，尝试切换到下一页
    const totalPages = Math.ceil(total.value / pageSize.value);
    if (currentPage.value < totalPages) {
      currentPage.value++;
      await fetchImageList();
      // 切换到新页面的第一张图片
      if (imageList.value.length > 0) {
        currentImageIndex.value = 0;
        // 确保新图片有效
        const targetImage = imageList.value[currentImageIndex.value];
        if (!targetImage || !targetImage.file_path) {
          // 如果第一张无效，向后查找
          while (currentImageIndex.value < imageList.value.length - 1) {
            currentImageIndex.value++;
            const img = imageList.value[currentImageIndex.value];
            if (img && img.file_path) {
              break;
            }
          }
        }
        ElMessage.info(t("materialLibrary.switchedToPage", { page: currentPage.value }) || `已切换到第 ${currentPage.value} 页`);
      }
    } else {
      // 已经是最后一页最后一张图片
      ElMessage.info(t("materialLibrary.alreadyLastImage") || "已经是最后一张图片");
    }
  }
};

// 图片加载成功
const handleImageLoad = () => {
  // 图片加载成功
};

// 图片加载错误
const handleImageError = () => {
  // 图片加载失败通常不需要用户提示，静默处理
};

// 键盘事件处理
const handleKeyDown = (event: KeyboardEvent) => {
  // 只在预览对话框打开时响应
  if (!previewVisible.value) return;

  switch (event.key.toLowerCase()) {
    case "a":
      event.preventDefault();
      prevImage();
      break;
    case "d":
      event.preventDefault();
      nextImage();
      break;
    case "escape":
      event.preventDefault();
      closePreview();
      break;
    case "arrowleft":
      event.preventDefault();
      prevImage();
      break;
    case "arrowright":
      event.preventDefault();
      nextImage();
      break;
  }
};

// 返回
const goBack = () => {
  try {
    if (router) {
      router.back();
    } else {
      // 如果 router 不存在，使用 window.history
      window.history.back();
    }
  } catch {
    window.history.back();
  }
};

// 初始化
onMounted(() => {
  try {
    // 安全地访问 route 对象及其属性
    if (!route) {
      ElMessage.error(t("materialLibrary.initFailed") || "页面初始化失败");
      if (router && typeof router.back === "function") {
        router.back();
      } else {
        window.history.back();
      }
      return;
    }

    // 安全地访问 route.query，避免访问 route.path 等可能不存在的属性
    const query = route && route.query ? route.query : {};
    const id = query?.id;
    const name = query?.name;

    if (id) {
      materialId.value = Number(id);
      materialName.value = (name as string) || t("materialLibrary.materialLibrary") || "素材库";
      fetchImageList();
    } else {
      ElMessage.error(t("materialLibrary.materialIdMissing") || "缺少素材ID参数");
      if (router && typeof router.back === "function") {
        router.back();
      } else {
        window.history.back();
      }
    }
  } catch {
    ElMessage.error(t("materialLibrary.initFailed") || "页面初始化失败");
    try {
      if (router && typeof router.back === "function") {
        router.back();
      } else {
        window.history.back();
      }
    } catch {
      window.history.back();
    }
  }

  // 添加键盘事件监听
  document.addEventListener("keydown", handleKeyDown);
});

// 清理
onUnmounted(() => {
  document.removeEventListener("keydown", handleKeyDown);
});
</script>

<style lang="scss" scoped>
.material-images-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 16px 20px;
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

    h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 500;
      color: #303133;
    }
  }

  .content {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

    .loading-container {
      padding: 20px;
    }

    .image-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
      gap: 16px;
      margin-bottom: 20px;

      .image-card {
        background: #fff;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
        }

        .image-wrapper {
          position: relative;
          width: 100%;
          height: 200px;
          overflow: hidden;

          .grid-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
          }

          .image-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(to bottom, transparent 0%, rgba(0, 0, 0, 0.7) 100%);
            opacity: 0;
            transition: opacity 0.3s ease;
            display: flex;
            align-items: flex-end;
            padding: 16px;

            .overlay-content {
              width: 100%;
              color: white;

              .image-info {
                h4 {
                  margin: 0 0 4px 0;
                  font-size: 14px;
                  font-weight: 500;
                  white-space: nowrap;
                  overflow: hidden;
                  text-overflow: ellipsis;
                }

                p {
                  margin: 0;
                  font-size: 12px;
                  opacity: 0.8;
                }
              }
            }
          }

          &:hover .image-overlay {
            opacity: 1;
          }

          &:hover .grid-image {
            transform: scale(1.05);
          }

          .image-slot {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            height: 100%;
            background: #f5f7fa;
            color: #909399;
            font-size: 30px;
          }
        }

        .card-footer {
          padding: 12px 16px;
          background: #fafafa;

          .file-info {
            display: flex;
            flex-direction: column;
            gap: 4px;

            .file-name {
              font-size: 13px;
              color: #303133;
              font-weight: 500;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
            }

            .date {
              font-size: 11px;
              color: #909399;
            }
          }
        }
      }
    }

    .empty-state {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 400px;
    }

    .pagination-container {
      display: flex;
      justify-content: center;
      margin-top: 20px;
    }
  }
}

// 预览对话框样式
:deep(.image-preview-dialog) {
  .el-dialog__body {
    padding: 20px;
  }

  .preview-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 20px;
    min-height: 60vh;

    .preview-image-wrapper {
      flex: 1;
      display: flex;
      justify-content: center;
      align-items: center;
      width: 100%;
      max-height: 70vh;
      overflow: auto;
      cursor: pointer;
      background: #000;
      border-radius: 8px;

      .preview-image {
        max-width: 100%;
        max-height: 70vh;
        object-fit: contain;
      }

      .preview-placeholder {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #909399;
        padding: 40px;

        p {
          margin-top: 16px;
          font-size: 14px;
        }
      }
    }

    .preview-controls {
      display: flex;
      gap: 12px;
      justify-content: center;
    }

    .preview-info {
      width: 100%;
      padding: 16px;
      background: #f5f7fa;
      border-radius: 8px;
      font-size: 14px;
      line-height: 1.8;

      p {
        margin: 4px 0;
        color: #606266;

        strong {
          color: #303133;
          margin-right: 8px;
        }
      }
    }
  }
}
</style>
