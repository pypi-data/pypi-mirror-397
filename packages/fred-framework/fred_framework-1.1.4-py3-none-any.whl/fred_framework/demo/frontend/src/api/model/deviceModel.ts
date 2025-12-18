/**
 * 设备相关数据模型
 */

/**
 * 网络信息
 */
export interface NetworkInfo {
  name: string;
  ip: string;
  ip_type?: "IPv4" | "IPv6";
  mac?: string;
  is_physical?: boolean;
}

/**
 * 设备信息
 */
export interface DeviceInfo {
  id: number;
  name: string;
  sn: string;
  store_id: number;
  store_name: string;
  province_id?: number;
  province_name?: string;
  city_id?: number;
  city_name?: string;
  district_id?: number;
  district_name?: string;
  cpu?: string;
  cpu_raw?: any;
  mem?: string;
  mem_raw?: any;
  os?: string;
  gpu?: string;
  gpu_raw?: any;
  npu?: string;
  network?: NetworkInfo[];
  created: string;
  modified: string;
  device_type?: string;
  binding_status?: number;
  binding_status_text?: string;
}

/**
 * 设备列表查询参数
 */
export interface DeviceListQuery {
  page?: number;
  limit?: number;
  name?: string;
  address?: string;
  store_id?: number;
  store_name?: string;
  province_id?: number;
  city_id?: number;
  district_id?: number;
}

/**
 * 设备保存参数
 */
export interface DeviceSaveParams {
  name: string;
  sn: string;
  store_id: number;
  cpu?: string;
  mem?: string;
  os?: string;
  gpu?: string;
  npu?: string;
  network?: NetworkInfo[];
}

/**
 * 设备更新参数
 */
export interface DeviceUpdateParams extends DeviceSaveParams {
  id: number;
}

/**
 * 设备删除参数
 */
export interface DeviceDeleteParams {
  id: number;
}

/**
 * 设备区域统计参数
 */
export interface DeviceRegionCountParams {
  province_id?: number;
  city_id?: number;
  district_id?: number;
}

/**
 * 设备区域统计响应
 */
export interface DeviceRegionCountResponse {
  count: number;
}

/**
 * 终端设备信息
 */
export interface TerminalInfo {
  id: number;
  name: string;
  sn: string;
  device_type?: string;
  cpu?: string;
  mem?: string;
  os?: string;
  gpu?: string;
  npu?: string;
  network?: NetworkInfo[];
  created: string;
}

/**
 * 终端设备列表查询参数
 */
export interface TerminalListQuery {
  page?: number;
  limit?: number;
  name?: string;
  sn?: string;
}

/**
 * 设备绑定参数
 */
export interface DeviceBindParams {
  device_id: number;
  terminal_id: number;
}

/**
 * 设备绑定到门店参数
 */
export interface DeviceBindToStoreParams {
  terminal_id: number;
  store_id: number;
}
