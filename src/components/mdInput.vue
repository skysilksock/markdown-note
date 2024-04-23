<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { marked } from "marked";
import { unified } from "unified";
import { markedHighlight } from "marked-highlight";
import hljs from "highlight.js";
// 注意引入样式，你可以前往 node_module 下查看更多的样式主题
import "highlight.js/styles/base16/tomorrow.css";
import { guideBtns } from "../js/const";
import remarkParse from "remark-parse";
import remarkRehype from "remark-rehype";
import rehypeStringify from "rehype-stringify";

// ! 定义响应式数据
const props = defineProps({
	htmlElementNodeList: NodeList,
	date: String,
	notes: Object,
	editToday: Boolean,
});

// ! 定义信号传递函数
const Emit = defineEmits(["parsed", "deleteNote"]);

// ! 暴露属性与方法
defineExpose({
	getMarkdownText,
	getHtmlText,
});

// ! 定义所需变量
const preUrl = "http://112.74.72.34:5001/api";
// const preUrl = "http://127.0.0.1:5001/api";
const MarkdownText = ref("");
const MarkdownTexts = ref([ref({ markdownText: "", noteId: -1 })]);
window.MarkdownTexts = MarkdownTexts.value;
const curidx = ref(0);
window.curidx = curidx;
let markdownInput;
let treeData = null;
let markdownElementList = new Array();
let htmlElementList = new Array();
const markdownEditor = ref("markdown-editor");
const markdowneditorLow = ref("markdown-editor-H-low");
const markdowneditorHigh = ref("markdown-editor-H-high");

// ! 钩子函数
onMounted(() => {
	markdownInput = document.getElementById("markdown-input");
	changeMarkdown(); // 加载自定义markdown语法
	// 高亮拓展
	marked.use(
		markedHighlight({
			langPrefix: "hljs language-",
			highlight(code, lang) {
				const language = hljs.getLanguage(lang) ? lang : "shell";
				return hljs.highlight(code, { language }).value;
			},
		})
	);
});

// ! 定义所需函数
/**
 * ? 防抖函数
 * @param {Function} -fn -需要防抖的函数
 * @param {Number} -t -延迟时间
 * @return {Function} -返回一个函数，该函数在给定的延迟时间内只会执行一次
 */
const debouce = function (fn, t) {
	let timeOut;
	return function (...args) {
		clearTimeout(timeOut);
		timeOut = setTimeout(() => {
			fn(...args);
		}, t);
	};
};

/**
 * ? 将 markdown 文本转换为 html 文本并发送给父组件
 * @param {String} -markdownText -markdown文本
 * @return {void}
 */
const parse = debouce((markdownText) => {
	if (!markdownText) {
		// markdownText = markdownInput.value;
		markdownText = MarkdownText.value;
	}
	let htmlText = marked.parse(markdownText);
	// 发送 htmlText 到父组件
	Emit("parsed", htmlText);
	// 等待页面渲染完成后将Dom元素数据发送到这
	setTimeout(() => {
		analyseHeight(markdownText, props.htmlElementNodeList);
	}, 1000);
}, 500);

/**
 * ? 添加自定义 markdown 语法
 * @return {void}
 */
