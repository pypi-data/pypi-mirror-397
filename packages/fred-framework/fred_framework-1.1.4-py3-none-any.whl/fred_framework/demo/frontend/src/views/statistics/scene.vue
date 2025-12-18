<template>
  <div class="statistics-scene">
    <div class="page-header">
      <div class="header-content">
        <h2>场景统计</h2>
        <p class="page-description">场景数据统计分析页面</p>
      </div>

      <!-- 门店选择 -->
      <div class="store-selector">
        <span>门店：</span>
        <el-select v-model="selectedStore" placeholder="请选择门店" style="width: 200px" @change="handleStoreChange">
          <el-option v-for="store in storeList" :key="store.id" :label="store.name" :value="store.id" />
        </el-select>
      </div>
    </div>

    <div class="content-area" v-loading="loading">
      <!-- 统计概览 -->
      <div class="overview-cards">
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-value">{{ statisticsData.scene_count || 0 }}</div>
            <div class="stat-label">场景总数</div>
          </div>
        </el-card>
        <el-card class="stat-card clickable-card" @click="showEmployeeDishTodayDialog">
          <div class="stat-item">
            <div class="stat-value">{{ statisticsData.today_dish_count || 0 }}</div>
            <div class="stat-label">
              当日传菜次数
              <span class="click-hint" @click.stop="showEmployeeDishTodayDialog">
                <el-icon><View /></el-icon>
                点击查看详情
              </span>
            </div>
          </div>
        </el-card>
        <el-card class="stat-card">
          <div class="stat-item">
            <div class="stat-value">{{ statisticsData.today_timeout_count || 0 }}</div>
            <div class="stat-label">当日清理超时次数</div>
          </div>
        </el-card>
      </div>

      <!-- 图表区域 -->
      <div class="charts-container">
        <!-- 场景每日检测数量线性图 -->
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>各场景每日检测数量趋势（最近15天）</span>
              <el-button type="primary" size="small" @click="refreshData">刷新数据</el-button>
            </div>
          </template>
          <div class="chart-container">
            <div ref="lineChartRef" class="chart"></div>
          </div>
        </el-card>

        <!-- 场景检测数量柱状图 -->
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>各场景检测数量</span>
            </div>
          </template>
          <div class="chart-container">
            <div ref="barChartRef" class="chart"></div>
          </div>
        </el-card>

        <!-- 小料台杂物清理超时统计 -->
        <el-card class="chart-card full-width">
          <template #header>
            <div class="card-header">
              <span>小料台杂物清理超时统计（最近30天）</span>
              <span class="click-tip">提示：点击图表中的数据点可查看详情</span>
            </div>
          </template>
          <div class="chart-container">
            <div ref="statusChartRef" class="chart"></div>
          </div>
        </el-card>

        <!-- 传菜次数统计 -->
        <el-card class="chart-card full-width">
          <template #header>
            <div class="card-header">
              <span>传菜次数统计（最近30天）</span>
              <span class="click-hint employee-detail-hint" @click="showEmployeeDishTrendDialog">
                <el-icon><View /></el-icon>
                点击查看员工详情
              </span>
            </div>
          </template>
          <div class="chart-container">
            <div ref="storeDailyChartRef" class="chart"></div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 员工当日传菜次数弹窗 -->
    <el-dialog
      v-model="employeeDishTodayDialogVisible"
      title="当日员工传菜次数统计"
      width="800px"
      @close="closeEmployeeDishTodayDialog"
    >
      <div class="dialog-chart-container">
        <div ref="employeeDishTodayChartRef" class="dialog-chart"></div>
      </div>
    </el-dialog>

    <!-- 员工传菜趋势弹窗 -->
    <el-dialog
      v-model="employeeDishTrendDialogVisible"
      title="员工传菜次数趋势（最近30天）"
      width="80%"
      class="employee-dish-trend-dialog"
      @close="closeEmployeeDishTrendDialog"
    >
      <template #header>
        <div class="dialog-header">
          <span>员工传菜次数趋势（最近30天）</span>
          <el-button type="primary" size="small" @click="toggleAllEmployeesVisibility">
            {{ showAllEmployees ? "隐藏所有" : "显示所有" }}
          </el-button>
        </div>
      </template>
      <div class="dialog-chart-container">
        <div ref="employeeDishTrendChartRef" class="dialog-chart"></div>
      </div>
    </el-dialog>

    <!-- 员工传菜记录详情弹窗 -->
    <el-dialog
      v-model="employeeDishRecordDialogVisible"
      title="员工传菜记录详情"
      width="80%"
      class="employee-dish-record-dialog"
      @close="closeEmployeeDishRecordDialog"
    >
      <template #header>
        <div class="dialog-header">
          <span>员工传菜记录详情</span>
        </div>
      </template>
      <div v-if="employeeDishRecord" class="record-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="员工工号">
            {{ employeeDishRecord.job_number || "未知" }}
          </el-descriptions-item>
          <el-descriptions-item label="门店">
            {{ employeeDishRecord.store_name || employeeDishRecord.store_id || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="日期" :span="2">
            {{ employeeDishRecord.date || "-" }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 图片列表 -->
        <div v-if="employeeDishRecord.images && employeeDishRecord.images.length > 0" class="images-section">
          <h3>传菜图片列表</h3>
          <el-table :data="employeeDishRecord.images" border style="width: 100%">
            <el-table-column prop="dish_time" label="传菜时间" />
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="primary" size="small" @click="viewImage(row)">查看图片</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else-if="employeeDishRecord.images && employeeDishRecord.images.length === 0" class="no-image">无图片信息</div>
      </div>
      <div v-else class="no-record">
        <el-empty description="未找到相关记录" />
      </div>
    </el-dialog>

    <!-- 超时日志弹窗 -->
    <el-dialog
      v-model="timeoutLogDialogVisible"
      :title="`超时日志列表 - ${timeoutLogDate}`"
      width="80%"
      class="timeout-log-dialog"
      @close="closeTimeoutLogDialog"
    >
      <template #header>
        <div class="dialog-header">
          <span>超时日志列表 - {{ timeoutLogDate }}</span>
        </div>
      </template>
      <div v-loading="timeoutLogLoading" class="timeout-log-container">
        <el-table :data="timeoutLogList" border style="width: 100%">
          <el-table-column prop="id" label="ID" width="100" />
          <el-table-column prop="store_name" label="门店" width="200" />
          <el-table-column prop="scene_name" label="场景" width="200" />
          <el-table-column prop="message" label="日志信息" show-overflow-tooltip />
          <el-table-column prop="the_time" label="触发时间" width="180">
            <template #default="{ row }">
              <span>{{ formatDateTime(row.the_time) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button v-if="row.image_url" type="primary" size="small" link @click="viewTimeoutLogImage(row)">
                查看图片
              </el-button>
              <span v-else style="color: #909399; font-size: 12px">无图片</span>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="timeoutLogPageNum"
            v-model:page-size="timeoutLogPageSize"
            :total="timeoutLogTotal"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleTimeoutLogPageChange(1)"
            @current-change="handleTimeoutLogPageChange"
          />
        </div>
      </div>
    </el-dialog>

    <!-- 超时日志图片预览弹窗 -->
    <el-dialog
      v-model="timeoutLogImageDialogVisible"
      title="图片预览"
      width="80%"
      class="timeout-log-image-dialog"
      @close="closeTimeoutLogImageDialog"
    >
      <template #header>
        <div class="dialog-header">
          <span>图片预览</span>
        </div>
      </template>
      <div v-if="timeoutLogImageUrl" class="timeout-log-image-container">
        <el-image
          :src="timeoutLogImageUrl"
          :preview-src-list="[timeoutLogImageUrl]"
          fit="contain"
          :preview-teleported="true"
          style="max-width: 100%; max-height: 70vh"
        >
          <template #error>
            <div class="image-error">
              <el-icon><Picture /></el-icon>
              <span>图片加载失败</span>
            </div>
          </template>
        </el-image>
      </div>
    </el-dialog>

    <!-- 图片预览弹窗 -->
    <el-dialog
      v-model="imagePreviewDialogVisible"
      title="图片预览"
      width="80%"
      class="image-preview-dialog"
      @close="closeImagePreview"
    >
      <template #header>
        <div class="dialog-header">
          <span>图片预览</span>
          <el-button
            v-if="previewImageData && previewImageData.bbox_parsed && previewImageData.bbox_parsed.length > 0"
            type="primary"
            size="small"
            @click="togglePreviewAnnotationVisibility"
          >
            {{ showPreviewAnnotation ? "隐藏标注" : "显示标注" }}
          </el-button>
        </div>
      </template>
      <div v-if="previewImageData" class="image-preview-container">
        <div class="image-viewer">
          <div class="image-wrapper" ref="previewImageWrapperRef">
            <img
              :src="getImageUrl(previewImageData.image_path)"
              alt="预览图片"
              class="viewer-image"
              ref="previewImageRef"
              @error="handlePreviewImageError"
              @load="handlePreviewImageLoad"
            />
            <!-- 标注框 -->
            <template
              v-if="
                showPreviewAnnotation &&
                previewImageData.bbox_parsed &&
                previewImageData.bbox_parsed.length > 0 &&
                previewImageLoaded
              "
            >
              <div
                v-for="(annotation, annotationIndex) in previewImageData.bbox_parsed"
                :key="annotationIndex"
                class="annotation-box"
                :style="getPreviewAnnotationStyle(annotation)"
              >
                <div class="annotation-label">
                  {{ annotation.label || `标注${annotationIndex + 1}` }}
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { getSceneLogList, type SceneLogInfo } from "@/api/modules/sceneLog";
import {
  getEmployeeDishFirstRecord,
  getEmployeeDishStatisticsToday,
  getEmployeeDishStatisticsTrend,
  getSceneDailyStatistics,
  getSceneStatistics,
  getSceneStatusStatistics,
  getSceneStoreDailyStatistics
} from "@/api/modules/statistics";
import { getStoreList, type StoreInfo } from "@/api/modules/store";
import { Picture, View } from "@element-plus/icons-vue";
import * as echarts from "echarts";
import { nextTick, onMounted, ref } from "vue";

// 定义数据类型
interface SceneData {
  scene_name: string;
  detection_count: number;
  scene_labels: string[];
}

interface StatisticsData {
  scenes: SceneData[];
  total_detections: number;
  scene_count: number;
  label_type_count: number;
  today_dish_count?: number;
  today_timeout_count?: number;
}

// 页面数据
const loading = ref(false);
const selectedStore = ref<number | null>(null);
const storeList = ref<StoreInfo[]>([]);
const statisticsData = ref<StatisticsData>({
  scenes: [],
  total_detections: 0,
  scene_count: 0,
  label_type_count: 0,
  today_dish_count: 0,
  today_timeout_count: 0
});

// 图表引用
const lineChartRef = ref();
const barChartRef = ref();
const statusChartRef = ref();
const storeDailyChartRef = ref();
const employeeDishTodayChartRef = ref();
const employeeDishTrendChartRef = ref();
let lineChart: echarts.ECharts | null = null;
let barChart: echarts.ECharts | null = null;
let statusChart: echarts.ECharts | null = null;
let storeDailyChart: echarts.ECharts | null = null;
let employeeDishTodayChart: echarts.ECharts | null = null;
let employeeDishTrendChart: echarts.ECharts | null = null;

// 弹窗状态
const employeeDishTodayDialogVisible = ref(false);
const employeeDishTrendDialogVisible = ref(false);
const employeeDishRecordDialogVisible = ref(false);
const employeeDishRecord = ref<any>(null);

// 图片预览状态
const imagePreviewDialogVisible = ref(false);
const previewImageData = ref<any>(null);
const showPreviewAnnotation = ref(true);
const previewImageLoaded = ref(false);
const previewImageWrapperRef = ref<HTMLElement | null>(null);
const previewImageRef = ref<HTMLImageElement | null>(null);

// 超时日志弹窗状态
const timeoutLogDialogVisible = ref(false);
const timeoutLogList = ref<SceneLogInfo[]>([]);
const timeoutLogLoading = ref(false);
const timeoutLogDate = ref<string>("");
const timeoutLogTotal = ref(0);
const timeoutLogPageNum = ref(1);
const timeoutLogPageSize = ref(20);

// 超时日志图片预览状态
const timeoutLogImageDialogVisible = ref(false);
const timeoutLogImageUrl = ref<string>("");

// 员工传菜趋势图显示控制
const showAllEmployees = ref(true);
const employeeDishTrendData = ref<{
  dates: string[];
  formattedData: any[];
} | null>(null);

// 获取门店列表
const fetchStoreList = async () => {
  try {
    const response = await getStoreList({ page: 1, limit: 1000 });
    if (response.code === 200 && response.data) {
      storeList.value = response.data.records || [];
      if (storeList.value.length > 0 && !selectedStore.value) {
        selectedStore.value = storeList.value[0].id;
        fetchStatistics();
        fetchStoreDailyStatistics();
      }
    }
  } catch (error) {
    console.error("获取门店列表失败:", error);
  }
};

// 获取统计数据
const fetchStatistics = async () => {
  try {
    loading.value = true;
    // 构建请求参数
    const params: any = {};
    if (selectedStore.value) {
      params.store_id = selectedStore.value;
    }

    const response = await getSceneStatistics(params);
    if (response.code === 200) {
      const data = response.data as any;
      statisticsData.value = {
        scenes: data.scenes || [],
        total_detections: data.total_detections || 0,
        scene_count: data.scene_count || 0,
        label_type_count: data.label_type_count || 0,
        today_dish_count: data.today_dish_count || 0,
        today_timeout_count: data.today_timeout_count || 0
      };
      await nextTick();
      initCharts();
    }

    // 同时获取每日统计数据和场景状态统计数据
    await fetchDailyStatistics();
    await fetchStatusStatistics();
  } catch (error) {
    console.error("获取统计数据失败:", error);
  } finally {
    loading.value = false;
  }
};

// 每日统计数据
const dailyStatisticsData = ref<{
  scenes: Array<{ id: number; name: string }>;
  dates: string[];
  data: Array<{ name: string; type: string; data: number[] }>;
}>({
  scenes: [],
  dates: [],
  data: []
});

// 场景状态统计数据
const statusStatisticsData = ref<{
  dates: string[];
  data: number[];
}>({
  dates: [],
  data: []
});

// 获取每日统计数据
const fetchDailyStatistics = async () => {
  try {
    if (!selectedStore.value) return;

    // 查询最近15天的数据
    const response = await getSceneDailyStatistics({
      store_id: selectedStore.value,
      days: 15
    });

    if (response.code === 200) {
      dailyStatisticsData.value = response.data as any;
      await nextTick();
      initLineChart();
    } else {
      console.error("获取每日统计数据失败:", response);
    }
  } catch (error) {
    console.error("获取每日统计数据失败:", error);
  }
};

// 获取场景状态统计数据
const fetchStatusStatistics = async () => {
  try {
    if (!selectedStore.value) return;

    const response = await getSceneStatusStatistics({
      store_id: selectedStore.value,
      scene_id: 2,
      status: 3,
      days: 30
    });

    if (response.code === 200) {
      statusStatisticsData.value = response.data as any;
      await nextTick();
      initStatusChart();
    } else {
      console.error("获取场景状态统计数据失败:", response);
    }
  } catch (error) {
    console.error("获取场景状态统计数据失败:", error);
  }
};

// 初始化图表
const initCharts = () => {
  initLineChart();
  initBarChart();
  initStatusChart();
};

// 初始化线性图
const initLineChart = () => {
  if (!lineChartRef.value) return;

  lineChart = echarts.init(lineChartRef.value);

  const { dates, data } = dailyStatisticsData.value;

  if (dates.length === 0 || data.length === 0) {
    lineChart.setOption({
      title: {
        text: "各场景每日检测数量趋势（最近15天）",
        left: "center"
      },
      tooltip: {
        trigger: "axis"
      },
      xAxis: {
        type: "category",
        data: []
      },
      yAxis: {
        type: "value"
      },
      series: []
    });
    return;
  }

  // 数据验证：确保每个数据数组的长度与日期数组长度一致
  const validatedData = data.map(item => {
    if (item.data.length !== dates.length) {
      // 如果数据长度不一致，截断或填充到正确长度
      const adjustedData = [...item.data];
      while (adjustedData.length < dates.length) {
        adjustedData.push(0);
      }
      while (adjustedData.length > dates.length) {
        adjustedData.pop();
      }
      return {
        ...item,
        data: adjustedData
      };
    }
    return item;
  });

  // 格式化日期显示（只显示月-日）
  const formattedDates = dates.map(date => {
    const d = new Date(date);
    return `${d.getMonth() + 1}-${d.getDate()}`;
  });

  const option = {
    title: {
      text: "各场景每日检测数量趋势（最近15天）",
      left: "center"
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross"
      },
      formatter: (params: any) => {
        // 自定义tooltip，显示完整日期和数据
        let result = `${params[0].axisValue}<br/>`;
        params.forEach((param: any) => {
          const dateIndex = formattedDates.indexOf(param.axisValue);
          const fullDate = dateIndex >= 0 ? dates[dateIndex] : param.axisValue;
          result += `${param.marker}${param.seriesName}: ${param.value} (${fullDate})<br/>`;
        });
        return result;
      }
    },
    legend: {
      data: validatedData.map(item => item.name),
      top: 30
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "3%",
      containLabel: true
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: formattedDates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: "value"
    },
    series: validatedData.map((item, index) => ({
      name: item.name,
      type: "line",
      // 移除 stack，避免数据堆叠导致的视觉混淆
      smooth: true,
      data: item.data,
      itemStyle: {
        color: ["#409EFF", "#67C23A", "#E6A23C", "#F56C6C", "#909399", "#606266", "#303133"][index % 7]
      }
    }))
  };

  lineChart.setOption(option);
};

// 初始化柱状图
const initBarChart = () => {
  if (!barChartRef.value) return;

  barChart = echarts.init(barChartRef.value);

  const sceneNames = statisticsData.value.scenes.map(scene => scene.scene_name);
  const detectionCounts = statisticsData.value.scenes.map(scene => scene.detection_count);

  const option = {
    title: {
      text: "各场景检测数量",
      left: "center"
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow"
      }
    },
    xAxis: {
      type: "category",
      data: sceneNames,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: "value"
    },
    series: [
      {
        name: "检测数量",
        type: "bar",
        data: detectionCounts,
        itemStyle: {
          color: "#409EFF"
        }
      }
    ]
  };

  barChart.setOption(option);
};

// 初始化场景状态统计图
const initStatusChart = () => {
  if (!statusChartRef.value) return;

  statusChart = echarts.init(statusChartRef.value);

  const { dates, data } = statusStatisticsData.value;

  if (dates.length === 0 || data.length === 0) {
    statusChart.setOption({
      title: {
        text: "小料台杂物清理超时统计（最近30天）",
        left: "center"
      },
      tooltip: {
        trigger: "axis"
      },
      xAxis: {
        type: "category",
        data: []
      },
      yAxis: {
        type: "value"
      },
      series: []
    });
    return;
  }

  // 格式化日期显示（只显示月-日）
  const formattedDates = dates.map(date => {
    const d = new Date(date);
    return `${d.getMonth() + 1}-${d.getDate()}`;
  });

  const option = {
    title: {
      text: "小料台杂物清理超时统计（最近30天）",
      left: "center"
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross"
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
      boundaryGap: false,
      data: formattedDates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: "value"
    },
    series: [
      {
        name: "超时次数",
        type: "line",
        smooth: true,
        data: data,
        itemStyle: {
          color: "#F56C6C"
        },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: "rgba(245, 108, 108, 0.3)"
              },
              {
                offset: 1,
                color: "rgba(245, 108, 108, 0.1)"
              }
            ]
          }
        }
      }
    ]
  };

  statusChart.setOption(option);

  // 添加点击事件监听
  statusChart.off("click");
  statusChart.on("click", (params: any) => {
    handleStatusChartClick(params);
  });
};

