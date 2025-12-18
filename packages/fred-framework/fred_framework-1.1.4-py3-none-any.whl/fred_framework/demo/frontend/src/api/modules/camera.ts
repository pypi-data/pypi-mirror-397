import type { ResPage } from "@/api/interface";
import { PORT1 } from "@/api/config/servicePort";
import http from "@/api";
import type { StoreInfo } from "@/api/model/storeModel";
import type {
  CameraInfo,
  CameraListQuery,
  CameraSaveParams,
  CameraChannelUpdateParams,
  CameraDeleteParams,
  CameraRegionCountParams,
  CameraRegionCountResponse,
  CameraBrandInfo
} from "@/api/model/cameraModel";

// 重新导出StoreInfo类型，供其他模块使用
export type { StoreInfo };

/**
 * 摄像头管理模块
 */

// 获取摄像头列表
export const getCameraList = (params: CameraListQuery) => {
  return http.get<ResPage<CameraInfo>>(PORT1 + `/camera/list`, params);
};

// 获取摄像头信息
export const getCameraInfo = (cameraId: number) => {
  return http.get<CameraInfo>(PORT1 + `/camera/info/${cameraId}`);
};

// 保存摄像头
export const saveCamera = (params: CameraSaveParams) => {
  return http.post(PORT1 + `/camera/save`, params);
};

// 更新摄像头
export const updateCamera = (cameraId: number, params: CameraSaveParams) => {
  return http.put(PORT1 + `/camera/update/${cameraId}`, params);
};

// 删除摄像头
export const deleteCamera = (params: CameraDeleteParams) => {
  return http.delete(PORT1 + `/camera/delete/${params.id}`);
};

// 根据省市区获取摄像头数量
export const getCameraCountByRegion = (params: CameraRegionCountParams) => {
  return http.get<CameraRegionCountResponse>(PORT1 + `/camera/count_by_region`, params);
};

// 更新摄像头通道
export const updateCameraChannels = (params: CameraChannelUpdateParams) => {
  return http.post(PORT1 + `/camera/channels/update`, params);
};

// 获取摄像头品牌列表
export const getCameraBrands = () => {
  return http.get<CameraBrandInfo[]>(PORT1 + `/camera/brands`);
};
