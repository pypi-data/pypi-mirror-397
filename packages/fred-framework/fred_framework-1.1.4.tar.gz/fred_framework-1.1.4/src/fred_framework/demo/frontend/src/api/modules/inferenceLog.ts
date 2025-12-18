import http from "@/api";

// 获取推理日志列表
export const getInferenceLogListApi = (params: any) => {
  return http.get("/admin/model/inference/log", params);
};
