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
              <el-select
                v-model="positionForm.symbol"
                class="form-input"
                placeholder="请选择"
                filterable
              >
                <el-option
                  v-for="item in futureSymbolList"
                  :key="item.order_book_id"
                  :label="item.order_book_id"
                  :value="item.order_book_id"
                />
              </el-select>
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
          <el-col :span="12">
            <el-form-item label="入场逻辑">
              <el-input
                v-model="positionForm.enterReason"
                :autosize="{ minRows: 4, maxRows: 4}"
                type="textarea"
                class="form-textarea-middle"
                placeholder="请输入"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col :span="18">
            <el-form-item label="持仓逻辑">
              <el-input
                v-model="positionForm.holdReason"
                :autosize="{ minRows: 4, maxRows: 4}"
                type="textarea"
                class="form-textarea-long"
                placeholder="请输入"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 动态止盈start -->
        <!--    编辑状态-->
        <el-divider content-position="left">持仓过程记录（ 动态止盈 | 加仓 | 锁仓 | 止损 ）</el-divider>
        <el-row
          v-for="(dynamicPosition, index) in positionForm.dynamicPositionList"
          :key="Math.random()"
        >
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
      style="width: 100%;"
      size="mini"
      :row-class-name="tableRowClassName"
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
          <el-tag v-if="props.row.holdReason">{{props.row.holdReason}}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="品种" prop="symbol" align="center" width="80">
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
      <el-table-column label="成本价" prop="price" align="center" width="80" />
      <el-table-column
        :key="Math.random()"
        label="最新价"
        width="80"
        align="center"
        v-if="positionQueryForm.status!=='winEnd' && positionQueryForm.status!=='loseEnd'"
      >
        <template slot-scope="{row}">
          {{
          (changeList?changeList[row.symbol].price:'获取中')
          }}
        </template>
      </el-table-column>
      <el-table-column
        :key="Math.random()"
        label="浮盈率"
        width="100"
        align="center"
        v-if="positionQueryForm.status!=='winEnd' && positionQueryForm.status!=='loseEnd'"
      >
        <template slot-scope="{row}">
          <el-tag :type="calcProfitRate(row) | percentTagFilter">{{calcProfitRate(row)}}%</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="止损价" width="80" align="center">
        <template slot-scope="{row}">{{row.stopLosePrice}}</template>
      </el-table-column>
      <el-table-column label="止损率" width="80" align="center">
        <template slot-scope="{row}">-{{calcStopLoseRate(row)}}%</template>
      </el-table-column>
      <el-table-column
        :key="Math.random()"
        label="盈亏比"
        width="80"
        align="center"
        v-if="positionQueryForm.status!=='winEnd' && positionQueryForm.status!=='loseEnd'"
      >
        <template slot-scope="{row}">
          <el-tag
            :type="calcWinLoseRate(row) | winLoseRateTagFilter"
            effect="dark"
          >{{calcWinLoseRate(row)}}</el-tag>
        </template>
      </el-table-column>
      <!-- 止盈结束的时候计算盈利率 -->
      <el-table-column
        :key="Math.random()"
        label="盈利率"
        width="100"
        align="center"
        v-if="positionQueryForm.status==='winEnd'"
      >
        <template slot-scope="{row}">
          <el-tag :type="calcWinEndRate(row) | percentTagFilter">{{calcWinEndRate(row)}}%</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="数量" prop="amount" align="center" width="100" />
      <el-table-column label="入场逻辑" prop="enterReason" align="center" width="300" />
      <!-- <el-table-column label="持仓逻辑" prop="holdReason" align="center" width="300" /> -->
      <el-table-column label="状态" width="130" align="center">
        <template slot-scope="{row}">
          <!--          <el-tag :type="row.status | statusTagFilter">{{ row.status |statusFilter }}</el-tag>-->
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
          <el-button type="primary" size="mini" @click="handleUpdate(row)">编辑</el-button>
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
import { futureApi } from "@/api/futureApi";

