<script>
// //////////////////////// SIDEBAR ////////////////////////////////////
// import Sidebar from './components/Sidebar/Sidebar.vue'
import { collapsed, toggleSidebar, sidebarWidth } from './components/Sidebar/state'
// ////////////////////////////////////////////////////////////
import TabNav from './components/TabNav.vue';
import Tab from './components/Tab.vue';

import Header from './components/header/Header.vue';



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
  // components: { SidebarMenu, MdEditor, MdPreview, Sidebar, TabNav, Tab, Header },
  components: { SidebarMenu, MdEditor, MdPreview, TabNav, Tab, Header },
  props: {},
    setup() {
        return { collapsed, toggleSidebar, sidebarWidth };
    },
    date(){
      return{
        selected: 'Home'
      }
    },
    methods:{
      setSelected(tab){
        this.selected = tab;
      },
      
    },
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

    // обработчик нажатия на кнопки меню sidebarMenu //////////////////////////////////////////////////////////////////////////////////////////////////
    const onSidebarMenuItemClick = (event, item) => {
      console.log(event, item)
      checkedSettingsFlag.value = item.href === '/settings'
      checkedSettingsAndTabsFlag.value = item.href === '/settings' || item.href === '/addition'
      checkedButtonPdf.value = item.href === '/settings' || item.href === '/addition'
    }
// ///////////////////////////////////////////////////////////////////////////
    // обработчик нажатия на кнопку скрытия sidebarMenu
    const onSidebarToggleCollapse = (collapsed) => {
      console.log(collapsed)
      checkedToggleCollapse.value = collapsed
      
    }
   
// ////////////////////////////////////////////////////////////////////////////

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
// ////////////////////////////////////////////////////////
   
// ///////////////////////////////////////////////////////

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
      onEditorReportCreateClick,
      // ///// SIDEBAR //////////
      sidebarWidth,
      toggleSidebar
      // ///////////////////////
      
    
    }
  }



}
</script>
<!-- onSidebarToggleCollapse -->
<!-- @update:collapsed="onSidebarToggleCollapse"    -->
<!-- @item-click="onSidebarMenuItemClick"  -->
<!-- v-if="!checkedSettingsFlag && !checkedToggleCollapse" -->

<template>
  <!-- <Sidebar/> -->
  
  
    <sidebar-menu 
      class="Sdbr"
         
      :theme="theme.value"
      :menu="sidebarMenu.menu"             
      @update:collapsed="onSidebarToggleCollapse(!checkedSettingsFlag && !checkedToggleCollapse), toggleSidebar()"    
      @item-click="onSidebarMenuItemClick" 
      width="450px"
      :style="{width: sidebarWidth}"      
    >


   
     
    <template v-slot:footer v-if="!checkedSettingsFlag && !checkedToggleCollapse">
        <!-- <div v-if="!checkedSettingsFlag && !checkedToggleCollapse "> -->

       
      <section class="radio-section">
      <div class="radio-list">
        <div class="form-check">
          <input
            type="radio"
            id="potentials"
            name="potentials"
            value="potentials"
            v-model="pickedMethod"
            @change="onChangeRadioButtons"
            
          />
          <label for="potentials">potentials</label>           
        </div>

        <div class="form-check">
          <input            
            type="radio"
            id="LSTM"
            name="LSTM"
            value="LSTM"
            v-model="pickedMethod"
            @change="onChangeRadioButtons"
          />
          <label for="LSTM">LSTM</label>     
        </div>
      </div>
      </section>


        <div class="form_select_1">
          <select
            class="form_select"
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


        <div class="row_1">
          <div class="row_1_1" v-if="!checkedButtonPdf">
            <Button class="btn_1" @click="onButtonPdfClick">PDF</Button>
          </div>
          <div v-if="progressBarActive">
            <ProgressBar class="col-10 align-self-center" :value="progressBarValue"></ProgressBar>
          </div>
        </div>
        <!-- :style="{ width: '50rem' }" -->


        <div class="row_1" v-if="!checkedButtonPdf">
          <Button class="btn_1" @click="onButtonDialogClick">Выделение интервалов</Button>
          <Dialog
            class="Dialog_1"
            v-model="dialogActive"
            :visible="dialogActive"
            :closable="false"
            header="Выделение интервалов"
            position="left"
            :modal="true"
            :draggable="false"
            :style="{ width: '50rem'}"
            
          >

          <!-- font-bold block mb-2 -->
            <div class="container">
              <div class="row">
                <label for="input-rolling" class="font-bold block mb-2 ">
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
        <div class="row_1">
          <Button class="btn_1" @click="onButtonDialogEditorClick">Редактор отчетов</Button>
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
             
            </div>
            <template #footer>
             
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
      <!-- </div> -->
      </template>
    
     </sidebar-menu>

  
  <div :style="{'margin-left': sidebarWidth}">
      <div class="common-margin-left">
        <div v-if="!checkedSettingsAndTabsFlag">
          <h1 class="text-center">Метод {{ pickedMethod }}: группа {{ pickedGroup }}</h1>
          <Header/>
          <!-- <TabNav :tabs="['Home', 'Settings', 'Profile']" :selected="selected" @selected="setSelected">
            <Tab :isSelected="selected === 'Home'"><p>Some test text</p> </Tab>
            <Tab :isSelected="selected === 'Settings'"> <h1>More test text</h1> </Tab>
            <Tab :isSelected="selected === 'Profile'">

              <ul>
                <li>List test1</li>
                <li>List test2</li>
                <li>List test3</li>
              </ul>
            
            </Tab>    


          </TabNav> -->

      
        

          <!-- <TabMenu v-model:active-index="activeTabMenu" :model="tabMenu" class="p-tabmenu-nav">
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
          </TabMenu> -->

          
        </div>
        <RouterView
          :active-method="pickedMethod"
          :active-group="pickedGroup"
          :flag-home-page-update="flagHomePageUpdate"
          @updateNewInterval="newAddedIntervalToMenus"
          class="common-margin-left"
        />
      </div>