const changeMarkdown = () => {
	// 定义一个 tokenizer 来识别和解析自定义语法结构 (自定义语法结构: {{选项1|选项2|选项3}} -> 下拉选项框)
	const selectNoteTokenizer = {
		name: "selectNote",
		level: "inline", // 侧边注释在行内出现
		start(src) {
			return src.indexOf("{{");
		}, // 简单的启动检查
		tokenizer(src) {
			const rule = /^\{\{(.+?)\}\}/; // 非贪婪匹配，匹配两个大括号内的内容
			const match = rule.exec(src);
			if (match) {
				return {
					type: "selectNote", // 必须与下面的renderer名称匹配
					raw: match[0], // 匹配的整个字符串，Marked.js将从源文本中消耗这部分
					text: match[1].trim(), // 注释的文本内容，去除首尾空格
				};
			}
		},
	};
	// 定义 renderer 来处理自定义语法结构
	const selectNoteRenderer = {
		name: "selectNote",
		renderer(token) {
			const args = token.text.split("|");
			let optionsText = "";
			for (let arg of args) {
				optionsText += `<option>${arg}</option>`;
			}
			return `<select>${optionsText}</select>`; // 使用class便于CSS样式定义
		},
	};

	// 定义一个 tokenizer 来识别和解析描述列表语法 (语法结构: 标题\n: 描述1\n: 描述2)
	const descriptionNoteTokenizer = {
		name: "descriptionNote",
		level: "inline",
		start(src) {
			return src.match(/.+\n:/)?.index;
		}, // 简单的启动检查
		tokenizer(src) {
			/.+(\n:\s.+)+/; // 无法匹配到带换行符的描述
			/.+\n(:\s[\s\S]+?\n(?=:))+/; // 如果使用block级则选择此规则
			const rule = /.+\n(:\s[\s\S]+)+/;
			const match = rule.exec(src);
			if (match) {
				return {
					type: "descriptionNote", // 必须与下面的renderer名称匹配
					raw: match[0], // 匹配的整个字符串，Marked.js将从源文本中消耗这部分
					text: match[0].trim(), // 注释的文本内容，去除首尾空格
				};
			}
		},
	};
	// 定义 renderer 来处理语法结构
	const descriptionNoteRenderer = {
		name: "descriptionNote",
		renderer(token) {
			const args = token.text.split("\n").reduce((acc, cur, idx) => {
				if (idx === 0) {
					acc.push(cur);
					return acc;
				}
				if (cur[0] === ":") acc.push(cur);
				else {
					acc[acc.length - 1] += "\n" + cur;
				}
				return acc;
			}, []);
			const title = marked.parseInline(args[0]);
			const descriptionList = args.slice(1).reduce((acc, cur) => {
				const value = cur.slice(2);
				return acc + `<dd>${marked.parseInline(value.trim())}</dd>`;
			}, "");
			return `<dl><dt>${title}</dt>${descriptionList}</dl>`;
		},
	};

	// 定义一个 tokenizer 来识别和解析描述勾选框语法 (语法结构: {?Y?} -> 勾选框)
	const checkboxTokenizer = {
		name: "checkbox",
		level: "inline",
		start(src) {
			return src.indexOf("{?");
		}, // 简单的启动检查
		tokenizer(src) {
			const rule = /^\{\?Y?\?\}/;
			const match = rule.exec(src);
			if (match) {
				return {
					type: "checkbox", // 必须与下面的renderer名称匹配
					raw: match[0], // 匹配的整个字符串，Marked.js将从源文本中消耗这部分
					text: match[0], // 注释的文本内容，去除首尾空格
				};
			}
		},
	};
	// 定义 renderer 来处理语法结构
	const checkboxRenderer = {
		name: "checkbox",
		renderer(token) {
			const checked = token.text.includes("Y");
			return `<input type="checkbox" ${checked ? "checked" : ""} />`; // 使用class便于CSS样式定义
		},
	};

	const lineBreakTokenizer = {
		name: "lineBreak",
		level: "inline",
		start(src) {
			return src.indexOf("\n");
		}, // 简单的启动检查
		tokenizer(src) {
			const rule = /^\n/;
			const match = rule.exec(src);
			if (match) {
				return {
					type: "lineBreak", //必须与下面的renderer名称匹配
					raw: match[0],
				};
			}
		},
	};
	const lineBreakRenderer = {
		name: "lineBreak",
		renderer(token) {
			return `<br>`;
		},
	};
	// 注册扩展
	marked.use({ extensions: [selectNoteTokenizer, selectNoteRenderer] });
	marked.use({ extensions: [lineBreakTokenizer, lineBreakRenderer] });
	marked.use({
		extensions: [descriptionNoteTokenizer, descriptionNoteRenderer],
	});
	marked.use({ extensions: [checkboxTokenizer, checkboxRenderer] });
};

/**
 * ? 解析出 Ast 语法树并与 DOM 元素高度对应，返回两个数组
 * @param {String} -markdownText
 * @param {NodeList} -htmlNodeList
 * @param {Number[][]}
 */
function analyseHeight(markdownText, htmlNodeList) {
	parseMarkdown(markdownText);
	htmlNodeList = Array.from(htmlNodeList).filter((node) => {
		if (node.nodeType === 3) return false; // 过滤文本节点
		if (node.nodeName === "P" && node.innerText === "") return false; // 默认在inline前加入无内容p标签，过滤！
		return true;
	});
	const Ast = Array.from(treeData.children).filter(
		(child) => child.type === "element"
	);
	console.log(treeData, treeData.children.length);
	Ast.forEach((child, idx) => {
		if (idx >= htmlNodeList.length) return;
		console.log(child, htmlNodeList[idx]);
		const offset = child.position.start.line * 15;
		markdownElementList.push(offset);
		htmlElementList.push(htmlNodeList[idx].offsetTop);
	});
	// console.log(markdownElementList, htmlElementList);
	return [markdownElementList, htmlElementList];
}

