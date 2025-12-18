/**
 * 摄像头相关数据模型
 */

/**
 * 摄像头通道信息
 */
export interface CameraChannelInfo {
  id?: number;
  camera_id?: number;
  channel_id?: string;
  status: number;
  image?: string;
}

/**
 * 摄像头品牌信息
 */
export interface CameraBrandInfo {
  id: number;
  name: string;
}

/**
 * 摄像头信息
 */
export interface CameraInfo {
  id: number;
  store_id: number;
  store_name: string;
  province_id?: number;
  province_name?: string;
  city_id?: number;
  city_name?: string;
  district_id?: number;
  district_name?: string;
  ip: string;
  user: string;
  pwd: string;
  brand?: string;
  brand_id?: number;
  type: "nvr" | "camera";
  channels?: CameraChannelInfo[];
  channel_count?: number;
  active_channel_count?: number;
  created?: string;
  modified?: string;
}

/**
 * 摄像头列表查询参数
 */
export interface CameraListQuery {
  page?: number;
  limit?: number;
  ip?: string;
  store_id?: number;
  store_name?: string;
  province_id?: number;
  city_id?: number;
  district_id?: number;
  type?: "nvr" | "camera";
  brand?: string;
}

/**
 * 摄像头保存参数
 */
export interface CameraSaveParams {
  store_id: number | null;
  ip: string;
  user: string;
  pwd: string;
  brand_id?: number;
  type: "nvr" | "camera";
}

/**
 * 摄像头更新参数
 */
export interface CameraUpdateParams extends CameraSaveParams {
  id: number;
}

/**
 * 摄像头通道更新参数
 */
export interface CameraChannelUpdateParams {
  camera_id: number;
  channels: CameraChannelInfo[];
}

/**
 * 摄像头删除参数
 */
export interface CameraDeleteParams {
  id: number;
}

/**
 * 摄像头区域统计参数
 */
export interface CameraRegionCountParams {
  province_id?: number;
  city_id?: number;
  district_id?: number;
}

/**
 * 摄像头区域统计响应
 */
export interface CameraRegionCountResponse {
  count: number;
}
