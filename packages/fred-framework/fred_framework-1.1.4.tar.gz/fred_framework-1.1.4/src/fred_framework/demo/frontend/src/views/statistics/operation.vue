<template>
  <div class="statistics-operation">
    <div class="page-header">
      <div class="header-content">
        <h2>运营统计</h2>
        <p class="page-description">视频识别数据统计分析页面</p>
      </div>

      <!-- 门店选择 -->
      <div class="store-selector">
        <span>门店：</span>
        <el-select v-model="selectedStore" placeholder="请选择门店" style="width: 200px" @change="handleStoreChange">
          <el-option label="财富又一城店" value="财富又一城店" />
        </el-select>
      </div>

      <!-- 时间选择 -->
      <div class="time-selector">
        <span>时间：</span>
        <el-date-picker
          v-model="selectedDateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          :shortcuts="dateShortcuts"
          :disabled-date="disabledDate"
          clearable
          class="time-picker"
          @change="handleDateRangeChange"
        />
        <el-button v-if="selectedDateRange" type="text" size="small" @click="clearDateRange" class="clear-btn"> 清除 </el-button>
      </div>
    </div>

    <div class="content-area" v-loading="loading">
      <!-- 核心指标卡片 -->
      <div class="overview-cards">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-value">{{ totalDetections || 0 }}</div>
            <div class="stat-label">检测总数</div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-value">{{ abnormalCount || 0 }}</div>
            <div class="stat-label">异常检测</div>
          </div>
        </el-card>
        <el-card class="stat-card danger-card">
          <div class="stat-item">
            <div class="stat-value danger">{{ employeeDressAbnormalCount || 0 }}</div>
            <div class="stat-label">员工着装异常</div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-value">{{ materialNeedCount || 0 }}</div>
            <div class="stat-label">需补料次数</div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-value">{{ employeeBehaviorCount || 0 }}</div>
            <div class="stat-label">员工行为检测</div>
          </div>
        </el-card>
      </div>

      <!-- 分类统计卡片 -->
      <div class="category-cards">
        <!-- 员工着装规范 -->
        <el-card class="category-card">
          <template #header>
            <div class="card-header">
              <span>员工着装规范</span>
            </div>
          </template>
          <div class="category-content">
            <div class="category-item highlight-item">
              <span class="item-label">员工着装异常：</span>
              <span class="item-value danger">{{ employeeDressAbnormalCount || 0 }}</span>
              <el-tag type="danger" size="small" style="margin-left: 8px">重点</el-tag>
            </div>
            <div class="category-item">
              <span class="item-label">工服：</span>
              <span class="item-value success">{{ labelCounts["工服"] || 0 }}</span>
            </div>
            <div class="category-item">
              <span class="item-label">非工服：</span>
              <span class="item-value warning">{{ labelCounts["非工服"] || 0 }}</span>
            </div>
            <div class="category-item">
              <span class="item-label">工帽：</span>
              <span class="item-value success">{{ labelCounts["工帽"] || 0 }}</span>
            </div>
            <div class="category-item">
              <span class="item-label">工帽异常：</span>
              <span class="item-value danger">{{ labelCounts["工帽异常"] || 0 }}</span>
            </div>
            <div class="category-item">
              <span class="item-label">口罩：</span>
              <span class="item-value success">{{ labelCounts["口罩"] || 0 }}</span>
            </div>
            <div class="category-item">
              <span class="item-label">口罩异常：</span>
              <span class="item-value danger">{{ labelCounts["口罩异常"] || 0 }}</span>
            </div>
          </div>
        </el-card>

        <!-- 员工行为 -->
        <el-card class="category-card">
          <template #header>
            <div class="card-header">
              <span>员工行为</span>
            </div>
          </template>
          <div class="category-content">
            <div class="category-item">
              <span class="item-label">手持手机：</span>
              <span class="item-value warning">{{ labelCounts["手持手机"] || 0 }}</span>
            </div>
            <div class="category-item">
              <span class="item-label">手持抹布：</span>
              <span class="item-value info">{{ labelCounts["手持抹布"] || 0 }}</span>
            </div>
            <div class="category-item">
              <span class="item-label">员工正侧：</span>
              <span class="item-value info">{{ labelCounts["员工正侧"] || 0 }}</span>
            </div>
            <div class="category-item">
              <span class="item-label">员工背面：</span>
              <span class="item-value info">{{ labelCounts["员工背面"] || 0 }}</span>
            </div>
          </div>
        </el-card>

        <!-- 物料管理 -->
        <el-card class="category-card">
          <template #header>
            <div class="card-header">
              <span>物料管理</span>
            </div>
          </template>
          <div class="category-content">
            <div class="category-item">
              <span class="item-label">需加料：</span>
              <span class="item-value warning">{{ labelCounts["需加料"] || 0 }}</span>
            </div>
            <div class="category-item">
              <span class="item-label">水果补料：</span>
              <span class="item-value warning">{{ labelCounts["水果补料"] || 0 }}</span>
            </div>
            <div class="category-item">
              <span class="item-label">小吃补料：</span>
              <span class="item-value warning">{{ labelCounts["小吃补料"] || 0 }}</span>
            </div>
            <div class="category-item">
              <span class="item-label">小料台杂物：</span>
              <span class="item-value danger">{{ labelCounts["小料台杂物"] || 0 }}</span>
            </div>
          </div>
        </el-card>

        <!-- 其他检测 -->
        <el-card class="category-card">
          <template #header>
            <div class="card-header">
              <span>其他检测</span>
            </div>
          </template>
          <div class="category-content">
            <div class="category-item">
              <span class="item-label">人体：</span>
              <span class="item-value info">{{ labelCounts["人体"] || 0 }}</span>
            </div>
            <div class="category-item">
              <span class="item-label">碗：</span>
              <span class="item-value info">{{ labelCounts["碗"] || 0 }}</span>
            </div>
            <div class="category-item">
              <span class="item-label">火锅油碟：</span>
              <span class="item-value info">{{ labelCounts["火锅油碟"] || 0 }}</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 图表区域 -->
      <div class="charts-container">
        <!-- 标签分布饼图 -->
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>识别标签分布</span>
              <el-button type="primary" size="small" @click="refreshData">刷新数据</el-button>
            </div>
          </template>
          <div class="chart-container">
            <div ref="pieChartRef" class="chart"></div>
          </div>
        </el-card>

        <!-- 分类统计柱状图 -->
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>分类统计对比</span>
            </div>
          </template>
          <div class="chart-container">
            <div ref="barChartRef" class="chart"></div>
          </div>
        </el-card>
      </div>

      <!-- 每日数据对比 -->
      <el-card class="table-card">
        <template #header>
          <div class="card-header">
            <span>每日数据对比</span>
            <el-button type="primary" size="small" @click="refreshData">刷新数据</el-button>
          </div>
        </template>
        <div class="daily-chart-container">
          <div ref="lineChartRef" class="daily-chart"></div>
        </div>
        <el-table :data="dailyData" stripe style="width: 100%" border>
          <el-table-column prop="date" label="日期" width="120" fixed="left" />
          <el-table-column prop="total_detections" label="检测总数" width="120" sortable />
          <el-table-column prop="employee_dress_abnormal" label="员工着装异常" width="140" sortable>
            <template #default="scope">
              <el-tag v-if="scope.row.employee_dress_abnormal > 0" type="danger" size="small">
                {{ scope.row.employee_dress_abnormal }}
              </el-tag>
              <span v-else>{{ scope.row.employee_dress_abnormal }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="abnormal_count" label="异常检测" width="120" sortable>
            <template #default="scope">
              <el-tag v-if="scope.row.abnormal_count > 0" type="warning" size="small">
                {{ scope.row.abnormal_count }}
              </el-tag>
              <span v-else>{{ scope.row.abnormal_count }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="material_need" label="需补料次数" width="120" sortable />
          <el-table-column prop="employee_behavior" label="员工行为检测" width="140" sortable />
          <el-table-column prop="mask_abnormal" label="口罩异常" width="120" sortable />
          <el-table-column prop="cap_abnormal" label="工帽异常" width="120" sortable />
          <el-table-column prop="uniform" label="工服" width="100" sortable />
          <el-table-column prop="non_uniform" label="非工服" width="120" sortable />
          <el-table-column prop="mobile_phone" label="手持手机" width="120" sortable />
        </el-table>
      </el-card>

      <!-- 详细数据表格 -->
      <el-card class="table-card">
        <template #header>
          <div class="card-header">
            <span>详细统计数据</span>
          </div>
        </template>
        <el-table :data="tableData" stripe style="width: 100%" border>
          <el-table-column prop="label" label="识别标签" width="150" />
          <el-table-column prop="count" label="检测数量" width="120" sortable />
          <el-table-column prop="category" label="分类" width="120">
            <template #default="scope">
              <el-tag :type="getCategoryTagType(scope.row.category)">
                {{ scope.row.category }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="percentage" label="占比" width="120">
            <template #default="scope">
              <span>{{ scope.row.percentage }}%</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.isAbnormal" type="danger">异常</el-tag>
              <el-tag v-else-if="scope.row.isWarning" type="warning">需注意</el-tag>
              <el-tag v-else type="success">正常</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from "vue";
import * as echarts from "echarts";
import { ElMessage } from "element-plus";

// 定义数据类型
interface StatisticsData {
  scenes: any[];
  total_detections: number;
  label_counts: Record<string, number>;
  scene_count: number;
}

// Mock数据
const mockLabelCounts: Record<string, number> = {
  工服: 156,
  非工服: 23,
  手持手机: 45,
  小料台杂物: 12,
  人体: 312,
  工帽: 142,
  碗: 289,
  火锅油碟: 267,
  需加料: 34,
  手持抹布: 67,
  水果补料: 28,
  小吃补料: 19,
  口罩: 178,
  员工正侧: 234,
  员工背面: 198,
  口罩异常: 8,
  工帽异常: 5
};

// 页面数据
const loading = ref(false);
const selectedStore = ref("财富又一城店");
const selectedDateRange = ref<[string, string] | null>(null);
const statisticsData = ref<StatisticsData>({
  scenes: [],
  total_detections: Object.values(mockLabelCounts).reduce((sum, count) => sum + count, 0),
  label_counts: mockLabelCounts,
  scene_count: 0
});

// 标签分类配置
const labelCategories: Record<string, string> = {
  工服: "员工着装",
  非工服: "员工着装",
  工帽: "员工着装",
  工帽异常: "员工着装",
  口罩: "员工着装",
  口罩异常: "员工着装",
  手持手机: "员工行为",
  手持抹布: "员工行为",
  员工正侧: "员工行为",
  员工背面: "员工行为",
  需加料: "物料管理",
  水果补料: "物料管理",
  小吃补料: "物料管理",
  小料台杂物: "物料管理",
  人体: "其他检测",
  碗: "其他检测",
  火锅油碟: "其他检测"
};

// 异常标签
const abnormalLabels = ["工帽异常", "口罩异常", "非工服", "手持手机", "小料台杂物"];

// 警告标签
const warningLabels = ["需加料", "水果补料", "小吃补料"];

// 计算属性
const labelCounts = computed(() => statisticsData.value.label_counts || {});

const totalDetections = computed(() => statisticsData.value.total_detections || 0);

const abnormalCount = computed(() => {
  return abnormalLabels.reduce((sum, label) => sum + (labelCounts.value[label] || 0), 0);
});

const materialNeedCount = computed(() => {
  return ["需加料", "水果补料", "小吃补料"].reduce((sum, label) => sum + (labelCounts.value[label] || 0), 0);
});

const employeeBehaviorCount = computed(() => {
  return ["手持手机", "手持抹布", "员工正侧", "员工背面"].reduce((sum, label) => sum + (labelCounts.value[label] || 0), 0);
});

// 员工着装异常统计：员工正侧 + (口罩异常或工帽异常)
// 统计同时检测到"员工正侧"和("口罩异常"或"工帽异常")的记录数
const employeeDressAbnormalCount = computed(() => {
  const employeePositive = labelCounts.value["员工正侧"] || 0;
  const maskAbnormal = labelCounts.value["口罩异常"] || 0;
  const capAbnormal = labelCounts.value["工帽异常"] || 0;

  if (employeePositive === 0) return 0;

  // 计算逻辑：员工正侧记录中同时存在口罩异常或工帽异常的数量
  // 由于mock数据无法知道具体关联关系，基于合理比例估算
  // 假设：口罩异常和工帽异常主要出现在员工正侧记录中
  // 取口罩异常和工帽异常的总数，但不超过员工正侧的数量
  const totalAbnormal = maskAbnormal + capAbnormal;

  // 如果异常总数小于等于员工正侧数，说明所有异常都可能在员工正侧中
  // 否则，取员工正侧数的合理比例（假设60%的员工正侧记录可能同时存在异常）
  if (totalAbnormal <= employeePositive) {
    return totalAbnormal;
  } else {
    // 取员工正侧数量的60%和异常总数中的较小值
    return Math.min(Math.floor(employeePositive * 0.6), totalAbnormal);
  }
});

const tableData = computed(() => {
  const labels = Object.keys(labelCounts.value);
  return labels
    .map(label => {
      const count = labelCounts.value[label];
      const percentage = totalDetections.value > 0 ? ((count / totalDetections.value) * 100).toFixed(2) : "0";
      return {
        label,
        count,
        category: labelCategories[label] || "其他",
        percentage,
        isAbnormal: abnormalLabels.includes(label),
        isWarning: warningLabels.includes(label)
      };
    })
    .sort((a, b) => b.count - a.count);
});

// 时间选择器配置
const dateShortcuts = [
  {
    text: "今天",
    value: () => {
      const today = new Date();
      return [today, today];
    }
  },
  {
    text: "昨天",
    value: () => {
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      return [yesterday, yesterday];
    }
  },
  {
    text: "最近7天",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setDate(start.getDate() - 6);
      return [start, end];
    }
  },
  {
    text: "最近30天",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setDate(start.getDate() - 29);
      return [start, end];
    }
  },
  {
    text: "最近90天",
    value: () => {
      const end = new Date();
      const start = new Date();
      start.setDate(start.getDate() - 89);
      return [start, end];
    }
  }
];

// 图表引用
const pieChartRef = ref();
const barChartRef = ref();
const lineChartRef = ref();
let pieChart: echarts.ECharts | null = null;
let barChart: echarts.ECharts | null = null;
let lineChart: echarts.ECharts | null = null;

// 每日数据接口
interface DailyData {
  date: string;
  total_detections: number;
  employee_dress_abnormal: number;
  abnormal_count: number;
  material_need: number;
  employee_behavior: number;
  mask_abnormal: number;
  cap_abnormal: number;
  uniform: number;
  non_uniform: number;
  mobile_phone: number;
}

// 生成每日mock数据
const generateDailyMockData = (days: number = 7): DailyData[] => {
  const data: DailyData[] = [];
  const today = new Date();

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split("T")[0];

    // 生成随机波动数据，基于基础数据
    const baseTotal = 2037;
    const randomFactor = 0.8 + Math.random() * 0.4; // 0.8-1.2倍波动
    const dayTotal = Math.floor(baseTotal * randomFactor);

    // 根据总数据按比例分配各项数据
    const uniform = Math.floor(156 * randomFactor);
    const nonUniform = Math.floor(23 * randomFactor);
    const mobilePhone = Math.floor(45 * randomFactor);
    const maskAbnormal = Math.floor(8 * randomFactor);
    const capAbnormal = Math.floor(5 * randomFactor);
    const employeePositive = Math.floor(234 * randomFactor);

    // 员工着装异常 = 员工正侧中同时存在口罩异常或工帽异常
    const employeeDressAbnormal =
      Math.min(Math.floor(employeePositive * 0.15), maskAbnormal + capAbnormal) ||
      Math.min(maskAbnormal, capAbnormal) ||
      Math.min(maskAbnormal + capAbnormal, employeePositive);

    const abnormalCount = nonUniform + mobilePhone + maskAbnormal + capAbnormal + Math.floor(12 * randomFactor);
    const materialNeed = Math.floor(34 * randomFactor) + Math.floor(28 * randomFactor) + Math.floor(19 * randomFactor);
    const employeeBehavior = mobilePhone + Math.floor(67 * randomFactor) + employeePositive + Math.floor(198 * randomFactor);

    data.push({
      date: dateStr,
      total_detections: dayTotal,
      employee_dress_abnormal: employeeDressAbnormal,
      abnormal_count: abnormalCount,
      material_need: materialNeed,
      employee_behavior: employeeBehavior,
      mask_abnormal: maskAbnormal,
      cap_abnormal: capAbnormal,
      uniform: uniform,
      non_uniform: nonUniform,
      mobile_phone: mobilePhone
    });
  }

  return data;
};