// ? 自定义插件，用于获取Ast语法树
const customPlugin = () => (tree, file) => {
	// console.log("tree", tree);
	treeData = tree;
};

/**
 * ? 将markdown文本转换为Ast语法树
 * @param {String} -markdownText -markdown文本
 * @return {void}
 */
function parseMarkdown(markdownText) {
	unified()
		.use(remarkParse)
		// .use(remarkWarning)
		.use(remarkRehype)
		.use(customPlugin)
		.use(rehypeStringify)
		.process(markdownText, (err, file) => {
			if (err) {
				console.error(err);
				return;
			}
			// console.log(treeData);
		});
}

/**
 * ? 在光标处插入文本
 * @param {String} -textToInsert -要插入的文本
 * @return {void}
 */
function InsertAtEditor(textToInsert) {
	const field = markdownInput;
	var startPos = field.selectionStart;
	var endPos = field.selectionEnd;

	// 更新 field 的内容，在当前光标位置插入文本
	field.value =
		field.value.substring(0, startPos) +
		textToInsert +
		field.value.substring(endPos, field.value.length);

	// 移动光标到插入文本的后面
	field.selectionStart = field.selectionEnd = startPos + textToInsert.length;

	// 保持焦点
	field.focus();
	MarkdownText.value = field.value;
}

/**
 * ? 用于比较今日日期和输入日期是否相同，如果相同则显示编辑框，不同则显示列表展示输入日期上传的笔记
 * @param {String} date1
 * @param {String} date2
 * @return {Boolean}
 */
function isSameDay(date1, date2 = null) {
	date2 = new Date().toLocaleString();
	return date1 == date2;
}

/**
 * ? 获取markdown文本
 * @return {string}
 */
function getMarkdownText() {
	// return markdownInput.value;
	return MarkdownText.value;
}

/**
 * ? 获取html文本
 * @return {String}
 */
function getHtmlText() {
	// return marked.parse(markdownInput.value);
	return marked.parse(MarkdownText.value);
}

/**
 * ? 切换选中笔记
 * @param {Number} -idx -索引
 * @return {void}
 */
function selectText(idx) {
	// 保存当前更改
	MarkdownTexts.value[curidx.value].value.markdownText = MarkdownText.value;
	// 更新当前选中索引和显示文本
	curidx.value = idx;
	MarkdownText.value = MarkdownTexts.value[idx].value.markdownText;
}

/**
 * ? 添加笔记
 * @param {String} -markdownText -markdown文本
 * @param {String} -noteId -笔记在数据库中的主键 id
 * @return {void}
 */
async function selectNote(noteId) {
	// 如果当前已有该笔记内容则选中已有内容
	for (let i = 0; i < MarkdownTexts.value.length; i++) {
		if (MarkdownTexts.value[i].value.noteId == noteId) {
			selectText(i);
			document.getElementById(`text-btn-${i}`).focus(); // 聚焦提醒
			// 后期加入非阻塞弹窗提示
			return;
		}
	}
	// 拿到对应id的笔记文本内容
	let markdownText;
	await fetch(preUrl + "/get-note", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			id: noteId,
		}),
	})
		.then((response) => response.json())
		.then((response) => {
			if (response.status == "ok") {
				markdownText = response.data;
			} else {
				alert("笔记获取失败", response.info);
			}
		})
		.catch((error) => {
			console.error("Error:", error);
		});
	parse(markdownText);
	const tmp = ref({ markdownText, noteId });
	MarkdownTexts.value.push(tmp);
	selectText(MarkdownTexts.value.length - 1);
}

/**
 * ? 关闭当前页面并选中顺序下一个笔记，如果当前是最后一个则选择最后一个
 */
function closeText() {
	if (curidx.value == MarkdownTexts.value.length - 1) {
		curidx.value -= 1;
		MarkdownTexts.value.splice(curidx.value + 1, 1);
	} else {
		MarkdownTexts.value.splice(curidx.value, 1);
	}
	// 更新当前选中索引和显示文本
	MarkdownText.value = MarkdownTexts.value[curidx.value].value.markdownText;
	document.getElementById(`text-btn-${curidx.value}`).focus();
}

