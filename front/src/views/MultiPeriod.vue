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
                class="ml-5">
            </el-date-picker>
            <el-input v-model="inputSymbol" placeholder="请输入股票代码" size="mini" class="stock-input ml-5" @change="submitSymbol"/>
        </div>

        <div class="echarts-list">
            <div class="echarts-item">
                <div id="main3" class="echarts">
                </div>
            </div>
            <div class="echarts-item">
                <div id="main15" class="echarts">
                </div>
            </div>
            <div class="echarts-item">
                <div id="main60" class="echarts">
                </div>
            </div>

            <div class="echarts-item">
                <div id="main5" class="echarts">
                </div>
            </div>
            <div class="echarts-item">
                <div id="main30" class="echarts">
                </div>
            </div>
            <div class="echarts-item">
                <div id="main240" class="echarts">
                </div>
            </div>
            <!--   <div class="echarts-item">
                   <div id="main1d" class="echarts">
                   </div>
               </div>-->

            <!--   <div class="echarts-item">
                   <div id="main1" class="echarts">
                   </div>
               </div>-->
        </div>
    </div>
</template>
<script src="./js/multi-period.js"></script>
<style lang="stylus" scoped>
    @import "../style/multi-period.styl";
</style>
