import type { ResPage } from "@/api/interface";
import { PORT1 } from "@/api/config/servicePort";
import http from "@/api";
import type { StoreInfo } from "@/api/model/storeModel";
import type {
  DeviceInfo,
  DeviceListQuery,
  DeviceSaveParams,
  DeviceDeleteParams,
  DeviceRegionCountParams,
  DeviceRegionCountResponse,
  TerminalInfo,
  TerminalListQuery,
  DeviceBindParams,
  DeviceBindToStoreParams
} from "@/api/model/deviceModel";

// 重新导出StoreInfo类型，供其他模块使用
export type { StoreInfo };

/**
 * 设备管理模块
 */

// 获取设备列表
export const getDeviceList = (params: DeviceListQuery) => {
  return http.get<ResPage<DeviceInfo>>(PORT1 + `/device/list`, params);
};

// 获取设备信息
export const getDeviceInfo = (deviceId: number) => {
  return http.get<DeviceInfo>(PORT1 + `/device/info/${deviceId}`);
};

// 保存设备
export const saveDevice = (params: DeviceSaveParams) => {
  return http.post(PORT1 + `/device/save`, params);
};

// 更新设备
export const updateDevice = (deviceId: number, params: DeviceSaveParams) => {
  return http.put(PORT1 + `/device/update/${deviceId}`, params);
};

// 删除设备
export const deleteDevice = (params: DeviceDeleteParams) => {
  return http.delete(PORT1 + `/device/delete/${params.id}`);
};

// 根据省市区获取设备数量
export const getDeviceCountByRegion = (params: DeviceRegionCountParams) => {
  return http.get<DeviceRegionCountResponse>(PORT1 + `/device/count_by_region`, params);
};

// 获取终端设备列表
export const getTerminalList = (params: TerminalListQuery) => {
  return http.get<ResPage<TerminalInfo>>(PORT1 + `/device/terminal/list`, params);
};

// 绑定设备到终端
export const bindDeviceToTerminal = (params: DeviceBindParams) => {
  return http.post(PORT1 + `/device/bind`, params);
};

// 绑定设备到门店
export const bindDeviceToStore = (params: DeviceBindToStoreParams) => {
  return http.post(PORT1 + `/device/bind_to_store`, params);
};

// 获取未绑定设备的门店列表
export const getUnboundStores = (params: DeviceListQuery) => {
  return http.get<ResPage<StoreInfo>>(PORT1 + `/device/unbound_stores`, params);
};
