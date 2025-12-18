import { ResPage } from "@/api/interface";
import { PORT1 } from "@/api/config/servicePort";
import http from "@/api";
import type {
  ApiInfo,
  ApiInfoListQuery,
  ApiInfoSaveParams,
  ApiInfoDeleteParams,
  ApiToken,
  ApiTokenListQuery,
  ApiTokenSaveParams,
  ApiTokenDeleteParams
} from "@/api/model/apiAuthModel";

/**
 * API授权管理相关接口
 */

// API信息管理
export const getApiInfoList = (params?: ApiInfoListQuery) => {
  return http.get<ApiInfo[]>(PORT1 + `/system/apiAuth`, params || {});
};

export const addApiInfo = (params: ApiInfoSaveParams) => {
  return http.post(PORT1 + `/system/apiAuth`, params);
};

export const editApiInfo = (params: ApiInfoSaveParams) => {
  return http.put(PORT1 + `/system/apiAuth`, params);
};

export const deleteApiInfo = (params: ApiInfoDeleteParams) => {
  return http.delete(PORT1 + `/system/apiAuth`, params);
};

// 获取所有蓝图名字
export const getBlueprintNames = () => {
  return http.get<string[]>(PORT1 + `/system/apiAuth/blueprints`);
};

// Token管理
export const getTokenList = (params: ApiTokenListQuery) => {
  return http.get<ResPage<ApiToken>>(PORT1 + `/system/apiAuth/token`, params);
};

export const addToken = (params: ApiTokenSaveParams) => {
  return http.post(PORT1 + `/system/apiAuth/token`, params);
};

export const editToken = (params: ApiTokenSaveParams) => {
  return http.put(PORT1 + `/system/apiAuth/token`, params);
};

export const deleteToken = (params: ApiTokenDeleteParams) => {
  return http.delete(PORT1 + `/system/apiAuth/token`, params);
};
