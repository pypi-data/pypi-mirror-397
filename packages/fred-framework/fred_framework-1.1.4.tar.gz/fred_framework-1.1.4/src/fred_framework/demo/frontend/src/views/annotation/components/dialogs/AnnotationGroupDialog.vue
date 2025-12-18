<template>
  <div class="annotation-group-sidebar">
    <div class="sidebar-header">
      <span class="sidebar-title">标注分组管理（快捷键：G 显示/隐藏）</span>
    </div>
    <div class="annotation-group-content">
      <!-- 批量删除按钮 -->
      <div class="batch-actions-bar">
        <el-button
          v-if="annotations.length > 0"
          size="default"
          type="danger"
          :disabled="selectedAnnotations.length === 0"
          @click="handleBatchDelete"
          class="batch-delete-button"
        >
          批量删除 ({{ selectedAnnotations.length }})
        </el-button>
      </div>

      <div v-if="annotations.length === 0" class="no-annotations">
        <el-empty description="暂无标注" :image-size="100" />
      </div>
      <div v-else class="annotation-list-container">
        <!-- 使用标签页显示分组 -->
        <el-tabs v-model="activeGroupTab" class="annotation-tabs">
          <el-tab-pane v-for="group in annotationGroups" :key="group.groupType" :name="group.groupType" :lazy="true">
            <template #label>
              <span class="tab-label">
                <span class="label-color-indicator" :style="{ backgroundColor: group.groupColor }"></span>
                <span class="tab-name">{{ group.groupName }}</span>
                <el-tag size="small" type="info" effect="plain" class="tab-count">{{ group.annotations.length }}</el-tag>
              </span>
            </template>

            <!-- 标签页头部操作栏 -->
            <div class="tab-header-actions">
              <div class="tab-actions-left">
                <el-checkbox
                  :model-value="isGroupAllSelected(group)"
                  :disabled="group.groupType === 'others'"
                  @change="handleSelectGroup(group, $event)"
                  class="group-select-checkbox"
                >
                  全选
                </el-checkbox>
                <el-button
                  size="small"
                  text
                  :disabled="group.groupType === 'others'"
                  @click="handleSelectGroupAnnotations(group)"
                  class="group-select-button"
                >
                  {{ isGroupAllSelected(group) ? "取消全选" : "全选组" }}
                </el-button>
              </div>
              <div class="tab-actions-right">
                <el-button
                  size="small"
                  :type="group.isVisible ? 'primary' : 'success'"
                  text
                  @click="handleToggleGroupVisibility(group)"
                >
                  {{ group.isVisible ? "隐藏组" : "显示组" }}
                </el-button>
              </div>
            </div>

            <!-- 标签页内容 -->
            <div class="tab-content" :class="{ 'group-hidden': !group.isVisible }">
              <div v-if="group.annotations.length === 0" class="empty-group">
                <el-empty description="暂无标注" :image-size="80" />
              </div>
              <div v-else class="annotation-items-list">
                <!-- 按标签名称分组显示 -->
                <div
                  v-for="labelGroup in getLabelGroupsForGroup(group)"
                  :key="`${group.groupType}-${labelGroup.labelName}`"
                  class="label-group"
                  :class="{ 'label-group-hidden': !labelGroup.isVisible }"
                >
                  <!-- 标签分组头部 -->
                  <div class="label-group-header">
                    <div class="label-group-title" @click="toggleLabelGroupCollapse(group.groupType, labelGroup.labelName)">
                      <el-icon class="collapse-icon" :class="{ collapsed: labelGroup.collapsed }">
                        <ArrowDown />
                      </el-icon>
                      <span class="label-color-indicator" :style="{ backgroundColor: labelGroup.labelColor }"></span>
                      <span class="label-group-name">{{ labelGroup.labelName }}</span>
                      <el-tag size="small" type="info" effect="plain">{{ labelGroup.annotations.length }}</el-tag>
                    </div>
                    <div class="label-group-actions" @click.stop>
                      <el-checkbox
                        :model-value="isLabelGroupAllSelected(labelGroup)"
                        :disabled="group.groupType === 'others'"
                        @change="handleSelectLabelGroup(labelGroup, $event)"
                        class="label-group-select-checkbox"
                      >
                        全选
                      </el-checkbox>
                      <el-button
                        size="small"
                        :type="labelGroup.isVisible ? 'primary' : 'success'"
                        text
                        @click="handleToggleLabelGroupVisibility(labelGroup)"
                        class="label-group-visibility-button"
                      >
                        {{ labelGroup.isVisible ? "隐藏类" : "显示类" }}
                      </el-button>
                    </div>
                  </div>

                  <!-- 标签分组内容 -->
                  <div v-if="!labelGroup.collapsed" class="label-group-content">
                    <div
                      v-for="annotation in labelGroup.annotations"
                      :key="annotation.id"
                      class="annotation-item"
                      :class="{
                        active: selectedAnnotation?.id === annotation.id,
                        modified: annotation.isModified,
                        'new-annotation': annotation.isNew,
                        'hidden-annotation': !annotation.isVisible
                      }"
                      @click="handleAnnotationItemClick(annotation, $event)"
                    >
                      <div class="annotation-header">
                        <el-checkbox
                          :model-value="isAnnotationSelected(annotation)"
                          :disabled="!isAnnotationDeletable(annotation)"
                          @change="handleAnnotationSelectChange(annotation, $event)"
                          @click.stop
                        />
                        <span class="annotation-name">
                          <span class="annotation-index">
                            #{{ annotation.sort || labelGroup.annotations.indexOf(annotation) + 1 }}
                          </span>
                        </span>
                        <div class="annotation-status">
                          <el-tag v-if="annotation.isModified" type="warning" size="small" effect="dark">已修改</el-tag>
                          <el-tag v-if="annotation.isVisible === false" type="info" size="small" effect="dark">已隐藏</el-tag>
                          <el-tag v-if="!isAnnotationDeletable(annotation)" type="info" size="small" effect="plain">
                            他人标注
                          </el-tag>
                        </div>
                      </div>

                      <div class="annotation-actions">
                        <el-button
                          size="small"
                          :type="annotation.isVisible !== false ? 'primary' : 'success'"
                          text
                          @click.stop="handleToggleAnnotationVisibility(annotation)"
                          class="annotation-visibility-button"
                        >
                          {{ annotation.isVisible !== false ? "隐藏" : "显示" }}
                        </el-button>
                        <el-button size="small" type="info" text @click.stop="handleChangeLabel(annotation)">
                          切换标签
                        </el-button>
                        <el-button
                          size="small"
                          type="danger"
                          text
                          :disabled="!isAnnotationDeletable(annotation)"
                          @click.stop="deleteAnnotation(annotation)"
                        >
                          删除
                        </el-button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { ArrowDown } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";

