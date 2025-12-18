/**
 * 素材库相关数据模型
 */

/**
 * 素材库信息
 */
export interface MaterialLibraryInfo {
  id: number;
  path: string;
  name: string;
  created?: string;
  total_num?: number;
}

/**
 * 素材库列表查询参数
 */
export interface MaterialLibraryListQuery {
  pageNum?: number;
  pageSize?: number;
  name?: string;
  path?: string;
}

/**
 * 素材库保存参数
 */
export interface MaterialLibrarySaveParams {
  id?: number;
  path: string;
  name: string;
}

/**
 * 素材库删除参数
 */
export interface MaterialLibraryDeleteParams {
  id: number;
}

/**
 * 上传文件夹信息
 */
export interface UploadFolderInfo {
  name: string;
  path: string;
}

/**
 * 素材库团队信息
 */
export interface MaterialTeamInfo {
  id: number;
  name: string;
  department_id?: number;
  department_name?: string;
  company_id?: number;
  company_name?: string;
}

/**
 * 素材库团队列表查询参数
 */
export interface MaterialTeamListQuery {
  material_id: number;
}

/**
 * 素材图片信息
 */
export interface MaterialImageInfo {
  id: number;
  file_name: string;
  file_path: string;
  width?: number;
  height?: number;
  created_at?: string;
}

/**
 * 素材图片列表查询参数
 */
export interface MaterialImageListQuery {
  material_id: number;
  pageNum?: number;
  pageSize?: number;
}
