<template>
  <div class="position-list-main">
    <!--持仓查询-->
    <el-form :inline="true" :model="positionQueryForm" size="mini">
      <el-form-item label="持仓状态">
        <el-select
          v-model="positionQueryForm.status"
          class="form-input-short"
          placeholder="请选择"
          @change="handleQueryStatusChange"
        >
          <el-option key="all" value="all" label="全部" />
          <el-option
            v-for="item in statusOptions"
            :key="item.key"
            :label="item.display_name"
            :value="item.key"
          />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button
          type="primary"
          @click="handleCreatePos"
          size="mini"
          class="query-position-form"
        >新增持仓</el-button>
      </el-form-item>
    </el-form>
    <!--        持仓对话框-->
    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogFormVisible" :fullscreen="true">
      <el-form
        ref="positionFormRef"
        :rules="rules"
        :model="positionForm"
        label-position="left"
        label-width="80px"
        size="mini"
        :inline="true"
      >
        <el-row>
          <el-col :span="6">
            <el-form-item label="品种" prop="symbol">
              <el-input
                v-model.number="positionForm.symbol"
                type="text"
                placeholder="请输入"
                class="form-input"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="入场信号" prop="signal">
              <el-select v-model="positionForm.signal" class="form-input" placeholder="请选择">
                <el-option
                  v-for="item in signalTypeOptions"
                  :key="item.key"
                  :label="item.display_name"
                  :value="item.key"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="方向" prop="direction">
              <!-- <el-input v-model="positionForm.direction" class="form-input" disabled='true'/> -->
              <el-select v-model="positionForm.direction" class="form-input" placeholder="请选择">
                <el-option
                  v-for="item in directionOptions"
                  :key="item.key"
                  :label="item.display_name"
                  :value="item.key"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="周期图" prop="period">
              <el-select v-model="positionForm.period" class="form-input" placeholder="请选择">
                <el-option
                  v-for="item in periodOptions"
                  :key="item.key"
                  :label="item.display_name"
                  :value="item.key"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="6">
            <el-form-item label="入场时间">
              <el-date-picker
                v-model="positionForm.enterTime"
                type="datetime"
                placeholder="选择时间"
                class="form-input"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="入场价格" prop="price">
              <el-input
                v-model.number="positionForm.price"
                type="number"
                placeholder="请输入"
                class="form-input"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="数量" prop="amount">
              <el-input
                v-model.number="positionForm.amount"
                type="number"
                placeholder="请输入"
                class="form-input"
              />
            </el-form-item>
          </el-col>
          <!-- <el-col :span="6">
            <el-form-item label="预期级别" prop="nestLevel">
              <el-select v-model="positionForm.nestLevel" class="form-input" placeholder="请选择">
                <el-option :key="2" label="2级套" value="2级套" />
                <el-option :key="3" label="3级套" value="3级套" />
              </el-select>
            </el-form-item>
          </el-col> -->
          <el-col :span="6">
             <el-form-item label="仓位" prop="positionPercent">
              <el-select
                v-model="positionForm.positionPercent"
                class="form-input"
                placeholder="请选择"
              >
                <el-option
                  v-for="item in positionPercentOptions"
                  :key="item.key"
                  :label="item.display_name"
                  :value="item.key"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="6">
            <el-form-item label="状态" prop="status">
              <el-select v-model="positionForm.status" class="form-input" placeholder="请选择">
                <el-option
                  v-for="item in statusOptions"
                  :key="item.key"
                  :label="item.display_name"
                  :value="item.key"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="止损价格" prop="price">
              <el-input
                v-model.number="positionForm.stopLosePrice"
                type="number"
                placeholder="请输入"
                class="form-input"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="入场逻辑">
              <el-input
                v-model="positionForm.enterReason"
                :autosize="{ minRows: 4, maxRows: 4}"
                type="textarea"
                class="form-input"
                placeholder="请输入"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="持仓逻辑">
              <el-input
                v-model="positionForm.holdReason"
                :autosize="{ minRows: 4, maxRows: 4}"
                type="textarea"
                class="form-input"
                placeholder="请输入"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 动态止盈start -->
        <!--    编辑状态-->
        <el-divider content-position="left">持仓过程记录（ 动态止盈 | 加仓 | 高抛低吸 | 止损 ）</el-divider>
        <el-row v-for="(dynamicPosition, index) in positionForm.dynamicPositionList" :key="index">
          <el-col :span="5">
            <el-form-item label="时间">
              <el-date-picker
                v-model="dynamicPosition.time"
                type="datetime"
                placeholder="选择时间"
                class="form-input"
              />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="价格">
              <el-input
                v-model="dynamicPosition.price"
                type="number"
                placeholder="输入价格"
                class="form-input-short"
              />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="数量">
              <el-input
                v-model="dynamicPosition.amount"
                type="number"
                placeholder="输入数量"
                class="form-input-short"
              />
            </el-form-item>
          </el-col>
          <el-col :span="3">
            <el-form-item label="方向" prop="direction">
              <el-select
                v-model="dynamicPosition.direction"
                class="form-input-short"
                placeholder="请选择"
              >
                <el-option
                  v-for="item in dynamicDirectionOptions"
                  :key="item.key"
                  :label="item.display_name"
                  :value="item.key"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="7">
            <el-form-item label="原因">
              <el-input
                v-model="dynamicPosition.reason"
                :autosize="{ minRows: 2, maxRows: 4}"
                type="textarea"
                class="long-textarea"
                placeholder="请输入"
              />
            </el-form-item>
          </el-col>
          <el-col :span="1">
            <el-button
              @click.prevent="removeDynamicPosition(index)"
              size="mini"
              type="danger"
              icon="el-icon-delete"
            >删除</el-button>
          </el-col>
        </el-row>
        <el-button @click="addDynamicPosition" size="mini" type="success">新增持仓操作</el-button>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false" size="mini">取消</el-button>
        <el-button
          type="primary"
          @click="dialogStatus==='create'?createData():updateData()"
          size="mini"
          :loading="submitBtnLoading"
        >确定</el-button>
      </div>
    </el-dialog>
    <!--        持仓列表-->
    <el-table
      :key="tableKey"
      v-loading="listLoading"
      :data="positionList"
      border
      fit
      highlight-current-row
      style="width: 100%;"
      size="mini"
    >
      <el-table-column type="expand" label="展开">
        <template slot-scope="props">
          <el-table
            :data="props.row.dynamicPositionList"
            border
            fit
            highlight-current-row
            style="width: 100%;"
            size="mini"
          >
            <el-table-column label="动态操作时间" align="center" width="120">
              <template slot-scope="{row}">
                <span>{{ row.time | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
              </template>
            </el-table-column>
            <el-table-column label="动态操作价格" prop="price" align="center" width="120" />
            <el-table-column label="动态操作数量" prop="amount" align="center" width="120" />
            <el-table-column label="动态操作原因" prop="reason" align="center" />
          </el-table>
        </template>
      </el-table-column>
      <el-table-column label="品种" prop="symbol" align="center" width="100">
        <template slot-scope="{row}">
          <el-link
            type="primary"
            :underline="false"
            @click="handleJumpToKline(row)"
          >{{ row.symbol }}</el-link>
        </template>
      </el-table-column>
      <el-table-column label="周期" prop="period" align="center" width="50" />
      <el-table-column label="入场时间" align="center" width="120">
        <template slot-scope="{row}">
          <span>{{ row.enterTime | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>
        </template>
      </el-table-column>
      <el-table-column label="信号" align="center" width="50">
        <template slot-scope="{row}">
          <span>{{ row.signal| signalTypeFilter }}</span>
        </template>
      </el-table-column>
      <el-table-column label="方向" prop="direction" align="center" width="55">
        <template slot-scope="{row}">
          <el-tag :type="row.direction | directionTagFilter">
            <span>{{ row.direction | directionFilter }}</span>
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="入场价格" prop="price" align="center" width="80" />
      <el-table-column label="数量" prop="amount" align="center" width="80" />
      <el-table-column label="止损价格" prop="stopLosePrice" align="center" width="80" />
      <el-table-column label="止损率" align="center" width="80">
         <template slot-scope="{row}">
           {{Math.round((row.stopLosePrice-row.price)/row.price*10000)/100}}%
         </template>
      </el-table-column>
      <el-table-column label="仓位" prop="positionPercent" align="center" width="50">
        <template slot-scope="{row}">
            <span>{{ row.positionPercent | positionPercentFilter }}</span>
        </template>
      </el-table-column>
      <!-- <el-table-column label="预期" prop="nestLevel" align="center" width="70" />
      <el-table-column label="危险系数" prop="important" align="center" width="100">
        <template slot-scope="{row}">
          <el-rate disabled v-model="row.importance" :colors="rateColors"></el-rate>
        </template>
      </el-table-column> -->
      <el-table-column label="入场逻辑" prop="enterReason" align="center" width="260" />
      <el-table-column label="持仓逻辑" prop="holdReason" align="center" width="260" />
      <el-table-column
        label="状态"
        width="130"
        align="center"
      >
         <template slot-scope="{row}">
          <el-select
            v-model="row.status"
            class="form-input-short"
            size="mini"
            @change="changeStatus(row._id,row.status)"
          >
            <el-option
              v-for="item in statusOptions"
              :key="item.key"
              :label="item.display_name"
              :value="item.key"
            />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column label="操作" align="center">
        <template slot-scope="{row,$index}">
          <el-button type="primary" size="mini" @click="handleUpdate(row)" icon="el-icon-edit">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      background
      layout="total,sizes,prev, pager, next"
      :current-page.sync="listQuery.current"
      :page-size="listQuery.size"
      :total="listQuery.total"
      :page-sizes="[10, 50, 100]"
      @current-change="handlePageChange"
      @size-change="handleSizeChange"
      class="mt-5"
    />
  </div>
</template>

<script>
import CommonTool from "@/tool/CommonTool";
import { stockApi } from "@/api/stockApi";
// 仓位控制
const positionPercentOptions = [
  { key: "10", display_name: "10%" },
  { key: "20", display_name: "20%" },
  { key: "30", display_name: "30%" },
  { key: "40", display_name: "40%" }
];
const signalTypeOptions = [
  { key: "tupo", display_name: "突破" },
  { key: "huila", display_name: "拉回" },
  { key: "break", display_name: "破坏" },
  { key: "vfan", display_name: "V反" }
];
const directionOptions = [
  { key: "long", display_name: "买" }
  // { key: "short", display_name: "卖" }
];
const dynamicDirectionOptions = [
  { key: "long", display_name: "买" },
  { key: "short", display_name: "卖" }
];
const statusOptions = [
  { key: "holding", display_name: "持仓" },
  { key: "prepare", display_name: "预埋单" },
  { key: "winEnd", display_name: "止盈" },
  { key: "loseEnd", display_name: "止损" },
];
const periodOptions = [
  { key: "3m", display_name: "3m" },
  { key: "5m", display_name: "5m" },
  { key: "15m", display_name: "15m" },
  { key: "30m", display_name: "30m" },
  { key: "60m", display_name: "60m" },
  { key: "180m", display_name: "180m" }
];
// arr to obj, such as { CN : "China", US : "USA" }
const signalTypeKeyValue = signalTypeOptions.reduce((acc, cur) => {
  acc[cur.key] = cur.display_name;
  return acc;
}, {});
const statusKeyValue = statusOptions.reduce((acc, cur) => {
  acc[cur.key] = cur.display_name;
  return acc;
}, {});
const directionKeyValue = directionOptions.reduce((acc, cur) => {
  acc[cur.key] = cur.display_name;
  return acc;
}, {});
const positionPercentKeyValue = positionPercentOptions.reduce((acc, cur) => {
  acc[cur.key] = cur.display_name;
  return acc;
}, {});
export default {
  name: "PositionList",
  filters: {
    statusTagFilter(status) {
      const statusMap = {
        holding: "success",
        prepare: "info",
        end: "danger"
      };
      return statusMap[status];
    },
    directionTagFilter(direction) {
      const directionMap = {
        long: "danger",
        short: "primary"
      };
      return directionMap[direction];
    },
    directionFilter(direction) {
      return directionKeyValue[direction];
    },
    signalTypeFilter(type) {
      return signalTypeKeyValue[type];
    },
    positionPercentFilter(type) {
      return positionPercentKeyValue[type];
    },
    statusFilter(type) {
      return statusKeyValue[type];
    },
    parseTime(time, fmt) {
      return CommonTool.parseTime(time, fmt);
    }
  },
  props: {
    // futureSymbolList: {
    //   type: Array,
    //   default: []
    // }
  },
  data() {
    return {
      rateColors: ["#99A9BF", "#F7BA2A", "#FF9900"],
      tableKey: 0,
      listLoading: false,
      // 持仓列表
      positionList: [],
      positionQueryForm: {
        status: "holding"
      },
      // 分页对象
      listQuery: {
        size: 10,
        total: 0,
        current: 1
      },
      // 表单
      positionForm: {
        // importance: 3,
        enterTime: new Date(),
        symbol: "",
        period: "",
        signal: "",
        status: "holding",
        // 方向
        direction: "long",
        positionPercent: "",
        // 价格
        price: "",
        // 数量
        amount: "",
        stopLosePrice: "",
        // 区间套级别
        // nestLevel: "2级套",
        // 介入逻辑
        enterReason: "",
        // 持仓逻辑
        holdReason: "",
        // 动态止盈,加仓，止损，锁仓列表
        dynamicPositionList: []
      },
      rules: {
        signal: [
          { required: true, message: "请选择入场信号", trigger: "change" }
        ],
        enterTime: [
          {
            type: "date",
            required: true,
            message: "请选择入场时间",
            trigger: "change"
          }
        ],
        symbol: [{ required: true, message: "请选择品种", trigger: "change" }],
        period: [
          { required: true, message: "请选择周期图", trigger: "change" }
        ],
        status: [{ required: true, message: "请选择状态", trigger: "change" }],
        direction: [
          { required: true, message: "请选择方向", trigger: "change" }
        ],
        price: [{ required: true, message: "请输入价格", trigger: "blur" }],
        amount: [{ required: true, message: "请输入数量", trigger: "blur" }],
        // nestLevel: [
        //   { required: true, message: "请选择预期级别", trigger: "change" }
        // ],
        // enterReason: [
        //   { required: true, message: "请输入入场逻辑", trigger: "blur" }
        // ],
        positionPercent: [
          { required: true, message: "请选择仓位", trigger: "change" }
        ]
      },
      dialogFormVisible: false,
      // 防止重复提交
      submitBtnLoading: false,
      dialogStatus: "",
      textMap: {
        update: "编辑",
        create: "新增"
      },
      statusOptions,
      signalTypeOptions,
      periodOptions,
      directionOptions,
      dynamicDirectionOptions,
      positionPercentOptions
    };
  },
  mounted() {
    this.getPositionList(
      this.positionQueryForm.status,
      this.listQuery.current,
      this.listQuery.size
    );
  },
  methods: {
    changeStatus(id, status) {
      console.log(id, status);
      stockApi
        .updatePositionStatus(id, status)
        .then(res => {
          if (res.code === "ok") {
            this.getPositionList(
              this.positionQueryForm.status,
              this.listQuery.current,
              this.listQuery.size
            );
          }
        })
        .catch(error => {
          console.log("更新状态失败", error);
        });
    },
    handleSizeChange(currentSize) {
      this.listQuery.size = currentSize;
      this.getPositionList(
        this.positionQueryForm.status,
        this.listQuery.current,
        this.listQuery.size
      );
    },
    handlePageChange(currentPage) {
      this.listQuery.current = currentPage;
      this.getPositionList(
        this.positionQueryForm.status,
        this.listQuery.current,
        this.listQuery.size
      );
    },
    handleQueryStatusChange() {
      this.getPositionList(
        this.positionQueryForm.status,
        this.listQuery.current,
        this.listQuery.size
      );
    },
    filterTags(value, row) {
      return row.status === value;
    },
    handleJumpToKline(row) {
      console.log(this.$parent);
      // this.$parent.jumpToKline(symbol)
      // 结束状态 k线页面不获取持仓信息
      if (row.status !== "winEnd" && row.status !== "loseEnd") {
        let routeUrl = this.$router.resolve({
          path: "/multi-period",
          query: {
            symbol: row.symbol,
            isPosition: true,
            endDate: CommonTool.dateFormat("yyyy-MM-dd")
          }
        });
        window.open(routeUrl.href, "_blank");
      }
    },
    getPositionList(status, page, size) {
      this.listLoading = true;
      stockApi
        .getPositionList(status, page, size)
        .then(res => {
          this.listLoading = false;
          this.listQuery.total = res.total;
          this.positionList = res.records;
          // console.log("后端返回的持仓列表", res);
        })
        .catch(error => {
          this.listLoading = false;
          console.log("获取持仓列表失败", error);
        });
    },
    handleModifyStatus(row, status) {
      this.$message({
        message: "操作Success",
        type: "success"
      });
      row.status = status;
    },

    resetForm() {
      this.positionForm = {
        // importance: 1,
        enterTime: new Date(),
        symbol: "",
        period: "",
        status: "holding",
        signal: "",
        direction: "long",
        positionPercent: "",
        price: "",
        amount: "",
        stopLosePrice: "",
        // nestLevel: "2级套",
        enterReason: "",
        holdReason: "",
        dynamicPositionList: []
      };
    },
    addDynamicPosition() {
      this.positionForm.dynamicPositionList.push({
        time: new Date(),
        price: "",
        amount: "",
        reason: ""
      });
    },
    removeDynamicPosition(index) {
      this.positionForm.dynamicPositionList.splice(index, 1);
    },
    // 新增持仓
    handleCreatePos() {
      this.resetForm();
      this.dialogStatus = "create";
      this.dialogFormVisible = true;
      this.$nextTick(() => {
        this.$refs["positionFormRef"].clearValidate();
      });
    },
    createData() {
      this.$refs["positionFormRef"].validate(valid => {
        if (valid) {
          this.submitBtnLoading = true;
          stockApi
            .createPosition(this.positionForm)
            .then(res => {
              this.submitBtnLoading = false;
              console.log("新增结果", res);
              this.dialogFormVisible = false;
              this.$notify({
                title: "Success",
                message: "新增成功",
                type: "success",
                duration: 2000
              });
              // 拉取后端接口获取最新持仓列表
              this.getPositionList(
                this.positionQueryForm.status,
                this.listQuery.current,
                this.listQuery.size
              );
            })
            .catch(error => {
              this.submitBtnLoading = false;

              console.log("新增失败:", error);
            });
        }
      });
    },
    handleUpdate(row) {
      // this.positionForm = Object.assign({}, row); // copy obj
      this.positionForm = JSON.parse(JSON.stringify(row));
      this.dialogStatus = "update";
      this.dialogFormVisible = true;
      this.$nextTick(() => {
        this.$refs["positionFormRef"].clearValidate();
      });
    },
    updateData() {
      this.$refs["positionFormRef"].validate(valid => {
        if (valid) {
          this.submitBtnLoading = true;
          // const tempData = Object.assign({}, this.positionForm)
          stockApi
            .updatePosition(this.positionForm)
            .then(res => {
              this.submitBtnLoading = false;
              console.log("更新结果", res);
              this.dialogFormVisible = false;
              this.$notify({
                title: "Success",
                message: "更新成功",
                type: "success",
                duration: 2000
              });
              // 拉取后端接口获取最新持仓列表
              this.getPositionList(
                this.positionQueryForm.status,
                this.listQuery.current,
                this.listQuery.size
              );
            })
            .catch(error => {
              this.submitBtnLoading = false;
              console.log("更新持仓失败:", error);
            });
        }
      });
    },
    handleDelete(row, index) {
      this.$notify({
        title: "Success",
        message: "Delete Successfully",
        type: "success",
        duration: 2000
      });
      this.positionList.splice(index, 1);
    }
  }
};
</script>
<style lang="stylus">
.position-list-main {
  .form-input {
    width: 200px !important;
  }

  .form-input-short {
    width: 100px !important;
  }

  .long-textarea {
    width: 350px;
  }

  .query-position-form {
    margin-bottom: 10px;
  }
}
</style>