interface AnnotationDetail {
  id: number;
  sort?: number;
  label_name: string;
  label_color: string;
  yolo_format: {
    label_id: number;
    center_x: number;
    center_y: number;
    width: number;
    height: number;
  };
  isModified?: boolean;
  isNew?: boolean;
  isVisible?: boolean;
  is_own?: boolean;
  is_auto?: boolean;
}

type GroupType = "my" | "others" | "system";

interface AnnotationGroup {
  groupType: GroupType;
  groupName: string;
  groupColor: string;
  annotations: AnnotationDetail[];
  isVisible: boolean;
}

interface LabelGroup {
  labelName: string;
  labelColor: string;
  labelId: number;
  annotations: AnnotationDetail[];
  isVisible: boolean;
  collapsed: boolean;
}

interface Props {
  annotations: AnnotationDetail[];
  selectedAnnotation: AnnotationDetail | null;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  selectAnnotation: [annotation: AnnotationDetail];
  deleteAnnotation: [annotation: AnnotationDetail];
  batchDeleteAnnotations: [annotations: AnnotationDetail[]];
  toggleAnnotationVisibility: [annotation: AnnotationDetail];
  toggleGroupVisibility: [group: AnnotationGroup];
  toggleLabelGroupVisibility: [labelGroup: LabelGroup];
  changeLabel: [annotation: AnnotationDetail];
}>();

// 当前激活的标签页
const activeGroupTab = ref<GroupType>("my");

// 标签分组折叠状态管理
const labelGroupCollapseStates = ref<Map<string, boolean>>(new Map());

// 多选相关状态
const selectedAnnotations = ref<AnnotationDetail[]>([]);