// 传菜次数统计数据
const storeDailyStatisticsData = ref<{
  stores: Array<{ id: number; name: string }>;
  dates: string[];
  data: Array<{ name: string; type: string; data: number[] }>;
}>({
  stores: [],
  dates: [],
  data: []
});

// 获取传菜次数统计数据
const fetchStoreDailyStatistics = async () => {
  try {
    if (!selectedStore.value) return;

    const response = await getSceneStoreDailyStatistics({
      store_id: selectedStore.value,
      days: 30
    });
    if (response.code === 200) {
      storeDailyStatisticsData.value = response.data as any;
      await nextTick();
      initStoreDailyChart();
    }
  } catch (error) {
    console.error("获取传菜次数统计数据失败:", error);
  }
};

// 初始化传菜次数统计图表
const initStoreDailyChart = () => {
  if (!storeDailyChartRef.value) return;
  storeDailyChart = echarts.init(storeDailyChartRef.value);
  const { dates, data } = storeDailyStatisticsData.value;

  // 格式化日期显示（只显示月-日）
  const formattedDates = dates.map(date => {
    const d = new Date(date);
    return `${d.getMonth() + 1}-${d.getDate()}`;
  });

  const option = {
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow"
      }
    },
    legend: {
      data: data.map(item => item.name),
      bottom: 0
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "15%",
      containLabel: true
    },
    xAxis: {
      type: "category",
      boundaryGap: true,
      data: formattedDates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: "value"
    },
    series: data.map((item, index) => ({
      name: item.name,
      type: "bar",
      data: item.data,
      itemStyle: {
        color: ["#409EFF", "#67C23A", "#E6A23C", "#F56C6C", "#909399", "#9C27B0", "#00BCD4", "#FF9800"][index % 8]
      }
    }))
  };

  storeDailyChart.setOption(option);
};

