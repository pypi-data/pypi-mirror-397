<template>
  <div class="statistics-conversation">
    <div class="page-header">
      <div class="header-content">
        <h2>智能统计</h2>
        <p class="page-description">通过智能对话方式查询和展示统计数据</p>
      </div>
    </div>

    <div class="conversation-container">
      <!-- 消息列表 -->
      <div class="messages-container" ref="messagesContainerRef">
        <div v-if="messages.length === 0" class="empty-state">
          <el-icon class="empty-icon"><ChatLineRound /></el-icon>
          <p>开始智能对话，查询统计数据</p>
          <p class="hint-text">例如：查询今日场景统计、查看最近7天的检测趋势等</p>
        </div>

        <div v-for="(message, index) in messages" :key="index" class="message-item" :class="message.type">
          <div class="message-avatar">
            <el-icon v-if="message.type === 'user'"><User /></el-icon>
            <el-icon v-else><Service /></el-icon>
          </div>
          <div class="message-content">
            <div v-if="message.type === 'user'" class="message-text">{{ message.content }}</div>
            <div v-else class="message-response">
              <div v-if="message.loading" class="loading-indicator">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>正在分析数据...</span>
              </div>
              <div v-else>
                <div v-if="message.text" class="message-text">{{ message.text }}</div>
                <!-- 统计数据展示 -->
                <div v-if="message.statistics" class="statistics-display">
                  <!-- 统计卡片 -->
                  <div v-if="message.statistics.cards && message.statistics.cards.length > 0" class="stat-cards">
                    <el-card v-for="(card, cardIndex) in message.statistics.cards" :key="cardIndex" class="stat-card">
                      <div class="stat-item">
                        <div class="stat-value">{{ card.value || 0 }}</div>
                        <div class="stat-label">{{ card.label }}</div>
                      </div>
                    </el-card>
                  </div>

                  <!-- 图表展示 -->
                  <div v-if="message.statistics.chart" class="chart-display">
                    <el-card class="chart-card">
                      <template #header>
                        <div class="card-header">
                          <span>{{ message.statistics.chart.title }}</span>
                        </div>
                      </template>
                      <!-- 图表容器 -->
                      <div class="chart-container">
                        <div :ref="el => setChartRef(el, index)" class="chart"></div>
                      </div>
                    </el-card>
                  </div>

                  <!-- 表格数据展示 -->
                  <div v-if="message.statistics.table && message.statistics.table.length > 0" class="table-display">
                    <el-card class="table-card">
                      <el-table :data="message.statistics.table" stripe style="width: 100%" border>
                        <el-table-column
                          v-for="(column, colIndex) in message.statistics.tableColumns"
                          :key="colIndex"
                          :prop="column.prop"
                          :label="column.label"
                          :width="column.width"
                          :sortable="column.sortable"
                        />
                      </el-table>
                    </el-card>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-container">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="2"
          placeholder="请输入您想查询的统计数据，例如：查询今日场景统计、查看最近7天的检测趋势..."
          @keydown.enter.exact.prevent="handleSendMessage"
          @keydown.enter.shift.exact="handleNewLine"
        />
        <div class="input-actions">
          <el-button type="primary" :loading="sending" @click="handleSendMessage">
            <el-icon><Promotion /></el-icon>
            发送
          </el-button>
          <el-button @click="handleClearMessages">清空对话</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { processConversationQuery } from "@/api/modules/statistics";
import { ChatLineRound, Loading, Promotion, Service, User } from "@element-plus/icons-vue";
// 使用完整的echarts库，支持所有图表类型
import * as echarts from "echarts";
import { ElMessage } from "element-plus";
import { nextTick, onMounted, onUnmounted, ref, watch } from "vue";

// 消息类型定义
interface Message {
  type: "user" | "assistant";
  content?: string;
  text?: string;
  loading?: boolean;
  statistics?: {
    cards?: Array<{ label: string; value: number | string }>;
    chart?: {
      title: string;
      type?: string; // 图表类型（可选，可以是任意字符串，前端不限制）
      option: any; // ECharts配置对象（可以是任意ECharts配置）
    };
    table?: any[];
    tableColumns?: Array<{ prop: string; label: string; width?: number; sortable?: boolean }>;
  };
}

// 页面数据
const messages = ref<Message[]>([]);
const inputText = ref("");
const sending = ref(false);
const messagesContainerRef = ref<HTMLElement | null>(null);

// 图表实例存储
const chartInstances = new Map<number, echarts.ECharts>();

// 设置图表引用
const setChartRef = (el: any, messageIndex: number) => {
  if (el && !chartInstances.has(messageIndex)) {
    const chartElement = el as HTMLElement;

    // 确保元素有尺寸
    if (chartElement.offsetWidth === 0 || chartElement.offsetHeight === 0) {
      // 如果元素还没有尺寸，延迟初始化
      setTimeout(() => {
        initChartForElement(chartElement, messageIndex);
      }, 100);
    } else {
      initChartForElement(chartElement, messageIndex);
    }
  }
};

