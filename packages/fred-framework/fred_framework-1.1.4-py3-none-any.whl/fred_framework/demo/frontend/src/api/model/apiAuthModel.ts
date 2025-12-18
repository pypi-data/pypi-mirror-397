/**
 * @description API授权管理相关类型定义
 */

// API信息
export interface ApiInfo {
  id?: number;
  name: string;
  api_pre: string;
  desc?: string;
  tokens?: ApiToken[];
  token_count?: number;
}

// Token信息
export interface ApiToken {
  id?: number;
  api_id: number;
  username?: string;
  token: string;
  expiration?: string;
  created?: string;
}

// API信息查询参数
export interface ApiInfoListQuery {
  name?: string;
  api_pre?: string;
  desc?: string;
  pageSize?: number;
  pageNum?: number;
}

// API信息保存参数
export interface ApiInfoSaveParams {
  id?: number;
  name: string;
  api_pre: string;
  desc?: string;
}

// API信息删除参数
export interface ApiInfoDeleteParams {
  id: number;
}

// Token查询参数
export interface ApiTokenListQuery {
  api_id: number;
  pageSize?: number;
  pageNum?: number;
}

// Token保存参数
export interface ApiTokenSaveParams {
  id?: number;
  api_id: number;
  username?: string;
  token?: string;
  expiration?: string;
}

// Token删除参数
export interface ApiTokenDeleteParams {
  id: number;
}

// API信息列表响应
export interface ApiInfoListResponse {
  records: ApiInfo[];
  total: number;
  pageNum: number;
  pageSize: number;
}

// Token列表响应
export interface ApiTokenListResponse {
  records: ApiToken[];
  total: number;
  pageNum: number;
  pageSize: number;
}