// 每日数据
const allDailyData = ref<DailyData[]>(generateDailyMockData(30));

// 根据时间范围筛选的每日数据
const dailyData = computed(() => {
  if (!selectedDateRange.value || selectedDateRange.value.length !== 2) {
    // 默认显示最近7天
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 6);
    return allDailyData.value.filter(item => {
      const itemDate = new Date(item.date);
      return itemDate >= start && itemDate <= end;
    });
  }

  const [startDate, endDate] = selectedDateRange.value;
  return allDailyData.value.filter(item => {
    return item.date >= startDate && item.date <= endDate;
  });
});

// 获取统计数据（使用Mock数据）
const fetchStatistics = async () => {
  try {
    loading.value = true;

    // 模拟网络延迟
    await new Promise(resolve => setTimeout(resolve, 500));

    // 使用Mock数据，可以根据筛选条件调整数据
    const total = Object.values(mockLabelCounts).reduce((sum, count) => sum + count, 0);
    statisticsData.value = {
      scenes: [],
      total_detections: total,
      label_counts: { ...mockLabelCounts },
      scene_count: 0
    };

    await nextTick();
    initCharts();

    ElMessage.success("数据加载成功");
  } catch (error) {
    console.error("获取统计数据失败:", error);
    ElMessage.error("获取统计数据失败");
  } finally {
    loading.value = false;
  }
};

