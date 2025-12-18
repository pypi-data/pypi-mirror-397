import { ResPage } from "@/api/interface";
import { PORT1 } from "@/api/config/servicePort";
import http from "@/api";
import type {
  ModelInfo,
  ModelListQuery,
  ModelDetailQuery,
  ModelCreateParams,
  ModelUpdateParams,
  ModelDeleteParams,
  ModelImageRelation,
  ModelImageRelationQuery,
  ModelImageRelationAddParams,
  ModelImageRelationRemoveParams,
  ModelUploadParams,
  ModelTrainParams,
  ModelInferenceParams
} from "@/api/model/modelModel";

/**
 * 模型管理相关接口
 */

// 获取模型列表
export const getModelListApi = (params: ModelListQuery) => {
  return http.get<ResPage<ModelInfo>>(PORT1 + "/model/list", params);
};

// 获取模型详情
export const getModelDetailApi = (params: ModelDetailQuery) => {
  return http.get<ModelInfo>(PORT1 + "/model/detail", params);
};

// 创建模型
export const createModelApi = (data: ModelCreateParams) => {
  return http.post(PORT1 + "/model/create", data);
};

// 更新模型
export const updateModelApi = (data: ModelUpdateParams) => {
  return http.post(PORT1 + "/model/update", data);
};

// 删除模型
export const deleteModelApi = (data: ModelDeleteParams) => {
  return http.delete(PORT1 + "/model/delete", data);
};

// 模型图片关联管理相关接口

/**
 * 获取模型图片关联列表
 */
export const getModelImageRelations = (params: ModelImageRelationQuery) => {
  return http.get<ResPage<ModelImageRelation>>(PORT1 + "/model/image/list", params);
};

/**
 * 添加模型图片关联
 */
export const addModelImageRelations = (data: ModelImageRelationAddParams) => {
  return http.post(PORT1 + "/model/image/add", data);
};

/**
 * 移除模型图片关联
 */
export const removeModelImageRelations = (data: ModelImageRelationRemoveParams) => {
  return http.post(PORT1 + "/model/image/remove", data);
};

/**
 * 上传模型文件
 */
export const uploadModelFile = (data: ModelUploadParams) => {
  const formData = new FormData();
  formData.append("file", data.file);
  formData.append("model_id", data.model_id.toString());
  if (data.version) {
    formData.append("version", data.version);
  }
  return http.post(PORT1 + "/model/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
};

/**
 * 训练模型
 */
export const trainModel = (data: ModelTrainParams) => {
  return http.post(PORT1 + "/model/train", data);
};

/**
 * 模型推理
 */
export const modelInference = (data: ModelInferenceParams) => {
  return http.post(PORT1 + "/model/inference", data);
};
