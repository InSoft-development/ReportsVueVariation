<script>
import { ref, onMounted, watch } from 'vue'

import { newPlot, react } from 'plotly.js-dist'

export default {
  name: 'UPlotlyInterval',
  props: {
    intervalDataTarget: Object(),
    intervalDataLayout: Object()
  },
  setup(props) {
    const plotlyInterval = ref(null)
    const plotlyConfig = {
      scrollZoom: true,
      displayModeBar: false
    }

    onMounted(() => {
      newPlot(
        plotlyInterval.value,
        [
          {
            x: props.intervalDataTarget['x'],
            y: props.intervalDataTarget['y'],
            type: props.intervalDataTarget['type']
          }
        ],
        props.intervalDataLayout,
        plotlyConfig
      )
    })

    watch(props, () => {
      react(
        plotlyInterval.value,
        [props.intervalDataTarget],
        props.intervalDataLayout,
        plotlyConfig
      )
    })

    return {
      plotlyInterval
    }
  }
}
</script>

<template>
  <div>
    <div ref="plotlyInterval"></div>
  </div>
</template>
