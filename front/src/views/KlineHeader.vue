<template>
    <div class="kline-header-main">
        <div class="input-form">
            <el-button type="primary" @click="jumpToControl('futures')" size="mini" class="primary-button">期货</el-button>
            <el-button type="danger" @click="jumpToControl('stock')" size="mini" class="primary-button">股票</el-button>
            <el-button type="success" @click="jumpToMultiPeriod" size="mini" v-if="showPeriodList" class="primary-button">多周期</el-button>
            <el-date-picker
                v-model="endDate_"
                type="date"
                placeholder="选择日期"
                format="yyyy 年 MM 月 dd 日"
                value-format="yyyy-MM-dd"
                size="mini"
                @change="changeDate"
                class="ml-5 mr-5">
            </el-date-picker>
            <el-button type="primary" class="primary-button" @click="quickSwitchDay('pre')" size="mini">前一天</el-button>
            <el-button type="primary" class="primary-button" @click="quickSwitchDay('next')" size="mini">后一天</el-button>
            <el-input v-model="inputSymbol_" placeholder="请输入代码" size="mini" class="search-symbol-input ml-5 mr-5" @change="submitSymbol"/>
            <el-button type="primary" class="primary-button" v-for="period in periodList" :key="period" size="mini" @click="switchPeriod(period)"
                       v-if="showPeriodList">{{period}}
            </el-button>
            计算开仓手数：
            <el-input v-model="quickCalc.openPrice" placeholder="开仓价" size="mini" class="input-short ml-5 mr-5"></el-input>
            <el-input v-model="quickCalc.stopPrice" placeholder="止损价" size="mini" class="input-short ml-5 mr-5" @change="quickCalcMaxCount"></el-input>
            <el-button size="mini" type="primary" class="primary-button" @click="quickCalcMaxCount">计算</el-button>
            开仓手数：<span class="up-red ml-5">{{quickCalc.count}}</span>
            止损率：<span class="up-red ml-5">{{(quickCalc.stopRate* 100).toFixed(2)}}%</span>
            1手止损：<span class="up-red ml-5">{{quickCalc.perOrderStopMoney}}</span>
        </div>
    </div>
</template>
<script>
    export default {
        name: "KlineHeader",
        data() {
            return {
                inputSymbol_: this.inputSymbol,
                endDate_: this.endDate
            }
        },
        props: {
            showPeriodList: {
                type: Boolean,
                default: false
            },
            quickCalc: {
                type: Object,
                default: null
            },
            submitSymbol: {
                type: Function,
                default: null
            },
            quickCalcMaxCount: {
                type: Function,
                default: null
            },
            quickSwitchDay: {
                type: Function,
                default: null
            },
            switchPeriod: {
                type: Function,
                default: null
            },
            jumpToControl: {
                type: Function,
                default: null
            },
            changeDate: {
                type: Function,
                default: null
            },
            jumpToMultiPeriod: {
                type: Function,
                default:null
            },
            periodList: {
                type: Array,
                default: null
            },
            inputSymbol: null,
            endDate: null
        },
        methods: {
            setELDatePicker(endDate) {
                this.endDate_ = endDate
            }
        }
    }
</script>
<style lang="stylus">
    @import "../style/kline-header.styl";
</style>
