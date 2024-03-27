<script>
import { ref, onMounted, watch } from 'vue'

import { newPlot, react } from 'plotly.js-dist'

export default {
  name: 'PlotlyMultiAxises',
  props: {
    intervalDataTarget: Array(),
    intervalDataLayout: Object()
  },
  setup(props) {
    const plotlyMulti = ref(null)
    const plotlyConfig = {
      scrollZoom: true,
      displayModeBar: false
    }

    onMounted(() => {
      newPlot(plotlyMulti.value, props.intervalDataTarget, props.intervalDataLayout, plotlyConfig)
    })

    watch(props, () => {
      react(plotlyMulti.value, props.intervalDataTarget, props.intervalDataLayout, plotlyConfig)
    })

    return {
      plotlyMulti
    }
  }
}
</script>

<template>
  <!-- <div > -->
    <div ref="plotlyMulti"></div>
  <!-- </div> -->
</template>

<style>
/* .graf{
  background: green;
  right: 120px;
} */
/* .Graf{
  
  clip-path: inset(0px 0px 0px 120px);
} */
/* .js-plotly-plot .plotly .main-svg{
  clip-path: inset(0px 0px 0px 120px);
} */
</style>
