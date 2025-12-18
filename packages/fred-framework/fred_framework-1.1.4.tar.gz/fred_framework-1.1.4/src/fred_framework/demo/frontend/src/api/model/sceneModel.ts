/**
 * 场景相关数据模型
 */

/**
 * 场景信息
 */
export interface SceneInfo {
  id: number;
  name: string;
  description?: string;
  status: number;
  sort_order?: number;
  hz?: number;
  model_ids?: number[];
  created?: string;
  modified?: string;
}

/**
 * 场景列表查询参数
 */
export interface SceneListQuery {
  pageNum: number;
  pageSize: number;
  name?: string;
  status?: number;
}

/**
 * 场景详情查询参数
 */
export interface SceneDetailQuery {
  id: number;
}

/**
 * 场景保存参数
 */
export interface SceneSaveParams {
  id?: number;
  name: string;
  description?: string;
  status?: number;
  sort_order?: number;
  hz?: number;
  model_ids?: number[];
}

/**
 * 场景状态更新参数
 */
export interface SceneStatusUpdateParams {
  id: number;
  status: number;
}

/**
 * 场景删除参数
 */
export interface SceneDeleteParams {
  id: number[];
}

/**
 * 场景模型关联信息
 */
export interface SceneModelRelation {
  id: number;
  scene_id: number;
  model_id: number;
  model_name?: string;
  created?: string;
}

/**
 * 场景模型列表查询参数
 */
export interface SceneModelListQuery {
  scene_id: number;
  pageNum?: number;
  pageSize?: number;
  name?: string;
}

/**
 * 场景模型绑定参数
 */
export interface SceneModelBindParams {
  scene_id: number;
  model_id: number;
}

/**
 * 场景模型解绑参数
 */
export interface SceneModelUnbindParams {
  relation_id: number;
}

/**
 * 场景模型批量绑定参数
 */
export interface SceneModelBatchBindParams {
  scene_id: number;
  model_ids: number[];
}

/**
 * 场景频率选项
 */
export interface SceneFrequencyOption {
  value: number;
  label: string;
}
