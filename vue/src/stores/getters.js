import { useApplicationStore } from './applicationStore'

/**
 * Процедура заполняет объект меню сайдбара, маршрутные вкладки tabMenu и
 * сохраняет аномальные интервалы в хранилище pinia
 * @param method наименование выбранного метода
 * @param group номер выбранной группы
 * @param sidebarMenu изменяемый reactive объект sidebarMenu для подстановки в App.vue
 * @param tabMenu изменяемый ref массив tabMenu для создания табов в App.vue
 * @param widthTab изменяемое ref число для корректного отображения tabMenu
 */
export async function getSidebarMenu(method, group, sidebarMenu, tabMenu, widthTab) {
  const applicationStore = useApplicationStore()
  tabMenu.value = [
    {
      label: 'Главная',
      route: '/'
    }
  ]
  // получение с eel найденных аномальных интервалов и их сохранение в pinia
  let intervalArray = await eel.get_interval_time_array(method, group)()

  applicationStore.intervals.value = await intervalArray
  widthTab.value = String((applicationStore.intervals.value.length + 1) * 350) + 'px'
  console.log(widthTab.value)

  let childIntervalArray = Array() // найденные аномальные интервалы для подстановки в sideBarMenu

  // цикл для формирования дочернего выпадающего меню интервалов
  for (let i = 0; i < intervalArray.length; i++) {
    let href_child = `/interval/${i}`
    let title_child = `${intervalArray[i][0]}-${intervalArray[i][1]}`
    childIntervalArray.push({
      href: href_child,
      title: title_child,
      hiddenOnCollapse: true
    })
    tabMenu.value.push({
      label: title_child,
      route: href_child
    })
  }

  // заполненный объект меню сайдбара
  sidebarMenu.menu = [
    {
      header: 'Меню',
      hiddenOnCollapse: true
    },
    {
      href: '/',
      title: 'Интервалы',
      hiddenOnCollapse: true,
      child: childIntervalArray
    },
    {
      href: '/addition',
      title: 'Дополнения',
      hiddenOnCollapse: true
    },
    {
      href: '/settings',
      title: 'Настройки',
      hiddenOnCollapse: true
    }
  ]
}

/**
 * Процедура получает количество групп оборудования и сохраняет его в pinia
 */
export async function getCountOfGroups() {
  const applicationStore = useApplicationStore()
  // получение с eel количества групп и их сохранение в pinia
  applicationStore.countOfGroups = await eel.get_groups_count()()
}

/**
 * Процедура получает интервалы найденные методом и сохраняет их в pinia
 */
export async function getGroupIntervals(method, group) {
  const applicationStore = useApplicationStore()
  // получение с eel интервалов найденных методом и их сохранение в pinia
  applicationStore.groupIntervals.value = await eel.get_group_interval_time_array(method, group)()
}

/**
 * Процедура получает интервалы добавленные пользователем и сохраняет их в pinia
 */
export async function getAddedIntervals(method, group) {
  const applicationStore = useApplicationStore()
  // получение с eel интервалов добавленных пользователем и их сохранение в pinia
  applicationStore.addedIntervals.value = await eel.get_added_interval_time_array(method, group)()
}

/**
 * Процедура заполняет в pinia словарь PLOT датчиков и их фиксированных цветов
 * @returns {Promise<void>} зарезолвенный промис и заполненный через сеттер словарь в pinia
 */
export async function getPlotFeatures() {
  const applicationStore = useApplicationStore()
  const plotFeatures = await eel.get_plot_features()()
  applicationStore.setDictSensorPlotPalette(plotFeatures)
  console.log(applicationStore.dictSensorPlotPalette)
}

/**
 * Процедура заполняет ref массив наименований групп и ref массив селектора выбора группы
 * @param namesOfGroups ref массив наименований групп
 * @param optionsSelectorOfGroups ref массив селектора выбора группы
 */
export async function getNamesAndSelectorOptionsOfGroups(namesOfGroups, optionsSelectorOfGroups) {
  const applicationStore = useApplicationStore()
  // получение с eel наименований групп и их сохранение в pinia
  let groupsName = await eel.get_groups_name_array()()
  applicationStore.namesOfGroups.value = groupsName
  namesOfGroups.value = groupsName

  for (const [index, name] of namesOfGroups.value.entries()) {
    optionsSelectorOfGroups.value.push({
      text: name,
      value: index + 1
    })
  }
}

