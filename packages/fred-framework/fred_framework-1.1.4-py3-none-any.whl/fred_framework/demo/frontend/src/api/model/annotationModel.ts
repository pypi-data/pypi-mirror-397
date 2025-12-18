/**
 * 标注相关数据模型
 */

/**
 * 标注信息
 */
export interface AnnotationInfo {
  id: number;
  image_path: string;
  image_name: string;
  width: number;
  height: number;
  labels: AnnotationLabel[];
  created?: string;
  modified?: string;
}

/**
 * 标注项接口（用于列表显示）
 */
export interface AnnotationItem {
  id: number | null;
  file_name: string;
  file_path: string;
  width: number;
  height: number;
  project_name?: string;
  creator_name?: string;
  annotation_count: number;
  created_at: string | null;
}

/**
 * 标注详情接口
 */
export interface AnnotationDetail {
  id: number;
  label_name: string;
  label_color: string;
  yolo_class_name?: string;
  label_id?: number;
  yolo_format: {
    label_id: number;
    center_x: number;
    center_y: number;
    width: number;
    height: number;
  };
  confidence?: number;
  is_auto?: boolean;
  annotator_name: string;
  isModified?: boolean; // 标记标注是否被修改
  isNew?: boolean; // 标记是否为新创建的标注
}

/**
 * 标注列表响应
 */
export interface AnnotationListResponse {
  list: AnnotationItem[];
  total: number;
  pageNum: number;
  pageSize: number;
}

/**
 * 标注详情响应
 */
export interface AnnotationDetailResponse {
  image: AnnotationItem;
  annotations: AnnotationDetail[];
}

/**
 * 标注标签
 */
export interface AnnotationLabel {
  id: number;
  label_id: number;
  label_name: string;
  x: number;
  y: number;
  width: number;
  height: number;
  confidence?: number;
}

/**
 * 标注列表查询参数
 */
export interface AnnotationListQuery {
  pageNum?: number;
  pageSize?: number;
  image_name?: string;
  label_id?: number;
  created_start?: string;
  created_end?: string;
}

/**
 * 标注详情查询参数
 */
export interface AnnotationDetailQuery {
  image_id: number;
  model_id?: number;
}

/**
 * 标注保存参数
 */
export interface AnnotationSaveParams {
  image_path: string;
  image_name: string;
  width: number;
  height: number;
  labels: Omit<AnnotationLabel, "id">[];
}

/**
 * 标注更新参数
 */
export interface AnnotationUpdateParams extends AnnotationSaveParams {
  id: number;
}

/**
 * 标注删除参数
 */
export interface AnnotationDeleteParams {
  id?: number; // 单个删除时使用
  ids?: number[]; // 批量删除时使用
}

/**
 * 标注图片上传参数
 */
export interface AnnotationImageUploadParams {
  file: File;
  label_ids?: number[];
}

/**
 * 标注图片上传响应
 */
export interface AnnotationImageUploadResponse {
  fileUrl: string;
  file_name: string;
  file_path: string;
  height: number;
  id: number;
  width: number;
}

/**
 * 标注导出参数
 */
export interface AnnotationExportParams {
  format: "json" | "xml" | "yolo";
  label_ids?: number[];
  model_id?: number;
  created_start?: string;
  created_end?: string;
}

/**
 * 标注导入参数
 */
export interface AnnotationImportParams {
  file: File;
  format: "json" | "xml" | "yolo";
  replace_existing?: boolean;
}
