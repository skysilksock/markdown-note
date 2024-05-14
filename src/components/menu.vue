<script>
import { preUrl } from "../js/const";

export default {
	data() {
		return {
			isShow: false,
			tags: [],
			notes: [],
		};
	},
	mounted() {
		this.getTags();
	},
	methods: {
		open() {
			this.isShow = true;
		},
		close() {
			document.body.style.overflow = "scroll";
			// 不显示菜单
			this.isShow = false;
		},
		getNoteByTag(id) {
			fetch(
				preUrl + "/get-notes-by-tag" + "?username=admin&tag_id=" + id,
				{
					method: "GET",
					headers: {
						"Content-Type": "application/json",
					},
				}
			)
				.then((response) => response.json())
				.then((response) => {
					if (response.status == "ok") {
						this.notes = response.data;
						console.log(this.notes);
					}
				})
				.catch((error) => {
					alert(error);
				});
		},
		getAllNotes() {
			fetch(preUrl + "/get-all-notes" + "?username=admin", {
				method: "GET",
				headers: {
					"Content-Type": "application/json",
				},
			})
				.then((response) => response.json())
				.then((response) => {
					if (response.status == "ok") {
						this.notes = response.data;
						console.log(this.notes);
					}
				})
				.catch((error) => {
					alert(error);
				});
		},
		selectNote(id) {
			this.$emit("selectNote", id);
		},
		getTags() {
			fetch(preUrl + "/get-tags" + "?username=admin", {
				method: "GET",
				headers: {
					"Content-Type": "application/json",
				},
			})
				.then((response) => response.json())
				.then((response) => {
					if (response.status == "ok") {
						this.tags = response.data;
						this.$emit("getTags", this.tags);
					} else {
						alert(response.message);
					}
				})
				.catch((error) => {
					alert(error);
				});
		},
		createTag() {
			const tag_name = prompt("请输入标签名");
			if (tag_name == null) {
				return;
			}
			fetch(
				preUrl + "/create-tag" + "?username=admin&tag_name=" + tag_name,
				{
					method: "GET",
					headers: {
						"Content-Type": "application/json",
					},
				}
			)
				.then((response) => response.json())
				.then((response) => {
					if (response.status == "ok") {
						this.getTags();
					} else {
						alert(response.info);
					}
				})
				.catch((error) => {
					alert(error);
				});
		},
	},
};
</script>

<template>
	<div v-show="isShow" class="menu">
		<div>
			<button class="close-btn" @click="close">关闭</button>
			<h1>全部笔记</h1>
			<ul>
				<button @click="getAllNotes">全部笔记</button>
				<button disabled>未分类</button>
				<button disabled>我的收藏</button>
				<button disabled>最近删除</button>
			</ul>
			<hr />
		</div>
		<div class="tags-container">
			<div class="tag w-half">
				<button
					v-for="item in tags"
					:key="item.id"
					@click="getNoteByTag(item.id)"
					class="w-full"
				>{{ item.name }}</button>
				<button @click="createTag" class="w-full">新建</button>
				<hr class="split-line" />
			</div>
			<div class="note w-half">
				<div v-for="item in notes" :key="item[0]">
					<div style="display: flex;">
						<button @click="selectNote(item[0])" class="note-display grow">{{ item[1] }}</button>
						<button @click="Emit('deleteNote',item[0])" class="note-delete-btn" disabled>删除</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style>
/* 悬浮窗口 */
.menu {
	--menu-height: 60%;
	--menu-width: 50%;
	position: fixed;
	top: calc(50% - var(--menu-height) / 2);
	left: calc(50% - var(--menu-width) / 2);
	width: var(--menu-width);
	height: var(--menu-height);
	/* 一个有区别度的背景颜色 */
	background-color: rgba(255, 255, 255);
	border-radius: 10px;
	/* 添加阴影 */
	box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
	z-index: 999;
	display: flex;
	flex-direction: column;
}

.menu .close-btn {
	position: absolute;
	top: 0;
	right: 0;
	background-color: rgba(255, 255, 255, 1);
}

.tags-container {
	display: flex;
	justify-content: space-between;
	flex-grow: 1;
	height: 200px;
}

.note {
	overflow-y: scroll;
	text-align: center;
}

.grow {
	flex-grow: 1;
}

.w-full {
	width: 100%;
}

.w-half {
	width: 45%;
}

.split-line {
	display: none;
}

@media screen and (max-width: 768px) {
	.menu {
		--menu-width: 100%;
		--menu-height: 100%;
	}
	.tags-container {
		flex-direction: column;
	}
	.note {
		flex-grow: 1;
	}
	.w-half {
		width: 100%;
	}
	.split-line {
		display: block;
		width: 100%;
		height: 0;
	}
	.tags-container {
		justify-content: flex-start;
	}
}
</style>