/**
 * Асинхронная процедура заполняет reactive объект
 * для отрисовки Plotly графика целевой функции на интервале (по умолчанию на всем периоде)
 * @param method наименование выбранного метода
 * @param group номер выбранной группы
 * @param PlotlyDataTarget reactive объект Plotly с данными для отрисовки графика
 * @param interval массив интервала в формате: [{начало_интервала}, {конец_интервала}]. Аргумент по умолчанию
 *  для отрисовки графика на всем временном интервале
 * @returns {Promise<void>} зарезолвенный промис reactive объекта
 */
export async function getPlotlyDataInterval(method, group, PlotlyDataTarget, interval = true) {
  let timeArray = Array()
  let dataArray = Array()

  /**
   * Процедура заполнения массивов данных графиков по частям, посылаемых из python
   * @param partTime
   * @param partData
   */
  function getPartOfDataInterval(partTime, partData) {
    timeArray.push(...partTime)
    dataArray.push(...partData)
  }
  window.eel.expose(getPartOfDataInterval, 'getPartOfDataInterval')

  const applicationStore = useApplicationStore()
  // узнаем размер передачи данных
  // let partOfData = await eel.get_consant_part_of_data()()
  // let start_part = 0
  // let end_part = 0
  // let intervalLengthAndIndentation = []
  if (typeof interval === 'boolean') {
    // intervalLengthAndIndentation = await eel.get_length_time_and_indentation()()
    // получение значений для графика за весь период
    let PlotlyVal = await eel.get_predict_values(method, group)()
    if (PlotlyVal === 'success') {
      PlotlyDataTarget.x = timeArray
      PlotlyDataTarget.y = dataArray
    }
  } else {
    const leftSpace = applicationStore.leftSpace
    const rightSpace = applicationStore.rightSpace
    // intervalLengthAndIndentation = await eel.get_length_time_and_indentation(
    //   interval,
    //   leftSpace,
    //   rightSpace
    // )()

    // определение и вычисление границ интервала с учетом видимой части отступов
    let PlotlyVal = await eel.get_predict_values(method, group, interval, leftSpace, rightSpace)()
    if (PlotlyVal === 'success') {
      PlotlyDataTarget.x = timeArray
      PlotlyDataTarget.y = dataArray
    }
  }
  // while (start_part < intervalLengthAndIndentation[0]) {
  //   if (end_part + Math.floor(partOfData / partOfData) >= intervalLengthAndIndentation[0])
  //     end_part += intervalLengthAndIndentation[0] % Math.floor(partOfData / 2)
  //   else end_part += Math.floor(partOfData / 2)
  //
  //   // запрашиваем кусок данных временных отметок
  //   let timeChunk = await eel.get_time_chunk(
  //     intervalLengthAndIndentation[1],
  //     start_part,
  //     end_part
  //   )()
  //   timeArray.push(...timeChunk)
  //
  //   // запрашиваем кусок значений целевой переменной
  //   let dataChunk = await eel.get_values_chunk(
  //     method,
  //     group,
  //     intervalLengthAndIndentation[1],
  //     start_part,
  //     end_part
  //   )()
  //   dataArray.push(...dataChunk)
  //   start_part += Math.floor(partOfData / 2)
  // }
  // PlotlyDataTarget.x = timeArray
  // PlotlyDataTarget.y = dataArray
}

/**
 * процедура сохраняет в pinia и ref объектах наименьшую и наибольшую обнаруженную в срезах временную отметку,
 * инциализирует поля ввода начала периода и конца периода
 * @param minTime ref объект наименьшей временной отметки
 * @param maxTime ref объект наибольшей временной отметки
 * @param dateTimeBegin ref объект поля ввода начала периода
 * @param dateTimeEnd ref объект поля ввода конца периода
 * @returns {Promise<void>} зарезолвенный промис с сохранением в pinia и полей ввода начала и конца периода
 */
export async function getMinMaxDateFromDataTarget(minTime, maxTime, dateTimeBegin, dateTimeEnd) {
  const applicationStore = useApplicationStore()

  let minString = await eel.get_min_time_value()()
  let maxString = await eel.get_max_time_value()()

  minTime.value = Date.parse(minString)
  maxTime.value = Date.parse(maxString)

  minTime.value = new Date(minTime.value)
  maxTime.value = new Date(maxTime.value)

  dateTimeBegin.value = minTime.value
  dateTimeEnd.value = maxTime.value

  applicationStore.minDateFromData = dateTimeBegin.value
  applicationStore.maxDateFromData = dateTimeEnd.value
}

