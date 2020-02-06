<template>
    <div class="future-control-main">
        <MyHeader></MyHeader>
        <!--仓位计算-->
        <el-divider content-position="center">仓位计算器</el-divider>
        <el-row>
            <el-form :inline="true" size="mini" :model="calcPosForm" class="demo-form-inline">
                <el-form-item label="资产总额">
                    <el-input v-model="calcPosForm.account" class="form-input"></el-input>
                </el-form-item>
                <el-form-item label="保证金系数">
                    <el-input v-model="calcPosForm.currentMarginRate" class="form-input" disabled></el-input>
                </el-form-item>
                <el-form-item label="合约乘数">
                    <el-input v-model="calcPosForm.contractMultiplier" class="form-input" disabled></el-input>
                </el-form-item>
                <el-form-item label="开仓价格">
                    <el-input v-model="calcPosForm.openPrice" class="form-input"></el-input>
                </el-form-item>
                <el-form-item label="止损价格">
                    <el-input v-model="calcPosForm.stopPrice" class="form-input"></el-input>
                </el-form-item>
                <el-form-item label="动止价(选填)">
                    <el-input v-model="calcPosForm.dynamicWinPrice" class="form-input"></el-input>
                </el-form-item>
                <el-form-item label="最大资金使用率">
                    <el-select v-model="calcPosForm.maxAccountUseRate" class="select-input">
                        <el-option label="10%" value="0.1"></el-option>
                        <el-option label="20%" value="0.2"></el-option>
                        <el-option label="30%" value="0.3"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="止损系数">
                    <el-select v-model="calcPosForm.stopRate" class="select-input">
                        <el-option label="1%" value="0.01"></el-option>
                        <el-option label="2%" value="0.02"></el-option>
                        <el-option label="3%" value="0.03"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="calcAccount">查询</el-button>
                </el-form-item>
                <el-form-item label="开仓手数">
                    <el-input v-model="calcPosForm.maxOrderCount" class="form-input" disabled></el-input>
                </el-form-item>
                <el-form-item label="资金使用率">
                    <el-input v-model="calcPosForm.accountUseRate" class="form-input" disabled></el-input>
                </el-form-item>
                <el-form-item label="1手保证金">
                    <el-input v-model="calcPosForm.perOrderMargin" class="form-input" disabled></el-input>
                </el-form-item>
                <el-form-item label="1手止损的金额">
                    <el-input v-model="calcPosForm.perOrderStopMoney" class="form-input" disabled></el-input>
                </el-form-item>
                <el-form-item label="止损百分比">
                    <el-input v-model="calcPosForm.perOrderStopRate" class="form-input" disabled></el-input>
                </el-form-item>
                <el-form-item label="总保证金">
                    <el-input v-model="calcPosForm.totalOrderMargin" class="form-input" disabled></el-input>
                </el-form-item>
                <el-form-item label="总止损额">
                    <el-input v-model="calcPosForm.totalOrderStopMoney" class="form-input" disabled></el-input>
                </el-form-item>
                <el-form-item label="动止手数">
                    <el-input v-model="calcPosForm.dynamicWinCount" class="form-input" disabled></el-input>
                </el-form-item>
            </el-form>
        </el-row>
        <!--持仓区域-->
        <el-divider content-position="center">持仓列表</el-divider>
        <PositionList :futureSymbolList="futureSymbolList"></PositionList>
        <el-divider content-position="center">信号列表 | 多空分布</el-divider>
        <el-progress :percentage="percentage" :color="customColorMethod" :text-inside="true" :stroke-width="24" ></el-progress>
        <el-row>
            <div class="current-market">
                <el-table
                    v-loading="beichiListLoading"
                    :data=
                        "futureSymbolList.filter(data => !symbolSearch || data.order_book_id.toLowerCase().includes(symbolSearch.toLowerCase()))"
                    size="mini"
                    :stripe="true"
                    :border="true"
                >
                    <el-table-column
                        align="left"
                        width="200">
                        <template slot="header" slot-scope="scope">
                            <el-input
                                v-model="symbolSearch"
                                size="mini"
                                placeholder="搜索">
                                <el-button type="primary" @click="switchStrategy('0')" size="mini" slot="append">刷新
                                </el-button>
                            </el-input>
                        </template>
                        <template slot-scope="scope">
                            <el-link type="primary" :underline="false" @click="jumpToKline(scope.row.order_book_id)">
                                {{scope.row.order_book_id}}
                            </el-link>
                        </template>
                    </el-table-column>
                    <el-table-column
                        label="保证金比率"
                        width="100"
                    >
                        <template slot-scope="scope">
                            <el-link @click="fillMarginRate(scope.row)" :underline="false">
                                {{ (scope.row.margin_rate *marginLevelCompany).toFixed(3)}}
                            </el-link>
                        </template>
                    </el-table-column>

                     <el-table-column
                        label="涨跌幅"
                        width="100"
                    >
                        <template slot-scope="scope">
                            <el-tag effect="dark" :type="changeList[scope.row.order_book_id]|changeTagFilter">
                                 {{ (changeList[scope.row.order_book_id] * (1 / scope.row.margin_rate *marginLevelCompany) *100).toFixed(1)}}%
                            </el-tag>

                        </template>
                    </el-table-column>

                    <el-table-column
                        label="3m">
                        <template slot-scope="scope">
                            <el-tag size="medium"
                                    :type="beichiList[scope.row.order_book_id]['3m'].indexOf('B')!==-1?'danger':'primary'">
                                {{ beichiList[scope.row.order_book_id]['3m'] }}
                            </el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column
                        label="5m">
                        <template slot-scope="scope">
                            <el-tag size="medium"
                                    :type="beichiList[scope.row.order_book_id]['5m'].indexOf('B')!==-1?'danger':'primary'">
                                {{ beichiList[scope.row.order_book_id]['5m'] }}
                            </el-tag>

                        </template>
                    </el-table-column>
                    <el-table-column
                        label="15m">
                        <template slot-scope="scope">
                            <el-tag size="medium"
                                    :type="beichiList[scope.row.order_book_id]['15m'].indexOf('B')!==-1?'danger':'primary'">
                                {{ beichiList[scope.row.order_book_id]['15m'] }}
                            </el-tag>

                        </template>
                    </el-table-column>
                    <el-table-column
                        label="30m">
                        <template slot-scope="scope">
                            <el-tag size="medium"
                                    :type="beichiList[scope.row.order_book_id]['30m'].indexOf('B')!==-1?'danger':'primary'">
                                {{ beichiList[scope.row.order_book_id]['30m'] }}
                            </el-tag>

                        </template>
                    </el-table-column>
                    <el-table-column
                        label="60m">
                        <template slot-scope="scope">
                            <el-tag size="medium"
                                    :type="beichiList[scope.row.order_book_id]['60m'].indexOf('B')!==-1?'danger':'primary'">
                                {{ beichiList[scope.row.order_book_id]['60m'] }}
                            </el-tag>
                        </template>
                    </el-table-column>
                </el-table>
            </div>
        </el-row>
    </div>

</template>

<script src="./js/future-control.js"></script>

<style lang="stylus" scoped>
    @import "../style/futures-control.styl";
</style>