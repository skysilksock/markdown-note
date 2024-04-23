<script>
export default {
	emits: ["dateChange", "uploadData", "editToday"],
	props: [],
	data() {
		return {
			date: null,
		};
	},
	mounted() {
		this.date = new Date().toLocaleString();
	},
	watch: {
		date(newValue, oldValue) {
			console.log(newValue);
			this.$emit("dateChange", newValue);
		},
	},
	methods: {
		uploadNote() {
			this.$emit("uploadData");
		},
		editToday() {
			this.$emit("editToday");
		},
	},
};
</script>

<template>
	<div class="container">
		<input type="date" v-model="date" class="margin-[5px]" />
		<button @click="uploadNote" class="margin-[5px]">上传</button>
		<button @click="editToday" class="margin-[5px]">查看</button>
	</div>
</template>

<style scoped>
.container {
	display: flex;
	justify-content: center;
	align-items: center;
}

.margin-\[5px\] {
	margin: 5px;
}
</style>