// 初始化图表
const initCharts = () => {
  initPieChart();
  initBarChart();
  initLineChart();
};

// 初始化饼图
const initPieChart = () => {
  if (!pieChartRef.value) return;

  if (pieChart) {
    pieChart.dispose();
  }
  pieChart = echarts.init(pieChartRef.value);

  const labelData = Object.entries(labelCounts.value)
    .map(([label, count]) => ({
      name: label,
      value: count
    }))
    .filter(item => item.value > 0)
    .sort((a, b) => b.value - a.value);

  const option = {
    title: {
      text: "识别标签分布",
      left: "center",
      textStyle: {
        fontSize: 16,
        fontWeight: "bold"
      }
    },
    tooltip: {
      trigger: "item",
      formatter: "{a} <br/>{b}: {c} ({d}%)"
    },
    legend: {
      orient: "vertical",
      left: "left",
      top: "middle",
      type: "scroll",
      itemGap: 8
    },
    series: [
      {
        name: "检测数量",
        type: "pie",
        radius: ["40%", "70%"],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: "#fff",
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: "{b}\n{d}%"
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: "bold"
          }
        },
        data: labelData
      }
    ]
  };

  pieChart.setOption(option);
};

// 初始化柱状图
const initBarChart = () => {
  if (!barChartRef.value) return;

  if (barChart) {
    barChart.dispose();
  }
  barChart = echarts.init(barChartRef.value);

  // 按分类统计
  const categoryCounts: Record<string, number> = {};
  Object.entries(labelCounts.value).forEach(([label, count]) => {
    const category = labelCategories[label] || "其他";
    categoryCounts[category] = (categoryCounts[category] || 0) + count;
  });

  const categories = Object.keys(categoryCounts);
  const counts = categories.map(cat => categoryCounts[cat]);

  const option = {
    title: {
      text: "分类统计对比",
      left: "center",
      textStyle: {
        fontSize: 16,
        fontWeight: "bold"
      }
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow"
      }
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      containLabel: true
    },
    xAxis: {
      type: "category",
      data: categories,
      axisLabel: {
        rotate: 0
      }
    },
    yAxis: {
      type: "value"
    },
    series: [
      {
        name: "检测数量",
        type: "bar",
        data: counts,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "#83bff6" },
            { offset: 0.5, color: "#188df0" },
            { offset: 1, color: "#188df0" }
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: "#2378f7" },
              { offset: 0.7, color: "#2378f7" },
              { offset: 1, color: "#83bff6" }
            ])
          }
        },
        label: {
          show: true,
          position: "top",
          formatter: "{c}"
        }
      }
    ]
  };

  barChart.setOption(option);
};