// 初始化图表元素
const initChartForElement = (chartElement: HTMLElement, messageIndex: number) => {
  if (chartInstances.has(messageIndex)) {
    return; // 已经初始化过了
  }

  // 确保元素有尺寸
  if (chartElement.offsetWidth === 0 || chartElement.offsetHeight === 0) {
    // 如果元素还没有尺寸，延迟初始化
    setTimeout(() => {
      if (chartElement.offsetWidth > 0 && chartElement.offsetHeight > 0) {
        doInitChart(chartElement, messageIndex);
      }
    }, 200);
    return;
  }

  doInitChart(chartElement, messageIndex);
};

// 执行图表初始化
const doInitChart = (chartElement: HTMLElement, messageIndex: number) => {
  if (chartInstances.has(messageIndex)) {
    return;
  }

  const chart = echarts.init(chartElement);
  chartInstances.set(messageIndex, chart);

  // 获取消息的图表配置 - 直接使用后端返回的option，不关心图表类型
  const message = messages.value[messageIndex];
  if (message?.statistics?.chart?.option) {
    // 直接使用后端返回的配置代码渲染图表，支持任意图表类型
    // 前端不做任何类型判断，完全依赖后端返回的配置
    try {
      chart.setOption(message.statistics.chart.option, { notMerge: true });
    } catch (error) {
      console.error("图表渲染失败:", error);
      console.error("图表配置:", message.statistics.chart.option);
    }

    // 确保图表正确渲染
    nextTick(() => {
      chart.resize();
      // 再次延迟确保完全渲染
      setTimeout(() => {
        chart.resize();
      }, 100);
    });

    // 监听窗口大小变化，自动调整图表大小
    const resizeHandler = () => {
      if (chart && !chart.isDisposed()) {
        chart.resize();
      }
    };
    window.addEventListener("resize", resizeHandler);
  }
};

// 处理发送消息
const handleSendMessage = async () => {
  if (!inputText.value.trim()) {
    ElMessage.warning("请输入查询内容");
    return;
  }

  if (sending.value) return;

  const userMessage: Message = {
    type: "user",
    content: inputText.value.trim()
  };

  messages.value.push(userMessage);
  const userInput = inputText.value.trim();
  inputText.value = "";

  // 添加加载中的助手消息
  const assistantMessage: Message = {
    type: "assistant",
    loading: true
  };
  messages.value.push(assistantMessage);

  sending.value = true;

  // 滚动到底部
  await nextTick();
  scrollToBottom();

  try {
    // 处理用户问题并获取统计数据
    const statistics = await processUserQuery(userInput);

    // 更新助手消息
    assistantMessage.loading = false;
    assistantMessage.text = statistics.text;
    assistantMessage.statistics = statistics.data;

    // 如果有图表，等待DOM更新后初始化
    if (statistics.data?.chart) {
      await nextTick();
      const messageIndex = messages.value.length - 1;
      // 使用 setTimeout 确保 DOM 完全渲染
      setTimeout(() => {
        const chartEl = messagesContainerRef.value?.querySelector(
          `.message-item:nth-child(${messageIndex + 1}) .chart`
        ) as HTMLElement;
        if (chartEl) {
          // 如果 setChartRef 还没有初始化，这里初始化
          if (!chartInstances.has(messageIndex)) {
            const chart = echarts.init(chartEl);
            chartInstances.set(messageIndex, chart);
            // 直接使用后端返回的配置代码渲染图表，支持任意图表类型
            try {
              chart.setOption(statistics.data.chart.option, { notMerge: true });
            } catch (error) {
              console.error("图表渲染失败:", error);
              console.error("图表配置:", statistics.data.chart.option);
            }

            // 确保图表正确渲染
            setTimeout(() => {
              if (chart && !chart.isDisposed()) {
                chart.resize();
              }
            }, 50);

            // 监听窗口大小变化，自动调整图表大小
            const resizeHandler = () => {
              if (chart && !chart.isDisposed()) {
                chart.resize();
              }
            };
            window.addEventListener("resize", resizeHandler);
          } else {
            // 如果已经初始化，更新配置
            const chart = chartInstances.get(messageIndex);
            if (chart && !chart.isDisposed()) {
              // 直接使用后端返回的配置代码更新图表，支持任意图表类型
              try {
                chart.setOption(statistics.data.chart.option, { notMerge: true });
                setTimeout(() => {
                  chart.resize();
                }, 50);
              } catch (error) {
                console.error("图表更新失败:", error);
                console.error("图表配置:", statistics.data.chart.option);
              }
            }
          }
        }
      }, 200);
    }
  } catch (error) {
    console.error("处理查询失败:", error);
    assistantMessage.loading = false;
    assistantMessage.text = "抱歉，处理您的查询时出现错误，请稍后重试。";
    ElMessage.error("查询失败，请稍后重试");
  } finally {
    sending.value = false;
    await nextTick();
    scrollToBottom();
  }
};