/**
 * процедура заполняет reactive объект
 * для определения Layout элемента графика целевой функции на всем периоде
 * @param method наименование выбранного метода
 * @param group номер выбранной группы
 * @param PlotlyLayoutTarget reactive объект Plotly с данными для определения Layout отрисуемого графика
 */
export async function getPlotlyCommonLayoutInterval(method, group, PlotlyLayoutTarget) {
  let groupIntervals = await eel.get_group_interval_time_array(method, group)()
  PlotlyLayoutTarget.shapes = []

  PlotlyLayoutTarget.title = `Метод: ${method}, Группа: ${group}`

  if (groupIntervals.length > 0) {
    groupIntervals.forEach((elem) => {
      PlotlyLayoutTarget.shapes.push({
        type: 'rect',
        xref: 'x',
        yref: 'paper',
        x0: elem[0],
        y0: 0,
        x1: elem[1],
        y1: 1,
        line: {
          width: 1,
          color: 'red',
          layer: 'below'
        }
      })
    })
  }
}

/**
 * процедура заполняет reactive объект
 * для определения Layout элемента графика целевой функции на определенном интервале
 * @param method наименование выбранного метода
 * @param group номер выбранной группы
 * @param interval массив интервала в формате: [{начало_интервала}, {конец_интервала}].
 * @param PlotlyLayoutTarget reactive объект Plotly с данными для определения Layout отрисуемого графика
 * @returns {Promise<void>} зарезолвенный промис reactive объекта
 */
export async function getPlotlyIntervalLayoutInterval(method, group, interval, PlotlyLayoutTarget) {
  const applicationStore = useApplicationStore()
  let groupIntervals = applicationStore.groupIntervals.value

  PlotlyLayoutTarget.shapes = []

  PlotlyLayoutTarget.title = `Метод: ${method}, Группа: ${group}, Интервал: ${interval[0]} % ${interval[1]}`
  // Массивы передаются по ссылке, поэтому чекаем через JSON представление
  if (JSON.stringify(groupIntervals).includes(JSON.stringify(interval))) {
    PlotlyLayoutTarget.shapes.push({
      type: 'rect',
      xref: 'x',
      yref: 'paper',
      x0: interval[0],
      y0: 0,
      x1: interval[1],
      y1: 1,
      line: {
        width: 1,
        color: 'red',
        layer: 'below'
      }
    })
  }
}

/**
 * Процедура заполнения объектов интервалов для формироавния таблицы добавленных пользователем интервалов
 * @param method наименование выбранного метода
 * @param group номер выбранной группы
 * @param addedToTableIntervals ссылка на объект
 * @returns {Promise<void>} зарезолвенный промис reactive объекта
 */
export async function getAddedToTableIntervals(method, group, addedToTableIntervals) {
  addedToTableIntervals.value = []
  let addedIntervals = await eel.get_added_interval_time_array(method, group)()

  for (const [index, interval] of addedIntervals.entries()) {
    addedToTableIntervals.value.push({
      id: index,
      buttonDisabled: false,
      period: `Период ${index + 1}`,
      begin: new Date(interval[0]),
      end: new Date(interval[1])
    })
  }
}

/**
 * Процедура заполнения ref массивов объектов для составления меню чекбоксов
 * @param method наименование выбранного метода
 * @param group номер выбранной группы
 * @param topSensors ссылка на ref объект чекбоксов топовых датчиков
 * @param otherGroupSensors ссылка на ref объект выбранных остальных датчиков группы
 * @param selectedTopSensors ссылка на ref объект выбранных датчиков, внесших максимальный вклад
 * @param intervalId номер интервала в полностью отсортированных интервалах
 * (интервалы найденные методом + интервалы добавленные пользователем)
 * @returns {Promise<void>} зарезолвенный промис ref объектов
 */
export async function getTopAndOtherGroupSensors(
  method,
  group,
  topSensors,
  otherGroupSensors,
  selectedTopSensors,
  intervalId
) {
  let valArray = await eel.get_top_and_other_interval_sensors(method, group, intervalId)()

  topSensors.value = []
  otherGroupSensors.value = []

  for (const [index, top] of valArray[0].entries()) {
    topSensors.value.push({
      id: index,
      kks: top,
      name: valArray[1][index]
    })
  }

  for (const [index, other] of valArray[2].entries()) {
    otherGroupSensors.value.push({
      id: index,
      kks: other,
      name: valArray[3][index]
    })
  }

  topSensors.value.forEach((elem) => {
    selectedTopSensors.value.push(elem.name)
  })
}

