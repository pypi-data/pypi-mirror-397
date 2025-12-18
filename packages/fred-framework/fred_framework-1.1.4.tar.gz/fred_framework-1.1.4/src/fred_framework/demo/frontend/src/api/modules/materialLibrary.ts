import { ResPage } from "@/api/interface";
import { PORT1 } from "@/api/config/servicePort";
import http from "@/api";
import type {
  MaterialLibraryInfo,
  MaterialLibraryListQuery,
  MaterialLibrarySaveParams,
  MaterialLibraryDeleteParams,
  UploadFolderInfo,
  MaterialTeamInfo,
  MaterialTeamListQuery,
  MaterialImageInfo,
  MaterialImageListQuery
} from "@/api/model/materialLibraryModel";

/**
 * 素材库管理相关接口
 */

// 获取素材库列表
export const getMaterialLibraryListApi = (params: MaterialLibraryListQuery) => {
  return http.get<ResPage<MaterialLibraryInfo>>(PORT1 + `/material-library/list`, params);
};

// 新增素材库
export const createMaterialLibraryApi = (data: MaterialLibrarySaveParams) => {
  return http.post(PORT1 + `/material-library/save`, data);
};

// 更新素材库
export const updateMaterialLibraryApi = (data: MaterialLibrarySaveParams) => {
  return http.put(PORT1 + `/material-library/save`, data);
};

// 删除素材库
export const deleteMaterialLibraryApi = (params: MaterialLibraryDeleteParams) => {
  return http.delete(PORT1 + `/material-library/delete`, params);
};

// 获取上传文件夹列表
export const getUploadFoldersApi = () => {
  return http.get<UploadFolderInfo[]>(PORT1 + `/material-library/upload-folders`);
};

// 获取素材库关联的团队列表
export const getMaterialTeamsApi = (params: MaterialTeamListQuery) => {
  return http.get<MaterialTeamInfo[]>(PORT1 + `/material-library/teams`, params);
};

// 获取所有团队列表（用于下拉选择）
export const getAllTeamsApi = () => {
  return http.get<MaterialTeamInfo[]>(PORT1 + `/material-library/teams/all`);
};

// 保存素材库团队绑定
export const saveMaterialTeamsApi = (data: { material_id: number; team_ids: number[] }) => {
  return http.post(PORT1 + `/material-library/teams/save`, data);
};

// 删除素材库团队绑定
export const deleteMaterialTeamApi = (params: { material_id: number; team_id: number }) => {
  return http.delete(PORT1 + `/material-library/teams/delete`, params);
};

// 同步素材库目录中的图片到数据库
export const syncMaterialLibraryApi = (params: { id: number }) => {
  return http.post(PORT1 + `/material-library/sync`, params);
};

// 获取当前用户所属团队的素材库列表
export const getUserTeamMaterialsApi = () => {
  return http.get<MaterialLibraryInfo[]>(PORT1 + `/material-library/user-teams`);
};

// 获取素材库图片列表
export const getMaterialImagesApi = (params: MaterialImageListQuery) => {
  return http.get<ResPage<MaterialImageInfo>>(PORT1 + `/material-library/images`, params);
};