// 刷新数据
const refreshData = () => {
  fetchStatistics();
  fetchDailyStatistics();
  fetchStatusStatistics();
  fetchStoreDailyStatistics();
};

// 门店变更处理
const handleStoreChange = () => {
  // 重新获取统计数据
  fetchStatistics();
  fetchStoreDailyStatistics();
};

// 显示员工当日传菜次数弹窗
const showEmployeeDishTodayDialog = async () => {
  if (!selectedStore.value) {
    return;
  }
  employeeDishTodayDialogVisible.value = true;
  await nextTick();
  await fetchEmployeeDishToday();
};

// 关闭员工当日传菜次数弹窗
const closeEmployeeDishTodayDialog = () => {
  employeeDishTodayDialogVisible.value = false;
  if (employeeDishTodayChart) {
    employeeDishTodayChart.dispose();
    employeeDishTodayChart = null;
  }
};

// 获取员工当日传菜次数数据
const fetchEmployeeDishToday = async () => {
  try {
    if (!selectedStore.value || !employeeDishTodayChartRef.value) return;

    const response = await getEmployeeDishStatisticsToday({
      store_id: selectedStore.value
    });

    if (response.code === 200) {
      const { employees, data } = response.data as any;

      // 将"未知"替换为"未知员工"
      const formattedEmployees = employees.map((name: string) => (name === "未知" ? "未知员工" : name));

      if (!employeeDishTodayChart) {
        employeeDishTodayChart = echarts.init(employeeDishTodayChartRef.value);
      }

      const option = {
        title: {
          text: "当日员工传菜次数统计",
          left: "center"
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
          bottom: "15%",
          containLabel: true
        },
        xAxis: {
          type: "category",
          data: formattedEmployees,
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: {
          type: "value"
        },
        series: [
          {
            name: "传菜次数",
            type: "bar",
            data: data,
            itemStyle: {
              color: "#409EFF"
            }
          }
        ]
      };

      employeeDishTodayChart.setOption(option);
    }
  } catch (error) {
    console.error("获取员工当日传菜次数统计失败:", error);
  }
};

// 显示员工传菜趋势弹窗
const showEmployeeDishTrendDialog = async () => {
  if (!selectedStore.value) {
    return;
  }
  employeeDishTrendDialogVisible.value = true;
  await nextTick();
  await fetchEmployeeDishTrend();
};

// 关闭员工传菜趋势弹窗
const closeEmployeeDishTrendDialog = () => {
  employeeDishTrendDialogVisible.value = false;
  showAllEmployees.value = true; // 重置为显示所有
  if (employeeDishTrendChart) {
    employeeDishTrendChart.dispose();
    employeeDishTrendChart = null;
  }
};

// 获取员工传菜趋势数据
const fetchEmployeeDishTrend = async () => {
  try {
    if (!selectedStore.value || !employeeDishTrendChartRef.value) return;

    const response = await getEmployeeDishStatisticsTrend({
      store_id: selectedStore.value,
      days: 30
    });

    if (response.code === 200) {
      const { dates, data } = response.data as any;

      if (!employeeDishTrendChart) {
        employeeDishTrendChart = echarts.init(employeeDishTrendChartRef.value);
      }

      // 格式化数据：确保显示名称正确
      const formattedData = data.map((item: any) => ({
        ...item,
        // 如果后端返回了job_number字段，使用它；否则使用name
        original_job_number: item.job_number || (item.name === "未知员工" ? "-1" : item.name),
        // 显示名称：如果name是"未知员工"或job_number是"-1"，显示为"未知员工"
        name: item.name === "未知员工" || item.job_number === "-1" ? "未知员工" : item.name
      }));

      // 保存原始数据
      employeeDishTrendData.value = {
        dates,
        formattedData
      };

      // 更新图表
      updateEmployeeDishTrendChart();
    }
  } catch (error) {
    console.error("获取员工传菜趋势失败:", error);
  }
};

// 更新员工传菜趋势图表
const updateEmployeeDishTrendChart = () => {
  if (!employeeDishTrendChart || !employeeDishTrendData.value) return;

  const { dates, formattedData } = employeeDishTrendData.value;

  // 格式化日期显示（只显示月-日）
  const formattedDates = dates.map((date: string) => {
    const d = new Date(date);
    return `${d.getMonth() + 1}-${d.getDate()}`;
  });

  // 创建所有 series，使用 legend.selected 来控制显示/隐藏
  // 当隐藏所有时，所有线条隐藏，但图例仍然可以点击来单独显示
  const legendNames = formattedData.map((item: any) => item.name);

  // 构建 legend.selected 对象，控制哪些系列被选中显示
  const legendSelected: Record<string, boolean> = {};
  legendNames.forEach(name => {
    legendSelected[name] = showAllEmployees.value;
  });

  const option = {
    title: {
      text: "员工传菜次数趋势（最近30天）",
      left: "center"
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "cross"
      }
    },
    legend: {
      data: legendNames,
      selected: legendSelected, // 使用 selected 控制显示/隐藏
      top: 30
    },
    grid: {
      left: "3%",
      right: "4%",
      bottom: "15%",
      containLabel: true
    },
    xAxis: {
      type: "category",
      boundaryGap: false,
      data: formattedDates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: "value"
    },
    series: formattedData.map((item: any, index: number) => ({
      name: item.name,
      type: "line",
      smooth: true,
      data: item.data,
      itemStyle: {
        color: ["#409EFF", "#67C23A", "#E6A23C", "#F56C6C", "#909399", "#606266", "#303133", "#9C27B0", "#00BCD4", "#FF9800"][
          index % 10
        ]
      }
    }))
  };

  // 使用 notMerge: true 确保完全替换配置，而不是合并
  employeeDishTrendChart.setOption(option, { notMerge: true });

  // 添加点击事件监听（始终启用，因为用户可能通过图例显示某个系列）
  employeeDishTrendChart.off("click");
  employeeDishTrendChart.on("click", (params: any) => {
    handleChartClick(params, dates, formattedData);
  });

  // 添加图例选择变化事件监听，用于自动更新按钮状态
  employeeDishTrendChart.off("legendselectchanged");
  employeeDishTrendChart.on("legendselectchanged", (params: any) => {
    handleLegendSelectChanged(params);
  });
};

