import { ResPage } from "@/api/interface";
import { PORT1 } from "@/api/config/servicePort";
import http from "@/api";
import type {
  AnnotationInfo,
  AnnotationListQuery,
  AnnotationDetailQuery,
  AnnotationSaveParams,
  AnnotationUpdateParams,
  AnnotationDeleteParams,
  AnnotationExportParams,
  AnnotationImportParams
} from "@/api/model/annotationModel";

/**
 * 标注管理相关接口
 */

// 获取标注列表
export const getAnnotationListApi = (params: AnnotationListQuery) => {
  return http.get<ResPage<AnnotationInfo>>(PORT1 + `/annotation/list`, params);
};

// 获取标注详情
export const getAnnotationDetailApi = (params: AnnotationDetailQuery) => {
  return http.get<AnnotationInfo>(PORT1 + `/annotation/detail`, params, {
    retry: 1, // 重试1次
    retryDelay: 2000 // 重试间隔2秒
  });
};

// 更新标注
export const updateAnnotationApi = (data: AnnotationUpdateParams) => {
  return http.post(PORT1 + `/annotation/update`, data, {
    retry: 1, // 重试1次
    retryDelay: 1000, // 重试间隔1秒
    loading: false // 禁用默认loading，由组件自己控制
  });
};

// 统一的标注创建接口
export const createAnnotationApi = (data: AnnotationSaveParams) => {
  return http.post(PORT1 + `/annotation/create`, data, {
    retry: 1, // 重试1次
    retryDelay: 1000, // 重试间隔1秒
    loading: false // 禁用默认loading，由组件自己控制
  });
};

// 删除标注（支持单个和批量删除）
export const deleteAnnotationApi = (data: AnnotationDeleteParams) => {
  return http.delete(PORT1 + `/annotation/delete`, data, {
    data: data, // 将数据作为请求体发送（用于批量删除）
    retry: 0 // 禁用重试，避免重复请求
  });
};

// 创建图片并添加标注（保持向后兼容）
export const createImageAndAnnotationApi = (data: AnnotationSaveParams) => {
  return http.post(
    PORT1 + `/annotation/create`,
    {
      operation_type: "create_image_and_annotation",
      ...data
    },
    {
      headers: {
        "Content-Type": "application/json"
      }
    }
  );
};

// 获取指定目录下的图片列表
export const getDirectoryImagesApi = (params: { directory_path: string; pageNum?: number; pageSize?: number }) => {
  return http.get<ResPage<AnnotationInfo>>(PORT1 + `/annotation/directory-images`, params, {
    retry: 1, // 重试1次
    retryDelay: 2000 // 重试间隔2秒
  });
};

// 导出标注内容
export const exportAnnotationsApi = (params: AnnotationExportParams) => {
  return http.get(PORT1 + `/annotation/export`, params);
};

// 导入标注内容
export const importAnnotationsApi = (data: AnnotationImportParams) => {
  const formData = new FormData();
  formData.append("file", data.file);
  formData.append("format", data.format);
  if (data.replace_existing !== undefined) {
    formData.append("replace_existing", data.replace_existing.toString());
  }

  return http.post(PORT1 + `/annotation/import`, formData, {
    headers: {
      "Content-Type": "multipart/form-data"
    }
  });
};

// 获取上传文件夹列表
export const getUploadFolders = () => {
  return http.get<string[]>(PORT1 + `/annotation/upload-folders`);
};

// 远程训练接口
export const trainInferenceApi = (params: { model_id: number }) => {
  return http.post(PORT1 + `/annotation/train`, params);
};

// 获取训练日志列表
export const getTrainLogListApi = (params: any) => {
  return http.get<ResPage<any>>(PORT1 + `/annotation/train`, params);
};

// 停止训练
export const stopTrainApi = (params: { id: number }) => {
  return http.post(PORT1 + `/annotation/train/stop`, params);
};

// 标记图片删除状态（支持单个和批量）
export const markImageDeletedApi = (params: { image_id?: number; image_ids?: number[]; deleted: number }) => {
  return http.delete(PORT1 + `/annotation/mark-deleted`, params, { data: params });
};

// 系统推理接口
export const systemInferenceApi = (params: { image_id: number; model_id: number }) => {
  return http.post(PORT1 + `/annotation/system-inference`, params);
};
