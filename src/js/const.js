const guideBtns = [
    {
        url: "/title.svg",
        message: "# 标题1\n## 标题2\n### 标题3\n#### 标题4\n##### 标题5\n###### 标题6",
    },
    {
        url: "/table.svg",
        message: "|列名1|列名2|\n|:-:|:-:|\n|内容1|内容2|"
    },
    {
        url: "/description.svg",
        message: "规划\n:\n{??} 内容\n{??} 内容"
    },
    {
        url: "/checkbox.svg",
        message: "{?Y?}"
    },
    {
        url: "/select.svg",
        message: "{{选项1|选项2|选项3}}"
    },
    {
        url: "/link.svg",
        message: "[ 显示的内容 ]( 网站URL )"
    }
];

const preUrl = "http://112.74.72.34:5001/api";
// const preUrl = "http://79.8.51.175:5001";
// const preUrl = "http://127.0.0.1:5001/api";

export { guideBtns, preUrl };