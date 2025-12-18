<template>
  <el-drawer v-model="drawerVisible" :title="drawerTitle" size="50%" :destroy-on-close="true" @close="handleClose">
    <div class="material-team-drawer">
      <!-- 添加团队区域 -->
      <el-card class="add-team-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">{{ t("materialLibrary.addTeam") }}</span>
          </div>
        </template>
        <el-form :inline="true" class="add-team-form">
          <el-form-item :label="t('materialLibrary.selectCompany')">
            <el-select
              v-model="selectedCompanyId"
              :placeholder="t('materialLibrary.selectCompany')"
              clearable
              filterable
              style="width: 200px"
              :loading="companiesLoading"
              @change="handleCompanyChange"
              @focus="loadCompanies"
            >
              <el-option v-for="company in companyOptions" :key="company.id" :label="company.name" :value="company.id" />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('materialLibrary.selectDepartment')">
            <el-select
              v-model="selectedDepartmentId"
              :placeholder="t('materialLibrary.selectDepartment')"
              clearable
              filterable
              style="width: 200px"
              :loading="departmentsLoading"
              :disabled="!selectedCompanyId"
              @change="handleDepartmentChange"
            >
              <el-option
                v-for="department in departmentOptions"
                :key="department.id"
                :label="department.name"
                :value="department.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('materialLibrary.selectTeam')">
            <el-select
              v-model="selectedTeamIds"
              :placeholder="t('materialLibrary.teamPlaceholder')"
              clearable
              filterable
              multiple
              style="width: 300px"
              :loading="teamsLoading"
              :disabled="!selectedDepartmentId"
              @change="handleTeamSelectionChange"
            >
              <el-option v-for="team in availableTeamOptions" :key="team.id" :label="team.name" :value="team.id" />
            </el-select>
          </el-form-item>
        </el-form>

        <!-- 待绑定团队列表 -->
        <div v-if="pendingTeams.length > 0" class="pending-teams-section">
          <div class="pending-teams-header">
            <el-icon><Clock /></el-icon>
            <span class="pending-count">待绑定团队（{{ pendingTeams.length }}）</span>
          </div>
          <div class="pending-teams-wrapper">
            <el-table :data="pendingTeams" border size="small" class="pending-teams-table">
              <el-table-column prop="company_name" :label="t('materialLibrary.company')" width="150" />
              <el-table-column prop="department_name" :label="t('materialLibrary.department')" width="150" />
              <el-table-column prop="team_name" :label="t('materialLibrary.selectTeam')" />
              <el-table-column :label="t('materialLibrary.operation')" width="100" fixed="right">
                <template #default="scope">
                  <el-button type="danger" link :icon="Delete" @click="removeFromPendingList(scope.$index)">{{
                    t("materialLibrary.remove")
                  }}</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div class="add-team-button-wrapper">
              <el-button type="primary" size="large" :icon="Plus" @click="bindAllPendingTeams" class="add-team-button">
                {{ t("materialLibrary.addTeam") }}
              </el-button>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 已绑定团队列表 -->
      <el-card class="bound-teams-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span class="card-title">{{ t("materialLibrary.boundTeams") }}</span>
            <span class="team-count">（{{ teamList.length }}）</span>
          </div>
        </template>
        <div class="team-list-wrapper">
          <el-table :data="teamList" border class="bound-teams-table">
            <el-table-column prop="id" :label="t('materialLibrary.id')" width="80" />
            <el-table-column prop="name" :label="t('materialLibrary.selectTeam')" min-width="150" />
            <el-table-column :label="t('materialLibrary.company')" width="150">
              <template #default="scope">
                <el-tag type="info" size="small">{{ scope.row.company_name || "-" }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('materialLibrary.department')" width="150">
              <template #default="scope">
                <el-tag type="warning" size="small">{{ scope.row.department_name || "-" }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('materialLibrary.operation')" width="120" fixed="right">
              <template #default="scope">
                <el-button type="danger" link :icon="Delete" @click="removeTeam(scope.row)">{{
                  t("materialLibrary.unbind")
                }}</el-button>
              </template>
            </el-table-column>
            <template #empty>
              <el-empty :description="t('materialLibrary.noTeams')">
                <template #image>
                  <el-icon :size="60" color="#c0c4cc">
                    <Document />
                  </el-icon>
                </template>
              </el-empty>
            </template>
          </el-table>
        </div>
      </el-card>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useHandleData } from "@/hooks/useHandleData";
import { ElMessage } from "element-plus";
import { Delete, Plus, Document, Clock } from "@element-plus/icons-vue";
import { getMaterialTeamsApi, saveMaterialTeamsApi, deleteMaterialTeamApi } from "@/api/modules/materialLibrary";
import {
  getAllCompanies,
  getDepartmentsByCompany,
  getTeamList,
  type CompanyInfo,
  type DepartmentInfo,
  type TeamInfo
} from "@/api/modules/organization";
import type { MaterialTeamInfo } from "@/api/model/materialLibraryModel";

// 国际化
const { t } = useI18n();

// Props
interface Props {
  visible: boolean;
  materialId: number;
  materialName: string;
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  materialId: 0,
  materialName: ""
});

