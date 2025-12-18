/**
 * 推理配置信息类型
 */
export interface InferenceConfigInfo {
  id: number;
  store_id: number;
  store_name: string;
  content: string;
  version: string;
  created: string;
  modified: string;
}

/**
 * 推理配置列表查询参数
 */
export interface InferenceConfigListParams {
  page?: number;
  limit?: number;
  store_id?: number;
  store_name?: string;
  version?: string;
}

/**
 * 门店信息类型
 */
export interface StoreInfo {
  id: number;
  name: string;
  address?: string;
  province_id?: number;
  city_id?: number;
  district_id?: number;
}