// 获取标注的分组类型
const getAnnotationGroupType = (annotation: AnnotationDetail): GroupType => {
  // 优先判断 is_own，如果为 true 则分到我的标注
  if (annotation.is_own === true) {
    return "my";
  }
  // 然后判断 is_auto，如果为 true 则分到系统标注
  if (annotation.is_auto === true) {
    return "system";
  }
  // 其他情况分到他人标注
  return "others";
};

// 计算分组数据
const annotationGroups = computed<AnnotationGroup[]>(() => {
  // 按分组类型分组
  const grouped = props.annotations.reduce(
    (groups, annotation) => {
      const groupType = getAnnotationGroupType(annotation);
      if (!groups[groupType]) {
        groups[groupType] = [];
      }
      groups[groupType].push(annotation);
      return groups;
    },
    {} as Record<GroupType, AnnotationDetail[]>
  );

  // 定义分组配置
  const groupConfigs: Record<GroupType, { name: string; color: string }> = {
    my: { name: "我的", color: "#67c23a" },
    others: { name: "他人", color: "#e6a23c" },
    system: { name: "系统", color: "#909399" }
  };

  // 定义分组显示顺序
  const groupOrder: GroupType[] = ["my", "others", "system"];

  // 转换为分组数组，按指定顺序排列，始终显示三个分类
  return groupOrder.map(groupType => {
    const config = groupConfigs[groupType];
    const annotations = grouped[groupType] || []; // 如果没有标注，使用空数组

    return {
      groupType,
      groupName: config.name,
      groupColor: config.color,
      annotations,
      isVisible: annotations.length > 0 ? annotations.some(ann => ann.isVisible !== false) : true // 组可见性基于是否有可见的标注，如果没有标注则默认为可见
    };
  });
});

// 计算每个分类下按标签名称分组的数据
const getLabelGroupsForGroup = (group: AnnotationGroup): LabelGroup[] => {
  // 按标签名称分组
  const labelGrouped = group.annotations.reduce(
    (groups, annotation) => {
      const labelName = annotation.label_name || "未命名标签";
      const labelId = annotation.yolo_format?.label_id || 0;
      const labelColor = annotation.label_color || "#409eff";

      if (!groups[labelName]) {
        groups[labelName] = {
          labelName,
          labelColor,
          labelId,
          annotations: []
        };
      }
      groups[labelName].annotations.push(annotation);
      return groups;
    },
    {} as Record<string, { labelName: string; labelColor: string; labelId: number; annotations: AnnotationDetail[] }>
  );

  // 转换为数组，按标签名称排序
  return Object.values(labelGrouped)
    .map(item => {
      const key = `${group.groupType}-${item.labelName}`;
      return {
        labelName: item.labelName,
        labelColor: item.labelColor,
        labelId: item.labelId,
        annotations: item.annotations,
        isVisible: item.annotations.some(ann => ann.isVisible !== false),
        collapsed: labelGroupCollapseStates.value.has(key) ? labelGroupCollapseStates.value.get(key)! : false
      };
    })
    .sort((a, b) => {
      // 按标签名称排序
      return a.labelName.localeCompare(b.labelName);
    });
};

// 切换标签分组折叠状态
const toggleLabelGroupCollapse = (groupType: GroupType, labelName: string) => {
  const key = `${groupType}-${labelName}`;
  const currentState = labelGroupCollapseStates.value.get(key);
  const newState = currentState === undefined ? true : !currentState;
  labelGroupCollapseStates.value.set(key, newState);
};

// 判断标注是否可删除（只能删除自己的标注或系统标注）
const isAnnotationDeletable = (annotation: AnnotationDetail): boolean => {
  // 系统标注（is_auto为true）可以删除
  if (annotation.is_auto === true) {
    return true;
  }
  // 自己的标注（is_own为true）可以删除
  if (annotation.is_own === true) {
    return true;
  }
  // 他人标注（is_own为false且is_auto为false）不能删除
  return false;
};

// 判断标注是否被选中
const isAnnotationSelected = (annotation: AnnotationDetail) => {
  return selectedAnnotations.value.some(ann => ann.id === annotation.id);
};