// 处理图例选择变化事件
const handleLegendSelectChanged = (params: any) => {
  if (!employeeDishTrendData.value) return;

  const { formattedData } = employeeDishTrendData.value;
  const selected = params.selected;

  // 统计当前有多少个系列被选中显示
  let selectedCount = 0;
  formattedData.forEach((item: any) => {
    if (selected[item.name]) {
      selectedCount++;
    }
  });

  // 按钮逻辑：
  // - 按钮显示"隐藏所有" → showAllEmployees = true（当前所有都显示，点击后隐藏所有）
  // - 按钮显示"显示所有" → showAllEmployees = false（当前所有都隐藏，点击后显示所有）

  // 如果全部被隐藏（selectedCount === 0），按钮应该显示"显示所有"
  if (selectedCount === 0) {
    showAllEmployees.value = false;
  }
  // 如果全部被显示（selectedCount === formattedData.length），按钮应该显示"隐藏所有"
  else if (selectedCount === formattedData.length) {
    showAllEmployees.value = true;
  }
  // 如果只有一个被显示（selectedCount === 1），按钮应该显示"隐藏所有"
  else if (selectedCount === 1) {
    showAllEmployees.value = true;
  }
  // 如果部分被选中（1 < selectedCount < total），保持当前按钮状态不变
};

