<template>
    <div class="kline-big-main">
        <div class="input-form">
            <el-button type="primary" @click="jumpToControl('futures')" size="mini">期货总控</el-button>
            <el-button type="danger" @click="jumpToControl('stock')" size="mini">股票总控</el-button>
            <el-button type="success" @click="jumpToMultiPeriod" size="mini">多周期</el-button>
            <el-date-picker
                v-model="endDate"
                type="date"
                placeholder="选择日期"
                format="yyyy 年 MM 月 dd 日"
                value-format="yyyy-MM-dd"
                size="mini"
                @change="submitSymbol"
                class="ml-5 mr-5"
            >
            </el-date-picker>
            <el-button @click="quickSwitchDay('pre')" size="mini">前一天</el-button>
            <el-button @click="quickSwitchDay('next')" size="mini">后一天</el-button>
            <el-input v-model="inputSymbol" placeholder="期货股票代码回车提交" size="mini" class="stock-input ml-5"
                      @change="submitSymbol"/>
            <el-button v-for="period in periodList" :key="period" size="mini" @click="switchPeriod(period)" class="ml-5">{{period}}</el-button>
        </div>
        <div class="echarts-item-big" id="mainParent">
            <div id="main">
            </div>
        </div>
    </div>
</template>
<script src="./js/kline-big.js"></script>
<style lang="stylus" scoped>
    @import "../style/kline-big.styl";
</style>
