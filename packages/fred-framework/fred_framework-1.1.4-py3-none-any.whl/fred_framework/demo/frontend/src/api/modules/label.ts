import http from "@/api";
import { ResPage } from "@/api/interface";
import { LabelItem, LabelByModelQuery } from "@/api/model/labelModel";

// 获取标签列表
export const getLabelListApi = (params?: any) => {
  return http.get<ResPage<LabelItem>>("/admin/label/list", params, {
    retry: 1, // 重试1次
    retryDelay: 1000 // 重试间隔1秒
  });
};

// 获取所有标签（不分页）
export const getAllLabelsApi = (params?: any) => {
  return http.get<ResPage<LabelItem>>(
    "/admin/label/list",
    { ...params, getAll: true },
    {
      retry: 1, // 重试1次
      retryDelay: 1000 // 重试间隔1秒
    }
  );
};

// 根据模型ID获取标签列表
export const getLabelListByModelApi = (params: LabelByModelQuery) => {
  return http.get<ResPage<LabelItem>>("/admin/model/label/list", { model_id: params.modelId });
};

// 获取标签详情
export const getLabelDetailApi = (params: { id: number }) => {
  return http.get<LabelItem>("/admin/label/detail", params);
};

// 创建标签
export const createLabelApi = (data: { name: string; color: string; model_id?: number }) => {
  return http.post<LabelItem>("/admin/label/create", data, {
    retry: 1, // 重试1次
    retryDelay: 1000 // 重试间隔1秒
  });
};

// 更新标签
export const updateLabelApi = (data: { id: number; name: string; color: string; model_id?: number }) => {
  return http.post<LabelItem>("/admin/label/update", data, {
    retry: 1, // 重试1次
    retryDelay: 1000 // 重试间隔1秒
  });
};

// 删除标签
export const deleteLabelApi = (data: { id: number }) => {
  return http.post("/admin/label/delete", data, {
    retry: 1, // 重试1次
    retryDelay: 1000 // 重试间隔1秒
  });
};

// 解除标签与模型的关联关系
export const unlinkLabelFromModelApi = (data: { label_id: number; model_id: number }) => {
  return http.post("/admin/label/unlink", data, {
    retry: 1, // 重试1次
    retryDelay: 1000 // 重试间隔1秒
  });
};

// 获取未绑定标签列表
export const getUnboundLabelsApi = (params?: any) => {
  return http.get<ResPage<LabelItem>>("/admin/label/unbound", params, {
    retry: 1, // 重试1次
    retryDelay: 1000 // 重试间隔1秒
  });
};

// 绑定标签到模型
export const bindLabelToModelApi = (data: { label_id: number; model_id: number }) => {
  return http.post("/admin/label/bind", data, {
    retry: 1, // 重试1次
    retryDelay: 1000 // 重试间隔1秒
  });
};

// 批量绑定标签到模型
export const batchBindLabelsToModelApi = (data: { label_ids: number[]; model_id: number }) => {
  return http.post("/admin/label/batch/bind", data, {
    retry: 1, // 重试1次
    retryDelay: 1000 // 重试间隔1秒
  });
};

// 更新标签排序
export const updateLabelSortApi = (data: { model_id: number; label_orders: Array<{ label_id: number; sort: number }> }) => {
  return http.post("/admin/label/sort/update", data, {
    retry: 1, // 重试1次
    retryDelay: 1000 // 重试间隔1秒
  });
};