// 切换所有员工趋势图显示/隐藏
const toggleAllEmployeesVisibility = () => {
  showAllEmployees.value = !showAllEmployees.value;
  updateEmployeeDishTrendChart();
};

// 处理图表点击事件
const handleChartClick = async (params: any, dates: string[], formattedData: any[]) => {
  try {
    if (!selectedStore.value) {
      return;
    }

    // 获取点击的数据点信息
    const seriesIndex = params.seriesIndex;
    const dataIndex = params.dataIndex;

    if (seriesIndex === undefined || dataIndex === undefined) {
      return;
    }

    // 获取员工数据点和日期
    const employeeData = formattedData[seriesIndex];
    const date = dates[dataIndex];

    if (!employeeData || !date) {
      return;
    }

    // 优先使用原始job_number，如果没有则根据name判断
    let jobNumber: string;
    if (employeeData.original_job_number) {
      jobNumber = employeeData.original_job_number;
    } else if (employeeData.job_number) {
      jobNumber = employeeData.job_number;
    } else {
      // 如果没有job_number字段，根据name判断
      const employeeName = employeeData.name;
      if (employeeName === "未知" || employeeName === "未知员工") {
        jobNumber = "-1";
      } else {
        jobNumber = employeeName;
      }
    }

    // 查询IOTDB第一条记录
    const response = await getEmployeeDishFirstRecord({
      store_id: selectedStore.value,
      job_number: jobNumber,
      date: date
    });

    if (response.code === 200 && response.data) {
      const record = response.data;
      // 为每张图片添加格式化后的时间
      if (record.images && Array.isArray(record.images)) {
        record.images = record.images.map((img: any) => ({
          ...img,
          dish_time: extractTimeFromImagePath(img.image_path)
        }));
      }
      employeeDishRecord.value = record;
      employeeDishRecordDialogVisible.value = true;
    } else {
      employeeDishRecord.value = null;
      employeeDishRecordDialogVisible.value = true;
    }
  } catch (error) {
    console.error("查询员工传菜记录失败:", error);
    employeeDishRecord.value = null;
    employeeDishRecordDialogVisible.value = true;
  }
};

