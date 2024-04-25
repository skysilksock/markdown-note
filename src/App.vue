<script setup>
import { onMounted, ref, watch } from "vue";
import Markdown from "./components/mdInput.vue";
import Html from "./components/htmlOutput.vue";
import Menu from "./components/others.vue";

import { preUrl } from "./js/const";

// ! 定义变量
// const preUrl = "http://127.0.0.1:5001/api";
const htmlText = ref("解析后的HTML将会在这里显示...");
const htmlElementNodeList = ref(null);
const uploadData = ref(null);
const markdownPage = ref(null);
const date = ref(new Date().toLocaleString());
const notes = ref([]);
const editToday = ref(false);
const scrollHeight = ref(0);

// 更新渲染页面，并收集渲染页面元素并传给编辑界面
const sendHtml = (data) => {
	htmlText.value = data;
};

// 将带高度信息的Dom元素传给编辑界面
const sendHtmlElementNodeList = (data) => {
	htmlElementNodeList.value = data;
};

const dateChange = (data) => {
	date.value = data;
	getNoteList();
};

const getNoteList = () => {
	fetch(preUrl + "/get-note-list", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			time: date.value,
		}),
	})
		.then((response) => response.json())
		.then((response) => {
			if (response.status == "ok") {
				// console.log("用于渲染的数据", response.data);
				notes.value = response.data;
			} else {
				alert("笔记获取失败", response.info);
			}
		})
		.catch((error) => {
			console.error("Error:", error);
		});
};

/**
 * 上传笔记
 * @param {undefined}
 * @return {void}
 */
const sendUploadData = (data) => {
	const time = new Date().toLocaleString();
	const markdownText = markdownPage.value.getMarkdownText();
	if (!markdownText) {
		alert("笔记不能为空");
		return;
	}
	// 笔记命名
	const noteName = prompt("请输入笔记名称", "无标题");
	if (noteName == null) {
		return; // 取消
	}
	fetch(preUrl + "/insert-note", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			time: time,
			markdownText: markdownText,
			noteName: noteName,
		}),
	})
		.then((response) => response.json())
		.then((response) => {
			if (response.status == "ok") {
				alert("笔记上传成功");
				getNoteList();
			} else {
				alert("笔记上传失败", response.info);
			}
		})
		.catch((error) => {
			console.error("Error:", error);
		});
};

function editTodayFunc() {
	dateChange(date.value);
	editToday.value = !editToday.value;
}

const deleteNote = (data) => {
	fetch(preUrl + "/delete-note", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			id: data,
		}),
	})
		.then((response) => response.json())
		.then((response) => {
			if (response.status == "ok") {
				alert("笔记删除成功");
				getNoteList();
			}
		})
		.catch((error) => {
			console.error("Error:", error);
		});
};

const scrollHtml = (data) => {
	scrollHeight.value = data;
};
</script>

<template>
	<!-- <HelloWorld /> -->
	<div class="markdown-preview">
		<div class="markdown-preview-left">
			<Markdown
				@parsed="sendHtml"
				@deleteNote="deleteNote"
				@scroll="scrollHtml"
				:htmlElementNodeList="htmlElementNodeList"
				:date="date"
				:notes="notes"
				:editToday="editToday"
				ref="markdownPage"
			/>
			<Menu @dateChange="dateChange" @uploadData="sendUploadData" @editToday="editTodayFunc" />
		</div>
		<Html @Element="sendHtmlElementNodeList" :text="htmlText" :scrollHeight="scrollHeight" />
	</div>
</template>

<style scoped>
.markdown-preview {
	display: flex;
	flex-direction: row;
	justify-content: space-between;
}

.markdown-preview-left {
	width: 50%;
	display: flex;
	flex-direction: column;
	justify-content: space-between;
}

@media screen and (max-width: 768px) {
	.markdown-preview {
		flex-direction: column;
	}

	.markdown-preview-left {
		width: 100%;
	}
}
</style>
