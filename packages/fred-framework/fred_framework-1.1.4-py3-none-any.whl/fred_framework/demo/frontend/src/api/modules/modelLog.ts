import http from "@/api";

// 获取模型日志列表
export const getModelLogListApi = (params: any) => {
  return http.get("/admin/model/log/list", params);
};

// 清除模型日志
export const clearModelLogApi = (data: { model_id?: number }) => {
  return http.delete("/admin/model/log/clear", data);
};
