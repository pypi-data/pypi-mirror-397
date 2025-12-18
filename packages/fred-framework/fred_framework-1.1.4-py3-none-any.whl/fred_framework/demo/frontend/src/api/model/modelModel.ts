/**
 * 模型相关数据模型
 */

/**
 * 模型信息
 */
export interface ModelInfo {
  id: number;
  name: string;
  desc: string;
  created?: string;
  modified?: string;
  status?: number;
  type?: string;
  version?: string;
  file_path?: string;
  file_size?: number;
}

/**
 * 模型列表查询参数
 */
export interface ModelListQuery {
  pageNum?: number;
  pageSize?: number;
  name?: string;
  status?: number;
  type?: string;
}

/**
 * 模型详情查询参数
 */
export interface ModelDetailQuery {
  id: number;
}

/**
 * 模型创建参数
 */
export interface ModelCreateParams {
  name: string;
  desc: string;
  file_path?: string;
  type?: string;
  version?: string;
}

/**
 * 模型更新参数
 */
export interface ModelUpdateParams {
  id: number;
  name: string;
  desc: string;
  file_path?: string;
  type?: string;
  version?: string;
}

/**
 * 模型删除参数
 */
export interface ModelDeleteParams {
  id: number;
}

/**
 * 模型图片关联信息
 */
export interface ModelImageRelation {
  id: number;
  model_id: number;
  image_path: string;
  image_name?: string;
  file_size?: number;
  width?: number;
  height?: number;
  created?: string;
}

/**
 * 模型图片关联列表查询参数
 */
export interface ModelImageRelationQuery {
  model_id: number;
  image_path?: string;
  pageNum?: number;
  pageSize?: number;
}

/**
 * 模型图片关联添加参数
 */
export interface ModelImageRelationAddParams {
  model_id: number;
  image_paths: string[];
}

/**
 * 模型图片关联移除参数
 */
export interface ModelImageRelationRemoveParams {
  model_id: number;
  relation_ids: number[];
}

/**
 * 模型上传参数
 */
export interface ModelUploadParams {
  model_id: number;
  file: File;
}

/**
 * 模型训练参数
 */
export interface ModelTrainParams {
  model_id: number;
  dataset_path: string;
  epochs?: number;
  batch_size?: number;
  learning_rate?: number;
}

/**
 * 模型推理参数
 */
export interface ModelInferenceParams {
  model_id: number;
  input_data: any;
  config?: any;
}