const signalTypeOptions = [
  { key: "tupo", display_name: "突破" },
  { key: "lahui", display_name: "拉回" },
  { key: "break", display_name: "破坏" },
  { key: "vfan", display_name: "V反" }
];
const directionOptions = [
  { key: "long", display_name: "多" },
  { key: "short", display_name: "空" }
];
const dynamicDirectionOptions = [
  { key: "long", display_name: "多" },
  { key: "short", display_name: "空" },
  { key: "close", display_name: "平" }
];
const statusOptions = [
  { key: "holding", display_name: "持仓中" },
  { key: "prepare", display_name: "预埋单" },
  { key: "winEnd", display_name: "止盈结束" },
  { key: "loseEnd", display_name: "止损结束" }
];
const periodOptions = [
  { key: "3m", display_name: "3m" },
  { key: "5m", display_name: "5m" },
  { key: "15m", display_name: "15m" },
  { key: "30m", display_name: "30m" },
  { key: "60m", display_name: "60m" },
  { key: "240m", display_name: "240m" }
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
    percentTagFilter(percent) {
      if (percent > 0) {
        return "danger";
      } else if (percent < 0) {
        return "primay";
      } else {
        return "info";
      }
    },
    winLoseRateTagFilter(rate) {
      if (rate >= 1) {
        return "success";
      } else {
        return "info";
      }
    },
    directionFilter(direction) {
      return directionKeyValue[direction];
    },
    signalTypeFilter(type) {
      return signalTypeKeyValue[type];
    },
    statusFilter(type) {
      return statusKeyValue[type];
    },
    parseTime(time, fmt) {
      return CommonTool.parseTime(time, fmt);
    }
  },
  props: {
    futureSymbolList: {
      type: Array,
      default: []
    },
    futureSymbolMap: {
      type: Object,
      default: null
    },
    changeList: {
      type: Object,
      default: null
    },
    marginLevelCompany: 0
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
        period: "3m",
        signal: "",
        status: "holding",
        //方向
        direction: "",
        //价格
        price: "",
        //数量
        amount: "",
        stopLosePrice: "",
        //区间套级别
        // nestLevel: "2级套",
        //介入逻辑
        enterReason: "",
        //持仓逻辑
        holdReason: "",
        //动态止盈,加仓，止损，锁仓列表
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
        amount: [{ required: true, message: "请输入数量", trigger: "blur" }]
        // nestLevel: [
        //   { required: true, message: "请选择预期级别", trigger: "change" }
        // ],
        // enterReason: [
        //   { required: true, message: "请输入入场逻辑", trigger: "blur" }
        // ]
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
      dynamicDirectionOptions
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
    calcWinEndRate(row) {
      // 获取动止列表中的最后一次平仓的价格
      if (row.dynamicPositionList.length > 0) {
        let winPrice =
          row.dynamicPositionList[row.dynamicPositionList.length - 1].price;
        let marginLevel = Number(
          (1 / (row.margin_rate + this.marginLevelCompany)).toFixed(2)
        );
        return Math.abs(
          ((winPrice - row.price) / row.price) * 100 * marginLevel
        ).toFixed(2);
      }
    },
    // 计算盈亏比
    calcWinLoseRate(row) {
      let profitRate = this.calcProfitRate(row);
      let stopLoseRate = this.calcStopLoseRate(row);
      if (profitRate === "获取中" || stopLoseRate === "获取中") {
        return "获取中";
      } else {
        return (profitRate / stopLoseRate).toFixed(1);
      }
    },
    // 计算止损率
    calcStopLoseRate(row) {
      if (this.changeList != null) {
        // let futureInfo = this.futureSymbolMap[row.symbol];
        let marginLevel = Number(
          (1 / (row.margin_rate + this.marginLevelCompany)).toFixed(2)
        );
        return Math.abs(
          ((row.stopLosePrice - row.price) / row.price) * 100 * marginLevel
        ).toFixed(2);
      } else {
        return "获取中";
      }
    },
    //  计算收益率
    calcProfitRate(row) {
      if (this.futureSymbolMap !== null && this.changeList != null) {
        // let futureInfo = this.futureSymbolMap[row.symbol];
        let marginLevel = Number(
          (1 / (row.margin_rate + this.marginLevelCompany)).toFixed(2)
        );
        let currentPercent = 0;
        if (row.direction === "long") {
          currentPercent = (
            ((this.changeList[row.symbol].price - row.price) / row.price) *
            100 *
            marginLevel
          ).toFixed(2);
        } else {
          currentPercent = (
            ((row.price - this.changeList[row.symbol].price) /
              this.changeList[row.symbol].price) *
            100 *
            marginLevel
          ).toFixed(2);
        }
        return currentPercent;
      } else {
        return "获取中";
      }
    },
    changeStatus(id, status) {
      console.log(id, status);
      futureApi
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
    tableRowClassName({ row, rowIndex }) {
      if (row.dynamicPositionList.length > 0) {
        return "success-row";
      }
      // else {
      //   return 'warning-row';
      // }
      return "";
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
      //结束状态 k线页面不获取持仓信息
      if (row.status !== "winEnd" && row.status !== "stopEnd") {
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
      this.positionList = [];
      this.listLoading = true;
      futureApi
        .getPositionList(status, page, size)
        .then(res => {
          this.listLoading = false;
          this.listQuery.total = res.total;
          this.positionList = res.records;
          console.log("后端返回的持仓列表", res);
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
        period: "3m",
        status: "holding",
        signal: "",
        direction: "",
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
          // 保存当时的保证金比率，方便计算 交割后的老的合约盈利率
          this.positionForm.margin_rate = this.futureSymbolMap[
            this.positionForm.symbol
          ].margin_rate;
          futureApi
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
              //拉取后端接口获取最新持仓列表
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
      this.positionForm = Object.assign({}, row); // copy obj
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
          this.positionForm.margin_rate = this.futureSymbolMap[
            this.positionForm.symbol
          ].margin_rate;
          futureApi
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
              //拉取后端接口获取最新持仓列表
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
    // formatJson(filterVal) {
    //     return this.positionList.map(v => filterVal.map(j => {
    //         if (j === 'enterTime') {
    //             return parseTime(v[j])
    //         } else {
    //             return v[j]
    //         }
    //     }))
    // },
    // getSortClass: function (key) {
    //     const sort = this.positionListQuery.sort
    //     return sort === `+${key}` ? 'ascending' : 'descending'
    // }
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

  .form-textarea-middle {
    width: 600px;
  }

  .form-textarea-long {
    width: 1000px;
  }

  .query-position-form {
    margin-bottom: 10px;
  }

  .el-table .warning-row {
    background: oldlace;
  }

  .el-table .success-row {
    background: #f0f9eb;
  }
}
</style>