</div>
</template>

<style scoped>
/* //////////////// Button RADIO///////////////////// */
/* *{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
} */

/* body{
  padding: 0;
  margin: 0;
  color: #fff;
} */
 /* body {
    font-family: var(--font-family);
    font-weight: normal;
    background: var(--surface-ground);
    color: var(--text-color);
    padding: 1rem;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
} */
.Sdbr{
  background-color:#1e293b;
  /* border-start-end-radius: 50px 50px; */
  color: #fff;

}
.radio-section{
  display: flex;
  align-items: end;
  justify-content: start;
  margin-top: 10px;
  margin-left: 1px;
  
}
.form-check {
  padding-left: 0;
  margin-bottom: 1px;
}
.form-check [type="radio"]{
  display: none;
}
.form-check + .form-check{
  margin-top: 1px;
}
.form-check label{
  display: block;
  padding: 10px 20px 10px 50px;
  background: #1e293b;
  /* border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 15px; */
  cursor: pointer;
  font-size: 18px;
  font-weight: 400;
  min-width: 150px;
  white-space: nowrap;
  position: relative;
  /* transition: .4s ease-in-out 0s; */
}
.form-check label:after,
.form-check label:before{
  content: "";
  position: absolute;
  border-radius: 50%;
}
.form-check label:after{
  height: 20px;
  width: 20px;
  border: 2px solid #fff;
  left: 20px;
  top: calc(50% - 10px);
}
.form-check label:before{
  background: #fff;
  height: 10px;
  width: 10px;
  left: 25px;
  top: calc(50% - 5px);
  transform: scale(5);
  opacity: 0;
  visibility: hidden;
  transition: .4s ease-in-out 0s;
}


.form-check [type="radio"]:checked ~ label{
  border-color: #fff;
}
.form-check [type="radio"]:checked ~ label:before{
  opacity: 1;
  visibility: visible;
  transform: scale(1);
}
/* ////////////////////    form-select /////////////////////////// */
.form_select_1{
  
  background: #1e293b;
  border-radius: 5px;
  color: #fff;
  min-width: 150px;
  display: block;
  padding: 10px 20px 10px 50px;
  cursor: pointer;
  padding-left: 1.2em;
  margin-bottom: 5px;
}
.form_select{  
  color: #fff;
  background: #1e293b;
  border-radius: 5px;  
  min-width: 150px;
  display: block;
  padding: 10px 10px 10px 50px;
  cursor: pointer;
  padding-left: 1.2em;
  margin-bottom: 5px;
}
/* ///////////////// BUTTON ///////////////// */
.row_1{
  display: inline-block;
  /* vertical-align: top; */
  margin-bottom: 5px;
  /* padding: 8px 21px; */
  padding: 0px 0px 0px 20px;
  font-size: 14px;
  font-weight: 400;
 
  text-transform: uppercase;
  text-decoration: none;
  margin-bottom: 5px;
}
.btn_1{
  display: inline-block;
  margin-bottom: 5px;
  /* vertical-align: top; */
  background: #1e293b;
  /* padding: 10px 20px 10px 50px; */
  /* padding: 0px 0px 0px 20px; */
  border: 1px solid #fff;
  border-radius: 5px;
  font-size: 14px;
  font-weight: 400;
  color: #fff;
  text-transform: uppercase;
  text-decoration: none;
  
  
  transition: background .1s linear, color .1s linear;
}




.btn_1:hover{
  background-color: #fff;
  color: #1e293b;
}

.row_1_1{
  margin-bottom: 5px;
}
/* ///////////////// ProgressBar ////////////////// */

.progress{
  background-color: #363636;
  width: 270px;
  height: 20px;
  border-radius: 100px;
  overflow: hidden;
}
/* .progress__item{
  border-radius: 100px;
  height: 100%;
  background-image: linear-gradient(90deg, #7ee8fa,#ff8494);
  animation: progressBarActive linear alternate;
  width: 0;
}
@keyframes progressBarActive{
 
  100%{
    width: 100%;
  }
}  */



/* ///////////////////////////////////// */
.Dialog_1{
  background-color: #1e293b;
}
/* ///////////////////////////////////// */
/* .common-margin-left {
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

.collapse-icon{
    position: absolute;
    bottom: 0;
    padding: 0.75em;
    color: rgba(255, 255, 255, 0.7);
    transition: 0.2s linear;
}
.rotate-180{
    transform: rotate(180deg);
    transition: 0.2s linear;
} */


</style>