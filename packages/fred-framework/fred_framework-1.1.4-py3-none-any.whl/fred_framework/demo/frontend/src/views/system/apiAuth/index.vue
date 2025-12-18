<template>
  <div class="table-box">
    <ProTable ref="proTable" :columns="columns" :request-api="getTableList" :init-param="initParam" :data-callback="dataCallback">
      <!-- 表格 header 按钮 -->
      <template #tableHeader>
        <el-button type="primary" :icon="CirclePlus" @click="openApiDrawer('新增')">新增API</el-button>
        <el-button type="info" :icon="InfoFilled" @click="showTokenUsageDialog = true">Token使用说明</el-button>
      </template>
      <!-- Expand - Token列表 -->
      <template #expand="scope">
        <div class="token-container">
          <el-table :data="scope.row.tokens || []" border :style="{ width: '100%' }">
            <el-table-column prop="username" label="用户名" width="150" />
            <el-table-column prop="token" label="Token" min-width="300">
              <template #default="tokenScope">
                <el-tooltip
                  :content="tokenScope.row.token"
                  placement="top"
                  :disabled="!tokenScope.row.token || tokenScope.row.token.length <= 100"
                >
                  <span>{{ formatToken(tokenScope.row.token) }}</span>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column prop="expiration" label="到期时间" width="180" />
            <el-table-column prop="created" label="创建时间" width="180" />
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="tokenScope">
                <el-button type="primary" link :icon="CopyDocument" @click="copyTokenHandle(tokenScope.row.token)">
                  复制
                </el-button>
                <el-button type="primary" link :icon="Delete" @click="deleteTokenHandle(tokenScope.row)"> 删除 </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </template>
      <!-- 表格操作 -->
      <template #operation="scope">
        <el-button type="primary" link :icon="View" @click="openApiDrawer('查看', scope.row)">查看</el-button>
        <el-button type="primary" link :icon="Key" @click="openTokenDrawer('新增', scope.row)">新增Token</el-button>
        <el-button type="primary" link :icon="Delete" @click="deleteApiHandle(scope.row)">删除</el-button>
      </template>
    </ProTable>
    <ApiDrawer ref="apiDrawerRef" />
    <TokenDrawer ref="tokenDrawerRef" />

    <!-- Token使用说明对话框 -->
    <el-dialog v-model="showTokenUsageDialog" title="Token使用说明" width="800px" :close-on-click-modal="false">
      <div class="token-usage-content">
        <el-alert type="info" :closable="false" show-icon style="margin-bottom: 20px">
          <template #title>
            <span>使用Authorization Header进行API认证</span>
          </template>
        </el-alert>

        <h3>1. 请求头设置</h3>
        <p>在API请求中，需要在HTTP请求头中添加 <code>Authorization</code> 字段，格式如下：</p>
        <el-card shadow="never" style="margin: 10px 0">
          <pre class="code-block">Authorization: Bearer {your_token}</pre>
        </el-card>

        <h3>2. 使用示例</h3>

        <h4>cURL 示例：</h4>
        <el-card shadow="never" style="margin: 10px 0">
          <!-- prettier-ignore -->
          <pre class="code-block">curl -X GET "https://api.example.com/api/endpoint" \
  -H "Authorization: Bearer your_token_here"</pre>
        </el-card>

        <h4>JavaScript (fetch) 示例：</h4>
        <el-card shadow="never" style="margin: 10px 0">
          <!-- prettier-ignore -->
          <pre class="code-block">fetch('https://api.example.com/api/endpoint', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer your_token_here',
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  // 数据已处理
});</pre>
        </el-card>

        <h4>Python (requests) 示例：</h4>
        <el-card shadow="never" style="margin: 10px 0">
          <!-- prettier-ignore -->
          <pre class="code-block">import requests

headers = {
    'Authorization': 'Bearer your_token_here',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://api.example.com/api/endpoint',
    headers=headers
)

print(response.json())</pre>
        </el-card>

        <h3>3. 注意事项</h3>
        <ul class="usage-notes">
          <li>Token需要以 <code>Bearer </code> 前缀开头，注意Bearer后面有一个空格</li>
          <li>Token具有有效期，过期后需要重新生成</li>
          <li>请妥善保管Token，不要泄露给他人</li>
          <li>如果Token泄露，请及时删除并重新生成</li>
        </ul>
      </div>
      <template #footer>
        <el-button type="primary" @click="showTokenUsageDialog = false">我知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from "vue";
import { ColumnProps } from "@/components/ProTable/interface";
import { CirclePlus, Delete, View, Key, CopyDocument, InfoFilled } from "@element-plus/icons-vue";
import ProTable from "@/components/ProTable/index.vue";
import { ElMessageBox, ElMessage } from "element-plus";
import { getApiInfoList, addApiInfo, deleteApiInfo, addToken, deleteToken } from "@/api/modules/apiAuth";
import ApiDrawer from "./components/ApiDrawer.vue";
import TokenDrawer from "./components/TokenDrawer.vue";

const proTable = ref();
const apiDrawerRef = ref();
const tokenDrawerRef = ref();
const showTokenUsageDialog = ref(false);