// Emits
const emit = defineEmits<{
  "update:visible": [value: boolean];
  close: [];
}>();

// 抽屉显示状态
const drawerVisible = computed({
  get: () => props.visible,
  set: value => emit("update:visible", value)
});

// 抽屉标题
const drawerTitle = computed(() => {
  return `${props.materialName} - ${t("materialLibrary.teams")}`;
});

// 已绑定团队列表
const teamList = ref<MaterialTeamInfo[]>([]);

// 三级联动选择
const selectedCompanyId = ref<number | undefined>(undefined);
const selectedDepartmentId = ref<number | undefined>(undefined);
const selectedTeamIds = ref<number[]>([]);
const companyOptions = ref<CompanyInfo[]>([]);
const departmentOptions = ref<DepartmentInfo[]>([]);
const teamOptions = ref<TeamInfo[]>([]);
const companiesLoading = ref(false);
const departmentsLoading = ref(false);
const teamsLoading = ref(false);

// 待绑定团队列表
interface PendingTeam {
  team_id: number;
  team_name: string;
  company_id: number;
  company_name: string;
  department_id: number;
  department_name: string;
}
const pendingTeams = ref<PendingTeam[]>([]);

// 加载公司列表
const loadCompanies = async () => {
  if (companyOptions.value.length > 0) {
    return;
  }

  companiesLoading.value = true;
  try {
    const res = await getAllCompanies();
    if (res && res.data && Array.isArray(res.data)) {
      companyOptions.value = res.data;
    } else if (Array.isArray(res)) {
      companyOptions.value = res;
    } else {
      companyOptions.value = [];
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || "加载公司列表失败");
    companyOptions.value = [];
  } finally {
    companiesLoading.value = false;
  }
};

// 公司选择变化
const handleCompanyChange = async (companyId: number | undefined) => {
  selectedDepartmentId.value = undefined;
  selectedTeamIds.value = [];
  departmentOptions.value = [];
  teamOptions.value = [];

  if (companyId) {
    departmentsLoading.value = true;
    try {
      const res = await getDepartmentsByCompany({ company_id: companyId });
      if (res && res.data && Array.isArray(res.data)) {
        departmentOptions.value = res.data;
      } else if (Array.isArray(res)) {
        departmentOptions.value = res;
      } else {
        departmentOptions.value = [];
      }
    } catch (error: any) {
      ElMessage.error(error.response?.data?.message || "加载部门列表失败");
      departmentOptions.value = [];
    } finally {
      departmentsLoading.value = false;
    }
  }
};

// 部门选择变化
const handleDepartmentChange = async (departmentId: number | undefined) => {
  selectedTeamIds.value = [];
  teamOptions.value = [];

  if (departmentId) {
    teamsLoading.value = true;
    try {
      const res = await getTeamList({ department_id: departmentId, pageNum: 1, pageSize: 1000 });
      if (res && res.data && res.data.records && Array.isArray(res.data.records)) {
        teamOptions.value = res.data.records;
      } else if (res && res.data && Array.isArray(res.data)) {
        teamOptions.value = res.data;
      } else if (Array.isArray(res)) {
        teamOptions.value = res;
      } else {
        teamOptions.value = [];
      }
    } catch (error: any) {
      ElMessage.error(error.response?.data?.message || "加载团队列表失败");
      teamOptions.value = [];
    } finally {
      teamsLoading.value = false;
    }
  }
};

// 检查团队是否已绑定
const isTeamBound = (teamId: number) => {
  return teamList.value.some(team => team.id === teamId);
};

// 检查团队是否已在待绑定列表中
const isTeamSelected = (teamId: number) => {
  return isTeamBound(teamId) || pendingTeams.value.some(team => team.team_id === teamId);
};

// 获取可用的团队选项
const availableTeamOptions = computed(() => {
  return teamOptions.value.filter(team => !isTeamSelected(team.id));
});

// 获取公司名称
const getCompanyName = (companyId: number | undefined) => {
  if (!companyId) return "";
  const company = companyOptions.value.find(c => c.id === companyId);
  return company?.name || "";
};

// 获取部门名称
const getDepartmentName = (departmentId: number | undefined) => {
  if (!departmentId) return "";
  const department = departmentOptions.value.find(d => d.id === departmentId);
  return department?.name || "";
};

// 团队选择变化时自动添加到待绑定列表
const handleTeamSelectionChange = (teamIds: number[]) => {
  if (!teamIds || teamIds.length === 0) {
    return;
  }

  if (!selectedCompanyId.value || !selectedDepartmentId.value) {
    ElMessage.warning("请先选择公司和部门");
    selectedTeamIds.value = [];
    return;
  }

  const companyName = getCompanyName(selectedCompanyId.value);
  const departmentName = getDepartmentName(selectedDepartmentId.value);
  let addedCount = 0;

  for (const teamId of teamIds) {
    if (pendingTeams.value.some(t => t.team_id === teamId)) {
      continue;
    }

    if (isTeamBound(teamId)) {
      continue;
    }

    const team = teamOptions.value.find(t => t.id === teamId);
    if (team) {
      pendingTeams.value.push({
        team_id: teamId,
        team_name: team.name,
        company_id: selectedCompanyId.value,
        company_name: companyName,
        department_id: selectedDepartmentId.value,
        department_name: departmentName
      });
      addedCount++;
    }
  }

  selectedTeamIds.value = [];

  if (addedCount > 0) {
    ElMessage.success(`已添加 ${addedCount} 个团队到待绑定列表`);
  }
};