/**
 * Процедура заполнения ref массива объектов чекбоксов многоосевого графика
 * @param selectedSignal наименование выбранного основного сигнала
 * @param multiAxisSensors ref массив чекбоксов многоосевого графика
 * @param selectedMultiAxisSensors ref массив выбранных чекбоксов многоосевого графика
 * @returns {Promise<void>} зарезолвенный промис ref массивов
 */
export async function getMultiAxisSensors(
  selectedSignal,
  multiAxisSensors,
  selectedMultiAxisSensors
) {
  multiAxisSensors.value = []
  selectedMultiAxisSensors.value = []

  let valArray = await eel.get_multi_axis_sensors(selectedSignal)()
  for (const [index, multiAxisSignals] of valArray[0].entries()) {
    multiAxisSensors.value.push({
      id: index,
      kks: valArray[1][index],
      name: multiAxisSignals
    })
  }

  // выставляем чекбоксы отмеченными по умолчанию
  multiAxisSensors.value.forEach((elem) => {
    selectedMultiAxisSensors.value.push(elem.name)
  })
}

/**
 * Процедура получает данные для многоосевого графика и заполняет объект данных Plotly для многоосевого графика
 * @param selectedMultiAxisSensors ref массив выбранных чекбоксов многоосевого графика
 * @param intervalID номер интервала в полностью отсортированных интервалах
 * (интервалы найденные методом + интервалы добавленные пользователем)
 * @param PlotlyMultiData массив объектов данных для графика Plotly
 * @returns {Promise<void>} зарезолвенный промис ref массива объектов данных Plotly
 */
export async function getPlotlyMultiAxisData(
  selectedMultiAxisSensors,
  intervalID,
  PlotlyMultiData
) {
  const applicationStore = useApplicationStore()
  PlotlyMultiData.value = []

  let sensors = []

  selectedMultiAxisSensors.value.forEach((elem) => {
    sensors.push(elem)
  })

  const interval = applicationStore.intervals.value[intervalID.value]
  const leftSpace = applicationStore.leftSpace
  const rightSpace = applicationStore.rightSpace
  const mainColor = applicationStore.plotMain
  const featureColor = applicationStore.dictSensorPlotPalette

  let multiAxisData = [[], []]
  // инициализируем массивы значений датчиков
  for (const [index, selectedMultiAxisSensor] of sensors.entries()) {
    multiAxisData[1][index] = []
  }

  // узнаем длину интервала и данных
  let intervalLengthAndIndentation = await eel.get_length_time_and_indentation(
    interval,
    leftSpace,
    rightSpace
  )()
  let partOfData = await eel.get_consant_part_of_data()()

  let start_part = 0
  let end_part = 0
  while (start_part < intervalLengthAndIndentation[0]) {
    if (end_part + Math.floor(partOfData / partOfData) >= intervalLengthAndIndentation[0])
      end_part += intervalLengthAndIndentation[0] % Math.floor(partOfData / 2)
    else end_part += Math.floor(partOfData / 2)
    // запрашиваем кусок данных временных отметок
    let timeChunk = await eel.get_time_chunk(
      intervalLengthAndIndentation[1],
      start_part,
      end_part
    )()
    multiAxisData[0].push(...timeChunk)

    // запрашиваем кусок значений для датчиков
    for (const [index, selectedMultiAxisSensor] of sensors.entries()) {
      let valuesChunk = await eel.get_multi_axis_sensor_values_chunk(
        selectedMultiAxisSensor,
        intervalLengthAndIndentation[1],
        start_part,
        end_part
      )()
      multiAxisData[1][index].push(...valuesChunk)
    }
    start_part += Math.floor(partOfData / 2)
  }

  for (const [index, multiAxisSignal] of multiAxisData[1].entries()) {
    if (index === 0) {
      PlotlyMultiData.value.push({
        x: multiAxisData[0],
        y: multiAxisSignal,
        name: sensors[index].split(' ')[2],
        type: 'scatter',
        line: {
          color: mainColor
        }
      })
    } else {
      PlotlyMultiData.value.push({
        x: multiAxisData[0],
        y: multiAxisSignal,
        name: sensors[index].split(' ')[2],
        type: 'scatter',
        yaxis: 'y' + Number(index + 1),
        line: {
          color: featureColor[sensors[index]]
        }
      })
    }
  }
}

