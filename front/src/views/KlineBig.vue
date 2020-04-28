<template>
    <div class="kline-big-main">
        <KlineHeader :periodList="periodList" :endDate="endDate" :inputSymbol="inputSymbol" :quickCalc="quickCalc"
        :submitSymbol="submitSymbol" :quickCalcMaxCount="quickCalcMaxCount" :quickSwitchDay="quickSwitchDay" :switchPeriod="switchPeriod" :jumpToControl="jumpToControl" :showPeriodList="true"></KlineHeader>
        <div class="echarts-item-big" id="mainParent">
            <div id="main">
            </div>
        </div>
    </div>
</template>
<script src="./js/kline-big.js"></script>
<style lang="stylus">
    @import "../style/kline-big.styl";
</style>