// 从图片路径中提取时间
// 路径格式: raw/ce5ee912-b3e9-d53b-876b-23282fef9496/1/1/20251107/unified/raw/121148_20535-1_raw.jpg
// 从目录中提取年月日: 20251107 -> 2025-11-07
// 从文件名中提取时分秒: 121148 (下划线前的部分) -> 12:11:48
const extractTimeFromImagePath = (imagePath: string): string => {
  if (!imagePath) return "-";

  try {
    // 提取年月日：从路径中找到8位数字（YYYYMMDD格式）
    const dateMatch = imagePath.match(/\/(\d{8})\//);
    if (!dateMatch) return "-";

    const dateStr = dateMatch[1];
    const year = dateStr.substring(0, 4);
    const month = dateStr.substring(4, 6);
    const day = dateStr.substring(6, 8);

    // 提取时分秒：从文件名中提取下划线前的6位数字（HHMMSS格式）
    const fileName = imagePath.split("/").pop() || "";
    const timeMatch = fileName.match(/^(\d{6})_/);
    if (!timeMatch) return `${year}-${month}-${day}`;

    const timeStr = timeMatch[1];
    const hour = timeStr.substring(0, 2);
    const minute = timeStr.substring(2, 4);
    const second = timeStr.substring(4, 6);

    return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
  } catch (error) {
    console.error("提取图片时间失败:", error);
    return "-";
  }
};

// 查看图片
const viewImage = (imageData: any) => {
  previewImageData.value = imageData;
  showPreviewAnnotation.value = true;
  previewImageLoaded.value = false;
  imagePreviewDialogVisible.value = true;
};

// 关闭图片预览弹窗
const closeImagePreview = () => {
  imagePreviewDialogVisible.value = false;
  previewImageData.value = null;
  showPreviewAnnotation.value = true;
  previewImageLoaded.value = false;
};

// 切换预览标注显示/隐藏
const togglePreviewAnnotationVisibility = () => {
  showPreviewAnnotation.value = !showPreviewAnnotation.value;
};

// 处理预览图片加载成功
const handlePreviewImageLoad = () => {
  previewImageLoaded.value = true;
  // 等待 DOM 更新后重新计算标注框位置
  nextTick(() => {
    // 触发响应式更新
    if (previewImageData.value) {
      previewImageData.value = { ...previewImageData.value };
    }
  });
};

// 处理预览图片加载错误
const handlePreviewImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  img.src = ""; // 清空src，显示默认的broken image图标
};

// 获取预览标注框样式
// annotation 参数可能是对象格式 {label: string, bbox: number[], ...} 或数组格式 [x, y, w, h]
const getPreviewAnnotationStyle = (annotation: any) => {
  if (!previewImageLoaded.value) {
    return { display: "none" };
  }

  // 提取 bbox 数组：如果是对象格式，从 annotation.bbox 获取；如果是数组格式，直接使用
  let bbox: number[] | null = null;
  if (Array.isArray(annotation)) {
    // 兼容旧格式：直接是数组
    bbox = annotation;
  } else if (annotation && typeof annotation === "object" && Array.isArray(annotation.bbox)) {
    // 新格式：对象包含 bbox 字段
    bbox = annotation.bbox;
  }

  if (!bbox || !Array.isArray(bbox) || bbox.length !== 4) {
    return { display: "none" };
  }

  const imgElement = previewImageRef.value;
  if (!imgElement || !imgElement.naturalWidth || !imgElement.naturalHeight) {
    return { display: "none" };
  }

  // 获取图片的原始尺寸和显示尺寸
  const imgRect = imgElement.getBoundingClientRect();
  const imgNaturalWidth = imgElement.naturalWidth || 0;
  const imgNaturalHeight = imgElement.naturalHeight || 0;
  const displayWidth = imgElement.clientWidth || imgElement.width || imgRect.width;
  const displayHeight = imgElement.clientHeight || imgElement.height || imgRect.height;

  if (imgNaturalWidth === 0 || imgNaturalHeight === 0) {
    return { display: "none" };
  }

  // 计算缩放比例
  const scaleX = displayWidth / imgNaturalWidth;
  const scaleY = displayHeight / imgNaturalHeight;

  // bbox 格式可能是 YOLO 格式 [center_x, center_y, width, height]（归一化的中心点坐标和宽高）
  // 或者是绝对坐标格式 [x1, y1, x2, y2]
  let left: number, top: number, width: number, height: number;

  // 判断是 YOLO 格式还是绝对坐标格式
  const isYoloFormat = bbox.every(val => val >= 0 && val <= 1);

  if (isYoloFormat) {
    // YOLO 格式：[center_x, center_y, width, height]（归一化）
    const [centerXNormalized, centerYNormalized, widthNormalized, heightNormalized] = bbox;
    const centerX = centerXNormalized * imgNaturalWidth * scaleX;
    const centerY = centerYNormalized * imgNaturalHeight * scaleY;
    width = widthNormalized * imgNaturalWidth * scaleX;
    height = heightNormalized * imgNaturalHeight * scaleY;
    left = centerX - width / 2;
    top = centerY - height / 2;
  } else {
    // 绝对坐标格式：[x1, y1, x2, y2]
    const [x1, y1, x2, y2] = bbox;
    left = x1 * scaleX;
    top = y1 * scaleY;
    width = (x2 - x1) * scaleX;
    height = (y2 - y1) * scaleY;
  }

  // 确保标注框不超出图片边界
  const clampedLeft = Math.max(0, Math.min(left, displayWidth - width));
  const clampedTop = Math.max(0, Math.min(top, displayHeight - height));
  const clampedWidth = Math.min(width, displayWidth - clampedLeft);
  const clampedHeight = Math.min(height, displayHeight - clampedTop);

  return {
    position: "absolute" as const,
    left: `${clampedLeft}px`,
    top: `${clampedTop}px`,
    width: `${clampedWidth}px`,
    height: `${clampedHeight}px`,
    border: "2px solid #409EFF",
    backgroundColor: "rgba(64, 158, 255, 0.1)",
    pointerEvents: "none" as const,
    zIndex: 10
  };
};