// 初始化折线图（每日数据对比）
const initLineChart = () => {
  if (!lineChartRef.value) return;

  if (lineChart) {
    lineChart.dispose();
  }
  lineChart = echarts.init(lineChartRef.value);

  const dates = dailyData.value.map(item => {
    const date = new Date(item.date);
    return `${date.getMonth() + 1}/${date.getDate()}`;
  });

  const option = {
    title: {
      text: "每日数据趋势对比",
      left: "center",
      textStyle: {
        fontSize: 16,
        fontWeight: "bold"
      }
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross"
      }
    },
    legend: {
      data: ["检测总数", "员工着装异常", "异常检测", "需补料次数"],
      top: "10%"
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      top: "20%",
      containLabel: true
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: [
      {
        type: "value",
        name: "数量",
        position: "left"
      }
    ],
    series: [
      {
        name: "检测总数",
        type: "line",
        smooth: true,
        data: dailyData.value.map(item => item.total_detections),
        itemStyle: {
          color: "#409EFF"
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(64, 158, 255, 0.3)" },
            { offset: 1, color: "rgba(64, 158, 255, 0.1)" }
          ])
        }
      },
      {
        name: "员工着装异常",
        type: "line",
        smooth: true,
        data: dailyData.value.map(item => item.employee_dress_abnormal),
        itemStyle: {
          color: "#F56C6C"
        },
        lineStyle: {
          width: 2,
          type: "dashed"
        }
      },
      {
        name: "异常检测",
        type: "line",
        smooth: true,
        data: dailyData.value.map(item => item.abnormal_count),
        itemStyle: {
          color: "#E6A23C"
        }
      },
      {
        name: "需补料次数",
        type: "line",
        smooth: true,
        data: dailyData.value.map(item => item.material_need),
        itemStyle: {
          color: "#67C23A"
        }
      }
    ]
  };

  lineChart.setOption(option);
};

