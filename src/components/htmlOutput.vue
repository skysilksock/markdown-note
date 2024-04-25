<script setup>
import { watch } from "vue";
import "../css/markdown.css";
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

// ! 钩子函数
onMounted(() => {
	box = document.getElementById("html-output");
	console.log(box);
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
</script>

<template>
	<div id="html-output" v-html="text"></div>
</template>

<style scoped>
/* 输入区与输出区的基本样式 */
#html-output {
	margin: 10px;
	padding: 20px;
	border: 1px solid #ddd;
	/* 边框颜色更轻，更柔和 */
	border-radius: 5px;
	/* 轻微的边框圆角 */
	height: 80vh;
	/* 调整高度，确保内容可见 */
	width: 45%;
	/* 调整宽度，为滚动条留出空间 */
	overflow-y: scroll;
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