// 关闭员工传菜记录详情弹窗
const closeEmployeeDishRecordDialog = () => {
  employeeDishRecordDialogVisible.value = false;
  employeeDishRecord.value = null;
};

// 获取图片完整URL - 直接使用后端返回的地址
const getImageUrl = (imagePath: string) => {
  if (!imagePath) {
    return "";
  }
  // 直接返回后端返回的图片路径，不做任何处理
  return imagePath;
};

// 处理场景状态统计图点击事件
const handleStatusChartClick = async (params: any) => {
  try {
    if (!selectedStore.value) {
      return;
    }

    // 获取点击的数据点信息
    const dataIndex = params.dataIndex;
    if (dataIndex === undefined) {
      return;
    }

    // 获取日期
    const { dates } = statusStatisticsData.value;
    const date = dates[dataIndex];
    if (!date) {
      return;
    }

    // 格式化日期为 YYYY-MM-DD
    const dateObj = new Date(date);
    const year = dateObj.getFullYear();
    const month = String(dateObj.getMonth() + 1).padStart(2, "0");
    const day = String(dateObj.getDate()).padStart(2, "0");
    const dateStr = `${year}-${month}-${day}`;

    // 打开弹窗
    timeoutLogDate.value = dateStr;
    timeoutLogPageNum.value = 1;
    timeoutLogDialogVisible.value = true;

    // 加载日志数据
    await fetchTimeoutLogs(dateStr);
  } catch (error) {
    console.error("处理场景状态统计图点击失败:", error);
  }
};

// 获取超时日志列表
const fetchTimeoutLogs = async (date: string) => {
  try {
    if (!selectedStore.value) {
      return;
    }

    timeoutLogLoading.value = true;

    const response = await getSceneLogList({
      pageNum: timeoutLogPageNum.value,
      pageSize: timeoutLogPageSize.value,
      store_id: selectedStore.value,
      scene_id: 2, // 小料台场景ID
      status: 3, // 状态为3
      start_date: date,
      end_date: date
    });

    if (response.code === 200 && response.data) {
      timeoutLogList.value = response.data.records || [];
      timeoutLogTotal.value = response.data.total || 0;
    } else {
      timeoutLogList.value = [];
      timeoutLogTotal.value = 0;
    }
  } catch (error) {
    console.error("获取超时日志列表失败:", error);
    timeoutLogList.value = [];
    timeoutLogTotal.value = 0;
  } finally {
    timeoutLogLoading.value = false;
  }
};

// 关闭超时日志弹窗
const closeTimeoutLogDialog = () => {
  timeoutLogDialogVisible.value = false;
  timeoutLogList.value = [];
  timeoutLogDate.value = "";
  timeoutLogPageNum.value = 1;
  timeoutLogTotal.value = 0;
};

// 处理分页变化
const handleTimeoutLogPageChange = (page: number) => {
  timeoutLogPageNum.value = page;
  if (timeoutLogDate.value) {
    fetchTimeoutLogs(timeoutLogDate.value);
  }
};

// 格式化时间
const formatDateTime = (dateString: string | null | undefined) => {
  if (!dateString) return "-";
  try {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    const seconds = String(date.getSeconds()).padStart(2, "0");
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  } catch {
    return "-";
  }
};

// 查看超时日志图片
const viewTimeoutLogImage = (row: any) => {
  if (row.image_url) {
    timeoutLogImageUrl.value = row.image_url;
    timeoutLogImageDialogVisible.value = true;
  }
};

// 关闭超时日志图片预览弹窗
const closeTimeoutLogImageDialog = () => {
  timeoutLogImageDialogVisible.value = false;
  timeoutLogImageUrl.value = "";
};

// 页面初始化
onMounted(() => {
  fetchStoreList();
  // fetchStoreDailyStatistics 会在 fetchStoreList 中选择门店后自动调用

  // 监听窗口大小变化
  window.addEventListener("resize", () => {
    lineChart?.resize();
    barChart?.resize();
    statusChart?.resize();
    storeDailyChart?.resize();
    employeeDishTodayChart?.resize();
    employeeDishTrendChart?.resize();
  });
});
</script>

