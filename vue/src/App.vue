<script>
import { useRouter, useRoute } from 'vue-router'
import { ref, reactive, onMounted, watch } from 'vue'
import { SidebarMenu } from 'vue-sidebar-menu'
import {
  getSidebarMenu,
  getCountOfGroups,
  getNamesAndSelectorOptionsOfGroups,
  getGroupIntervals,
  getAddedIntervals,
  getPlotFeatures,
  createReport,
  getRollingInput,
  rebuildIntervals,
  templateReportCreate
} from './stores'

import { MdEditor, MdPreview, config } from 'md-editor-v3'

import 'vue-sidebar-menu/dist/vue-sidebar-menu.css'

import 'md-editor-v3/lib/style.css'

import ru from '@vavt/cm-extension/dist/locale/ru'

config({
  editorConfig: {
    languageUserDefined: {
      ru: ru
    }
  }
})

import { useApplicationStore } from './stores/applicationStore'

// заглушка выбора метода

export default {
  components: { SidebarMenu, MdEditor, MdPreview },
  setup() {
    const applicationStore = useApplicationStore()
    const router = useRouter()
    const route = useRoute()
    // sidebarMenu
    let sidebarMenu = reactive({ menu: Object() })
    let theme = ref('default-theme')
    let checkedSettingsFlag = ref(false)
    let checkedToggleCollapse = ref(false)
    let checkedSettingsAndTabsFlag = ref(false)
    let checkedButtonPdf = ref(false)

    // tabMenu
    let tabMenu = ref([])
    const activeTabMenu = ref(0)
    // ширина вкладок для красивого отображения
    const widthTab = ref('2000px')

    // выбранный метод
    const pickedMethod = ref('potentials')
    // выбранная группа
    const pickedGroup = ref(1)
    // массив наименований групп
    let namesOfGroups = ref([])
    // массив селектора для выбора группы
    let optionsSelectorOfGroups = ref([])

    // значение выполенния прогресс бара при построении отчета
    const progressBarValue = ref('0')
    // флаг показа прогресс бара
    let progressBarActive = ref(false)

    // значение сглаживания в часах
    const rollingInput = ref(0)
    const rollingInputMax = ref(0)
    // параметры выделения интервалов
    const shortThreshold = ref(96)
    const longThreshold = ref(86)
    const lenShortAnomaly = ref(72)
    const lenLongAnomaly = ref(288)
    const countContinueShort = ref(5)
    const countContinueLong = ref(5)

    // флаг показа выпадающего окна выделения интервалов
    const dialogActive = ref(false)
    // флаг необходимости обновления начальной страницы
    const flagHomePageUpdate = ref(false)

    // значение выполенния прогресс бара при перевыделении интервалов
    const progressBarRebuildIntervalValue = ref('0')
    // флаг показа прогресс бара при перевыделении интервалов
    let progressBarRebuildIntervalActive = ref(false)

    // флаг показа выпадающего окна редактирования отчетов
    const dialogEditorActive = ref(false)

    // содержимое редактора ввода markdown
    const editorContent = ref('# Hello Editor')
    const editorToolbars = ref([
      'bold',
      'underline',
      'italic',
      '-',
      'strikeThrough',
      'title',
      'sub',
      'sup',
      'quote',
      'unorderedList',
      'orderedList',
      'task', // ^2.4.0
      '-',
      'codeRow',
      'code',
      'table',
      'mermaid',
      'katex',
      '-',
      'revoke',
      'next',
      '=',
      'preview',
      'catalog'
    ])
    const htmlContent = ref('')
    const editorRef = ref()

    const templateReportName = ref('')

    onMounted(async () => {
      // Заполняем объекты sidebarMenu, tabMenu получаем количество и наименования групп
      await getSidebarMenu(pickedMethod.value, pickedGroup.value, sidebarMenu, tabMenu, widthTab)
      await getNamesAndSelectorOptionsOfGroups(namesOfGroups, optionsSelectorOfGroups)
      // Заносим в pinia количество групп, интервалы метода, инетрвалы добавленные пользователем
      await getCountOfGroups()
      await getGroupIntervals(pickedMethod.value, pickedGroup.value)
      await getAddedIntervals(pickedMethod.value, pickedGroup.value)
      await getPlotFeatures()
      activeTabMenu.value = await tabMenu.value.findIndex(
        (tab) => route.path === router.resolve(tab.route).path
      )
      await getRollingInput(rollingInput, rollingInputMax)
    })

    watch(
      route,
      () => {
        activeTabMenu.value = tabMenu.value.findIndex(
          (tab) => route.path === router.resolve(tab.route).path
        )
      },
      { immediate: true }
    )

    // обработчик нажатия на кнопки меню sidebarMenu
    const onSidebarMenuItemClick = (event, item) => {
      console.log(event, item)
      checkedSettingsFlag.value = item.href === '/settings'
      checkedSettingsAndTabsFlag.value = item.href === '/settings' || item.href === '/addition'
      checkedButtonPdf.value = item.href === '/settings' || item.href === '/addition'
    }

    // обработчик нажатия на кнопку скрытия sidebarMenu
    const onSidebarToggleCollapse = (collapsed) => {
      console.log(collapsed)
      checkedToggleCollapse.value = collapsed
    }

    // обработчик нажатия на кнопки выбора метода
    function onChangeRadioButtons() {
      // Перезаполняем объект sidebarMenu новым методом и группой
      getSidebarMenu(pickedMethod.value, pickedGroup.value, sidebarMenu, tabMenu, widthTab)
      // Обновляем в pinia интервалы
      getGroupIntervals(pickedMethod.value, pickedGroup.value)
      getAddedIntervals(pickedMethod.value, pickedGroup.value)
      if (!checkedButtonPdf.value) router.push('/')
    }

    // обработчик нажатия на селектор группы
    function onChangeSelector() {
      // Перезаполняем объект sidebarMenu новым методом и группой
      getSidebarMenu(pickedMethod.value, pickedGroup.value, sidebarMenu, tabMenu, widthTab)
      // Обновляем в pinia интервалы
      getGroupIntervals(pickedMethod.value, pickedGroup.value)
      getAddedIntervals(pickedMethod.value, pickedGroup.value)
      if (!checkedButtonPdf.value) router.push('/')
    }

    // обработчик нажатия на кнопку PDF
    function onButtonPdfClick() {
      alert('Запуск построения PDF отчета по всем периодам')
      createReport(pickedMethod.value, pickedGroup.value, progressBarValue, progressBarActive)
    }

    // обновление прогресс бара по значению из python
    function setProgressBarValue(count) {
      progressBarValue.value = String(count)
    }
    window.eel.expose(setProgressBarValue, 'setProgressBarValue')

    // обработка emit от HomeView.vue при добавлении нового интервала
    function newAddedIntervalToMenus() {
      console.log('emits from HomeView.vue')
      // Перезаполняем объект sidebarMenu новым методом и группой
      getSidebarMenu(pickedMethod.value, pickedGroup.value, sidebarMenu, tabMenu, widthTab)
      // Обновляем в pinia интервалы
      getGroupIntervals(pickedMethod.value, pickedGroup.value)
      getAddedIntervals(pickedMethod.value, pickedGroup.value)
      router.push('/')
    }

    // обаботчик открытия диалога выделения инетервалов
    function onButtonDialogClick() {
      dialogActive.value = true
    }

    // обаботчик запуска выделения новых интервалов
    async function onButtonNewIntervalClick() {
      progressBarRebuildIntervalActive.value = true
      progressBarRebuildIntervalValue.value = '0'
      await rebuildIntervals(
        pickedMethod.value,
        rollingInput.value,
        shortThreshold.value,
        longThreshold.value,
        lenShortAnomaly.value,
        lenLongAnomaly.value,
        countContinueShort.value,
        countContinueLong.value
      )
      progressBarRebuildIntervalValue.value = '100'
      progressBarRebuildIntervalActive.value = false

      // Перезаполняем объект sidebarMenu новым методом и группой
      await getSidebarMenu(pickedMethod.value, pickedGroup.value, sidebarMenu, tabMenu, widthTab)
      // Обновляем в pinia интервалы
      await getGroupIntervals(pickedMethod.value, pickedGroup.value)
      await getAddedIntervals(pickedMethod.value, pickedGroup.value)

      dialogActive.value = false
      router.push('/')
      flagHomePageUpdate.value = !flagHomePageUpdate.value
    }

    // обновление прогресс бара по значению из python при переопределении инетервалов
    function setProgressBarRebuildIntervalValue(count) {
      progressBarRebuildIntervalValue.value = String(count)
    }
    window.eel.expose(setProgressBarRebuildIntervalValue, 'setProgressBarRebuildIntervalValue')

    // обработчик открытия диалога редактирования отчетов
    function onButtonDialogEditorClick() {
      dialogEditorActive.value = true
    }

    // обработчик изменения текста редактора
    const onEditorChange = (val) => {}

    // обработчик получения html редактора
    const onEditorHtmlChanged = (val) => {
      htmlContent.value = val
    }

    // обработчки создания отчета по шаблону
    function onEditorReportCreateClick() {
      templateReportCreate(editorContent.value, htmlContent.value, templateReportName.value)
      editorRef.value?.on('htmlPreview', (status) => console.log(status))
      console.log(editorRef.value)
      console.log(editorContent.value)
    }

    return {
      theme,
      sidebarMenu,
      checkedSettingsFlag,
      checkedToggleCollapse,
      checkedSettingsAndTabsFlag,
      checkedButtonPdf,
      activeTabMenu,
      tabMenu,
      onSidebarMenuItemClick,
      onSidebarToggleCollapse,
      pickedMethod,
      onChangeRadioButtons,
      pickedGroup,
      namesOfGroups,
      optionsSelectorOfGroups,
      onChangeSelector,
      onButtonPdfClick,
      newAddedIntervalToMenus,
      widthTab,
      progressBarValue,
      progressBarActive,
      setProgressBarValue,
      rollingInput,
      rollingInputMax,
      shortThreshold,
      longThreshold,
      lenShortAnomaly,
      lenLongAnomaly,
      countContinueShort,
      countContinueLong,
      dialogActive,
      onButtonDialogClick,
      onButtonNewIntervalClick,
      flagHomePageUpdate,
      progressBarRebuildIntervalValue,
      progressBarRebuildIntervalActive,
      setProgressBarRebuildIntervalValue,
      dialogEditorActive,
      onButtonDialogEditorClick,
      editorContent,
      editorToolbars,
      editorRef,
      htmlContent,
      templateReportName,
      onEditorChange,
      onEditorHtmlChanged,
      onEditorReportCreateClick
    }
  }
}
</script>

