<template>
  <div class="store-manage-container">
    <div class="map-container">
      <div id="amapMap" class="map-view"></div>
      <div v-if="loading" class="loading-mask">
        <el-loading :text="'加载中...'" />
      </div>
      <div v-else-if="provinceData.length === 0" class="no-data-mask">
        <div class="no-data-content">
          <el-empty class="no-data-icon" />
          <p>暂无门店数据</p>
        </div>
      </div>
      <!-- 图例说明 -->
      <div class="map-legend" v-if="!loading && provinceData.length > 0">
        <div class="legend-title">门店数量图例</div>
        <div class="legend-item">
          <div class="legend-color" style="background-color: #cccccc"></div>
          <div class="legend-text">0家</div>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background-color: #409eff"></div>
          <div class="legend-text">1-9家</div>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background-color: #67c23a"></div>
          <div class="legend-text">10-49家</div>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background-color: #e6a23c"></div>
          <div class="legend-text">50-99家</div>
        </div>
        <div class="legend-item">
          <div class="legend-color" style="background-color: #f56c6c"></div>
          <div class="legend-text">100家以上</div>
        </div>
      </div>
    </div>
    <div class="action-bar">
      <el-button @click="refreshMap">刷新地图</el-button>
      <el-button @click="zoomToNation">全国视图</el-button>
    </div>
    <div class="store-count-info">
      <p>总计: {{ getTotalStoreCount() }} 家门店</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from "vue";
import { AMAP_MAP_KEY } from "@/config/amapMap";
import { ElMessage } from "element-plus";
import { getRegionTree, RegionTreeItem } from "@/api/modules/store";

let map: any = null;
let AMap: any = null;
let currentMarkers: any[] = []; // 当前显示的标记

const provinceData = ref<RegionTreeItem[]>([]);

// 状态管理
const loading = ref(false);

// 地图配置
const mapOptions = ref({
  zoom: 5,
  center: { lng: 116.404, lat: 39.915 }, // 北京
  minZoom: 3,
  maxZoom: 15
});

