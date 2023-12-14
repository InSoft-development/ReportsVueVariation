import UPlotlyInterval from './UPlotlyInterval.vue'
import UAddedRow from './UAddedRow.vue'

const components = [
  {
    name: 'UPlotlyInterval',
    component: UPlotlyInterval
  },
  {
    name: 'UAddedRow',
    component: UAddedRow
  }
]

export default {
  install(app) {
    components.forEach(({ name, component }) => {
      app.component(name, component)
    })
  }
}