/**
 * Процедура заполняет объект Layout Plotly для многоосевого графика
 * @param selectedMultiAxisSensors ref массив выбранных чекбоксов многоосевого графика
 * @param intervalID номер интервала в полностью отсортированных интервалах
 * (интервалы найденные методом + интервалы добавленные пользователем)
 * @param PlotlyMultiLayout ref объект Layout для графика Plotly
 * @returns {Promise<void>} зарезолвенный промис ref объекта Plotly
 */
export async function getPlotlyMultiAxisLayout(
  selectedMultiAxisSensors,
  intervalID,
  PlotlyMultiLayout
) {
  const applicationStore = useApplicationStore()

  const interval = applicationStore.intervals.value[intervalID.value]
  const groupIntervals = applicationStore.groupIntervals.value
  const mainColor = applicationStore.plotMain
  const featureColor = applicationStore.dictSensorPlotPalette

  PlotlyMultiLayout.value = {}

  for (const [index, sensor] of selectedMultiAxisSensors.value.entries()) {
    if (index === 0) {
      PlotlyMultiLayout.value = {
        title: sensor.split(' ')[2],
        xaxis: { domain: [0.3, 1] },
        showlegend: false,
        yaxis: {
          title: sensor.split(' ')[2],
          titlefont: {
            size: 14,
            color: mainColor
          },
          tickfont: {
            size: 14,
            color: mainColor
          }
        },
        shapes: []
      }
    } else if (index <= 2) {
      PlotlyMultiLayout.value[`yaxis${index + 1}`] = {
        title: sensor.split(' ')[2],
        titlefont: {
          size: 14,
          color: featureColor[sensor]
        },
        tickfont: {
          size: 14,
          color: featureColor[sensor]
        },
        anchor: 'free',
        overlaying: 'y',
        side: 'right',
        autoshift: true,
        showline: true,
        showgrid: false,
        zeroline: false,
        ticks: 'outside',
        tickwidth: 0.5,
        tickcolor: 'black',
        title_standoff: 10
      }
    } else {
      PlotlyMultiLayout.value[`yaxis${index + 1}`] = {
        title: sensor.split(' ')[2],
        titlefont: {
          size: 14,
          color: featureColor[sensor]
        },
        tickfont: {
          size: 14,
          color: featureColor[sensor]
        },
        anchor: 'free',
        overlaying: 'y',
        side: 'left',
        autoshift: true,
        showline: true,
        showgrid: false,
        zeroline: false,
        ticks: 'outside',
        tickwidth: 0.5,
        tickcolor: featureColor[sensor],
        title_standoff: 10,
        layer: 'below traces'
      }
    }

    if (JSON.stringify(groupIntervals).includes(JSON.stringify(interval))) {
      PlotlyMultiLayout.value['shapes'].push({
        type: 'rect',
        xref: 'x',
        yref: 'paper',
        x0: interval[0],
        y0: 0,
        x1: interval[1],
        y1: 1,
        line: {
          width: 1,
          color: 'red',
          layer: 'below'
        }
      })
    }
  }
}

/**
 * Асинхронная процедура заполнения объектов гистрограммы
 * @param group номер выбранной группы
 * @param PlotlyHistData ref объект для данных гистограммы Plotly
 * @param PlotlyHistLayout reactive объект Layout для гистограммы Plotly
 * @returns {Promise<void>}
 */
export async function getPlotlyHist(group, PlotlyHistData, PlotlyHistLayout) {
  const applicationStore = useApplicationStore()

  const probabilityColor = applicationStore.plotMain
  const potentialColor = '#10E8E7'
  const resultArray = await eel.get_hist_data(group)()

  PlotlyHistData.value[0] = {
    x: resultArray[0],
    y: resultArray[1],
    name: 'probability',
    line: {
      color: probabilityColor
    },
    width: 10,
    type: 'scatter'
  }
  PlotlyHistData.value[1] = {
    x: resultArray[0],
    y: resultArray[2],
    name: 'potential',
    line: {
      color: potentialColor
    },
    width: 10,
    type: 'scatter'
  }
  PlotlyHistLayout.shapes = []
  PlotlyHistLayout.shapes.push({
    type: 'line',
    xref: 'x',
    yref: 'paper',
    x0: resultArray[0][resultArray[3]],
    y0: 0,
    x1: resultArray[0][resultArray[3]],
    y1: 1,
    line: {
      width: 1,
      color: 'red',
      layer: 'below'
    }
  })
}

export async function getRollingInput(rollingInput, rollingInputMax) {
  rollingInput.value = await eel.get_config_rolling()()
  rollingInputMax.value = await eel.get_length_slice()()
}