// 初始化高德地图
const initMap = () => {
  try {
    // 检查是否已经加载了高德地图
    if ((window as any).AMap) {
      initAmapInstance();
      return;
    }

    // 检查API Key是否配置
    if (!AMAP_MAP_KEY) {
      ElMessage.warning("高德地图API Key未配置，地图无法显示，但会尝试加载门店数据");
      // 即使地图未配置，也加载门店数据
      loadStoreData();
      return;
    }

    // 加载高德地图脚本
    const script = document.createElement("script");
    script.type = "text/javascript";
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${AMAP_MAP_KEY}&callback=initAmapCallback`;
    script.onerror = () => {
      ElMessage.error("高德地图加载失败，请检查网络连接或API Key是否正确");
      loading.value = false;
      // 即使地图加载失败，也尝试加载门店数据
      loadStoreData();
    };
    document.head.appendChild(script);

    // 定义全局回调函数
    (window as any).initAmapCallback = () => {
      try {
        // 使用 nextTick 确保 DOM 已渲染
        nextTick(() => {
          initAmapInstance();
        });
      } catch (error) {
        console.error("高德地图回调函数执行失败:", error);
        ElMessage.error(`高德地图初始化失败: ${error}`);
        loading.value = false;
        // 即使地图初始化失败，也尝试加载门店数据
        loadStoreData();
      }
    };

    // 设置超时，如果地图在5秒内没有加载完成，也尝试加载数据
    setTimeout(() => {
      if (!map && (window as any).AMap) {
        // 地图API已加载但实例未创建，尝试初始化
        try {
          nextTick(() => {
            initAmapInstance();
          });
        } catch (error) {
          console.error("延迟初始化地图失败:", error);
          // 即使失败也加载数据
          loadStoreData();
        }
      } else if (!map && !(window as any).AMap) {
        // 地图API未加载，直接加载数据
        console.warn("地图API加载超时，直接加载门店数据");
        loadStoreData();
      }
    }, 5000);
  } catch {
    ElMessage.error("高德地图脚本加载失败");
    loading.value = false;
    // 即使出错也加载数据
    loadStoreData();
  }
};

// 初始化高德地图实例
const initAmapInstance = () => {
  try {
    AMap = (window as any).AMap;
    if (!AMap) {
      throw new Error("高德地图API未加载");
    }

    // 检查容器是否存在
    const containerId = "amapMap";
    const container = document.getElementById(containerId);
    if (!container) {
      throw new Error(`地图容器不存在，容器ID: ${containerId}`);
    }

    // 确保容器有高度和宽度
    if (container.offsetWidth === 0 || container.offsetHeight === 0) {
      console.warn("地图容器尺寸为0，延迟初始化");
      setTimeout(() => {
        initAmapInstance();
      }, 100);
      return;
    }

    // 高德地图初始化配置
    const mapConfig: any = {
      zoom: mapOptions.value.zoom,
      center: [mapOptions.value.center.lng, mapOptions.value.center.lat],
      minZoom: mapOptions.value.minZoom,
      maxZoom: mapOptions.value.maxZoom
    };

    // 检查是否支持 3D 视图模式（某些版本可能不支持）
    try {
      // 尝试使用 3D 模式
      mapConfig.viewMode = "3D";
      mapConfig.mapStyle = "amap://styles/normal";
    } catch {
      console.warn("不支持3D视图模式，使用默认模式");
    }

    map = new AMap.Map(containerId, mapConfig);

    // 添加地图控件
    try {
      map.addControl(new AMap.Scale());
      map.addControl(
        new AMap.ToolBar({
          position: "LT"
        })
      );
      map.addControl(
        new AMap.MapType({
          defaultType: 0
        })
      );
    } catch (controlError) {
      console.warn("添加地图控件失败:", controlError);
      // 控件添加失败不影响地图使用
    }

    // 添加地图事件监听
    map.on("zoomend", handleZoomChange);
    map.on("moveend", () => {
      const center = map.getCenter();
      mapOptions.value.center = { lng: center.getLng(), lat: center.getLat() };
    });

    loading.value = false;
  } catch (error: any) {
    console.error("高德地图实例初始化失败:", {
      error,
      errorMessage: error?.message,
      errorStack: error?.stack,
      containerId: "amapMap",
      hasContainer: !!document.getElementById("amapMap"),
      AMapExists: !!(window as any).AMap
    });
    ElMessage.error(`地图初始化失败: ${error?.message || "未知错误"}，但仍会尝试加载门店数据`);
    loading.value = false;
  }

  // 无论地图是否初始化成功，都加载门店数据
  loadStoreData();
};

// 处理地图缩放变化
const handleZoomChange = () => {
  mapOptions.value.zoom = map.getZoom();
  // 根据当前缩放级别重新显示标记
  displayMarkersByZoomLevel();
};

// 根据缩放级别显示不同层级的标记
const displayMarkersByZoomLevel = () => {
  if (!map || !provinceData.value || provinceData.value.length === 0) {
    return;
  }

  // 清除现有标记
  clearCurrentMarkers();

  const zoom = map.getZoom();
  let level = 0; // 0: 省级, 1: 市级, 2: 区县级

  if (zoom >= 12) {
    level = 2; // 区县级
  } else if (zoom >= 8) {
    level = 1; // 市级
  } else {
    level = 0; // 省级
  }

  showMarkersByLevel(level);
};

// 显示指定层级的标记
const showMarkersByLevel = (level: number) => {
  if (!map) {
    console.warn("地图未初始化，无法显示标记");
    return;
  }

  if (!provinceData.value || provinceData.value.length === 0) {
    console.warn("门店数据为空，无法显示标记");
    return;
  }

  // 清除现有标记
  clearCurrentMarkers();

  const markers: any[] = [];

  // 递归处理数据，显示指定层级的标记
  const processNode = (node: RegionTreeItem, nodeLevel: number) => {
    if (!node) return;

    // 只显示当前层级的数据
    if (nodeLevel === level) {
      // 获取节点中心坐标
      const nodeCenter = getNodeCenter(node.label, nodeLevel);
      if (nodeCenter) {
        // 根据门店数量设置标记样式
        const count = node.count || 0;
        let markerSize, bgColor;

        if (count === 0) {
          markerSize = 20;
          bgColor = "#ccc";
        } else if (count < 10) {
          markerSize = 24;
          bgColor = "#409EFF";
        } else if (count < 50) {
          markerSize = 28;
          bgColor = "#67C23A";
        } else if (count < 100) {
          markerSize = 32;
          bgColor = "#E6A23C";
        } else {
          markerSize = 36;
          bgColor = "#F56C6C";
        }

        // 高德地图标记
        const icon = createAmapIcon(bgColor, markerSize, count);
        const marker = new AMap.Marker({
          position: [nodeCenter.lng, nodeCenter.lat],
          icon: icon,
          offset: new AMap.Pixel(-markerSize / 2, -markerSize / 2)
        });

        // 添加标签
        const label = new AMap.Text({
          text: `${node.label} (${count})`,
          position: [nodeCenter.lng, nodeCenter.lat],
          offset: new AMap.Pixel(markerSize / 2 + 5, -markerSize / 2 - 10),
          style: {
            "background-color": "rgba(255, 255, 255, 0.9)",
            border: "1px solid #ccc",
            "border-radius": "3px",
            padding: "2px 5px",
            "font-size": "12px",
            color: "#333",
            "box-shadow": "0 0 3px rgba(0,0,0,0.3)",
            "white-space": "nowrap"
          }
        });

        // 添加点击事件
        marker.on("click", () => {
          let zoomLevel = 5;
          if (nodeLevel === 0) zoomLevel = 8;
          else if (nodeLevel === 1) zoomLevel = 10;
          else zoomLevel = 12;

          map.setZoomAndCenter(zoomLevel, [nodeCenter.lng, nodeCenter.lat]);
          ElMessage.info(`点击了${node.label}，共有${count}家门店`);
        });

        map.add([marker, label]);
        markers.push(marker, label);
      }
    } else if (nodeLevel < level) {
      // 递归处理子节点
      if (node.children && Array.isArray(node.children)) {
        node.children.forEach((child: RegionTreeItem) => {
          processNode(child, nodeLevel + 1);
        });
      }
    }
  };

  // 创建高德地图图标
  const createAmapIcon = (bgColor: string, size: number, count: number) => {
    const canvas = document.createElement("canvas");
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext("2d");

    if (ctx) {
      ctx.beginPath();
      ctx.arc(size / 2, size / 2, size / 2 - 2, 0, 2 * Math.PI);
      ctx.fillStyle = bgColor;
      ctx.fill();
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.fillStyle = "#ffffff";
      ctx.font = `bold ${size / 2}px Arial`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(count.toString(), size / 2, size / 2);
    }

    return new AMap.Icon({
      image: canvas.toDataURL(),
      size: new AMap.Size(size, size),
      imageSize: new AMap.Size(size, size)
    });
  };

  // 处理每个根节点
  provinceData.value.forEach((node: RegionTreeItem) => {
    processNode(node, 0);
  });

  // 保存当前标记
  currentMarkers = markers;
};

// 清除当前标记
const clearCurrentMarkers = () => {
  if (map && currentMarkers.length > 0) {
    map.remove(currentMarkers);
    currentMarkers = [];
  }
};

// 刷新地图
const refreshMap = () => {
  loading.value = true;
  clearCurrentMarkers();

  // 重新加载门店数据
  loadStoreData().finally(() => {
    loading.value = false;
  });
};

// 缩放到全国视图
const zoomToNation = () => {
  if (!map) return;
  map.setZoomAndCenter(5, [mapOptions.value.center.lng, mapOptions.value.center.lat]);
  // 显示省级数据
  showMarkersByLevel(0);
};

// 加载门店数据
const loadStoreData = async () => {
  try {
    loading.value = true;

    // 调用API获取省市区树形数据
    const response = await getRegionTree(true);

    // 检查响应数据结构
    if (!response) {
      throw new Error("API响应为空");
    }

    if (!response.data) {
      throw new Error("API响应中缺少data字段");
    }

    if (!Array.isArray(response.data)) {
      throw new Error("API响应中的data字段不是数组");
    }

    // 保存完整的省市区树形数据
    provinceData.value = response.data;

    // 如果数据为空，检查是否有门店但未关联省市区
    if (response.data.length === 0) {
      console.warn("省市区树形数据为空，可能是门店未关联省市区信息");
      ElMessage({
        message: "暂无门店分布数据，请确保门店已关联省市区信息（省份、城市、区县）才能在地图上显示",
        type: "warning",
        duration: 5000
      });
      return;
    }

    // 显示省级数据
    showMarkersByLevel(0);
  } catch (error: any) {
    console.error("加载门店数据失败:", error);
    ElMessage.error(`加载省市区门店分布数据失败: ${error.message || "未知错误"}`);
  } finally {
    loading.value = false;
  }
};

// 获取节点中心坐标
const getNodeCenter = (nodeName: string, level: number) => {
  // 省级坐标
  const provinceCenters: Record<string, { lng: number; lat: number }> = {
    北京市: { lng: 116.4074, lat: 39.9042 },
    上海市: { lng: 121.4737, lat: 31.2304 },
    天津市: { lng: 117.1902, lat: 39.1256 },
    重庆市: { lng: 106.5505, lat: 29.5638 },
    河北省: { lng: 114.5025, lat: 38.0455 },
    山西省: { lng: 112.5492, lat: 37.857 },
    辽宁省: { lng: 123.4291, lat: 41.7969 },
    吉林省: { lng: 125.3245, lat: 43.8868 },
    黑龙江省: { lng: 126.6425, lat: 45.7569 },
    江苏省: { lng: 118.7674, lat: 32.0415 },
    浙江省: { lng: 120.1536, lat: 30.2875 },
    安徽省: { lng: 117.283, lat: 31.8612 },
    福建省: { lng: 119.3062, lat: 26.0753 },
    江西省: { lng: 115.8165, lat: 28.6385 },
    山东省: { lng: 117.0009, lat: 36.6758 },
    河南省: { lng: 113.6654, lat: 34.7578 },
    湖北省: { lng: 114.2986, lat: 30.5844 },
    湖南省: { lng: 112.9823, lat: 28.1959 },
    广东省: { lng: 113.2644, lat: 23.1291 },
    海南省: { lng: 110.3312, lat: 20.0319 },
    四川省: { lng: 104.0659, lat: 30.6595 },
    贵州省: { lng: 106.7135, lat: 26.5783 },
    云南省: { lng: 102.7123, lat: 25.0406 },
    陕西省: { lng: 108.948, lat: 34.2632 },
    甘肃省: { lng: 103.8236, lat: 36.058 },
    青海省: { lng: 101.7789, lat: 36.6232 },
    台湾省: { lng: 121.5091, lat: 25.0443 },
    内蒙古自治区: { lng: 111.6708, lat: 40.8183 },
    广西壮族自治区: { lng: 108.32, lat: 22.824 },
    西藏自治区: { lng: 91.1322, lat: 29.6604 },
    宁夏回族自治区: { lng: 106.2782, lat: 38.4664 },
    新疆维吾尔自治区: { lng: 87.6177, lat: 43.7928 },
    香港特别行政区: { lng: 114.1095, lat: 22.3964 },
    澳门特别行政区: { lng: 113.5491, lat: 22.199 }
  };

  // 主要城市坐标
  const cityCenters: Record<string, { lng: number; lat: number }> = {
    北京市: { lng: 116.4074, lat: 39.9042 },
    上海市: { lng: 121.4737, lat: 31.2304 },
    天津市: { lng: 117.1902, lat: 39.1256 },
    重庆市: { lng: 106.5505, lat: 29.5638 },
    广州市: { lng: 113.2644, lat: 23.1291 },
    深圳市: { lng: 113.9459, lat: 22.5461 },
    杭州市: { lng: 120.1536, lat: 30.2875 },
    南京市: { lng: 118.7969, lat: 32.0603 },
    武汉市: { lng: 114.2986, lat: 30.5844 },
    成都市: { lng: 104.0659, lat: 30.6595 },
    西安市: { lng: 108.948, lat: 34.2632 },
    青岛市: { lng: 120.3822, lat: 36.0671 },
    大连市: { lng: 121.6186, lat: 38.9146 },
    厦门市: { lng: 118.0894, lat: 24.4791 },
    宁波市: { lng: 121.5497, lat: 29.8746 },
    无锡市: { lng: 120.3017, lat: 31.5747 },
    哈尔滨市: { lng: 126.6425, lat: 45.7569 },
    沈阳市: { lng: 123.4291, lat: 41.7969 },
    长春市: { lng: 125.3245, lat: 43.8868 },
    石家庄市: { lng: 114.5025, lat: 38.0455 },
    济南市: { lng: 117.0009, lat: 36.6758 },
    太原市: { lng: 112.5492, lat: 37.857 },
    合肥市: { lng: 117.283, lat: 31.8612 },
    福州市: { lng: 119.3062, lat: 26.0753 },
    南昌市: { lng: 115.8165, lat: 28.6385 },
    长沙市: { lng: 112.9823, lat: 28.1959 },
    郑州市: { lng: 113.6654, lat: 34.7578 },
    昆明市: { lng: 102.7123, lat: 25.0406 },
    贵阳市: { lng: 106.7135, lat: 26.5783 },
    兰州市: { lng: 103.8236, lat: 36.058 },
    西宁市: { lng: 101.7789, lat: 36.6232 },
    呼和浩特市: { lng: 111.6708, lat: 40.8183 },
    乌鲁木齐市: { lng: 87.6177, lat: 43.7928 },
    拉萨市: { lng: 91.1322, lat: 29.6604 },
    银川市: { lng: 106.2782, lat: 38.4664 },
    南宁市: { lng: 108.32, lat: 22.824 },
    海口市: { lng: 110.3312, lat: 20.0319 },
    台北市: { lng: 121.5091, lat: 25.0443 },
    香港特别行政区: { lng: 114.1095, lat: 22.3964 },
    澳门特别行政区: { lng: 113.5491, lat: 22.199 }
  };

  if (level === 0) {
    // 省级
    return provinceCenters[nodeName] || null;
  } else if (level === 1) {
    // 市级
    // 首先精确匹配城市名
    if (cityCenters[nodeName]) {
      return cityCenters[nodeName];
    }

    // 如果没有精确匹配，尝试模糊匹配
    const cityKeys = Object.keys(cityCenters);
    for (const key of cityKeys) {
      if (nodeName.includes(key.replace("市", ""))) {
        return cityCenters[key];
      }
    }

    // 如果还是没有找到，使用所属省份的坐标作为近似
    const provinceName = Object.keys(provinceCenters).find(name =>
      nodeName.includes(name.replace("省", "").replace("市", "").replace("自治区", "").replace("特别行政区", ""))
    );
    return provinceName ? provinceCenters[provinceName] : null;
  } else {
    // 区县级，使用所属城市的坐标作为近似
    // 这里简化处理，实际项目中可以建立更详细的区县坐标数据库
    const cityName = Object.keys(cityCenters).find(name => nodeName.includes(name.replace("市", "")));
    if (cityName) {
      return cityCenters[cityName];
    }

    // 如果找不到城市，使用省级坐标
    const provinceName = Object.keys(provinceCenters).find(name =>
      nodeName.includes(name.replace("省", "").replace("市", "").replace("自治区", "").replace("特别行政区", ""))
    );
    return provinceName ? provinceCenters[provinceName] : null;
  }
};

// 组件挂载时初始化地图
onMounted(() => {
  initMap();

  // 备用方案：如果地图在3秒后还没有加载完成，直接尝试加载门店数据
  // 这确保即使地图加载失败，门店数据接口也会被调用
  setTimeout(() => {
    if (!provinceData.value || provinceData.value.length === 0) {
      loadStoreData();
    }
  }, 3000);
});

// 组件卸载时清理资源
onUnmounted(() => {
  // 清理地图资源
  if (map) {
    clearCurrentMarkers();
    map.off("zoomend", handleZoomChange);
    map.destroy();
    map = null;
  }
  AMap = null;
});

// 计算总门店数
const getTotalStoreCount = () => {
  // 只统计省级节点的门店数量，避免重复计算
  if (!provinceData.value || provinceData.value.length === 0) return 0;

  return provinceData.value.reduce((total, province) => {
    return total + (province.count || 0);
  }, 0);
};
</script>

<style scoped lang="scss">
.store-manage-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.map-container {
  position: relative;
  flex: 1;
}
.map-view {
  width: 100%;
  height: 100%;
}
.loading-mask {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background-color: rgb(255 255 255 / 70%);
}
.no-data-mask {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  background-color: rgb(255 255 255 / 70%);
}
.no-data-content {
  color: #909399;
  text-align: center;
}
.no-data-icon {
  margin-bottom: 10px;
  font-size: 48px;
}
.action-bar {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding: 10px;
  background-color: #f5f5f5;
  border-top: 1px solid #e9e9e9;
}
.store-count-info {
  padding: 10px;
  font-size: 14px;
  color: #303133;
  background-color: #f5f5f5;
  border-bottom: 1px solid #e9e9e9;
}
.map-legend {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1000;
  min-width: 120px;
  padding: 10px;
  background-color: rgb(255 255 255 / 90%);
  border-radius: 4px;
  box-shadow: 0 0 10px rgb(0 0 0 / 20%);
}
.legend-title {
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: bold;
  color: #333333;
}
.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}
.legend-color {
  width: 20px;
  height: 20px;
  margin-right: 8px;
  border: 1px solid #ffffff;
  border-radius: 50%;
  box-shadow: 0 0 2px rgb(0 0 0 / 30%);
}
.legend-text {
  font-size: 12px;
  color: #666666;
}
</style>
