<template>
    <div class="multi-period-main">
        <div class="input-form">
            <el-button type="primary" @click="jumpToControl('futures')" size="mini">期货总控</el-button>
            <el-button type="danger" @click="jumpToControl('stock')" size="mini">股票总控</el-button>
            <el-date-picker
                v-model="endDate"
                type="date"
                placeholder="选择日期"
                format="yyyy 年 MM 月 dd 日"
                value-format="yyyy-MM-dd"
                size="mini"
                @change="submitSymbol"
                class="ml-5 mr-5">
            </el-date-picker>
            <el-button @click="quickSwitchDay('pre')" size="mini">前一天</el-button>
            <el-button @click="quickSwitchDay('next')" size="mini">后一天</el-button>
            <el-input v-model="inputSymbol" placeholder="请输入股票代码" size="mini" class="stock-input ml-5" @change="submitSymbol"/>
            <el-button v-for="period in periodList" :key="period" size="mini" @click="switchPeriod(period)">{{period}}</el-button>
            快速计算开仓手数：
            <el-input v-model="quickCalc.openPrice" placeholder="开仓" size="mini" class="stock-input-short ml-5 mr-5"></el-input>
            <el-input v-model="quickCalc.stopPrice" placeholder="止损" size="mini" class="stock-input-short ml-5 mr-5" @change="quickCalcMaxCount"></el-input>
            <el-button size="mini" type="success" @click="quickCalcMaxCount">计算</el-button>
            开仓手数：<el-tag type="danger" class="ml-5">{{quickCalc.count}}</el-tag>
            止损率：<el-tag type="danger" class="ml-5">{{(quickCalc.stopRate* 100).toFixed(2)}}%</el-tag>
            1手止损：<el-tag type="danger" class="ml-5">{{quickCalc.perOrderStopMoney}}</el-tag>
        </div>

        <div class="echarts-list">
            <div class="echarts-item" id="main3Parent">
                <div id="main3" class="echarts">
                </div>
            </div>
            <div class="echarts-item" id="main15Parent">
                <div id="main15" class="echarts">
                </div>
            </div>
            <div class="echarts-item" id="main60Parent">
                <div id="main60" class="echarts">
                </div>
            </div>

            <div class="echarts-item" id="main5Parent">
                <div id="main5" class="echarts">
                </div>
            </div>
            <div class="echarts-item" id="main30Parent">
                <div id="main30" class="echarts">
                </div>
            </div>
            <div class="echarts-item" id="main240Parent" v-if="!isShow1Min">
                <div id="main240" class="echarts">
                </div>
            </div>
            <div class="echarts-item" id="main1Parent" v-else>
                <div id="main1" class="echarts">
                </div>
            </div>
            <!--   <div class="echarts-item">
                   <div id="main1d" class="echarts">
                   </div>
               </div>-->
        </div>
    </div>
</template>
<script src="./js/multi-period.js"></script>
<style lang="stylus" scoped>
    @import "../style/multi-period.styl";
</style>
