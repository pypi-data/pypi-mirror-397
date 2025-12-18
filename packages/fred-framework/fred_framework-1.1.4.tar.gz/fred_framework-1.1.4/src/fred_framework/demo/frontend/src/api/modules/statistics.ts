import http from "@/api";
import { PORT1 } from "@/api/config/servicePort";
import type {
  AnnotationStatistics,
  CameraStatistics,
  DeviceStatistics,
  ModelStatistics,
  PerformanceStatistics,
  RegionStatistics,
  SceneStatistics,
  StatisticsQuery,
  StoreStatistics,
  TimeSeriesData
} from "@/api/model/statisticsModel";

/**
 * 统计管理相关接口
 */

// 获取设备统计数据
export const getDeviceStatistics = (params?: StatisticsQuery) => {
  return http.get<DeviceStatistics>(PORT1 + `/statistics/device`, params);
};

// 获取摄像头统计数据
export const getCameraStatistics = (params?: StatisticsQuery) => {
  return http.get<CameraStatistics>(PORT1 + `/statistics/camera`, params);
};

// 获取门店统计数据
export const getStoreStatistics = (params?: StatisticsQuery) => {
  return http.get<StoreStatistics>(PORT1 + `/statistics/store`, params);
};

// 获取模型统计数据
export const getModelStatistics = (params?: StatisticsQuery) => {
  return http.get<ModelStatistics>(PORT1 + `/statistics/model`, params);
};

// 获取场景统计数据
export const getSceneStatistics = (params?: StatisticsQuery) => {
  return http.get<SceneStatistics>(PORT1 + `/statistics/scene`, params);
};

// 获取标注统计数据
export const getAnnotationStatistics = (params?: StatisticsQuery) => {
  return http.get<AnnotationStatistics>(PORT1 + `/statistics/annotation`, params);
};

// 获取时间序列统计数据
export const getTimeSeriesStatistics = (params: StatisticsQuery) => {
  return http.get<TimeSeriesData[]>(PORT1 + `/statistics/timeseries`, params);
};

// 获取区域统计数据
export const getRegionStatistics = (params?: StatisticsQuery) => {
  return http.get<RegionStatistics[]>(PORT1 + `/statistics/region`, params);
};

// 获取性能统计数据
export const getPerformanceStatistics = () => {
  return http.get<PerformanceStatistics>(PORT1 + `/statistics/performance`);
};

// 获取场景图片列表
export const getSceneImages = (sceneName: string) => {
  return http.get<string[]>(PORT1 + `/statistics/scene/images`, { scene_name: sceneName });
};

// 获取场景每日统计数据（用于线性图）
export const getSceneDailyStatistics = (params?: { store_id?: number; days?: number }) => {
  return http.get<{
    scenes: Array<{ id: number; name: string }>;
    dates: string[];
    data: Array<{ name: string; type: string; data: number[] }>;
  }>(PORT1 + `/statistics/scene/daily`, params);
};

// 获取场景状态统计数据（用于线性图）
export const getSceneStatusStatistics = (params?: { store_id?: number; scene_id?: number; status?: number; days?: number }) => {
  return http.get<{
    dates: string[];
    data: number[];
  }>(PORT1 + `/statistics/scene/status`, params);
};

// 获取场景门店每日统计数据（用于线性图）
export const getSceneStoreDailyStatistics = (params?: { store_id?: number; days?: number }) => {
  return http.get<{
    stores: Array<{ id: number; name: string }>;
    dates: string[];
    data: Array<{ name: string; type: string; data: number[] }>;
  }>(PORT1 + `/statistics/scene/store-daily`, params);
};

// 获取当日员工传菜次数统计（用于柱状图）
export const getEmployeeDishStatisticsToday = (params?: { store_id?: number }) => {
  return http.get<{
    employees: string[];
    data: number[];
  }>(PORT1 + `/statistics/employee/dish-today`, params);
};

// 获取员工30日传菜次数趋势（用于线性图）
export const getEmployeeDishStatisticsTrend = (params?: { store_id?: number; days?: number }) => {
  return http.get<{
    employees: string[];
    dates: string[];
    data: Array<{ name: string; type: string; data: number[] }>;
  }>(PORT1 + `/statistics/employee/dish-trend`, params);
};

// 根据员工工号、门店、日期、摄像头查询IOTDB第一条记录
export const getEmployeeDishFirstRecord = (params?: {
  store_id?: number;
  job_number?: string;
  date?: string;
  camera_id?: number;
}) => {
  return http.get<any>(PORT1 + `/statistics/employee/dish-first-record`, params);
};

// 对话统计查询接口
export const processConversationQuery = (params: { query: string; store_id?: number }) => {
  return http.post<{
    text: string;
    data?: {
      cards?: Array<{ label: string; value: number | string }>;
      chart?: {
        title: string;
        type: "line" | "bar" | "pie";
        option: any;
      };
      table?: any[];
      table_columns?: Array<{ prop: string; label: string; width?: number; sortable?: boolean }>;
    };
  }>(PORT1 + `/statistics/conversation`, params);
};