<template>
  <div>
    <sidebar-menu
      :theme="theme.value"
      :menu="sidebarMenu.menu"
      @update:collapsed="onSidebarToggleCollapse"
      @item-click="onSidebarMenuItemClick"
      width="450px"
    >
      <template v-slot:footer v-if="!checkedSettingsFlag && !checkedToggleCollapse">
        <div class="form-check">
          <input
            class="form-check-input"
            type="radio"
            id="potentials"
            name="potentials"
            value="potentials"
            v-model="pickedMethod"
            @change="onChangeRadioButtons"
          />
          <label class="form-check-label" for="potentials">
            <span class="badge rounded-pill bg-primary">potentials</span>
          </label>
        </div>
        <div class="form-check">
          <input
            class="form-check-input"
            type="radio"
            id="LSTM"
            name="LSTM"
            value="LSTM"
            v-model="pickedMethod"
            @change="onChangeRadioButtons"
          />
          <label class="form-check-label" for="LSTM">
            <span class="badge rounded-pill bg-primary">LSTM</span>
          </label>
        </div>
        <div>
          <select
            class="form-select"
            aria-label="Default select example"
            id="select-group"
            v-model="pickedGroup"
            @change="onChangeSelector"
          >
            <option v-for="option in optionsSelectorOfGroups" :value="option.value">
              {{ option.text }}
            </option>
          </select>
        </div>
        <div class="row">
          <div class="col-2" v-if="!checkedButtonPdf">
            <Button @click="onButtonPdfClick">PDF</Button>
          </div>
          <div class="col-10 align-self-center" v-if="progressBarActive">
            <ProgressBar :value="progressBarValue"></ProgressBar>
          </div>
        </div>
        <div v-if="!checkedButtonPdf">
          <Button @click="onButtonDialogClick">Выделение интервалов</Button>
          <Dialog
            v-model="dialogActive"
            :visible="dialogActive"
            :closable="false"
            header="Выделение интервалов"
            position="left"
            :modal="true"
            :draggable="false"
            :style="{ width: '50rem' }"
          >
            <div class="container">
              <div class="row">
                <label for="input-rolling" class="font-bold block mb-2">
                  Сглаживание в часах
                </label>
              </div>
              <div class="row">
                <div class="col-6">
                  <InputNumber
                    v-model="rollingInput"
                    inputId="input-rolling"
                    mode="decimal"
                    show-buttons
                    :min="0"
                    :max="rollingInputMax"
                    :step="1"
                    :allow-empty="false"
                    :aria-label="rollingInput"
                  />
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <label for="short-threshold" class="font-bold block mb-2">
                    Short threshold
                  </label>
                </div>
                <div class="col">
                  <label for="long-threshold" class="font-bold block mb-2"> Long threshold </label>
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <InputNumber
                    v-model="shortThreshold"
                    inputId="short-threshold"
                    mode="decimal"
                    show-buttons
                    :min="1"
                    :max="100"
                    :step="1"
                    :allow-empty="false"
                    :aria-label="shortThreshold"
                  />
                </div>
                <div class="col">
                  <InputNumber
                    v-model="longThreshold"
                    inputId="long-threshold"
                    mode="decimal"
                    show-buttons
                    :min="1"
                    :max="100"
                    :step="1"
                    :allow-empty="false"
                    :aria-label="longThreshold"
                  />
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <label for="len-short-anomaly" class="font-bold block mb-2">
                    Len short anomaly
                  </label>
                </div>
                <div class="col">
                  <label for="len-long-anomaly" class="font-bold block mb-2">
                    Len long anomaly
                  </label>
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <InputNumber
                    v-model="lenShortAnomaly"
                    inputId="len-short-anomaly"
                    mode="decimal"
                    show-buttons
                    :min="0"
                    :max="1000000"
                    :step="1"
                    :allow-empty="false"
                    :aria-label="lenShortAnomaly"
                  />
                </div>
                <div class="col">
                  <InputNumber
                    v-model="lenLongAnomaly"
                    inputId="len-long-anomaly"
                    mode="decimal"
                    show-buttons
                    :min="0"
                    :max="1000000"
                    :step="1"
                    :allow-empty="false"
                    :aria-label="lenLongAnomaly"
                  />
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <label for="count-continue-short" class="font-bold block mb-2">
                    Len short anomaly
                  </label>
                </div>
                <div class="col">
                  <label for="count-continue-long" class="font-bold block mb-2">
                    Len long anomaly
                  </label>
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <InputNumber
                    v-model="countContinueShort"
                    inputId="count-continue-short"
                    mode="decimal"
                    show-buttons
                    :min="0"
                    :max="1000000"
                    :step="1"
                    :allow-empty="false"
                    :aria-label="countContinueShort"
                  />
                </div>
                <div class="col">
                  <InputNumber
                    v-model="countContinueLong"
                    inputId="count-continue-long"
                    mode="decimal"
                    show-buttons
                    :min="0"
                    :max="1000000"
                    :step="1"
                    :allow-empty="false"
                    :aria-label="countContinueLong"
                  />
                </div>
              </div>
            </div>
            <template #footer>
              <Button label="Отмена" icon="pi pi-times" @click="dialogActive = false" text />
              <Button
                label="Запустить выделение интервалов"
                icon="pi pi-check"
                @click="onButtonNewIntervalClick"
              />
              <ProgressBar
                :value="progressBarRebuildIntervalValue"
                v-if="progressBarRebuildIntervalActive"
              ></ProgressBar>
            </template>
          </Dialog>
        </div>
        <div>
          <Button @click="onButtonDialogEditorClick">Редактор отчетов</Button>
          <Dialog
            v-model="dialogEditorActive"
            :visible="dialogEditorActive"
            :closable="false"
            header="Редактор отчетов"
            position="left"
            :modal="true"
            :draggable="false"
            :style="{ width: '50rem' }"
          >
            <div class="container">
              <MdEditor
                language="ru"
                v-model="editorContent"
                @change="onEditorChange"
                ref="editorRef"
                @onHtmlChanged="onEditorHtmlChanged"
                :toolbars="editorToolbars"
              ></MdEditor>
              <!--              <MdPreview editorId="1" v-model="editorContent"-->
              <!--              ></MdPreview>-->
            </div>
            <template #footer>
              <!--              <label for="template-report-name">Наименование html</label>-->
              <InputText
                id="template-report-name"
                type="text"
                v-model="templateReportName"
                labe
              ></InputText>
              .html
              <Button label="Скрыть" icon="pi pi-minus" @click="dialogEditorActive = false" text />
              <Button label="Создать отчет" icon="pi pi-check" @click="onEditorReportCreateClick" />
            </template>
          </Dialog>
        </div>
      </template>
    </sidebar-menu>
  </div>
  <div class="common-margin-left">
    <div v-if="!checkedSettingsAndTabsFlag">
      <h1 class="text-center">Метод {{ pickedMethod }}: группа {{ pickedGroup }}</h1>
      <TabMenu v-model:active-index="activeTabMenu" :model="tabMenu" class="p-tabmenu-nav">
        <template #item="{ label, item, props }">
          <router-link v-if="item.route" v-slot="routerProps" :to="item.route" custom>
            <a
              :href="routerProps.href"
              v-bind="props.action"
              @click="($event) => routerProps.navigate($event)"
              @keydown.enter.space="($event) => routerProps.navigate($event)"
            >
              <span v-bind="props.label">{{ label }}</span>
            </a>
          </router-link>
        </template>
      </TabMenu>
    </div>
    <RouterView
      :active-method="pickedMethod"
      :active-group="pickedGroup"
      :flag-home-page-update="flagHomePageUpdate"
      @updateNewInterval="newAddedIntervalToMenus"
      class="common-margin-left"
    />
  </div>
</template>

<style scoped>
.common-margin-left {
  margin-left: 5%;
}
.p-tabmenu-nav {
  width: v-bind(widthTab);
  display: flex;
  margin: 0;
  padding: 0;
  list-style-type: none;
  flex-wrap: nowrap;
}
</style>
