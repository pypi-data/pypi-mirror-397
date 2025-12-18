/**
 * 统计相关数据模型
 */

/**
 * 统计数据基础信息
 */
export interface StatisticsBase {
  date: string;
  value: number;
  label?: string;
}

/**
 * 设备统计信息
 */
export interface DeviceStatistics {
  total_devices: number;
  online_devices: number;
  offline_devices: number;
  bound_devices: number;
  unbound_devices: number;
  device_types: {
    type: string;
    count: number;
  }[];
}

/**
 * 摄像头统计信息
 */
export interface CameraStatistics {
  total_cameras: number;
  online_cameras: number;
  offline_cameras: number;
  nvr_count: number;
  camera_count: number;
  total_channels: number;
  active_channels: number;
}

/**
 * 门店统计信息
 */
export interface StoreStatistics {
  total_stores: number;
  stores_with_devices: number;
  stores_without_devices: number;
  stores_with_cameras: number;
  stores_without_cameras: number;
  region_distribution: {
    province: string;
    count: number;
  }[];
}

/**
 * 模型统计信息
 */
export interface ModelStatistics {
  total_models: number;
  active_models: number;
  inactive_models: number;
  model_types: {
    type: string;
    count: number;
  }[];
  inference_count: number;
  success_rate: number;
}

/**
 * 场景统计信息
 */
export interface SceneStatistics {
  total_scenes: number;
  active_scenes: number;
  inactive_scenes: number;
  scenes_with_models: number;
  average_models_per_scene: number;
}

/**
 * 标注统计信息
 */
export interface AnnotationStatistics {
  total_annotations: number;
  total_images: number;
  labeled_images: number;
  unlabeled_images: number;
  label_distribution: {
    label_name: string;
    count: number;
  }[];
}

/**
 * 统计查询参数
 */
export interface StatisticsQuery {
  start_date?: string;
  end_date?: string;
  type?: "device" | "camera" | "store" | "model" | "scene" | "annotation";
  group_by?: "day" | "week" | "month" | "year";
}

/**
 * 时间序列统计数据
 */
export interface TimeSeriesData {
  date: string;
  value: number;
  label?: string;
  category?: string;
}

/**
 * 区域统计数据
 */
export interface RegionStatistics {
  province: string;
  city?: string;
  district?: string;
  device_count: number;
  camera_count: number;
  store_count: number;
  model_count: number;
}

/**
 * 性能统计数据
 */
export interface PerformanceStatistics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_usage: number;
  inference_time: number;
  accuracy: number;
}
