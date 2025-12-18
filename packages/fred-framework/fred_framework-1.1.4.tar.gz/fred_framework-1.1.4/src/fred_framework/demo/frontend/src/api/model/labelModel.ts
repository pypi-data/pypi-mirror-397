/**
 * 标签相关数据模型
 */

/**
 * 标签项接口
 */
export interface LabelItem {
  id: number;
  name: string;
  color: string;
  model_id: number;
  model_name: string;
  sort?: number;
}

/**
 * 标签列表响应
 */
export interface LabelListResponse {
  records: LabelItem[];
  total: number;
}

/**
 * 根据模型ID获取标签的查询参数
 */
export interface LabelByModelQuery {
  modelId: number;
}

/**
 * 标签列表查询参数
 */
export interface LabelListQuery {
  pageNum?: number;
  pageSize?: number;
  name?: string;
  model_id?: number;
}

/**
 * 标签保存参数
 */
export interface LabelSaveParams {
  name: string;
  color: string;
  model_id?: number;
}

/**
 * 标签更新参数
 */
export interface LabelUpdateParams extends LabelSaveParams {
  id: number;
}

/**
 * 标签删除参数
 */
export interface LabelDeleteParams {
  id: number;
}
