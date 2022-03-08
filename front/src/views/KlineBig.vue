<template>
    <div class="kline-big-main">
        <KlineHeader ref="klineHeader" :periodList="periodList" :endDate="endDate" :inputSymbol="inputSymbol" :quickCalc="quickCalc"
                     :submitSymbol="submitSymbol" :quickCalcMaxCount="quickCalcMaxCount" :quickSwitchDay="quickSwitchDay"
                     :switchPeriod="switchPeriod" :jumpToControl="jumpToControl" :showPeriodList="true" :changeDate="changeDate" :jumpToMultiPeriod="jumpToMultiPeriod"
                     :quickSwitchSymbol="quickSwitchSymbol" :futureSymbolList="futureSymbolList" :themeOptions="themeOptions"
                     :brushOptions="brushOptions" :showBrushSwitch="true" :changeBiType="changeBiType" :biType="biType" :changeSecondChance="changeSecondChance"
                     :secondChance="secondChance"
        ></KlineHeader>
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