// 处理用户查询
const processUserQuery = async (query: string): Promise<{ text: string; data?: any }> => {
  try {
    // 调用后端智能统计接口
    const params = {
      query: query
    };

    const response = await processConversationQuery(params);
    if (response.code === 200) {
      return response.data as { text: string; data?: any };
    } else {
      return {
        text: response.message || "查询失败，请稍后重试",
        data: undefined
      };
    }
  } catch (error: any) {
    console.error("处理查询失败:", error);
    return {
      text: error.message || "查询失败，请稍后重试",
      data: undefined
    };
  }
};

// 处理换行
const handleNewLine = () => {
  // Shift+Enter 换行，不做任何处理
};

// 清空对话
const handleClearMessages = () => {
  // 销毁所有图表实例
  chartInstances.forEach(chart => {
    chart.dispose();
  });
  chartInstances.clear();

  messages.value = [];
  ElMessage.success("对话已清空");
};

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainerRef.value) {
      messagesContainerRef.value.scrollTop = messagesContainerRef.value.scrollHeight;
    }
  });
};

// 监听消息变化，自动滚动
watch(
  () => messages.value.length,
  () => {
    scrollToBottom();
  }
);

// 组件挂载
onMounted(() => {
  // 页面初始化
});

// 组件卸载时清理图表实例
onUnmounted(() => {
  chartInstances.forEach(chart => {
    chart.dispose();
  });
  chartInstances.clear();
});
</script>

<style lang="scss" scoped>
.statistics-conversation {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    background-color: #fff;
    border-bottom: 1px solid #e4e7ed;
    flex-shrink: 0;

    .header-content {
      h2 {
        margin: 0 0 5px 0;
        font-size: 20px;
        font-weight: 600;
        color: #303133;
      }

      .page-description {
        margin: 0;
        font-size: 14px;
        color: #909399;
      }
    }
  }

  .conversation-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    margin: 20px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);

    .messages-container {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
      background-color: #fafafa;

      .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        color: #909399;

        .empty-icon {
          font-size: 64px;
          margin-bottom: 20px;
          color: #c0c4cc;
        }

        p {
          margin: 5px 0;
          font-size: 16px;
        }

        .hint-text {
          font-size: 14px;
          color: #c0c4cc;
        }
      }

      .message-item {
        display: flex;
        margin-bottom: 20px;
        animation: fadeIn 0.3s ease-in;

        &.user {
          flex-direction: row-reverse;

          .message-content {
            background-color: #409eff;
            color: #fff;
            margin-right: 10px;
            margin-left: 60px;
          }
        }

        &.assistant {
          .message-content {
            background-color: #fff;
            color: #303133;
            margin-left: 10px;
            margin-right: 60px;
            max-width: 90%; // assistant 消息使用更宽的显示
            flex: 1; // 确保在 flex 布局中能够正确显示宽度
            min-width: 0; // 允许 flex 子元素收缩
          }
        }

        .message-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
          background-color: #e4e7ed;
          color: #606266;
          font-size: 20px;
        }

        .message-content {
          max-width: 70%;
          padding: 12px 16px;
          border-radius: 8px;
          word-wrap: break-word;
          flex: 1; // 确保在 flex 布局中能够正确显示宽度
          min-width: 0; // 允许 flex 子元素收缩，避免宽度计算问题

          .message-text {
            white-space: pre-wrap;
            line-height: 1.6;
          }

          // 确保统计数据显示区域可以全宽
          .statistics-display {
            width: 100%;
            max-width: 100%;
          }

          .loading-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #909399;

            .el-icon {
              font-size: 18px;
            }
          }

          .statistics-display {
            margin-top: 16px;
            width: 100%;
            max-width: 100%;

            .stat-cards {
              display: grid;
              grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
              gap: 12px;
              margin-bottom: 16px;

              .stat-card {
                .stat-item {
                  text-align: center;

                  .stat-value {
                    font-size: 24px;
                    font-weight: 600;
                    color: #303133;
                    margin-bottom: 8px;
                  }

                  .stat-label {
                    font-size: 14px;
                    color: #909399;
                  }
                }
              }
            }

            .chart-display {
              margin-bottom: 16px;
              width: 100%;
              max-width: 100%;
              // 突破父容器的宽度限制，最大化显示
              margin-left: -16px;
              margin-right: -16px;
              padding-left: 16px;
              padding-right: 16px;

              .chart-card {
                width: 100%;
                max-width: 100%;

                .card-header {
                  font-weight: 600;
                  color: #303133;
                }

                .chart-container {
                  width: 100%;
                  max-width: 100%;
                  min-height: 600px;
                  position: relative;

                  .chart {
                    width: 100% !important;
                    height: 600px !important;
                    min-width: 100%;
                    display: block;
                  }
                }
              }
            }

            .table-display {
              margin-bottom: 16px;
            }
          }
        }
      }
    }

    .input-container {
      padding: 16px;
      border-top: 1px solid #e4e7ed;
      background-color: #fff;
      flex-shrink: 0;

      .input-actions {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin-top: 10px;
      }
    }
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .statistics-conversation {
    .conversation-container {
      margin: 10px;

      .messages-container {
        .message-item {
          .message-content {
            max-width: 85%;
          }
        }
      }
    }
  }
}
</style>
