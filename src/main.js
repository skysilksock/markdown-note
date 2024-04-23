import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

const preUrl = "http://112.74.72.34:5001/api";

Date.prototype.toLocaleString = function () {
    let dd = ["00", "01", "02", "03", "04", "05", "06", "07", "08", "09"];
    return [
        this.getFullYear(),
        dd[this.getMonth() + 1] || this.getMonth() + 1,
        dd[this.getDate()] || this.getDate(),
    ].join("-");
};

createApp(App).mount('#app')