// 处理标注选择变化（只能选择可删除的标注）
const handleAnnotationSelectChange = (annotation: AnnotationDetail, checked: boolean) => {
  // 如果标注不可删除，不允许选择
  if (!isAnnotationDeletable(annotation)) {
    ElMessage.warning("无权选择他人标注");
    return;
  }

  if (checked) {
    if (!isAnnotationSelected(annotation)) {
      selectedAnnotations.value.push(annotation);
    }
  } else {
    const index = selectedAnnotations.value.findIndex(ann => ann.id === annotation.id);
    if (index > -1) {
      selectedAnnotations.value.splice(index, 1);
    }
  }
};

// 处理标注项点击（点击非checkbox区域时选中标注）
const handleAnnotationItemClick = (annotation: AnnotationDetail, event: MouseEvent) => {
  // 如果点击的是checkbox、按钮区域或标签，不处理（这些元素有自己的点击事件）
  const target = event.target as HTMLElement;

  // 检查是否点击了需要阻止的元素
  const clickedCheckbox = target.closest(".el-checkbox");
  const clickedActions = target.closest(".annotation-actions");
  const clickedTag = target.closest(".el-tag");
  const clickedButton = target.closest(".el-button");
  const clickedStatus = target.closest(".annotation-status");

  // 如果点击了这些元素，不处理
  if (clickedCheckbox || clickedActions || clickedTag || clickedButton || clickedStatus) {
    return;
  }

  // 点击标注项的其他位置（包括标注名称、索引、空白区域），选中该标注
  emit("selectAnnotation", annotation);
};

// 判断分组是否全选（只统计可删除的标注）
const isGroupAllSelected = (group: AnnotationGroup) => {
  const deletableAnnotations = group.annotations.filter(ann => isAnnotationDeletable(ann));
  if (deletableAnnotations.length === 0) return false;
  return deletableAnnotations.every(ann => isAnnotationSelected(ann));
};

// 处理分组全选/取消全选（只选择可删除的标注）
const handleSelectGroup = (group: AnnotationGroup, checked: boolean) => {
  // 如果是"他人标注"组，不允许全选
  if (group.groupType === "others") {
    ElMessage.warning("无权选择他人标注");
    return;
  }

  if (checked) {
    // 全选该分组中可删除的标注
    group.annotations.forEach(annotation => {
      if (isAnnotationDeletable(annotation) && !isAnnotationSelected(annotation)) {
        selectedAnnotations.value.push(annotation);
      }
    });
  } else {
    // 取消全选该分组
    selectedAnnotations.value = selectedAnnotations.value.filter(
      ann => !group.annotations.some(groupAnn => groupAnn.id === ann.id)
    );
  }
};

// 全选分组的所有可删除标注
const handleSelectGroupAnnotations = (group: AnnotationGroup) => {
  // 如果是"他人标注"组，不允许全选
  if (group.groupType === "others") {
    ElMessage.warning("无权选择他人标注");
    return;
  }

  if (isGroupAllSelected(group)) {
    // 取消全选该分组
    selectedAnnotations.value = selectedAnnotations.value.filter(
      ann => !group.annotations.some(groupAnn => groupAnn.id === ann.id)
    );
  } else {
    // 全选该分组中可删除的标注
    group.annotations.forEach(annotation => {
      if (isAnnotationDeletable(annotation) && !isAnnotationSelected(annotation)) {
        selectedAnnotations.value.push(annotation);
      }
    });
  }
};

// 判断标签分组是否全选（只统计可删除的标注）
const isLabelGroupAllSelected = (labelGroup: LabelGroup) => {
  const deletableAnnotations = labelGroup.annotations.filter(ann => isAnnotationDeletable(ann));
  if (deletableAnnotations.length === 0) return false;
  return deletableAnnotations.every(ann => isAnnotationSelected(ann));
};

// 处理标签分组全选/取消全选（只选择可删除的标注）
const handleSelectLabelGroup = (labelGroup: LabelGroup, checked: boolean) => {
  if (checked) {
    // 全选该标签分组中可删除的标注
    labelGroup.annotations.forEach(annotation => {
      if (isAnnotationDeletable(annotation) && !isAnnotationSelected(annotation)) {
        selectedAnnotations.value.push(annotation);
      }
    });
  } else {
    // 取消全选该标签分组
    selectedAnnotations.value = selectedAnnotations.value.filter(
      ann => !labelGroup.annotations.some(labelAnn => labelAnn.id === ann.id)
    );
  }
};

