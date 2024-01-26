import { useApplicationStore } from './applicationStore'

/**
 * процедура сохранения добавляемых пользователем интервалов
 * @param method наименование выбранного метода
 * @param group номер выбранной группы
 * @param dateBegin ссылка на объект даты начала добавляемого интервала класса Date()
 * @param dateEnd ссылка на объект даты конца добавляемого интервала класса Date()
 * @returns {Promise<void>} зарезолвенный промис с выводом контексного сообщения в зависимости от завершения операции
 * сохранения нового добавляемого интервала
 */
export async function saveAddedIntervals(method, group, dateBegin, dateEnd) {
  let formatDateBegin = new Date(dateBegin.toString().split('GMT')[0] + ' UTC').toISOString()
  let formatDateEnd = new Date(dateEnd.toString().split('GMT')[0] + ' UTC').toISOString()
  let result = await eel.add_new_interval(method, group, formatDateBegin, formatDateEnd)()
  alert(result)
}

/**
 * процедура удаления добавленного пользователем интервала
 * @param method наименование выбранного метода
 * @param group номер выбранной группы
 * @param intervalId номер удаляемого интервала
 * @returns {Promise<void>} зарезолвенный промис с удалением интервала и выводом контексного сообщения
 */
export async function removeIntervalById(method, group, intervalId) {
  let status = await eel.remove_interval(method, group, intervalId)()
  alert(status)
}

/**
 * процедура обновления добавленного пользователем интервала
 * @param method method наименование выбранного метода
 * @param group номер выбранной группы
 * @param dateBegin ссылка на объект даты начала добавляемого интервала класса Date()
 * @param dateEnd ссылка на объект даты конца добавляемого интервала класса Date()
 * @param intervalId номер удаляемого интервала
 * @returns {Promise<void>} зарезолвенный промис с обновлением интервала и выводом контексного сообщения
 */
export async function updateInterval(method, group, dateBegin, dateEnd, intervalId) {
  let formatDateBegin = new Date(dateBegin.toString().split('GMT')[0] + ' UTC').toISOString()
  let formatDateEnd = new Date(dateEnd.toString().split('GMT')[0] + ' UTC').toISOString()
  let result = await eel.add_new_interval(
    method,
    group,
    formatDateBegin,
    formatDateEnd,
    true,
    intervalId
  )()
  alert(result)
}

/**
 * Процедура запускает построение pdf отчета по всем периодам
 * @param method наименование выбранного метода
 * @param group номер выбранной группы
 * @param progressBarValue ссылка на ref объект значения прогресс бара создания отчета по всем периодам
 * @param progressBarActive ссылка на ref объект показа прогресс бара по всем периодам
 * @returns {Promise<void>} зарезолвенный промис c статусом завершения операции
 */
export async function createReport(method, group, progressBarValue, progressBarActive) {
  const applicationStore = useApplicationStore()

  const leftSpace = applicationStore.leftSpace
  const rightSpace = applicationStore.rightSpace
  const orientation = applicationStore.pickedOrientation
  progressBarActive.value = true

  let result = await eel.create_report(method, group, orientation, leftSpace, rightSpace)()
  progressBarActive.value = false
  alert(result)

  let pdfOpenStatus = await eel.get_common_pdf_report(method, group)()
  console.log(pdfOpenStatus)
  if (pdfOpenStatus === 'success') {
    const link = document.createElement('a')
    const path_common_report = 'common_report.pdf'
    link.setAttribute('download', 'common_report.pdf')
    link.setAttribute('type', 'application/octet-stream')
    link.setAttribute('href', path_common_report)
    document.body.appendChild(link)
    link.click()
    link.remove()
  }
}

/**
 * Процедура запускает построение pdf отчета по открытой вкладке периода
 * @param method наименование выбранного метода
 * @param group номер выбранной группы
 * @param interval массив интервала в формате: [{начало_интервала}, {конец_интервала}].
 * @param selectedTopSensors ссылка на ref объект выбранных датчиков, внесших максимальный вклад
 * @param selectedOtherGroupSensors ссылка на ref объект выбранных остальных датчиков группы
 * @param progressTabBarValue ссылка на ref объект значения прогресс бара создания отчета по открытой вкладке периода
 * @param progressTabBarActive ссылка на ref объект показа прогресс бара создания отчета по открытой вкладке периода
 * @returns {Promise<void>} зарезолвенный промис с выводом контексного сообщения в зависимости от завершения операции
 * создания отчета по открытой вкладке периода
 */
export async function createTabReport(
  method,
  group,
  interval,
  selectedTopSensors,
  selectedOtherGroupSensors,
  progressTabBarValue,
  progressTabBarActive
) {
  const applicationStore = useApplicationStore()

  const leftSpace = applicationStore.leftSpace
  const rightSpace = applicationStore.rightSpace
  const orientation = applicationStore.pickedOrientation
  const dictSelectedCheckbox = applicationStore.dictSelectedCheckbox

  progressTabBarActive.value = true

  let result = await eel.create_tab_report(
    method,
    group,
    interval,
    orientation,
    selectedTopSensors.value,
    selectedOtherGroupSensors.value,
    dictSelectedCheckbox,
    leftSpace,
    rightSpace
  )()

  alert(result)
  progressTabBarActive.value = false

  let pdfOpenStatus = await eel.get_tab_pdf_report(method, group, interval)()
  console.log(pdfOpenStatus)
  if (pdfOpenStatus === 'success') {
    const link = document.createElement('a')
    const path_tab_report = `tab_report.pdf`
    link.setAttribute('download', 'tab_report.pdf')
    link.setAttribute('type', 'application/octet-stream')
    link.setAttribute('href', path_tab_report)
    document.body.appendChild(link)
    link.click()
    link.remove()
  }
}

/**
 * Процедура запускает выделение новых аномальных интервалов для метода
 * @param method наименование выбранного метода
 * @param rollingInput сглаживание в часах
 * @param shortThreshold порог для определения аномального значения для поиска коротких интервалов
 * @param longThreshold порог для определения аномального значения для поиска длинных интервалов
 * @param lenShortAnomaly настройка определяет минимальную длину короткого обнаруженного интервала аномалии
 * @param lenLongAnomaly настройка определяет минимальную длину длинного обнаруженного интервала аномалии
 * @param countContinueShort количество отсчетов для прерывания короткого интервала
 * @param countContinueLong количество отсчетов для прерывания длинного интервала
 * @returns {Promise<void>} зарезолвенный промис с выводом контексного сообщения в зависимости от завершения операции
 * выделения новых аномальных интервалов для метода
 */
export async function rebuildIntervals(
  method,
  rollingInput,
  shortThreshold,
  longThreshold,
  lenShortAnomaly,
  lenLongAnomaly,
  countContinueShort,
  countContinueLong
) {
  let result = await eel.rebuild_anomaly_interval(
    method,
    rollingInput,
    shortThreshold,
    longThreshold,
    lenShortAnomaly,
    lenLongAnomaly,
    countContinueShort,
    countContinueLong
  )()
  alert(result)
}

export async function templateReportCreate(content) {
  let result = await eel.template_report_create(content)()
  alert(result)
}
