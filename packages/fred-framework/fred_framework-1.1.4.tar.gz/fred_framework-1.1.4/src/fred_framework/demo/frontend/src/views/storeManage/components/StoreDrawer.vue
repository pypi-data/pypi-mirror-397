<script setup lang="ts" name="StoreDrawer">
import { ref, watch, nextTick, onUnmounted } from "vue";
import { useI18n } from "vue-i18n";
import { ElMessage, FormInstance } from "element-plus";

// 国际化
const { t } = useI18n();

interface DrawerProps {
  title: string;
  isView: boolean;
  row: any;
  api?: (params: any) => Promise<any>;
  getTableList?: (operationType?: string, storeData?: any) => void;
  regionTreeData?: any[]; // 添加省市区数据参数
}

const drawerVisible = ref(false);

const drawerProps = ref<DrawerProps>({
  isView: false,
  title: "",
  row: {}
});

// 省市区选项
const regionOptions = ref<any[]>([]);
const treeData = ref<any[]>([]); // 恢复为普通的ref

// 转换带count的数据为纯树形数据
const transformTreeData = (data: any[]): any[] => {
  return data.map(item => {
    // 保持原始ID格式不变，只移除count字段
    const newItem: any = {
      id: item.id,
      label: item.label,
      country_id: item.country_id
    };

    // 如果有stores字段，也保留（可能在某些逻辑中需要用到）
    if (item.stores) {
      newItem.stores = item.stores;
    }

    // 保留count字段用于显示
    if (item.count !== undefined) {
      newItem.count = item.count;
    }

    if (item.children) {
      newItem.children = transformTreeData(item.children);
    }

    return newItem;
  });
};

// 接收父组件传过来的参数
const acceptParams = (params: DrawerProps) => {
  // 参数验证
  if (!params) {
    console.error("Invalid params passed to acceptParams");
    return;
  }

  // 重置表单数据，确保每次打开都使用新的数据
  drawerProps.value = {
    isView: params.isView || false,
    title: params.title || "",
    row: params.row ? { ...params.row } : {}, // 深拷贝row对象
    api: params.api,
    getTableList: params.getTableList,
    regionTreeData: params.regionTreeData
  };

  // 初始化表单数据
  if (!drawerProps.value.row.region) drawerProps.value.row.region = [];
  // 使用后端返回的address作为detailAddress的初始值，如果没有则设为空字符串
  drawerProps.value.row.detailAddress = drawerProps.value.row.address || "";
  if (drawerProps.value.row.scene_num === undefined) drawerProps.value.row.scene_num = 0;

  // 使用父组件传递的树形数据，取消接口请求
  if (params.regionTreeData && params.regionTreeData.length > 0) {
    // 转换为纯树形数据格式（去除count字段和ID中的country前缀）
    treeData.value = transformTreeData(params.regionTreeData);
    buildRegionOptions();

    // 确保树形数据加载完成后，再解析省市区信息（编辑模式）
    if (drawerProps.value.title === "编辑") {
      // 使用nextTick确保DOM更新完成
      nextTick(() => {
        // 再使用setTimeout确保级联选择器完全初始化
        setTimeout(() => {
          parseStoreRegionInfo();
        }, 100);
      });
    }
  } else {
    // 如果没有传递数据，记录错误日志
    console.error("没有接收到省市区树形数据，请检查父组件数据传递");
    treeData.value = [];
    regionOptions.value = [];
  }

  drawerVisible.value = true;
};

// 构建级联选择器选项
const buildRegionOptions = () => {
  regionOptions.value = treeData.value.map(province => ({
    id: province.id,
    label: province.label + (province.count !== undefined ? ` (${province.count})` : ""),
    children: province.children?.map(city => ({
      id: city.id,
      label: city.label + (city.count !== undefined ? ` (${city.count})` : ""),
      children: city.children?.map(district => ({
        id: district.id,
        label: district.label + (district.count !== undefined ? ` (${district.count})` : "")
      }))
    }))
  }));
};

