import { createApp } from 'vue'
import { createPinia } from 'pinia'

import PrimeVue from 'primevue/config'
import 'primevue/resources/themes/bootstrap4-light-blue/theme.css'
import 'primeicons/primeicons.css'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'

import App from './App.vue'
import router from './router'

import '@fortawesome/fontawesome-free/js/all'

import globalComponents from './components/global'

import Button from 'primevue/button'
import TabMenu from 'primevue/tabmenu'
import InputNumber from 'primevue/inputnumber'
import Calendar from 'primevue/calendar'
import Checkbox from 'primevue/checkbox'
import ProgressBar from 'primevue/progressbar'
import ProgressSpinner from 'primevue/progressspinner'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.use(globalComponents)

app.use(PrimeVue)
app.component('Button', Button)
app.component('TabMenu', TabMenu)
app.component('InputNumber', InputNumber)
app.component('Calendar', Calendar)
app.component('Checkbox', Checkbox)
app.component('ProgressBar', ProgressBar)
app.component('ProgressSpinner', ProgressSpinner)
app.component('Dialog', Dialog)
app.component('InputText', InputText)

app.mount('#app')
