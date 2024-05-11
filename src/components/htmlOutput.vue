<script setup>
import { watch } from "vue";
import { onMounted, ref } from "vue";
import { marked } from "marked";

// ! 定义传输信号
const Emit = defineEmits(["element"]);

// ! 定义响应式数据
const props = defineProps({
	text: String,
	scrollHeight: Number,
});

// ! 定义所需变量
let box = null;
let styleSheet = null;
const selectedStyleSheet = ref("src/css/markdown-light.css");

// ! 钩子函数
onMounted(() => {
	box = document.getElementById("html-output");
	styleSheet = document.createElement("link");
	styleSheet.rel = "stylesheet";
	styleSheet.id = "markdown-css";
	styleSheet.href = "src/css/markdown-light.css";
	document.head.appendChild(styleSheet);
});

// ! 监听部分
watch(
	() => props.text,
	(newValue, oldValue) => {
		setTimeout(() => {
			Emit("element", box.childNodes);
		}, 500);
	}
);

watch(
	() => props.scrollHeight,
	(newValue, oldValue) => {
		box.scrollTop = newValue - box.clientHeight;
	}
);

// ! 函数
// 改变css样式
function changeStyle(newStyleSheet) {
	console.log(newStyleSheet);
	styleSheet.href = newStyleSheet;
}
</script>

<template>
	<div class="container">
		<select v-model="selectedStyleSheet" @change="changeStyle(selectedStyleSheet)">
			<option value>默认</option>
			<option value="src/css/markdown-github.css">GIthub</option>
			<option value="src/css/markdown-light.css">学术</option>
			<option value="src/css/markdown-dogs/dogs.css">寒蝉锦书</option>
			<option value="src/css/markdown-cartoon/cartoon.css">卡通</option>
			<!-- 添加更多样式表选项 -->
		</select>
		<div id="html-output" v-html="text"></div>
	</div>
</template>

<style scoped>
.container {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
	height: 90vh;
	/* 调整高度，确保内容可见 */
	width: 50%;
	/* 调整宽度，为滚动条留出空间 */
}

select {
	align-content: flex-end;
	margin: 5px 10px;
	padding: 5px 5px;
	border: 1px solid #ddd;
	border-radius: 5px;
	background-color: white;
	color: #333;
	font-size: 15px;
	cursor: pointer;
	width: max-content;
	box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
	transition: border-color 0.3s ease;
}

select:focus {
	outline: none;
	border-color: dodgerblue;
}

/* 输入区与输出区的基本样式 */
#html-output {
	margin: 10px;
	padding: 20px;
	border: 1px solid #ddd;
	/* 边框颜色更轻，更柔和 */
	border-radius: 5px;
	/* 轻微的边框圆角 */
	overflow-y: scroll;
	flex-grow: 1;
	width: -webkit-fill-available;
	/* 添加滚动条 */
	box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
	/* 添加轻微的阴影，增加层次感 */
}

@media screen and (max-width: 768px) {
	#html-output {
		width: auto;
	}
}
</style>