// 从区域ID中提取纯数字ID
const extractIdFromRegionId = (regionId: string): number | undefined => {
  let extractedId: number | undefined;

  // 处理ID格式：如 "province_1", "city_2", "district_3"
  if (typeof regionId === "string") {
    // 匹配最后的数字部分
    const match = regionId.match(/(\d+)$/);
    if (match) {
      extractedId = parseInt(match[1]);
    }
  } else if (typeof regionId === "number") {
    extractedId = regionId;
  }

  return extractedId;
};

// 解析门店省市区信息（编辑模式）
const parseStoreRegionInfo = () => {
  // 确保drawerProps存在
  if (!drawerProps.value || !drawerProps.value.row) {
    return;
  }

  const { country_id, province_id, city_id, district_id, address } = drawerProps.value.row;

  // 每次都使用后端返回的address作为detailAddress的值，确保数据是最新的
  drawerProps.value.row.detailAddress = address || "";

  // 每次都重置region数组
  drawerProps.value.row.region = [];

  // 如果有省市区ID，构建级联选择器的值
  if (province_id && city_id && district_id) {
    // 根据后端返回的ID格式构建路径
    // 后端返回的是纯数字ID，需要根据树形数据的ID格式来构建
    let provinceNode, cityNode, districtNode;

    // 查找匹配的省份节点
    for (const province of treeData.value) {
      const extractedId = extractIdFromRegionId(province.id);
      if (extractedId === province_id) {
        provinceNode = province;
        // 查找匹配的城市节点
        if (province.children) {
          for (const city of province.children) {
            const extractedCityId = extractIdFromRegionId(city.id);
            if (extractedCityId === city_id) {
              cityNode = city;
              // 查找匹配的区县节点
              if (city.children) {
                for (const district of city.children) {
                  const extractedDistrictId = extractIdFromRegionId(district.id);
                  if (extractedDistrictId === district_id) {
                    districtNode = district;
                    break;
                  }
                }
              }
              break;
            }
          }
        }
        break;
      }
    }

    // 如果找到了匹配的节点，则设置级联选择器的值
    if (provinceNode && cityNode && districtNode) {
      const regionPath = [provinceNode.id, cityNode.id, districtNode.id];

      // 使用nextTick确保DOM完全更新后再设置值
      nextTick(() => {
        // 先清空再设置，确保响应式更新
        drawerProps.value.row.region = [];
        // 使用setTimeout确保级联选择器完全初始化
        setTimeout(() => {
          drawerProps.value.row.region = [...regionPath]; // 创建新数组引用触发响应式更新
        }, 50);
      });
    }

    // 确保国家ID存在，如果没有则默认为中国
    if (!country_id) {
      drawerProps.value.row.country_id = 1; // 默认为中国
      drawerProps.value.row.country_name = "中国";
    }
  } else {
    // 如果没有ID信息，使用传统解析方式
    parseAddressToRegion(address || "");
  }
};

// 解析地址获取省市区（兼容老数据）
const parseAddressToRegion = (address: string) => {
  // 确保drawerProps存在
  if (!drawerProps.value || !drawerProps.value.row) {
    return;
  }

  // 这里实现简单的地址解析，实际项目中可能需要更复杂的解析逻辑
  drawerProps.value.row.region = [];
  // 使用传入的地址作为detailAddress的值
  drawerProps.value.row.detailAddress = address || "";
};

// 监听详细地址变化
watch(
  () => drawerProps.value?.row?.detailAddress,
  newVal => {
    // 确保drawerProps存在
    if (!drawerProps.value || !drawerProps.value.row) {
      return;
    }

    // 直接使用详细地址作为地址字段，不再拼接省市区
    drawerProps.value.row.address = newVal || "";
  }
);

// 监听门店名称变化，更新地图标记
watch(
  () => drawerProps.value.row.name,
  () => {
    // 移除地图标记更新逻辑
    // if (currentMarker && drawerMap && newName) {
    //   // 更新标签文本
    //   const label = currentMarker.getLabel();
    //   if (label) {
    //     label.setContent(newName);
    //   }
    // }
  }
);

// 监听抽屉显示状态
watch(
  () => drawerVisible.value,
  () => {
    // 移除地图资源清理逻辑
    // if (!newVisible) {
    //   // 抽屉关闭时清理地图资源
    //   if (drawerMap) {
    //     drawerMap.clearOverlays();
    //   }
    //   currentMarker = null;
    // }
  }
);