/**
 * ? 更新笔记
 * @return {void}
 */
function updateNote() {
	const markdownText = getMarkdownText();
	fetch(preUrl + "/update-note", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify({
			id: MarkdownTexts.value[curidx.value].value.noteId,
			markdownText: markdownText,
		}),
	})
		.then((response) => response.json())
		.then((response) => {
			if (response.status == "ok") {
				alert("笔记更新成功");
			} else {
				alert("笔记更新失败", response.info);
			}
		})
		.catch((error) => {
			console.error("Error:", error);
		});
}

// ! 计算属性
const displayEditBtn = computed(() => {
	return MarkdownTexts.value[curidx.value].value.noteId != -1;
});

// ! 监听器
watch(
	MarkdownText,
	debouce((newValue, oldValue) => {
		let htmlText = marked.parse(newValue);
		// 发送 htmlText 到父组件
		Emit("parsed", htmlText);
	}, 500)
);
</script>

<template>
	<div :class="[markdownEditor, editToday ? markdowneditorLow : markdowneditorHigh]">
		<div class="editor-menu">
			<div class="guide-btns">
				<button
					v-for="(item, idx) in guideBtns"
					:key="idx"
					@click="InsertAtEditor(item.message)"
					class="guide-btn"
				>
					<img :src="item.url" />
				</button>
			</div>
			<div>
				<button v-show="MarkdownTexts.length > 1" @click="closeText">关闭</button>
				<button v-show="displayEditBtn" @click="updateNote">更新</button>
			</div>
		</div>
		<textarea v-model="MarkdownText" id="markdown-input" placeholder="输入Markdown文本..."></textarea>
		<div class="text-btn-lst">
			<button
				v-for="(item, idx) in MarkdownTexts"
				:key="idx"
				@click="selectText(idx)"
				class="text-btn"
				:id="'text-btn-'+idx"
			>{{ idx + 1 }}</button>
		</div>
	</div>
	<div v-show="editToday">
		<div v-if="notes.length" class="note-list">
			<div v-for="item in notes" :key="item[0]">
				<div style="display: flex;">
					<button @click="selectNote(item[0])" class="note-display grow">{{ item[1] }}</button>
					<button @click="Emit('deleteNote',item[0])" class="note-delete-btn">删除</button>
				</div>
			</div>
		</div>
		<div v-else class="note-list">暂无笔记</div>
	</div>
</template>

<style scoped>
/* 输入区与输出区的基本样式 */
textarea {
	margin-left: 10px;
	margin-right: 10px;
	padding: 20px;
	border: 1px solid #ddd;
	border-radius: 5px;
	max-width: -webkit-fill-available;
	flex-grow: 1;
	overflow-y: scroll;
	box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
	outline: none;
}

.grow {
	flex-grow: 1;
}

.markdown-editor {
	width: 100%;
	display: flex;
	flex-direction: column;
}

.markdown-editor-H-low {
	height: 50vh;
}

.markdown-editor-H-high {
	height: 80vh;
}

.editor-menu {
	margin-left: 10px;
	margin-right: 10px;
	display: flex;
	justify-content: space-between;
}

.note-list {
	width: auto;
	height: 20vh;
	margin-left: 10px;
	margin-right: 10px;
	box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
	overflow-y: scroll;
	text-align: center;
	font-size: 1em;
	border-radius: 5px;
}

.note-display {
	width: 80%;
	margin: 1px;
	border: 1px solid #ebebeb;
}

.note-delete-btn {
	margin: 1px;
	border: 1px solid #ebebeb;
}

.note-display:hover,
.note-delete-btn:hover {
	border: 1px solid #646cff;
}

.guide-btn {
	display: flex;
	width: 30px;
	height: 30px;
	padding: 0px;
	margin-right: 10px;
	justify-content: center;
}

.guide-btns {
	/* height: 30px; */
	/* padding: 0px; */
	display: flex;
	flex-direction: row;
	align-items: flex-end;
}

.text-btn-lst {
	margin-left: 10px;
	margin-right: 10px;
}

.text-btn {
	font-size: 10px;
	height: 30px;
}

img {
	width: 100%;
}
</style>
