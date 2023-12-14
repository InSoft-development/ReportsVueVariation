import { ref, reactive } from 'vue'
import { defineStore } from 'pinia'

export const useApplicationStore = defineStore('ApplicationStore', () => {
  const intervals = ref([]) // массив всех интервалов
  const groupIntervals = ref([]) // массив интервалов найденных методом
  const addedIntervals = ref([]) // массив интервалов добавленных пользователем

  const countOfGroups = ref(1) // количество групп оборудования
  const namesOfGroups = ref([]) // наименования групп оборудования

  const leftSpace = ref(1000) // отступ слева для графика
  const rightSpace = ref(1000) // отступ справа для графика
  const pickedOrientation = ref('book') // выбранная в настройках ориентация страниц pdf-отчета

  const minDateFromData = reactive(new Date()) // начальная дата из данных срезов
  const maxDateFromData = reactive(new Date()) // конечная дата из данных срезов

  let dictSelectedCheckbox = Object() // словарь: ключ - полное наименование датчика PLOT;
  // значение -  массив наименований датчиков, отмеченных чекбоксами многоосевого графика

  let dictSensorPlotPalette = Object() // словарь: ключ - полное наименование датчика;
  // значение -  фиксированный цвет датчика
  const plotMain = '#1f77b4'
  const plotPalette = ['#ff7f0e', '#d62728', '#9467bd', '#52a852', '#10E8E7'] // цвета PLOT датчиков

  // сеттер для установки новых значений отступов
  const setSpace = (leftValue, rightValue) => {
    if (leftValue > 50000) leftSpace.value = 50000
    else leftSpace.value = leftValue

    if (rightValue > 50000) rightSpace.value = 50000
    else rightSpace.value = rightValue
  }

  // сеттер для занесения в словарь выбранных чекбоксов
  const setDictSelectedCheckbox = (selectedSignal, selectedMultiAxisSensors) => {
    dictSelectedCheckbox[selectedSignal.value.split(' ')[0]] = selectedMultiAxisSensors.value
  }

  // удаление в словаре ключа выбранных чекбоксов при размонтировании компонента UPlotlyMultiAxises.vue
  const removeFromDictSelectedCheckbox = (selectedSignal) => {
    delete dictSelectedCheckbox[selectedSignal.value.split(' ')[0]]
  }

  // сеттер для заполнения словаря PLOT датчиков
  const setDictSensorPlotPalette = (plotSignals) => {
    for (const [index, plotSignal] of plotSignals.entries()) {
      dictSensorPlotPalette[plotSignal] = plotPalette[index]
    }
  }

  return {
    intervals,
    countOfGroups,
    groupIntervals,
    addedIntervals,
    namesOfGroups,
    leftSpace,
    rightSpace,
    pickedOrientation,
    minDateFromData,
    maxDateFromData,
    dictSelectedCheckbox,
    dictSensorPlotPalette,
    plotMain,
    plotPalette,
    setSpace,
    setDictSelectedCheckbox,
    removeFromDictSelectedCheckbox,
    setDictSensorPlotPalette
  }
})
