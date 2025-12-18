import http from "@/api";
import { PORT1 } from "@/api/config/servicePort";
import { ResPage } from "@/api/interface";
import { InferenceConfigInfo, InferenceConfigListParams } from "../types/inference.types";

// 推理配置相关接口
const MODULE_URL = PORT1 + "/inference_config";

/**
 * 获取推理配置列表
 */
export const getInferenceConfigList = (params: InferenceConfigListParams) => {
  return http.get<ResPage<InferenceConfigInfo>>(`${MODULE_URL}/list`, params);
};

/**
 * 删除推理配置
 */
export const deleteInferenceConfig = (id: number) => {
  return http.delete(`${MODULE_URL}/delete/${id}`);
};

/**
 * 新增推理配置
 */
export const saveInferenceConfig = (data: { store_id: number; version: string; content: string }) => {
  return http.post(`${MODULE_URL}/save`, data);
};

/**
 * 获取默认推理配置
 */
export const getDefaultInferenceConfig = () => {
  return http.get(`${MODULE_URL}/default`);
};

/**
 * 获取没有配置的门店列表
 */
export const getStoresWithoutConfig = () => {
  return http.get(`${PORT1}/store/without_config`);
};

/**
 * 获取最新推理配置
 */
export const getLatestInferenceConfig = (storeId: number) => {
  return http.get<InferenceConfigInfo>(`${MODULE_URL}/latest/${storeId}`);
};

/**
 * 统一更新推理配置（后端自动判断更新或新增）
 */
export const unifiedUpdateInferenceConfig = (data: { store_id: number; version: string; content: string }) => {
  return http.post(`${MODULE_URL}/unified_update`, data);
};