// 从待绑定列表中移除
const removeFromPendingList = (index: number) => {
  pendingTeams.value.splice(index, 1);
};

// 绑定所有待绑定的团队
const bindAllPendingTeams = async () => {
  if (pendingTeams.value.length === 0) {
    ElMessage.warning("待绑定列表为空");
    return;
  }

  const teamIds = pendingTeams.value.map(t => t.team_id);

  try {
    await saveMaterialTeamsApi({
      material_id: props.materialId,
      team_ids: teamIds
    });
    ElMessage.success(`成功绑定 ${teamIds.length} 个团队`);
    pendingTeams.value = [];
    await loadMaterialTeams();
    if (selectedDepartmentId.value) {
      await handleDepartmentChange(selectedDepartmentId.value);
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || "绑定失败");
  }
};

// 加载已绑定的团队列表
const loadMaterialTeams = async () => {
  if (!props.materialId) return;

  try {
    const res = await getMaterialTeamsApi({ material_id: props.materialId });
    if (res && res.data && Array.isArray(res.data)) {
      teamList.value = res.data;
    } else if (Array.isArray(res)) {
      teamList.value = res;
    } else {
      teamList.value = [];
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || "获取团队列表失败");
    teamList.value = [];
  }
};

// 解绑团队
const removeTeam = async (row: MaterialTeamInfo) => {
  try {
    await useHandleData(
      deleteMaterialTeamApi,
      { material_id: props.materialId, team_id: row.id },
      t("materialLibrary.removeTeamConfirm", { name: row.name }),
      "warning",
      t
    );
    ElMessage.success(t("materialLibrary.removeTeamSuccess"));
    await loadMaterialTeams();
    if (selectedDepartmentId.value) {
      await handleDepartmentChange(selectedDepartmentId.value);
    }
  } catch {
    ElMessage.error(t("materialLibrary.removeTeamFailed"));
  }
};

// 关闭抽屉
const handleClose = () => {
  selectedCompanyId.value = undefined;
  selectedDepartmentId.value = undefined;
  selectedTeamIds.value = [];
  pendingTeams.value = [];
  companyOptions.value = [];
  departmentOptions.value = [];
  teamOptions.value = [];
  emit("close");
};

// 监听 visible 变化，打开时加载数据
watch(
  () => props.visible,
  async newVal => {
    if (newVal) {
      await loadMaterialTeams();
      await loadCompanies();
    } else {
      handleClose();
    }
  },
  { immediate: true }
);
</script>

<style lang="scss" scoped>
.material-team-drawer {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 100%;
  padding-bottom: 20px;

  .add-team-card {
    flex-shrink: 0;
    display: flex;
    flex-direction: column;

    :deep(.el-card__body) {
      display: flex;
      flex-direction: column;
      padding: 20px;
    }
  }

  .bound-teams-card {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0;

    :deep(.el-card__body) {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      padding: 20px;
      min-height: 0;
    }
  }

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }

    .team-count {
      font-size: 14px;
      color: #909399;
      font-weight: normal;
    }
  }

  .add-team-form {
    margin-bottom: 0;

    :deep(.el-form-item) {
      margin-bottom: 16px;
    }
  }

  .pending-teams-section {
    margin-top: 20px;
    padding: 16px;
    background: #f5f7fa;
    border-radius: 6px;
    border: 1px solid #e4e7ed;

    .pending-teams-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
      font-size: 14px;
      font-weight: 500;
      color: #606266;

      .pending-count {
        color: #409eff;
      }
    }

    .pending-teams-wrapper {
      display: flex;
      flex-direction: column;
      gap: 16px;

      .pending-teams-table {
        width: 100%;
      }

      .add-team-button-wrapper {
        display: flex;
        justify-content: flex-end;
        padding-top: 8px;

        .add-team-button {
          font-size: 16px;
          font-weight: 600;
          padding: 14px 28px;
          box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
          transition: all 0.3s ease;

          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(64, 158, 255, 0.5);
          }

          &:active {
            transform: translateY(0);
          }
        }
      }
    }
  }

  .team-list-wrapper {
    position: relative;
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;

    .bound-teams-table {
      flex: 1;
      width: 100%;
    }

    .add-team-button-wrapper {
      position: absolute;
      bottom: 16px;
      right: 16px;
      z-index: 10;

      .add-team-button {
        font-size: 16px;
        font-weight: 600;
        padding: 14px 28px;
        box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 16px rgba(64, 158, 255, 0.5);
        }

        &:active {
          transform: translateY(0);
        }
      }
    }
  }
}
</style>