const initParam = reactive({});

const dataCallback = (data: any) => {
  // 后端直接返回数组，需要转换为分页格式
  if (Array.isArray(data)) {
    // 实时统计每个API的token数量
    const records = data.map((item: any) => {
      const tokenCount = item.tokens ? item.tokens.length : 0;
      return {
        ...item,
        token_count: tokenCount
      };
    });
    return {
      records: records,
      total: records.length,
      pageNum: 1,
      pageSize: records.length || 10
    };
  }
  return {
    records: [],
    total: 0,
    pageNum: 1,
    pageSize: 10
  };
};

const columns = computed<ColumnProps[]>(() => [
  { type: "expand", label: "Token", width: 80 },
  { type: "index", label: "#", width: 80 },
  {
    prop: "name",
    label: "API名字",
    search: { el: "input", props: { placeholder: "请输入API名字" } }
  },
  {
    prop: "api_pre",
    label: "API前缀",
    search: { el: "input", props: { placeholder: "请输入API前缀" } }
  },
  {
    prop: "desc",
    label: "说明",
    search: { el: "input", props: { placeholder: "请输入说明" } }
  },
  {
    prop: "token_count",
    label: "Token数量",
    width: 120
  },
  { prop: "operation", label: "操作", width: 280, fixed: "right" }
]);

const getTableList = (params: any) => {
  return getApiInfoList(params);
};

const openApiDrawer = (title: string, row: any = {}) => {
  const params = {
    title,
    isView: title === "查看",
    row: title === "新增" ? {} : JSON.parse(JSON.stringify(row)),
    api: addApiInfo,
    getTableList: proTable.value?.getTableList
  };
  apiDrawerRef.value?.acceptParams(params);
};

const openTokenDrawer = (title: string, apiRow: any) => {
  const params = {
    title,
    isView: title === "查看",
    row: {
      api_id: apiRow.id
    },
    api: addToken,
    getTableList: () => {
      // 刷新API列表以更新Token数据
      proTable.value?.getTableList();
    }
  };
  tokenDrawerRef.value?.acceptParams(params);
};

const deleteApiHandle = async (row: any) => {
  try {
    await ElMessageBox.confirm("确定要删除该API信息吗？如果该API下存在Token，请先删除Token。", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    await deleteApiInfo({ id: row.id });
    ElMessage.success("删除成功");
    proTable.value?.getTableList();
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error(error.message || "删除失败");
    }
  }
};

// 格式化token显示，超过100字符显示前50后50，否则显示全部
const formatToken = (token: string) => {
  if (!token) return "";
  if (token.length <= 100) return token;
  return `${token.substring(0, 50)}...${token.substring(token.length - 50)}`;
};

const copyTokenHandle = async (token: string) => {
  try {
    // 优先使用现代 Clipboard API
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(token);
      ElMessage.success("Token已复制到剪贴板");
      return;
    }
    // Fallback: 使用传统的 execCommand 方法
    const textArea = document.createElement("textarea");
    textArea.value = token;
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    textArea.style.top = "-999999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    const successful = document.execCommand("copy");
    document.body.removeChild(textArea);
    if (successful) {
      ElMessage.success("Token已复制到剪贴板");
    } else {
      throw new Error("复制命令执行失败");
    }
  } catch (error: any) {
    console.error("复制失败:", error);
    ElMessage.error("复制失败，请手动复制");
  }
};

const deleteTokenHandle = async (row: any) => {
  try {
    await ElMessageBox.confirm("确定要删除该Token吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning"
    });
    await deleteToken({ id: row.id });
    ElMessage.success("删除成功");
    proTable.value?.getTableList();
  } catch (error: any) {
    if (error !== "cancel") {
      ElMessage.error(error.message || "删除失败");
    }
  }
};
</script>

<style scoped lang="scss">
.token-container {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
  margin: 10px 0;
}

.token-usage-content {
  h3 {
    margin-top: 20px;
    margin-bottom: 10px;
    font-size: 16px;
    font-weight: 600;
    color: #303133;

    &:first-child {
      margin-top: 0;
    }
  }

  h4 {
    margin-top: 15px;
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: 600;
    color: #606266;
  }

  p {
    margin: 10px 0;
    color: #606266;
    line-height: 1.6;

    code {
      background-color: #f5f7fa;
      padding: 2px 6px;
      border-radius: 3px;
      font-family: "Courier New", monospace;
      color: #e6a23c;
    }
  }

  .code-block {
    margin: 0;
    padding: 15px;
    background-color: #f5f7fa;
    border-radius: 4px;
    font-family: "Courier New", monospace;
    font-size: 13px;
    line-height: 1.6;
    color: #303133;
    overflow-x: auto;
    white-space: pre-wrap;
    word-wrap: break-word;
  }

  .usage-notes {
    margin: 10px 0;
    padding-left: 20px;
    color: #606266;
    line-height: 1.8;

    li {
      margin: 8px 0;

      code {
        background-color: #f5f7fa;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: "Courier New", monospace;
        color: #e6a23c;
      }
    }
  }
}
</style>
