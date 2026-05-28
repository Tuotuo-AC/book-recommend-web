<!--模板部分-->
<template>
  <div id="app">
    <h1>图书推荐系统(SVD)</h1>
    <div>
      <label>用户ID: </label>
      <!--将输入框的值与userId数据双向绑定， .number修饰符自动将输入转为数字类型-->
      <!--:max="maxUserId" 动态绑定max属性，限制用户ID不能超过后端模型的实际用户数减一-->
      <input v-model.number="userId" type="number" min="0" :max="maxUserId" />
      <!--点击按钮时使用getRecommendations方法；当loading为True时禁用按钮，防止重复提交-->
      <button @click="getRecommendations" :disabled="loading">获取推荐</button>
    </div>
    <!--条件渲染 -->
    <!--请求过程中显示“加载中...”-->
    <div v-if="loading">加载中...</div>
    <!-- 有推荐结果时显示表格-->
    <div v-else-if="recommendations.length">
      <h2>推荐列表（Top-10）</h2>
      <table border="1" cellpadding="8" style="border-collapse: collapse;">
        <thead>
          <tr><th>排名</th><th>书名</th><th>预测评分</th></tr>
        </thead>
        <tbody>
          <!--遍历推荐列表生成表格行，:key="idx"提供唯一标识-->
          <tr v-for="(item, idx) in recommendations" :key="idx">
            <!--{{...}}插值表达式，以下分别显示排名（从1开始），书名，预测评分（保留俩位小数）-->
            <td>{{ idx+1 }}</td>
            <td>{{ item.title }}</td>
            <td>{{ item.score.toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <!--有错误信息时显示错误提示-->
    <div v-else-if="errorMsg" class="error">{{ errorMsg }}</div>
  </div>
</template>

<!--脚本部分-->
<script>
// 引入axios用于发送HTTP请求到后端Flask API
import axios from 'axios';

export default {
  name: 'App',
  data() {
    return {
      userId: 0,  //当前输入的用户ID,初始为0
      maxUserId: 1799,   // 前端允许的最大用户ID,应与模型实际用户数匹配（P.shape[0] - 1）
      recommendations: [],  // 存储后端返回的推荐列表，每个元素包含title和score
      loading: false,  // 请求状态标志
      errorMsg: ''  // 存储错误信息
    };
  },
  // 方法getRecommendations
  //1.重置状态：清楚旧数据，显示加载动画
  methods: {
    async getRecommendations() {
      this.loading = true;
      this.errorMsg = '';
      this.recommendations = [];
      try {
        // 2.使用axios.post向http://localhost:5000/recommend发送POST请求，携带{ user_id: this.userId }
        const response = await axios.post('http://localhost:5000/recommend', {
          user_id: this.userId
        });
         // 3.处理响应：若成功且有recommendations字段，更新列表；若有error字段，显示后端返回的错误信息
        if (response.data.recommendations) {
          this.recommendations = response.data.recommendations;
        } else if (response.data.error) {
          this.errorMsg = response.data.error;
        }
      } catch (err) {
        this.errorMsg = err.message;  //4.捕获网络异常，显示错误信息
      } finally {
        this.loading = false;  //5.关闭加载状态
      }
    }
  }
};
</script>

<!--样式部分-->
<style>

#app {
  font-family: 宋体;
  text-align: center;
  margin-top: 60px;
  font-size:25px;
}
label{
  font-weight: bolder;
}
.error {
  color: red;
}
input {
  margin: 0 10px;
  padding: 8px;
  height:20px;
  width:100px;
  font-size:20px;
}
button {
  padding: 3px 15px;
  height:40px;
  width:100px;
  font-size:15px;
  font-weight:bold;
}
table {
  margin: 20px auto;
}
th, td {
  padding: 25px 30px;
}

</style>