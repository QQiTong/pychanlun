<template>
    <div class="future-control-main">
        <MyHeader/>
        <!--仓位计算-->
        <el-divider content-position="center">仓位计算器</el-divider>
        <el-row>
            <el-form :inline="true" size="mini" :model="calcPosForm" class="demo-form-inline">
                <el-form-item label="资产总额">
                    <el-input v-model="calcPosForm.account" class="form-input "/>
                </el-form-item>
                <el-form-item label="保证金系数">
                    <el-input v-model="calcPosForm.currentMarginRate" class="form-input " disabled/>
                </el-form-item>
                <el-form-item label="杠杠倍数">
                    <el-input v-model="calcPosForm.marginLevel" class="form-input " disabled/>
                </el-form-item>
                <el-form-item label="合约乘数">
                    <el-input v-model="calcPosForm.contractMultiplier" class="form-input " disabled/>
                </el-form-item>
                <el-form-item label="开仓价格">
                    <el-input v-model="calcPosForm.openPrice" class="form-input"/>
                </el-form-item>
                <el-form-item label="止损价格">
                    <el-input v-model="calcPosForm.stopPrice" class="form-input"/>
                </el-form-item>
                <el-form-item label="动止价(选填)">
                    <el-input v-model="calcPosForm.dynamicWinPrice" class="form-input"/>
                </el-form-item>
                <el-form-item label="最大资金使用率">
                    <el-select v-model="calcPosForm.maxAccountUseRate" class="select-input">
                        <el-option label="10%" value="0.1"/>
                        <el-option label="20%" value="0.2"/>
                        <el-option label="30%" value="0.3"/>
                    </el-select>
                </el-form-item>
                <el-form-item label="止损系数">
                    <el-select v-model="calcPosForm.stopRate" class="select-input">
                        <el-option label="1%" value="0.01"/>
                        <el-option label="2%" value="0.02"/>
                        <el-option label="3%" value="0.03"/>
                    </el-select>
                </el-form-item>
                <el-form-item>
                    <el-button type="primary" @click="calcAccount">查询</el-button>
                </el-form-item>
                <el-form-item label="开仓手数">
                    <el-input v-model="calcPosForm.maxOrderCount" class="form-input " disabled/>
                </el-form-item>
                <el-form-item label="资金使用率">
                    <el-input v-model="calcPosForm.accountUseRate" class="form-input " disabled/>
                </el-form-item>
                <el-form-item label="1手保证金">
                    <el-input v-model="calcPosForm.perOrderMargin" class="form-input " disabled/>
                </el-form-item>
                <el-form-item label="1手止损的金额">
                    <el-input v-model="calcPosForm.perOrderStopMoney" class="form-input " disabled/>
                </el-form-item>
                <el-form-item label="止损百分比">
                    <el-input v-model="calcPosForm.perOrderStopRate" class="form-input " disabled/>
                </el-form-item>
                <el-form-item label="总保证金">
                    <el-input v-model="calcPosForm.totalOrderMargin" class="form-input" disabled/>
                </el-form-item>
                <el-form-item label="总止损额">
                    <el-input v-model="calcPosForm.totalOrderStopMoney" class="form-input" disabled/>
                </el-form-item>
                <el-form-item label="动止手数">
                    <el-input v-model="calcPosForm.dynamicWinCount" class="form-input" disabled/>
                </el-form-item>
            </el-form>
        </el-row>
        <!--持仓区域-->
        <el-divider content-position="center">持仓列表</el-divider>
        <FuturePositionList
            :futureSymbolList="futureSymbolList"
            :futureSymbolMap="futureSymbolMap"
            :marginLevelCompany="marginLevelCompany"
        />
        <el-divider content-position="center">信号列表 | 多空分布 | 内盘 | 外盘</el-divider>
        <el-progress
            :percentage="percentage"
            :color="customColorMethod"
            :text-inside="true"
            :stroke-width="24"
        />
        <el-progress
            :percentage="globalFuturePercentage"
            :color="customColorMethod"
            :text-inside="true"
            :stroke-width="24"
            class="mt-5"
        />
        <el-tabs v-model="activeTab" type="card" @tab-click="handleChangeTab" class="mt-5">
            <el-tab-pane label="最新行情" name="first">
                <el-row>
                    <div class="current-market">
                        <el-table
                            v-loading="beichiListLoading"
                            :data="futureSymbolList.filter(data => !symbolSearch || data.order_book_id.toLowerCase().includes(symbolSearch.toLowerCase()))"
                            size="mini"
                            :stripe="true"
                            :border="true"
                        >
                            <el-table-column align="left" width="80">
                                <template slot="header" slot-scope="scope">
                                    <el-input v-model="symbolSearch" size="mini" placeholder="搜索">
                                        <!--                                <el-button type="primary" @click="getSignalList" size="mini" slot="append">刷新-->
                                        <!--                                </el-button>-->
                                    </el-input>
                                </template>
                                <template slot-scope="scope">
                                    <el-link
                                        type="primary"
                                        :underline="false"
                                        @click="jumpToKline(scope.row.order_book_id)"
                                    >{{scope.row.order_book_id}}
                                    </el-link>
                                </template>
                            </el-table-column>
                            <el-table-column label="保证金率" width="80">
                                <template slot-scope="scope">
                                    <el-link
                                        @click="fillMarginRate(scope.row,changeList && changeList[scope.row.order_book_id]?
                                changeList[scope.row.order_book_id]['price'] : 0)"
                                        :underline="false" v-if="scope.row.order_book_id.indexOf('BTC')===-1"
                                    >{{ (scope.row.margin_rate +marginLevelCompany).toFixed(3)}}
                                    </el-link>
                                    <el-link
                                        @click="fillMarginRate(scope.row,btcTicker.price)"
                                        :underline="false" v-else
                                    >{{ (scope.row.margin_rate).toFixed(3)}}
                                    </el-link>
                                </template>
                            </el-table-column>
                            <el-table-column label="涨跌幅" width="90">
                                <template slot-scope="scope">
                                    <el-tag
                                        effect="dark"
                                        :type="changeList && changeList[scope.row.order_book_id]? changeList[scope.row.order_book_id]['change'] : 0|changeTagFilter"
                                        v-if="scope.row.order_book_id.indexOf('BTC')===-1"
                                    >
                                        {{ ((changeList && changeList[scope.row.order_book_id]?
                                        changeList[scope.row.order_book_id]['change'] : 0) * (1 /( scope.row.margin_rate
                                        +marginLevelCompany)) *100).toFixed(1)}}%
                                    </el-tag>
                                    <el-tag
                                        effect="dark"
                                        :type="btcTicker.change|changeTagFilter"
                                        v-else
                                    >
                                        {{ ((btcTicker.change?btcTicker.change:0) * (1 /scope.row.margin_rate)
                                        *100).toFixed(1)}}%
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <el-table-column label="最新价" width="70">
                                <template slot-scope="scope">
                    <span v-if="scope.row.order_book_id.indexOf('BTC')===-1">
                        {{(changeList && changeList[scope.row.order_book_id]?
                        changeList[scope.row.order_book_id]['price'] : 0)}}
                    </span>
                                    <span v-else>
                        {{btcTicker.price}}
                    </span>
                                </template>
                            </el-table-column>
                            <el-table-column label="多空走势" width="500">
                                <template slot-scope="scope">
                                    <!--                                    <el-tag-->
                                    <!--                                        size="medium"-->
                                    <!--                                        :type="levelDirectionList&&levelDirectionList[scope.row.order_book_id]?-->
                                    <!--                            levelDirectionList[scope.row.order_book_id]['3m']==='多'?'danger':'primary'-->
                                    <!--                            :'info'"-->
                                    <!--                                    >{{-->
                                    <!--                                        levelDirectionList&&levelDirectionList[scope.row.order_book_id]?levelDirectionList[scope.row.order_book_id]['3m']:''-->
                                    <!--                                        }}-->
                                    <!--                                    </el-tag>-->
                                    <el-progress
                                        :percentage="beichiList[scope.row.order_book_id]['percentage']"
                                        :color="customColorMethod"
                                        :text-inside="true"
                                        :stroke-width="24"
                                        class="mt-5"
                                    ></el-progress>
                                </template>
                            </el-table-column>
                            <el-table-column label="3m">
                                <template slot-scope="scope">
                                    <el-tag
                                        size="medium"
                                        :type="beichiList[scope.row.order_book_id]['3m'].indexOf('B')!==-1?'danger':'primary'"
                                    >{{ beichiList[scope.row.order_book_id]['3m'] }}
                                    </el-tag>
                                </template>
                            </el-table-column>

                            <!--                            <el-table-column label="5F级别" width="65">-->
                            <!--                                <template slot-scope="scope">-->
                            <!--                                    <el-tag-->
                            <!--                                        size="medium"-->
                            <!--                                        class="mr-5"-->
                            <!--                                        :type="levelDirectionList&&levelDirectionList[scope.row.order_book_id]?-->
                            <!--                            levelDirectionList[scope.row.order_book_id]['5m']==='多'?'danger':'primary'-->
                            <!--                            :'info'"-->
                            <!--                                    >{{-->
                            <!--                                        levelDirectionList&&levelDirectionList[scope.row.order_book_id]?levelDirectionList[scope.row.order_book_id]['5m']:''-->
                            <!--                                        }}-->
                            <!--                                    </el-tag>-->
                            <!--                                </template>-->
                            <!--                            </el-table-column>-->
                            <el-table-column label="5m">
                                <template slot-scope="scope">
                                    <el-tag
                                        size="medium"
                                        :type="beichiList[scope.row.order_book_id]['5m'].indexOf('B')!==-1?'danger':'primary'"
                                    >{{ beichiList[scope.row.order_book_id]['5m'] }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <!--                            <el-table-column label="15F级别" width="70">-->
                            <!--                                <template slot-scope="scope">-->
                            <!--                                    <el-tag-->
                            <!--                                        size="medium"-->
                            <!--                                        class="mr-5"-->
                            <!--                                        :type="levelDirectionList&&levelDirectionList[scope.row.order_book_id]?-->
                            <!--                            levelDirectionList[scope.row.order_book_id]['15m']==='多'?'danger':'primary'-->
                            <!--                            :'info'"-->
                            <!--                                    >{{-->
                            <!--                                        levelDirectionList&&levelDirectionList[scope.row.order_book_id]?levelDirectionList[scope.row.order_book_id]['15m']:''-->
                            <!--                                        }}-->
                            <!--                                    </el-tag>-->
                            <!--                                </template>-->
                            <!--                            </el-table-column>-->
                            <el-table-column label="15m">
                                <template slot-scope="scope">
                                    <el-tag
                                        size="medium"
                                        :type="beichiList[scope.row.order_book_id]['15m'].indexOf('B')!==-1?'danger':'primary'"
                                    >{{ beichiList[scope.row.order_book_id]['15m'] }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <!--                            <el-table-column label="30F级别" width="70">-->
                            <!--                                <template slot-scope="scope">-->
                            <!--                                    <el-tag-->
                            <!--                                        size="medium"-->
                            <!--                                        class="mr-5"-->
                            <!--                                        :type="levelDirectionList&&levelDirectionList[scope.row.order_book_id]?-->
                            <!--                            levelDirectionList[scope.row.order_book_id]['30m']==='多'?'danger':'primary'-->
                            <!--                            :'info'"-->
                            <!--                                    >{{-->
                            <!--                                        levelDirectionList&&levelDirectionList[scope.row.order_book_id]?levelDirectionList[scope.row.order_book_id]['30m']:''-->
                            <!--                                        }}-->
                            <!--                                    </el-tag>-->
                            <!--                                </template>-->
                            <!--                            </el-table-column>-->
                            <el-table-column label="30m">
                                <template slot-scope="scope">
                                    <el-tag
                                        size="medium"
                                        :type="beichiList[scope.row.order_book_id]['30m'].indexOf('B')!==-1?'danger':'primary'"
                                    >{{ beichiList[scope.row.order_book_id]['30m'] }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                            <!--                            <el-table-column label="60F级别" width="70">-->
                            <!--                                <template slot-scope="scope">-->
                            <!--                                    <el-tag-->
                            <!--                                        size="medium"-->
                            <!--                                        class="mr-5"-->
                            <!--                                        :type="levelDirectionList&&levelDirectionList[scope.row.order_book_id]?-->
                            <!--                            levelDirectionList[scope.row.order_book_id]['60m']==='多'?'danger':'primary'-->
                            <!--                            :'info'"-->
                            <!--                                    >{{-->
                            <!--                                        levelDirectionList&&levelDirectionList[scope.row.order_book_id]?levelDirectionList[scope.row.order_book_id]['60m']:''-->
                            <!--                                        }}-->
                            <!--                                    </el-tag>-->
                            <!--                                </template>-->
                            <!--                            </el-table-column>-->
                            <el-table-column label="60m">
                                <template slot-scope="scope">
                                    <el-tag
                                        size="medium"
                                        :type="beichiList[scope.row.order_book_id]['60m'].indexOf('B')!==-1?'danger':'primary'"
                                    >{{ beichiList[scope.row.order_book_id]['60m'] }}
                                    </el-tag>
                                </template>
                            </el-table-column>
                        </el-table>
                    </div>
                </el-row>
            </el-tab-pane>
            <el-tab-pane label="每日复盘" name="second">
                <el-row>
                    <div class="prejudge-form">
                        <el-date-picker
                            v-model="endDate"
                            type="date"
                            placeholder="选择日期"
                            format="yyyy 年 MM 月 dd 日"
                            value-format="yyyy-MM-dd"
                            size="mini"
                            @change="changePrejudgeDate"
                            class="ml-5 mr-5"
                        ></el-date-picker>
                        <el-button
                            @click="createOrUpdatePrejudgeList('create')"
                            type="primary"
                            size="mini"
                            v-if="prejudgeTableStatus ==='current'"
                            :loading="btnPrejudgeLoading"
                        >新增
                        </el-button>
                        <el-button
                            @click="createOrUpdatePrejudgeList('update')"
                            type="danger"
                            size="mini"
                            v-if="prejudgeTableStatus ==='history'"
                            :loading="btnPrejudgeLoading"
                        >更新
                        </el-button>
                    </div>

                    <div class="current-market mt-5">
                        <div>
                            <!-- 新增 使用主力合约 -->
                            <el-table :data="prejudgeFormList" v-if="prejudgeTableStatus==='current'">
                                <el-table-column label="品种" width="100">
                                    <template slot-scope="scope">{{scope.row.order_book_id}}</template>
                                </el-table-column>

                                <el-table-column width="80">
                                    <el-button
                                        @click="createOrUpdatePrejudgeList('create')"
                                        type="primary"
                                        size="mini"
                                        v-if="prejudgeTableStatus ==='current'"
                                        :loading="btnPrejudgeLoading"
                                    >新增
                                    </el-button>
                                    <el-button
                                        @click="createOrUpdatePrejudgeList('update')"
                                        type="danger"
                                        size="mini"
                                        v-if="prejudgeTableStatus ==='history'"
                                        :loading="btnPrejudgeLoading"
                                    >更新
                                    </el-button>

                                </el-table-column>
                                <el-table-column label="走势预判">
                                    <template slot-scope="scope">
                                        <input
                                            type="text"
                                            v-model="prejudgeFormMap[scope.row.order_book_id]"
                                            class="prejudge-input"
                                            @keyup.enter="onInputChange"
                                        />
                                    </template>
                                </el-table-column>
                            </el-table>
                            <!-- 更新 不一定是主力合约-->
                            <el-table :data="historyPrejudgeList" v-if="prejudgeTableStatus==='history'">
                                <el-table-column label="历史品种" width="100">
                                    <template slot-scope="scope">{{scope.row}}</template>
                                </el-table-column>
                                <el-table-column width="80">
                                    <el-button
                                        @click="createOrUpdatePrejudgeList('create')"
                                        type="primary"
                                        size="mini"
                                        v-if="prejudgeTableStatus ==='current'"
                                        :loading="btnPrejudgeLoading"
                                    >新增
                                    </el-button>
                                    <el-button
                                        @click="createOrUpdatePrejudgeList('update')"
                                        type="danger"
                                        size="mini"
                                        v-if="prejudgeTableStatus ==='history'"
                                        :loading="btnPrejudgeLoading"
                                    >更新
                                    </el-button>
                                </el-table-column>
                                <el-table-column label="历史走势预判">
                                    <template slot-scope="scope">
                                        <!-- {{historyPrejudgeMap[scope.row]}} -->
                                        <input
                                            type="text"
                                            v-model="historyPrejudgeMap[scope.row]"
                                            class="prejudge-input"
                                            @keyup.enter="onInputChange"
                                        />
                                    </template>
                                </el-table-column>
                            </el-table>
                        </div>
                    </div>
                </el-row>
            </el-tab-pane>
            <el-tab-pane label="统计数据" name="third">
                <StatisticsChat></StatisticsChat>
            </el-tab-pane>
        </el-tabs>
    </div>
</template>

<script src="./js/future-control.js"></script>

<style lang="stylus">
    @import '../style/futures-control.styl';
</style>