<style scoped lang="scss">
.statistics-scene {
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

    .store-selector {
      display: flex;
      align-items: center;
      gap: 10px;

      .el-select {
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
      transition: all 0.3s ease;

      &.clickable-card {
        cursor: pointer;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
      }

      .stat-item {
        text-align: center;
        padding: 20px;

        .stat-value {
          font-size: 32px;
          font-weight: bold;
          color: #409eff;
          margin-bottom: 8px;
        }

        .stat-label {
          font-size: 14px;
          color: #909399;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 4px;

          .click-hint {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 12px;
            color: #409eff;
            margin-top: 4px;
            opacity: 0.8;
            transition: opacity 0.3s ease;
            cursor: pointer;

            &:hover {
              opacity: 1;
              text-decoration: underline;
            }
          }
        }
      }

      &.clickable-card:hover .stat-label .click-hint {
        opacity: 1;
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

    .full-width {
      grid-column: 1 / -1;
    }

    .chart-card {
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 600;
        color: #303133;

        .click-tip {
          font-size: 12px;
          color: #909399;
          font-weight: normal;
          margin-left: 12px;
        }

        .click-hint {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          color: #409eff;
          font-weight: normal;
          opacity: 0.8;
          transition: opacity 0.3s ease;
          cursor: pointer;

          &:hover {
            opacity: 1;
            text-decoration: underline;
          }

          &.employee-detail-hint {
            color: #1d39c4;
            font-weight: 600;
            font-size: 13px;
            opacity: 1;
            padding: 4px 8px;
            border-radius: 4px;
            background-color: rgba(29, 57, 196, 0.08);
            transition: all 0.3s ease;

            &:hover {
              background-color: rgba(29, 57, 196, 0.15);
              color: #0d2ba0;
              transform: translateY(-1px);
              box-shadow: 0 2px 4px rgba(29, 57, 196, 0.2);
            }
          }
        }
      }

      .chart-container {
        height: 400px;
        padding: 20px;

        &.clickable-chart {
          cursor: pointer;
          transition: all 0.3s ease;

          &:hover {
            background-color: rgba(64, 158, 255, 0.02);
          }
        }

        .chart {
          width: 100%;
          height: 100%;
        }
      }
    }

    .chart-card:hover .card-header .click-hint {
      opacity: 1;
    }
  }

  // 弹窗图表样式
  .dialog-chart-container {
    height: 500px;
    padding: 20px;

    .dialog-chart {
      width: 100%;
      height: 100%;
    }
  }

  // 记录详情样式
  .record-detail {
    .image-info {
      max-height: 200px;
      overflow-y: auto;
      pre {
        margin: 0;
        white-space: pre-wrap;
        word-break: break-all;
        font-size: 12px;
      }
    }

    .image-names {
      word-break: break-all;
    }

    .images-section {
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid #ebeef5;

      h3 {
        margin: 0 0 20px 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }

      :deep(.el-table) {
        width: 100% !important;
      }

      .image-viewer {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 400px;
        position: relative;
      }

      .image-wrapper {
        position: relative;
        display: inline-block;
        max-width: 100%;
      }

      .viewer-image {
        max-width: 100%;
        max-height: 70vh;
        object-fit: contain;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        display: block;
      }

      .annotation-box {
        position: absolute;
        border: 2px solid #409eff;
        background-color: rgba(64, 158, 255, 0.1);
        pointer-events: none;
        z-index: 10;

        .annotation-label {
          position: absolute;
          top: -22px;
          left: 0;
          background-color: #409eff;
          color: white;
          padding: 2px 6px;
          font-size: 12px;
          border-radius: 2px;
          white-space: nowrap;
          line-height: 1.2;
        }
      }
    }

    .no-image {
      text-align: center;
      color: #909399;
      font-size: 14px;
      padding: 20px;
    }
  }

  .no-record {
    padding: 40px 0;
    text-align: center;
  }
}

// 员工传菜趋势弹窗样式
:deep(.employee-dish-trend-dialog) {
  .el-dialog {
    height: 100vh;
    margin-top: 7.5vh !important;
    display: flex;
    flex-direction: column;
  }

  .el-dialog__body {
    flex: 1;
    overflow-y: auto;
  }
}

// 员工传菜记录详情弹窗样式
:deep(.employee-dish-record-dialog) {
  .el-dialog {
    height: 100vh;
    margin-top: 7.5vh !important;
    display: flex;
    flex-direction: column;
  }

  .el-dialog__body {
    flex: 1;
    overflow-y: auto;
  }
}

// 超时日志弹窗样式
:deep(.timeout-log-dialog) {
  .el-dialog {
    height: 100vh;
    margin-top: 7.5vh !important;
    display: flex;
    flex-direction: column;
  }

  .el-dialog__body {
    flex: 1;
    overflow-y: auto;
  }
}

.timeout-log-container {
  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}

// 超时日志图片预览弹窗样式
:deep(.timeout-log-image-dialog) {
  .el-dialog {
    height: 100vh;
    margin-top: 7.5vh !important;
    display: flex;
    flex-direction: column;
  }

  .el-dialog__body {
    flex: 1;
    overflow-y: auto;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.timeout-log-image-container {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;

  .image-error {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    color: #909399;
    font-size: 14px;
    min-height: 200px;

    .el-icon {
      font-size: 48px;
    }
  }
}

// 图片预览弹窗样式
:deep(.image-preview-dialog) {
  .el-dialog {
    height: 100vh;
    margin-top: 7.5vh !important;
    display: flex;
    flex-direction: column;
  }

  .el-dialog__body {
    flex: 1;
    overflow-y: auto;
  }
}

.image-preview-container {
  .image-viewer {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 400px;
    position: relative;

    .image-wrapper {
      position: relative;
      display: inline-block;
      max-width: 100%;
    }

    .viewer-image {
      max-width: 100%;
      max-height: 70vh;
      object-fit: contain;
      border-radius: 4px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      display: block;
    }

    .annotation-box {
      position: absolute;
      border: 2px solid #409eff;
      background-color: rgba(64, 158, 255, 0.1);
      pointer-events: none;
      z-index: 10;

      .annotation-label {
        position: absolute;
        top: -22px;
        left: 0;
        background-color: #409eff;
        color: white;
        padding: 2px 6px;
        font-size: 12px;
        border-radius: 2px;
        white-space: nowrap;
        line-height: 1.2;
      }
    }
  }
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 80px;
  position: relative;

  > span {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    padding-right: 12px;
  }

  .el-button {
    margin-right: 20px;
    flex-shrink: 0;
  }
}
</style>
