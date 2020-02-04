<template>
    <div class="kline-big-main">
        <div class="input-form">
            <el-button type="primary" @click="jumpToControl" size="mini">期货总控</el-button>
            <el-button type="danger" @click="jumpToControl" size="mini">股票总控</el-button>
            <el-button type="success" @click="jumpToMultiPeriod" size="mini">多周期</el-button>
            <el-date-picker
                v-model="endDate"
                type="date"
                placeholder="选择日期"
                format="yyyy 年 MM 月 dd 日"
                value-format="yyyy-MM-dd"
                size="mini">
            </el-date-picker>
            <!--            <el-button size="mini" v-for="symbolInfo in futureSymbolList" @click="switchHistorySymbol(symbolInfo.order_book_id)">-->
            <!--                {{ symbolInfo.underlying_symbol }}-->
            <!--            </el-Button>-->
            <el-select v-model="selectedSymbol" placeholder="请选择品种" size="mini">
                <el-option
                    v-for="symbolInfo in futureSymbolList"
                    :key="symbolInfo.order_book_id"
                    :label="symbolInfo.underlying_symbol"
                    :value="symbolInfo.order_book_id">
                </el-option>
            </el-select>
            <el-input v-model="inputSymbol" placeholder="请输入股票代码" size="mini" class="stock-input"></el-input>
            <el-button @click="submitSymbol" size="mini"> 提交</el-button>
        </div>

        <div class="echarts-list-big">
            <div class="echarts-item-big" id="3m">
                <div id="main3" class="echarts-big">
                </div>
            </div>
            <div class="echarts-item-big" id="15m">
                <div id="main15" class="echarts-big">
                </div>
            </div>
            <div class="echarts-item-big" id="60m">
                <div id="main60" class="echarts-big">
                </div>
            </div>

            <div class="echarts-item-big" id="5m">
                <div id="main5" class="echarts-big">
                </div>
            </div>
            <div class="echarts-item-big" id="30m">
                <div id="main30" class="echarts-big">
                </div>
            </div>
            <div class="echarts-item-big" id="240m">
                <div id="main240" class="echarts-big">
                </div>
            </div>
            <!--   <div class="echarts-item-big">
                   <div id="main1d" class="echarts-big">
                   </div>
               </div>-->

            <!--   <div class="echarts-item-big">
                   <div id="main1" class="echarts-big">
                   </div>
               </div>-->
        </div>
    </div>
</template>
<script src="./js/kline-big.js"></script>
<style lang="stylus" scoped>
    @import "../style/kline-big.styl";

</style>
