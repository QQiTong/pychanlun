<template>
    <div class="kline-header-main">
        <div class="input-form">
            <el-button type="primary" @click="jumpToControl('futures')" size="mini" class="primary-button">期货
            </el-button>
            <el-button type="danger" @click="jumpToControl('stock')" size="mini" class="primary-button">股票</el-button>
            <el-button type="success" @click="jumpToMultiPeriod" size="mini" v-if="showPeriodList"
                       class="primary-button">多周期
            </el-button>
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
            <el-input v-model="inputSymbol_" placeholder="请输入代码" size="mini" class="search-symbol-input ml-5 mr-5"
                      @change="submitSymbol"/>
            <el-button type="primary" class="primary-button" v-for="period in periodList" :key="period" size="mini"
                       @click="switchPeriod(period)"
                       v-if="showPeriodList">{{period}}
            </el-button>
            计算开仓手数：
            <el-input v-model="quickCalc.openPrice" placeholder="开仓价" size="mini"
                      class="input-short ml-5 mr-5"></el-input>
            <el-input v-model="quickCalc.stopPrice" placeholder="止损价" size="mini" class="input-short ml-5 mr-5"
                      @change="quickCalcMaxCount"></el-input>
            <el-input v-model="quickCalc.dynamicWinPrice" placeholder="动止价" size="mini" class="input-short ml-5 mr-5"
                      @change="quickCalcMaxCount"></el-input>
            <el-button size="mini" type="primary" class="primary-button" @click="quickCalcMaxCount">计算</el-button>
            开仓手数：<span class="up-red ml-5">{{quickCalc.count}}</span>
            止损率：<span class="up-red ml-5">{{(quickCalc.stopRate* 100).toFixed(2)}}%</span>
            1手止损：<span class="up-red ml-5">{{quickCalc.perOrderStopMoney}}</span>
            动止手数：<span class="up-red ml-5 mr-5">{{quickCalc.dynamicWinCount}}</span>
            <!--            <el-button size="mini" type="primary" class="primary-button ml-5" @click="quickSwitchSymbol('RU2009')">RU2009</el-button>-->
            <!--            <el-button size="mini" type="primary" class="primary-button" @click="quickSwitchSymbol('RB2010')">RB2010</el-button>-->
            <!--            <el-button size="mini" type="primary" class="primary-button" @click="quickSwitchSymbol('MA2009')">MA2009</el-button>-->
            <!--            <el-button size="mini" type="primary" class="primary-button" @click="quickSwitchSymbol('M2009')">M2009</el-button>-->
            <!--            <el-button size="mini" type="primary" class="primary-button" @click="quickSwitchSymbol('Y2009')">Y2009</el-button>-->
            <!--            <el-button size="mini" type="primary" class="primary-button" @click="quickSwitchSymbol('RM2009')">RM2009</el-button>-->
            <!--            <el-button size="mini" type="primary" class="primary-button" @click="quickSwitchSymbol('NI2007')">NI2007</el-button>-->
            <el-select size="mini" v-model="inputSymbol_" class="form-input" placeholder="请选择"
                       @change="quickSwitchSymbol(inputSymbol_)">
                <el-option
                    v-for="item in futureSymbolList"
                    :key="item.order_book_id"
                    :label="item.order_book_id"
                    :value="item.order_book_id"
                />
            </el-select>
            <el-popover
                placement="bottom"
                width="250"
                trigger="hover">
                <el-table :data="shortCutData">
                    <el-table-column width="100" property="name" label="快捷键"></el-table-column>
                    <el-table-column width="100" property="desc" label="说明"></el-table-column>
                </el-table>
                <el-button slot="reference" type="primary" class="primary-button" size="mini">快捷键</el-button>
            </el-popover>
        </div>
    </div>
</template>
<script>
    export default {
        name: "KlineHeader",
        data() {
            return {
                inputSymbol_: this.inputSymbol,
                endDate_: this.endDate,
                shortCutData: [{
                    name: 'Space',
                    desc: '裸K',
                }, {
                    name: 'PageUp',
                    desc: '上一合约',
                }, {
                    name: 'PageDw',
                    desc: '下一合约',
                }, {
                    name: 'Left',
                    desc: '上一日',
                }, {
                    name: 'Right',
                    desc: '下一日',
                }, {
                    name: 'Up',
                    desc: '放大',
                }, {
                    name: 'Down',
                    desc: '缩小',
                }, {
                    name: 'Num1',
                    desc: '1分钟',
                }, {
                    name: 'Num2',
                    desc: '3分钟',
                }, {
                    name: 'Num3',
                    desc: '5分钟',
                }, {
                    name: 'Num4',
                    desc: '15分钟',
                }, {
                    name: 'Num5',
                    desc: '30分钟',
                }, {
                    name: 'Num6',
                    desc: '60分钟',
                }, {
                    name: 'Num7',
                    desc: '180分钟',
                }, {
                    name: 'Num8',
                    desc: '日线',
                }]
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
                default: null
            },
            quickSwitchSymbol: {
                type: Function,
                default: null
            },
            periodList: {
                type: Array,
                default: null
            },
            inputSymbol: null,
            endDate: null,
            futureSymbolList: {
                type: Array,
                default: null
            }
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