// 获取分类标签类型
const getCategoryTagType = (category: string): "success" | "warning" | "danger" | "info" => {
  const typeMap: Record<string, "success" | "warning" | "danger" | "info"> = {
    员工着装: "success",
    员工行为: "info",
    物料管理: "warning",
    其他检测: "info"
  };
  return typeMap[category] || "info";
};

// 刷新数据
const refreshData = () => {
  fetchStatistics();
};

// 门店变更处理
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const handleStoreChange = (_store: string) => {
  fetchStatistics();
};

// 禁用日期（禁用未来日期）
const disabledDate = (time: Date) => {
  return time.getTime() > Date.now();
};

// 清除时间范围
const clearDateRange = () => {
  selectedDateRange.value = null;
  fetchStatistics();
};

// 时间范围变更处理
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const handleDateRangeChange = (_dateRange: [string, string] | null) => {
  fetchStatistics();
  // 时间范围变更时更新折线图
  nextTick(() => {
    initLineChart();
  });
};

// 页面初始化
onMounted(() => {
  fetchStatistics();

  // 监听窗口大小变化
  window.addEventListener("resize", () => {
    pieChart?.resize();
    barChart?.resize();
    lineChart?.resize();
  });
});
</script>

<style scoped lang="scss">
.statistics-operation {
  padding: 20px;
  background-color: #f5f5f5;
  min-height: calc(100vh - 120px);

  .page-header {
    margin-bottom: 20px;
    padding: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;

    .header-content {
      h2 {
        margin: 0 0 8px 0;
        color: #303133;
        font-size: 24px;
        font-weight: 600;
      }

      .page-description {
        margin: 0;
        color: #909399;
        font-size: 14px;
      }
    }

    .store-selector,
    .time-selector {
      display: flex;
      align-items: center;
      gap: 10px;

      .el-select,
      .el-date-editor {
        .el-input__wrapper {
          border-radius: 6px;
          transition: all 0.3s ease;

          &:hover {
            border-color: #409eff;
            box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
          }

          &.is-focus {
            border-color: #409eff;
            box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
          }
        }
      }
    }

    .store-selector {
      margin-right: 30px;
    }

    .time-selector {
      position: relative;

      .time-picker {
        width: 320px;

        .el-input__wrapper {
          background-color: #fff;
          border: 1px solid #dcdfe6;

          &:hover {
            border-color: #c0c4cc;
          }
        }
      }

      .clear-btn {
        margin-left: 8px;
        color: #909399;
        font-size: 12px;
        padding: 4px 8px;
        border-radius: 4px;
        transition: all 0.3s ease;

        &:hover {
          color: #409eff;
          background-color: rgba(64, 158, 255, 0.1);
        }
      }
    }
  }

  .content-area {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  // 概览卡片样式
  .overview-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 20px;

    .stat-card {
      .stat-item {
        text-align: center;
        padding: 20px;

        .stat-value {
          font-size: 32px;
          font-weight: bold;
          color: #409eff;
          margin-bottom: 8px;

          &.danger {
            color: #f56c6c;
          }
        }

        .stat-label {
          font-size: 14px;
          color: #909399;
        }
      }

      &.danger-card {
        border: 2px solid #f56c6c;
        background: linear-gradient(135deg, #fff5f5 0%, #ffffff 100%);

        .stat-item {
          .stat-value {
            color: #f56c6c;
          }
        }
      }
    }
  }

  // 分类卡片样式
  .category-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 20px;

    .category-card {
      .card-header {
        font-weight: 600;
        color: #303133;
        font-size: 16px;
      }

      .category-content {
        .category-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 0;
          border-bottom: 1px solid #f0f0f0;

          &:last-child {
            border-bottom: none;
          }

          &.highlight-item {
            background-color: #fef0f0;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 8px;
            border: 1px solid #fbc4c4;
            border-bottom: 1px solid #fbc4c4 !important;

            .item-label {
              font-weight: 600;
              color: #f56c6c;
            }
          }

          .item-label {
            font-size: 14px;
            color: #606266;
          }

          .item-value {
            font-size: 18px;
            font-weight: bold;

            &.success {
              color: #67c23a;
            }

            &.warning {
              color: #e6a23c;
            }

            &.danger {
              color: #f56c6c;
            }

            &.info {
              color: #409eff;
            }
          }
        }
      }
    }
  }

  // 图表容器样式
  .charts-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;

    @media (max-width: 1200px) {
      grid-template-columns: 1fr;
    }

    .chart-card {
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 600;
        color: #303133;
      }

      .chart-container {
        height: 400px;
        padding: 20px;

        .chart {
          width: 100%;
          height: 100%;
        }
      }
    }
  }

  // 表格卡片样式
  .table-card {
    .card-header {
      font-weight: 600;
      color: #303133;
    }

    .daily-chart-container {
      margin-bottom: 20px;
      padding: 20px;
      background-color: #fafafa;
      border-radius: 8px;

      .daily-chart {
        width: 100%;
        height: 400px;
      }
    }
  }
}
</style>