// 批量删除（只删除可删除的标注）
const handleBatchDelete = async () => {
  // 过滤出可删除的标注
  const deletableAnnotations = selectedAnnotations.value.filter(ann => isAnnotationDeletable(ann));

  if (deletableAnnotations.length === 0) {
    ElMessage.warning("请先选择要删除的标注（只能删除自己的标注或系统标注）");
    return;
  }

  // 如果有选中的标注但不可删除，提示用户
  const undeletableCount = selectedAnnotations.value.length - deletableAnnotations.length;
  if (undeletableCount > 0) {
    ElMessage.warning(`已过滤 ${undeletableCount} 个无权删除的标注`);
  }

  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${deletableAnnotations.length} 个标注吗？`, "批量删除标注", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });

    // 触发批量删除事件，只传递可删除的标注
    emit("batchDeleteAnnotations", [...deletableAnnotations]);
    // 清空选中状态
    selectedAnnotations.value = [];
  } catch {
    // 用户取消操作
  }
};

const deleteAnnotation = (annotation: AnnotationDetail) => {
  // 检查是否有删除权限
  if (!isAnnotationDeletable(annotation)) {
    ElMessage.warning("无权删除他人标注");
    return;
  }
  // 直接删除，不需要确认弹框
  emit("deleteAnnotation", annotation);
};

const handleToggleGroupVisibility = (group: AnnotationGroup) => {
  emit("toggleGroupVisibility", group);
};

// 处理标签类（标签分组）可见性切换
const handleToggleLabelGroupVisibility = (labelGroup: LabelGroup) => {
  emit("toggleLabelGroupVisibility", labelGroup);
};

// 处理单个标注可见性切换
const handleToggleAnnotationVisibility = (annotation: AnnotationDetail) => {
  emit("toggleAnnotationVisibility", annotation);
};

const handleChangeLabel = (annotation: AnnotationDetail) => {
  // 先选中该标注，然后触发切换标签事件
  emit("selectAnnotation", annotation);
  emit("changeLabel", annotation);
};

// 监听标注列表变化，清除已删除标注的选择状态
watch(
  () => props.annotations,
  newAnnotations => {
    // 移除已不存在的标注的选择状态
    selectedAnnotations.value = selectedAnnotations.value.filter(selectedAnn =>
      newAnnotations.some(ann => ann.id === selectedAnn.id)
    );
  },
  { deep: true }
);
</script>

<style lang="scss" scoped>
.annotation-group-sidebar {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 400px;
  max-width: 100%;
  z-index: 20;
  background: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;

  .sidebar-header {
    padding: 15px 20px;
    border-bottom: 1px solid var(--el-border-color-lighter);
    flex-shrink: 0;
    background: #fff;
    position: sticky;
    top: 0;
    z-index: 1;

    .sidebar-title {
      font-size: 16px;
      font-weight: 500;
      color: var(--el-text-color-primary);
    }
  }

  .annotation-group-content {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    overflow-x: hidden;
    min-height: 0;

    .batch-actions-bar {
      margin-bottom: 16px;
      display: flex;
      justify-content: flex-start;
      align-items: center;

      .batch-delete-button {
        &:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }
      }
    }

    .no-annotations {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 200px;
    }

    .annotation-list-container {
      display: flex;
      flex-direction: column;
      overflow: hidden;

      .annotation-tabs {
        flex: 1;
        display: flex;
        flex-direction: column;
        min-height: 0;
        overflow: hidden;

        :deep(.el-tabs__header) {
          margin: 0 0 12px 0;
          flex-shrink: 0;
        }

        :deep(.el-tabs__content) {
          flex: 1;
          min-height: 0;
          overflow-y: auto;
          overflow-x: hidden;
        }

        :deep(.el-tab-pane) {
          height: 100%;
          display: flex;
          flex-direction: column;
          min-height: 0;
          overflow: visible;
        }

        .tab-label {
          display: flex;
          align-items: center;
          gap: 6px;

          .label-color-indicator {
            width: 12px;
            height: 12px;
            border-radius: 2px;
            flex-shrink: 0;
          }

          .tab-name {
            font-weight: 500;
          }

          .tab-count {
            margin-left: 2px;
          }
        }

        .tab-header-actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 8px 0;
          margin-bottom: 8px;
          border-bottom: 1px solid #e4e7ed;
          flex-shrink: 0;

          .tab-actions-left {
            display: flex;
            align-items: center;
            gap: 8px;

            .group-select-checkbox {
              flex-shrink: 0;
            }

            .group-select-button {
              font-size: 12px;
              padding: 4px 8px;
              color: #409eff;
              transition: all 0.2s ease;

              &:hover {
                color: #66b1ff;
                background-color: #f0f9ff;
              }
            }
          }

          .tab-actions-right {
            display: flex;
            gap: 8px;
            align-items: center;

            .el-button {
              font-size: 12px;
              padding: 4px 8px;
            }
          }
        }

        .tab-content {
          flex: 1;
          overflow-y: auto;
          overflow-x: hidden;
          min-height: 0;
          padding: 8px 0;

          &.group-hidden {
            opacity: 0.6;
          }

          .empty-group {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 200px;
          }

          .annotation-items-list {
            display: flex;
            flex-direction: column;
            gap: 8px;

            .label-group {
              border: 1px solid #e4e7ed;
              border-radius: 6px;
              background: #fafafa;
              overflow: hidden;
              transition: all 0.2s ease;

              &.label-group-hidden {
                opacity: 0.6;
                background: #f5f5f5;
                border-color: #d3d4d6;
              }

              .label-group-header {
                padding: 8px 12px;
                background: #f5f7fa;
                border-bottom: 1px solid #e4e7ed;
                transition: background-color 0.2s ease;
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 12px;

                .label-group-title {
                  display: flex;
                  align-items: center;
                  gap: 8px;
                  flex: 1;
                  min-width: 0;
                  cursor: pointer;

                  &:hover {
                    opacity: 0.8;
                  }

                  .collapse-icon {
                    transition: transform 0.2s ease;
                    font-size: 12px;
                    color: #606266;

                    &.collapsed {
                      transform: rotate(-90deg);
                    }
                  }

                  .label-color-indicator {
                    width: 12px;
                    height: 12px;
                    border-radius: 2px;
                    flex-shrink: 0;
                  }

                  .label-group-name {
                    font-weight: 500;
                    color: #303133;
                    flex: 1;
                    min-width: 0;
                  }
                }

                .label-group-actions {
                  display: flex;
                  align-items: center;
                  gap: 8px;
                  flex-shrink: 0;

                  .label-group-select-checkbox {
                    flex-shrink: 0;
                  }

                  .label-group-visibility-button {
                    font-size: 12px;
                    padding: 4px 8px;
                  }
                }
              }

              .label-group-content {
                padding: 4px;
                display: flex;
                flex-direction: column;
                gap: 4px;

                .annotation-item {
                  background: white;
                  border: 1px solid #e4e7ed;
                  border-radius: 6px;
                  padding: 8px 10px;
                  margin-bottom: 4px;
                  cursor: pointer;
                  transition: all 0.2s ease;
                  display: flex;
                  align-items: center;
                  justify-content: space-between;

                  &:hover {
                    border-color: #409eff;
                    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
                  }

                  &.active {
                    border-color: #409eff;
                    background: #f0f9ff;
                    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
                  }

                  &.modified {
                    border-color: #e6a23c;
                    background: #fdf6ec;
                  }

                  &.new-annotation {
                    border-color: #67c23a;
                    background: #f0f9ff;
                  }

                  &.hidden-annotation {
                    opacity: 0.6;
                    background: #f5f5f5;
                    border-color: #d3d4d6;
                  }

                  .annotation-header {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    flex: 1;
                    min-width: 0;
                    cursor: pointer;

                    .el-checkbox {
                      flex-shrink: 0;
                    }

                    .annotation-name {
                      display: flex;
                      align-items: center;
                      gap: 6px;
                      font-weight: 500;
                      color: #303133;
                      flex: 1;
                      min-width: 0;
                      cursor: pointer;
                      user-select: none;

                      .annotation-index {
                        font-size: 12px;
                        color: #909399;
                        font-weight: 400;
                        min-width: 20px;
                      }
                    }

                    .annotation-status {
                      display: flex;
                      gap: 4px;
                      align-items: center;
                    }
                  }

                  .annotation-actions {
                    display: flex;
                    gap: 8px;
                    align-items: center;

                    .el-button {
                      font-size: 12px;
                      padding: 4px 8px;
                    }

                    .annotation-visibility-button {
                      font-size: 12px;
                      padding: 4px 8px;
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
</style>
