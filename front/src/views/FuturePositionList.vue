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
                    <el-option key="all" value="all" label="全部"/>
                    <el-option
                        v-for="item in statusOptions"
                        :key="item.key"
                        :label="item.display_name"
                        :value="item.key"
                    />
                </el-select>
                <el-date-picker
                    v-model="endDate"
                    type="date"
                    placeholder="选择日期"
                    format="yyyy 年 MM 月 dd 日"
                    value-format="yyyy-MM-dd"
                    size="mini"
                    @change="getPositionList()"
                    class="ml-5 mr-5">
                </el-date-picker>
                <el-button @click="quickSwitchDay('pre')" size="mini">前一天</el-button>
                <el-button @click="quickSwitchDay('next')" size="mini">后一天</el-button>
            </el-form-item>
            <!--      <el-form-item>-->
            <!--        <el-button-->
            <!--          type="primary"-->
            <!--          @click="handleCreatePos"-->
            <!--          size="mini"-->
            <!--          class="query-position-form"-->
            <!--        >新增持仓</el-button>-->
            <!--      </el-form-item>-->
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
                    :key="index"
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
                        >删除
                        </el-button>
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
                >确定
                </el-button>
            </div>
        </el-dialog>
        <!--        持仓列表-->
        <el-table
            :key="tableKey"
            :data="positionList"
            border
            fit
            style="width: 100%;"
            size="mini"
            show-summary
            :summary-method="getSummaries"
            :row-class-name="tableRowClassName"
        >
            <!--        -->
            <!--      <el-table-column type="expand" label="展开">-->
            <!--        <template slot-scope="props">-->
            <!--          <el-table-->
            <!--            :data="props.row.dynamicPositionList"-->
            <!--            border-->
            <!--            fit-->
            <!--            highlight-current-row-->
            <!--            style="width: 100%;"-->
            <!--            size="mini"-->
            <!--          >-->
            <!--            <el-table-column label="动态操作时间" align="center" width="120">-->
            <!--              <template slot-scope="{row}">-->
            <!--                <span>{{ row.time | parseTime('{y}-{m}-{d} {h}:{i}') }}</span>-->
            <!--              </template>-->
            <!--            </el-table-column>-->
            <!--            <el-table-column label="动态操作价格" prop="price" align="center" width="120" />-->
            <!--            <el-table-column label="动态操作数量" prop="amount" align="center" width="120" />-->
            <!--            <el-table-column label="动态操作原因" prop="reason" align="center" />-->
            <!--          </el-table>-->
            <!--          <el-tag v-if="props.row.holdReason">{{props.row.holdReason}}</el-tag>-->
            <!--        </template>-->
            <!--      </el-table-column>-->
            <el-table-column label="品种" prop="symbol" align="center" width="80">
                <template slot-scope="{row}">
                    <el-link
                        type="primary"
                        :underline="false"
                        @click="handleJumpToKline(row)"
                    >{{ row.symbol }}
                    </el-link>
                    <!-- todo                      @click="handleJumpToKline(row)"-->
                </template>
            </el-table-column>
            <el-table-column label="周期" prop="period" align="center" width="50"/>
            <el-table-column label="入场时间" align="center" width="150">
                <template slot-scope="{row}">
                    <span>{{ row.date_created}}</span>
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
            <el-table-column label="成本价" prop="price" align="center" width="80"/>
            <el-table-column label="数量" prop="amount" align="center" width="100"/>
            <!--            后台只更新持仓单的最新价，浮盈率，浮盈额. 老合约没必要继续更新最新价，因此这几个字段都不显示，但是列不能删除
                            删除了会导致表格求和位置要修改-->
            <el-table-column
                label="最新价"
                width="80"
                align="center"
            >
                <template slot-scope="{row}" v-if="positionQueryForm.status==='holding'">
                    {{Number(row.close_price)}}
                </template>
            </el-table-column>
            <el-table-column
                label="浮盈率"
                width="100"
                align="center"
                prop="current_profit_rate"
            >
                <template slot-scope="{row}" v-if="positionQueryForm.status==='holding'">
                    <el-tag :type="row.current_profit_rate| percentTagFilter">{{(row.current_profit_rate*100).toFixed(2)}}%</el-tag>
                </template>
            </el-table-column>

            <el-table-column
                label="浮盈额"
                width="100"
                align="center"
                prop="current_profit"
            >
                <template slot-scope="{row}" v-if="positionQueryForm.status==='holding'">
                    <el-tag :type="row.current_profit| percentTagFilter">{{row.current_profit}}</el-tag>
                </template>
            </el-table-column>
            <el-table-column label="保证金" width="80" align="center">
                <template slot-scope="{row}">{{row.total_margin}}</template>
            </el-table-column>
            <el-table-column label="止损价" width="80" align="center">
                <template slot-scope="{row}">
                    <el-tag type="warning">
                        {{row.stop_lose_price}}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column label="止损率" width="80" align="center">
                <template slot-scope="{row}">-{{calcStopLoseRate(row).toFixed(2)}}%</template>
            </el-table-column>
            <el-table-column label="预计止损额" prop="predict_stop_money" width="110" align="center">
            </el-table-column>
            <el-table-column label="实际亏损价" prop="lose_end_price" width="110" align="center">
                <template slot-scope="{row}" v-if="row.status==='loseEnd'">
                    {{row.status ==='loseEnd'?row.lose_end_price:0}}
                </template>
            </el-table-column>
            <el-table-column label="亏损额" width="110" align="center">
                <template slot-scope="{row}" v-if="row.status==='loseEnd'">
                    <el-tag :type="row.lose_end_money|percentTagFilter">
                        {{row.status ==='loseEnd'?row.lose_end_money:0}}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column label="亏损额比率" prop="lose_end_rate" width="110" align="center">
                <template slot-scope="{row}" v-if="row.status==='loseEnd'">
                    {{row.status==='loseEnd'?(row.lose_end_rate * 100).toFixed(0)+'%':0}}
                </template>
            </el-table-column>


            <el-table-column label="止盈价" width="110" align="center">
                <template slot-scope="{row}" v-if="row.status==='winEnd'">
                    {{row.status ==='winEnd'?row.win_end_price:0}}
                </template>
            </el-table-column>

            <el-table-column label="已盈利额" width="110" align="center">
                <template slot-scope="{row}" v-if="row.status==='winEnd'">
                    <el-tag type="danger">
                        {{row.status ==='winEnd'?row.win_end_money:0}}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column label="已盈利比率" prop="win_end_rate" width="110" align="center">
                <template slot-scope="{row}" v-if="row.status==='winEnd'">
                    <el-tag type="danger">
                        {{row.status==='winEnd'?(row.win_end_rate * 100).toFixed(0)+'%':0}}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column
                label="盈亏比"
                width="80"
                align="center"
            >
                <template slot-scope="{row}">
                    <el-tag
                        :type="calcWinLoseRate(row) | winLoseRateTagFilter"
                        effect="dark"
                    >{{calcWinLoseRate(row)}}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column label="动止数" prop="stop_win_count" width="90" align="center">
                <template slot-scope="{row}" >
                    {{row.stop_win_count}}
                </template>
            </el-table-column>
            <el-table-column label="动止价" prop="stop_win_count" width="90" align="center">
                <template slot-scope="{row}" >
                    {{row.stop_win_price}}
                </template>
            </el-table-column>
            <el-table-column label="动止收益" prop="stop_win_money" width="90" align="center">
                <template slot-scope="{row}" >
                    {{row.stop_win_money}}
                </template>
            </el-table-column>
            <!-- 止盈结束的时候计算盈利率 -->
            <!--            <el-table-column-->
            <!--                label="盈利率"-->
            <!--                width="100"-->
            <!--                align="center"-->
            <!--            >-->
            <!--&lt;!&ndash;                <template slot-scope="{row}">&ndash;&gt;-->
            <!--&lt;!&ndash;                    <el-tag :type="calcWinEndRate(row) | percentTagFilter">{{calcWinEndRate(row)}}%</el-tag>&ndash;&gt;-->
            <!--&lt;!&ndash;                </template>&ndash;&gt;-->
            <!--            </el-table-column>-->

            <!--      <el-table-column label="入场逻辑" prop="enterReason" align="center" width="300" />-->
            <!-- <el-table-column label="持仓逻辑" prop="holdReason" align="center" width="300" /> -->
            <el-table-column label="最后更新时间" prop="last_update_time" align="center" width="150"/>
            <el-table-column label="最后信号" prop="last_update_signal" align="center" width="80"/>
            <el-table-column label="最后周期" prop="last_update_period" align="center" width="80"/>
            <el-table-column label="操作状态" align="center">
                <template slot-scope="{row}">
                    <el-select
                        v-model="row.status"
                        class="form-input-short"
                        size="mini"
                        @change="changeStatus(row._id,row.status,row.close_price)"
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
            <!--            <el-table-column label="操作" align="center">-->
            <!--                <template slot-scope="{row,$index}">-->
            <!--                    &lt;!&ndash;          <el-button type="primary" size="mini" @click="handleUpdate(row)">编辑</el-button>&ndash;&gt;-->
            <!--                </template>-->
            <!--            </el-table-column>-->
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
    import {futureApi} from "@/api/futureApi";

    const signalTypeOptions = [
        {key: "tupo", display_name: "突破"},
        {key: "huila", display_name: "拉回"},
        {key: "break", display_name: "破坏"},
        {key: "vfan", display_name: "V反"},
        {key: "beichi", display_name: "背驰"}
    ];
    const directionOptions = [
        {key: "long", display_name: "多"},
        {key: "short", display_name: "空"}
    ];
    const dynamicDirectionOptions = [
        {key: "long", display_name: "多"},
        {key: "short", display_name: "空"},
        {key: "close", display_name: "平"}
    ];
    const statusOptions = [
        {key: "holding", display_name: "持仓中"},
        // {key: "prepare", display_name: "预埋单"},
        {key: "winEnd", display_name: "止盈结束"},
        {key: "loseEnd", display_name: "止损结束"}
    ];
    const periodOptions = [
        {key: "3m", display_name: "3m"},
        {key: "5m", display_name: "5m"},
        {key: "15m", display_name: "15m"},
        {key: "30m", display_name: "30m"},
        {key: "60m", display_name: "60m"},
        {key: "240m", display_name: "240m"}
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
            marginLevelCompany: 0
        },
        data() {
            return {
                endDate: CommonTool.dateFormat('yyyy-MM-dd'),
                futureConfig: {},
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
                    size: 50,
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
                    // 方向
                    direction: "",
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
                        {required: true, message: "请选择入场信号", trigger: "change"}
                    ],
                    enterTime: [
                        {
                            type: "date",
                            required: true,
                            message: "请选择入场时间",
                            trigger: "change"
                        }
                    ],
                    symbol: [{required: true, message: "请选择品种", trigger: "change"}],
                    period: [
                        {required: true, message: "请选择周期图", trigger: "change"}
                    ],
                    status: [{required: true, message: "请选择状态", trigger: "change"}],
                    direction: [
                        {required: true, message: "请选择方向", trigger: "change"}
                    ],
                    price: [{required: true, message: "请输入价格", trigger: "blur"}],
                    amount: [{required: true, message: "请输入数量", trigger: "blur"}]
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
            let symbolConfig = window.localStorage.getItem('symbolConfig')
            if (symbolConfig !== null) {
                this.futureConfig = JSON.parse(symbolConfig)
                this.getPositionList();
            }
            // 静默更新合约配置
            this.getFutureConfig()
        },
        methods: {
            // calcWinEndRate(row) {
            //     // 获取动止列表中的最后一次平仓的价格
            //     if (row.dynamicPositionList.length > 0) {
            //         let winPrice =
            //             row.dynamicPositionList[row.dynamicPositionList.length - 1].price;
            //         let marginLevel = Number(
            //             (1 / (row.margin_rate + this.marginLevelCompany)).toFixed(2)
            //         );
            //         return Math.abs(
            //             ((winPrice - row.price) / row.price) * 100 * marginLevel
            //         ).toFixed(2);
            //     }
            // },
            quickSwitchDay(type) {
                let tempDate = this.endDate.replace(/-/g, '/')
                let date = new Date(tempDate)
                let preDay = date.getTime() - 3600 * 1000 * 24
                let nextDay = date.getTime() + 3600 * 1000 * 24
                if (type === 'pre') {
                    this.endDate = CommonTool.parseTime(preDay, '{y}-{m}-{d}')
                } else {
                    this.endDate = CommonTool.parseTime(nextDay, '{y}-{m}-{d}')
                }
                this.getPositionList();
            },
            getFutureConfig() {
                futureApi.getFutureConfig().then(res => {
                    console.log('合约配置信息:', res)
                    this.futureConfig = res
                    window.localStorage.setItem('symbolConfig', JSON.stringify(this.futureConfig))
                    setInterval(() => {
                        this.getPositionList();
                    }, 5000)

                }).catch((error) => {
                    console.log('获取合约配置失败:', error)
                })
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
                return row.per_order_stop_rate * 100
            },
            //  计算收益率
            calcProfitRate(row) {
                let marginLevel = 1
                if (row.symbol === 'BTC') {
                    // BTC
                    marginLevel = 1 / this.futureConfig[row.symbol].margin_rate
                } else if (row.symbol.indexOf('sz') !== -1 || row.symbol.indexOf('sh') !== -1) {
                    marginLevel = 1
                } else {
                    // 期货简单代码   RB
                    let simpleSymbol = row.symbol.replace(/[0-9]/g, '')
                    const margin_rate = this.futureConfig[simpleSymbol].margin_rate
                    let currentMarginRate = margin_rate + this.marginLevelCompany
                    marginLevel = Number((1 / (currentMarginRate)).toFixed(2))
                }
                let currentPercent = 0;
                if (row.direction === "long") {
                    currentPercent = (
                        ((row.close_price - row.price) / row.price) *
                        100 *
                        marginLevel
                    ).toFixed(2);
                } else {
                    currentPercent = (
                        ((row.price - row.close_price) /
                            row.close_price) *
                        100 *
                        marginLevel
                    ).toFixed(2);
                }
                return currentPercent;
            },
            changeStatus(id, status, close_price) {
                console.log(id, status);
                futureApi
                    .updatePositionStatus(id, status, close_price)
                    .then(res => {
                        if (res.code === "ok") {
                            this.getPositionList();
                        }
                    })
                    .catch(error => {
                        console.log("更新状态失败", error);
                    });
            },
            tableRowClassName({row, rowIndex}) {
                if (row.status === 'loseEnd') {
                    return "warning-row";
                } else if (row.status === 'winEnd') {
                    return 'success-row';
                }
                return "";
            },
            handleSizeChange(currentSize) {
                this.listQuery.size = currentSize;
                this.getPositionList();
            },
            handlePageChange(currentPage) {
                this.listQuery.current = currentPage;
                this.getPositionList();
            },
            handleQueryStatusChange() {
                this.getPositionList();
            },
            filterTags(value, row) {
                return row.status === value;
            },
            handleJumpToKline(row) {
                console.log(this.$parent);
                // this.$parent.jumpToKline(symbol)
                // 结束状态 k线页面不获取持仓信息
                // if (row.status !== "winEnd" && row.status !== "loseEnd") {
                let routeUrl = this.$router.resolve({
                    path: "/multi-period",
                    query: {
                        symbol: row.symbol,
                        isPosition: true,           //是否持过仓
                        positionPeriod: row.period, // 开仓周期
                        positionDirection: row.direction,// 持仓方向
                        positionStatus: row.status,  // 当前状态
                        endDate: CommonTool.dateFormat("yyyy-MM-dd")
                    }
                });
                window.open(routeUrl.href, "_blank");
                // }
            },
            getPositionList() {
                // this.positionList = [];
                // this.listLoading = true;
                futureApi
                    .getPositionList(this.positionQueryForm.status,
                        this.listQuery.current,
                        this.listQuery.size, this.endDate)
                    .then(res => {
                        this.listLoading = false;
                        this.listQuery.total = res.total;
                        this.positionList = res.records;
                        console.log("后端返回的持仓列表", res);
                    })
                    .catch(error => {
                        // this.listLoading = false;
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
                                // 拉取后端接口获取最新持仓列表
                                this.getPositionList();
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
                                // 拉取后端接口获取最新持仓列表
                                this.getPositionList();
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
            },
            getSummaries(param) {
                const {columns, data} = param;
                const sums = [];
                let stopSum = 0
                let currentProfitSum = 0
                // 占用保证金
                let totalMargin = 0
                // 已止损
                let loseEndSum = 0
                // 已盈利
                let winEndSum = 0
                if (data.length === 0) {
                    return sums
                }
                columns.forEach((column, index) => {
                    if (index === 0) {
                        sums[index] = '合计';
                        return;
                    }
                    // 累加 预计止损
                    if (index === 13) {
                        data.forEach((item) => {
                            stopSum += item.predict_stop_money
                        })
                        sums[13] = stopSum.toFixed(2)
                    } else if (index === 15) {

                        // 累加已止损
                        data.forEach((item) => {
                            if (item.status === 'loseEnd') {
                                loseEndSum += item.lose_end_money
                            }
                        })
                        sums[15] = loseEndSum.toFixed(2)
                    } else if (index === 18) {
                        // 累加已盈利
                        data.forEach((item) => {
                            if (item.status === 'winEnd') {
                                winEndSum += item.win_end_money
                            }
                        })
                        sums[18] = winEndSum.toFixed(2)
                    } else if (index === 9) {

                        // 累加当前盈利
                        data.forEach((item) => {
                            // 只累加还在持仓中的
                            if (item.status === 'holding') {
                                currentProfitSum += item.current_profit
                            }
                        })
                        sums[9] = currentProfitSum.toFixed(2)
                    } else if (index === 10) {

                        // 累加当前盈利
                        data.forEach((item) => {
                            // 只累加还在持仓中的
                            if (item.status === 'holding') {
                                // 兼容老数据
                                if (item.total_margin) {
                                    totalMargin += item.total_margin
                                }
                            }
                        })
                        sums[10] = totalMargin.toFixed(2)
                    } else {
                        sums[index] = ''
                    }
                });
                return sums;
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