// 组件挂载时不再需要加载数据，由父组件传递
// onMounted(() => {
//   loadRegionData();
// });

// 组件卸载时清理资源
onUnmounted(() => {
  // 清理全局回调函数
  (window as any).initDrawerMapCallback = undefined;
});

// 添加表单验证规则
const rules = ref({
  name: [{ required: true, message: "请填写门店名称" }],
  region: [{ required: true, message: "请选择所在地区" }],
  detailAddress: [{ required: true, message: "请填写详细地址" }]
});

// 表单实例引用
const ruleFormRef = ref<FormInstance>();

// 防止重复提交的标志
const isSubmitting = ref(false);

// 提交数据（新增/编辑）
const handleSubmit = () => {
  if (isSubmitting.value) {
    return;
  }

  // 确保表单引用存在
  if (!ruleFormRef.value) {
    return;
  }

  ruleFormRef.value.validate(async valid => {
    if (!valid) return;

    // 确保drawerProps的值存在
    if (!drawerProps.value) {
      ElMessage.error("操作失败，数据异常");
      return;
    }

    isSubmitting.value = true;
    try {
      // 构造提交数据，只包含后端需要的字段
      const formData: any = {
        name: drawerProps.value.row?.name || "",
        address: drawerProps.value.row?.detailAddress || ""
        // scene_num 字段已移除
      };

      // 解析省市区信息，只提取ID
      if (drawerProps.value.row?.region && drawerProps.value.row.region.length >= 3) {
        const [provinceId, cityId, districtId] = drawerProps.value.row.region;

        // 提取ID（从格式如"province_1"中提取数字）
        formData.province_id = extractIdFromRegionId(provinceId);
        formData.city_id = extractIdFromRegionId(cityId);
        formData.district_id = extractIdFromRegionId(districtId);
        formData.country_id = 1; // 默认为中国
      }

      // 确保API函数存在
      if (!drawerProps.value.api) {
        throw new Error("API function is not defined");
      }

      // 调用API
      await drawerProps.value.api(formData);

      // 关闭抽屉
      drawerVisible.value = false;

      // 刷新表格数据
      if (drawerProps.value.getTableList) {
        drawerProps.value.getTableList(drawerProps.value.title, formData);
      }
    } catch {
      ElMessage.error("操作失败");
    } finally {
      isSubmitting.value = false;
    }
  });
};

defineExpose({
  acceptParams
});
</script>

<template>
  <el-drawer v-model="drawerVisible" :destroy-on-close="true" size="500px" :title="`${drawerProps?.title || ''}门店`">
    <el-form
      ref="ruleFormRef"
      label-width="100px"
      label-suffix=" :"
      :rules="rules"
      :disabled="drawerProps?.isView"
      :model="drawerProps?.row"
      :hide-required-asterisk="drawerProps?.isView"
    >
      <el-form-item :label="t('store.storeName')" prop="name">
        <el-input v-model="drawerProps.row.name" :placeholder="t('store.enterStoreName')" clearable></el-input>
      </el-form-item>

      <el-form-item :label="t('store.region')" prop="region">
        <el-cascader
          v-model="drawerProps.row.region"
          :options="regionOptions"
          :props="{ checkStrictly: true, expandTrigger: 'hover', value: 'id', label: 'label' }"
          :placeholder="t('store.selectRegion')"
          clearable
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item :label="t('store.detailAddress')" prop="detailAddress">
        <el-input
          v-model="drawerProps.row.detailAddress"
          :placeholder="t('store.enterDetailAddress')"
          clearable
          type="textarea"
        ></el-input>
      </el-form-item>

      <!-- 场景数量字段已移除 -->
    </el-form>

    <template #footer>
      <el-button @click="drawerVisible = false">{{ t("common.cancel") }}</el-button>
      <el-button v-show="!drawerProps?.isView" type="primary" @click="handleSubmit">{{ t("common.confirm") }}</el-button>
    </template>
  </el-drawer>
</template>
