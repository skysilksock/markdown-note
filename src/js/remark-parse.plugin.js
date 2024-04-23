import { visit } from 'unist-util-visit';

export default function myRemarkPlugin(options) {
    return function transformer(tree, file) {
        visit(tree, 'text', (node, index, parent) => {
            console.log("from plugin.js", node, index, parent);
            // 在这里编写你的语法解析逻辑
            // 例如，将某种特定格式的文本转换为强调节点
            if (node.value.match(/.+(\n:\s.+)+/)) {
                parent.children.splice(index, 1, {
                    type: 'element',
                    children: [{ type: 'text', value: '被转换的文本' }],
                });
            }
        });
    };
};
