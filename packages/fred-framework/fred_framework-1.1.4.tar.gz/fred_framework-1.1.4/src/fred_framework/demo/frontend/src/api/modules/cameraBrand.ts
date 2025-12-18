import type { ResPage } from "@/api/interface";
import { PORT1 } from "@/api/config/servicePort";
import http from "@/api";

/**
 * 摄像头品牌管理模块
 */

// 摄像头品牌信息接口
export interface CameraBrandInfo {
  id: number;
  name: string;
}

// 摄像头品牌列表查询参数
export interface CameraBrandListParams {
  page?: number;
  limit?: number;
  name?: string;
}

// 保存摄像头品牌参数
export interface CameraBrandSaveParams {
  name: string;
}

// 更新摄像头品牌参数
export interface CameraBrandUpdateParams {
  name: string;
}

// 获取摄像头品牌列表
export const getCameraBrandList = (params: CameraBrandListParams) => {
  return http.get<ResPage<CameraBrandInfo>>(PORT1 + `/camera-brand/list`, params);
};

// 获取摄像头品牌信息
export const getCameraBrandInfo = (brandId: number) => {
  return http.get<CameraBrandInfo>(PORT1 + `/camera-brand/info/${brandId}`);
};

// 保存摄像头品牌
export const saveCameraBrand = (params: CameraBrandSaveParams) => {
  return http.post(PORT1 + `/camera-brand/save`, params);
};

// 更新摄像头品牌
export const updateCameraBrand = (brandId: number, params: CameraBrandUpdateParams) => {
  return http.put(PORT1 + `/camera-brand/update/${brandId}`, params);
};

// 删除摄像头品牌
export const deleteCameraBrand = (brandId: number) => {
  return http.delete(PORT1 + `/camera-brand/delete/${brandId}`);
};

// 获取所有摄像头品牌列表（用于下拉选择）
export const getAllCameraBrands = () => {
  return http.get<CameraBrandInfo[]>(PORT1 + `/camera-brand/all`);
};
