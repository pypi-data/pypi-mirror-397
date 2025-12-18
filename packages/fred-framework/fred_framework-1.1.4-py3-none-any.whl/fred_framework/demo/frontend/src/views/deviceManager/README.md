# DeviceManager 文件结构说明

## 目录结构

```
deviceManager/
├── components/              # 组件文件
│   ├── camera/             # 摄像头相关组件
│   │   └── CameraDrawer.vue
│   ├── device/             # 设备相关组件
│   │   ├── DeviceDrawer.vue
│   │   ├── BindDeviceDrawer.vue
│   │   └── UnboundDevicesDrawer.vue
│   └── common/             # 通用组件
│       ├── CameraBrandDrawer.vue
│       └── StoreSelectionDialog.vue
├── camera.vue              # 摄像头管理页面
├── list.vue                # 设备列表页面
└── README.md               # 本说明文件
```

## 文件说明

### API 接口

- 摄像头相关 API 接口统一在 `api/modules/camera.ts` 中管理
- 类型定义统一在 `api/model/cameraModel.ts` 中管理

### 样式文件

- 摄像头页面样式统一在 `styles/modules/device-manager.scss` 中管理

### 组件文件 (components/)

#### 摄像头组件 (camera/)

- `CameraDrawer.vue`: 摄像头新增/编辑抽屉组件

#### 设备组件 (device/)

- `DeviceDrawer.vue`: 设备新增/编辑抽屉组件
- `BindDeviceDrawer.vue`: 设备绑定抽屉组件
- `UnboundDevicesDrawer.vue`: 未绑定设备查看抽屉组件

#### 通用组件 (common/)

- `CameraBrandDrawer.vue`: 摄像头品牌管理抽屉组件
- `StoreSelectionDialog.vue`: 门店选择对话框组件

### 页面文件

- `camera.vue`: 摄像头管理页面，包含门店筛选和摄像头列表
- `list.vue`: 设备列表页面，包含地区筛选和设备列表

## 使用说明

1. **添加新的 API 接口**: 在 `apis/` 目录下创建对应的 API 文件
2. **添加新的类型定义**: 在 `types/` 目录下创建对应的类型文件
3. **添加新的样式**: 在 `styles/` 目录下创建对应的样式文件
4. **添加新的组件**: 根据功能分类放入对应的组件目录
5. **导入路径**: 使用相对路径导入，如 `./apis/camera.api`、`./types/camera.types` 等

## 整理原则

1. **按功能分类**: 将相关功能的文件放在同一目录下
2. **按类型分类**: API、类型、样式、组件分别放在不同目录
3. **保持一致性**: 命名规范和目录结构保持一致
4. **便于维护**: 结构清晰，便于后续维护和扩展
