import { ResPage } from "@/api/interface";
import { PORT1 } from "@/api/config/servicePort";
import http from "@/api";
import type {
  SceneInfo,
  SceneListQuery,
  SceneDetailQuery,
  SceneSaveParams,
  SceneStatusUpdateParams,
  SceneDeleteParams,
  SceneModelRelation,
  SceneModelListQuery,
  SceneModelBindParams,
  SceneModelUnbindParams,
  SceneModelBatchBindParams,
  SceneFrequencyOption
} from "@/api/model/sceneModel";

/**
 * 场景管理相关接口
 */

/**
 * 获取场景列表
 */
export const getSceneList = (params: SceneListQuery, config?: { cancel?: boolean }) => {
  return http.get<ResPage<SceneInfo>>(PORT1 + "/scene/list", params, config || {});
};

/**
 * 获取场景详情
 */
export const getSceneDetail = (params: SceneDetailQuery) => {
  return http.get<SceneInfo>(PORT1 + "/scene/detail", params);
};

/**
 * 保存场景（新增/编辑）
 */
export const saveScene = (data: SceneSaveParams) => {
  // 根据是否有id判断是新增还是编辑
  if (data.id) {
    return http.put(PORT1 + "/scene/save", data);
  } else {
    return http.post(PORT1 + "/scene/save", data);
  }
};

/**
 * 更新场景状态（启用/禁用）
 */
export const updateSceneStatus = (data: SceneStatusUpdateParams) => {
  return http.put(PORT1 + "/scene/status", data);
};

/**
 * 删除场景
 */
export const deleteScene = (data: SceneDeleteParams) => {
  return http.delete(PORT1 + "/scene/delete", data, {
    data: data // 将数据作为请求体发送
  });
};

/**
 * 获取场景关联的模型列表
 */
export const getSceneModelList = (params: SceneModelListQuery) => {
  return http.get<ResPage<SceneModelRelation>>(PORT1 + "/scene/model/list", params);
};

/**
 * 绑定场景模型
 */
export const bindSceneModel = (data: SceneModelBindParams) => {
  return http.post(PORT1 + "/scene/model/bind", data);
};

/**
 * 解绑场景模型
 */
export const unbindSceneModel = (data: SceneModelUnbindParams) => {
  return http.post(PORT1 + "/scene/model/unbind", data);
};

/**
 * 批量绑定场景模型
 */
export const batchBindSceneModels = (data: SceneModelBatchBindParams) => {
  return http.post(PORT1 + "/scene/batch-bind-models", data);
};

/**
 * 获取场景执行频率选项
 */
export const getSceneFrequencyOptions = () => {
  return http.get<SceneFrequencyOption[]>(PORT1 + "/scene/frequency-options");
};
