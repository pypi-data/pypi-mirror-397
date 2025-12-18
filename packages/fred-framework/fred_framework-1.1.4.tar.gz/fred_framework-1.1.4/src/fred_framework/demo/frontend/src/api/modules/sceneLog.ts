import http from "@/api";
import { PORT1 } from "@/api/config/servicePort";
import { ResPage } from "@/api/interface";

/**
 * 场景日志相关接口
 */

// 场景日志信息接口
export interface SceneLogInfo {
  id: number;
  scene_id: number;
  store_id: number;
  message: string;
  status: number;
  created?: string;
  image_url?: string;
  scene_name?: string;
  store_name?: string;
  province_name?: string;
  city_name?: string;
  district_name?: string;
  show_notification?: boolean;
}

// 场景日志查询参数
export interface SceneLogQueryParams {
  pageNum?: number;
  pageSize?: number;
  store_id?: number;
  scene_id?: number;
  province_id?: number;
  city_id?: number;
  district_id?: number;
  status?: number;
  start_date?: string;
  end_date?: string;
}

/**
 * 通知信息接口
 */
export interface NotificationInfo {
  id: number;
  accept_user?: number;
  plat?: string;
  message?: string;
  message_type?: number;
  status?: number;
  store_id?: number;
  type_id?: number;
  created?: string;
}

/**
 * 通知查询参数
 */
export interface NotificationQueryParams {
  scene_log_id: number;
}

/**
 * 重新发送通知参数
 */
export interface ResendNotificationParams {
  notification_id: number;
}

/**
 * 获取场景日志列表
 */
export const getSceneLogList = (params: SceneLogQueryParams) => {
  return http.get<ResPage<SceneLogInfo>>(PORT1 + "/scene/log/list", params);
};

/**
 * 根据场景日志ID查询通知信息
 */
export const getNotificationBySceneLog = (params: NotificationQueryParams) => {
  return http.get<NotificationInfo>(PORT1 + "/scene/log/notification", params);
};

/**
 * 重新发送通知
 */
export const resendNotification = (params: ResendNotificationParams) => {
  return http.post(PORT1 + "/scene/log/notification/resend", params);
};
